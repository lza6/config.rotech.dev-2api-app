"""OpenChat 1.4.1 -> OpenAI 兼容网关

用法:
    python server.py                 # 监听 0.0.0.0:8941
    OPENCHAT_PORT=9000 python server.py

端点:
    GET  /                      demo 页
    GET  /v1/models             模型列表
    POST /v1/chat/completions   OpenAI Chat Completions（支持 stream=true 伪流式）
    GET  /health                健康检查
"""
from __future__ import annotations

import asyncio
import json
import os
import time
import uuid as _uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

import openchat

PORT = int(os.environ.get("OPENCHAT_PORT", "8941"))
DEFAULT_MODEL = os.environ.get("OPENCHAT_DEFAULT_MODEL", "auto")
# 上游只接受单条 question，这里把多轮消息压成一份对话记录
MAX_CHARS = int(os.environ.get("OPENCHAT_MAX_CHARS", "12000"))
LANG = os.environ.get("OPENCHAT_LANG", "en")

app = FastAPI(title="OpenChat 2API", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

client = openchat.default_client()


class ChatMessage(BaseModel):
    role: str
    content: Any


class ChatRequest(BaseModel):
    model: Optional[str] = DEFAULT_MODEL
    messages: List[ChatMessage] = []
    stream: Optional[bool] = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    length: Optional[str] = None      # auto | detail | short（上游原生参数）
    style: Optional[str] = None       # auto | academic | creativity | humor | major | popular
    session: Optional[str] = None     # 同 session 复用 conversation_sign 保上下文


def _flatten(messages: List[ChatMessage]) -> str:
    """把 OpenAI messages 压成上游能吃的单条 question。"""
    parts: List[str] = []
    for m in messages:
        c = m.content
        if isinstance(c, list):  # 多模态数组 -> 取文本块
            c = "".join(
                b.get("text", "") if isinstance(b, dict) else str(b) for b in c
            )
        c = (c or "").strip()
        if not c:
            continue
        if m.role == "system":
            parts.append(f"[System]\n{c}")
        elif m.role == "assistant":
            parts.append(f"[Assistant]\n{c}")
        else:
            parts.append(c if len(messages) == 1 else f"[User]\n{c}")
    text = "\n\n".join(parts)
    return text[-MAX_CHARS:]


def _estimate_tokens(text: str) -> int:
    # 粗略估算：中文 1 字≈1 token，英文 ≈4 字符 1 token
    cn = sum(1 for ch in text if "一" <= ch <= "鿿")
    other = len(text) - cn
    return max(1, cn + other // 4)


def _err(msg: str, code: str = "upstream_error", status: int = 502) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"message": msg, "type": code, "code": code}},
    )


@app.get("/health")
def health():
    return {"status": "ok", "upstream": openchat.BASE, "version": openchat.VERSION}


@app.get("/v1/models")
def models():
    now = int(time.time())
    data = []
    for upstream, name in openchat.MODELS.items():
        data.append(
            {
                "id": name,
                "object": "model",
                "created": now,
                "owned_by": "rotech-dev",
                "upstream": upstream,
            }
        )
    return {"object": "list", "data": data}


def _prepare(req: ChatRequest):
    prompt = _flatten(req.messages)
    if not prompt:
        return None, "empty messages"
    # session 复用：同一 session -> 同一 uuid + 同一 conversation_sign
    if req.session:
        uid = str(_uuid.uuid5(_uuid.NAMESPACE_URL, req.session))
        sign = f"{uid}#{req.session}"
        sign_key = sign
    else:
        uid, sign_key = openchat.Client.new_session()
        sign = sign_key
    return (prompt, uid, sign), None


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    prepared, err = _prepare(req)
    if err:
        return _err(err, "invalid_request_error", 400)
    prompt, uid, sign = prepared
    model = req.model or DEFAULT_MODEL
    length = req.length or "auto"
    style = req.style or "auto"

    def _run() -> openchat.Reply:
        return client.chat(
            prompt, uuid=uid, sign=sign, model=model, length=length,
            style=style, lang=LANG,
        )

    cmpl_id = f"chatcmpl-{_uuid.uuid4().hex[:24]}"
    created = int(time.time())

    if not req.stream:
        try:
            reply = await asyncio.to_thread(_run)
        except openchat.OpenChatError as exc:
            return _err(str(exc), "upstream_error", 502)
        except Exception as exc:  # noqa: BLE001
            return _err(f"{type(exc).__name__}: {exc}", "internal_error", 500)
        pt = _estimate_tokens(prompt)
        ct = _estimate_tokens(reply.content)
        return {
            "id": cmpl_id,
            "object": "chat.completion",
            "created": created,
            "model": openchat.MODELS.get(reply.model, reply.model),
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": reply.content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": pt,
                "completion_tokens": ct,
                "total_tokens": pt + ct,
            },
            "upstream_latency": round(reply.latency, 3),
        }

    async def gen():
        try:
            reply = await asyncio.to_thread(_run)
        except Exception as exc:  # noqa: BLE001
            payload = {"error": {"message": str(exc), "type": "upstream_error"}}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return
        # 上游一次性返回，这里按 12 字符切片做伪流式，体验与真流式接近
        content = reply.content
        step = 12
        first = {
            "id": cmpl_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": openchat.MODELS.get(reply.model, reply.model),
            "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
        }
        yield f"data: {json.dumps(first, ensure_ascii=False)}\n\n"
        for i in range(0, len(content), step):
            chunk = {
                "id": cmpl_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": openchat.MODELS.get(reply.model, reply.model),
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": content[i : i + step]},
                        "finish_reason": None,
                    }
                ],
            }
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.01)
        last = {
            "id": cmpl_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": openchat.MODELS.get(reply.model, reply.model),
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(last, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join(os.path.dirname(__file__), "demo.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
