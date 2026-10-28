"""OpenChat (rotech.dev) 1.4.1 协议客户端

逆向自 open.chat.gpt.aichat.bot.free.app v1.4.1
协议要点：
  POST https://gptapi.rotech.dev/api/{path}   Content-Type: x-www-form-urlencoded
  form: pkg / modetype=1 / version / data
  data = Base64_NOWRAP( AES-128-CBC-PKCS5( compact_json, key, iv ) )
  key = md5(seed)[0:16] ascii, iv = md5(seed)[16:32] ascii
  seed = librocore.so 内嵌证书 DER 的小写 hex（与 APK 签名无关，mod 版通用）
响应同样是 AES 加密的 Base64。
"""
from __future__ import annotations
import base64, hashlib, json, os, random, threading, time, uuid as _uuid
from dataclasses import dataclass, field
from typing import Any, Optional

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

PKG = "open.chat.gpt.aichat.bot.free.app"
BASE = "https://gptapi.rotech.dev/api/"
VERSION = "1.4.1"

# librocore.so 内嵌的证书 DER（小写 hex，偏移 0x1298）
SEED = os.environ.get("OPENCHAT_SEED") or (
    "3082058930820371a003020102021500d35a488404281bb910ad93994ce87595545fb3c6300d06092a864886f70d01010b05"
    "003074310b3009060355040613025553311330110603550408130a43616c69666f726e6961311630140603550407130d4d6f"
    "756e7461696e205669657731143012060355040a130b476f6f676c6520496e632e3110300e060355040b1307416e64726f69"
    "643110300e06035504031307416e64726f69643020170d3233303333313034333631355a180f323035333033333130343336"
    "31355a3074310b3009060355040613025553311330110603550408130a43616c69666f726e6961311630140603550407130d"
    "4d6f756e7461696e205669657731143012060355040a130b476f6f676c6520496e632e3110300e060355040b1307416e6472"
    "6f69643110300e06035504031307416e64726f696430820222300d06092a864886f70d01010105000382020f003082020a02"
    "82020100b8c1a88119517b04bfccb1c0a0549e06245ccbf2eed130d6a3d2682aa5bb3270bf5b5d491e5f8591036516a2ef2e"
    "f74b32bc7db51637e9321f827f54a9457eaf865fbd702577f3d049564e10feddd2c5f24c2e0812f9f43fe07f2938d1dcd906"
    "67317daad89c99e989ba1668967129c91fea83f908975d763263ff8aad0bb1f4da42cacecb1e46f99b1c352c0b770b2df18b"
    "f5d79ecc14e81c249043e5c081040c1a8dc3f7f2b045712d194108435a010ebd4ca790d3ff38f507426b6f41f1f2b04be81f"
    "01187c7aab3425f91a972b2ba750c9fb3c7d624aab085f9c08b31c0da6c30f7ff0a65df875e70e5a1f420bdbaee257610850"
    "701b44ba7cbe3849ac118e4d4049f7d831cbb867a334d5f506ec56cdd13c7003186327ee0fcfda13973f682609cce29e7efc"
    "dc448c9b49ffb6bc96cd6cbfff4d145d2258a0883da66e048e65039f06469692e6c765558bbdc6f27e1ac2ca8244fe279269"
    "457be100c58196df8e67cc3f5f0bf49cb206441e5d1ca5e44d8be9e94e274d4ac59149e711b3c51604f3bb5138021c0cc83d"
    "b1ab51765830f8bc17df16a411a792a6701bfbc947d6aa58ff7e590cd1b917ea534075fce22feebefb8de35a07b512eb059e"
    "a2693e5cdf0ecf3bb7b98cf45c89769c3ea35e0101efcff6650b68cccc823b34c079e3c4a63479537895dea194407e6d4111"
    "31ccba4b2bd25ff40133aa60221e092d0203010001a310300e300c0603551d13040530030101ff300d06092a864886f70d01"
    "010b050003820201000de6632386dc399abf5c1e29b036e7748096b67ba32a910baa6f1eb6773bc96e2b009aa9768a2bbf63"
    "359a57263af28c12549a5037e958cf84d2f45935dc8d18edc4e6a44f3804f5476859b524ee3613ab0e3c840372eef8d26af4"
    "038adad892c08ae37c3938baec6a734f7ce61957f187ae1b26fe12e4ae6f033aa3dbad6c1af8f6f98eb3856dc29d3af666f4"
    "8ed3fdf6b96101b3d2573f2bf72f332e82c3bb9758b0bd8486250892f42129599fc795fdf5f0b17eaa57abe405a323b2509b"
    "9a960e6e02fb63245a8152e0f770862c6ec757d4e6c167ebc4ebb95c3c4282ec17111b18a0250aeb522dcf3ec5cc49518f71"
    "a92e67562601824017be6d528dcb26e85456c5e0bb1852793dc734a0f42252d9770a034f6f28cae49dd8ce50e1ebc8bb2b44"
    "93267ee25d686ea3cdc93f0630875cc283aa847e2d974c407cd0ffb16b21d8f82b7e54607620fa38518868b3a0e509e33790"
    "4a4cdf3cc937be05cdfc52fe5a3005018e04b9bd6f15471c444a5b010c9d4a1280a4f758f26f8a68e78039973f0ebdda1f15"
    "2e4bcc3e75ee60fe7492fd74de17cdb2642f1fc19c3d34b0e5b2fc23e5fd5e36b9ca22caee91660b25c40665e0a9ef911bbc"
    "ba0ad8afb435dcf9d172c531df2f5c662f894e4e61828aebbe6e76c742092048dfb348409c85951391528a9dee6580bd2f98"
    "2d2bec583932824f0aa830b4666cd0edfbc372aa71"
)
_MD5 = hashlib.md5(SEED.lower().encode()).hexdigest()
KEY = _MD5[:16].encode()
IV = _MD5[16:].encode()


def encrypt(plain: str) -> str:
    return base64.b64encode(AES.new(KEY, AES.MODE_CBC, IV).encrypt(pad(plain.encode(), 16))).decode()


def decrypt(cipher_b64: str) -> str:
    return unpad(AES.new(KEY, AES.MODE_CBC, IV).decrypt(base64.b64decode(cipher_b64)), 16).decode()


# app 内的模型代号 -> 对外暴露名
MODELS = {
    "auto": "openchat-auto",
    "gpt5": "openchat-gpt5",
    "gpt4o": "openchat-gpt4o",
    "claude45": "openchat-claude45",
    "gemini3": "openchat-gemini3",
    "grok41": "openchat-grok41",
}
MODEL_ALIAS = {
    # 常见 OpenAI 命名 -> 上游代号
    "gpt-5": "gpt5", "gpt-5-nano": "auto", "gpt-4o": "gpt4o", "gpt-4.1": "gpt4o",
    "claude-4.5": "claude45", "claude-sonnet-4.5": "claude45", "claude": "claude45",
    "gemini-3": "gemini3", "gemini": "gemini3", "grok-4.1": "grok41", "grok": "grok41",
    "auto": "auto", "gpt5": "gpt5", "gpt4o": "gpt4o", "claude45": "claude45",
    "gemini3": "gemini3", "grok41": "grok41",
}
# 允许直接传对外名（openchat-xxx）
for _up, _pub in list(MODELS.items()):
    MODEL_ALIAS[_pub] = _up
    MODEL_ALIAS[_pub.replace("openchat-", "")] = _up

LENGS = {"auto", "detail", "short"}


@dataclass
class Reply:
    content: str
    model: str
    conversation_sign: str
    latency: float
    raw: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return bool(self.content)


class OpenChatError(RuntimeError):
    def __init__(self, code, msg, raw=None):
        super().__init__(f"[{code}] {msg}")
        self.code, self.msg, self.raw = code, msg, raw


class Client:
    """线程安全客户端；内部复用连接池。"""

    def __init__(self, version: str = VERSION, use_proxy: bool = False, timeout: int = 180):
        self.version = version
        self.timeout = timeout
        self._s = requests.Session()
        self._s.trust_env = use_proxy  # False = 忽略系统代理，直连
        ad = requests.adapters.HTTPAdapter(pool_connections=64, pool_maxsize=64, max_retries=2)
        self._s.mount("https://", ad)
        self._s.mount("http://", ad)
        self._lock = threading.Lock()

    # ---------- 底层 ----------
    def _post(self, path: str, payload: dict) -> Any:
        body = {
            "pkg": PKG,
            "modetype": "1",
            "version": self.version,
            # 必须紧凑 JSON：上游严格解析，带空格会返回 param error
            "data": encrypt(json.dumps(payload, separators=(",", ":"), ensure_ascii=False)),
        }
        r = self._s.post(BASE + path, data=body, timeout=self.timeout)
        text = (r.text or "").strip()
        if not text:
            raise OpenChatError("empty_response", f"HTTP {r.status_code} empty body", None)
        try:
            outer = json.loads(decrypt(text))
        except Exception as exc:  # 解密/解析失败
            raise OpenChatError("decode_error", f"cannot decrypt response: {text[:80]}", {"err": str(exc)}) from exc
        if not isinstance(outer, dict):
            raise OpenChatError("bad_response", str(outer)[:120], outer)
        if outer.get("code") != 200:
            raise OpenChatError(outer.get("code"), outer.get("msg") or "upstream error", outer)
        return outer

    # ---------- 业务 ----------
    @staticmethod
    def new_session() -> tuple[str, str]:
        uid = str(_uuid.uuid4())
        return uid, f"{uid}#{int(time.time() * 1000)}"

    def chat(
        self,
        question: str,
        *,
        uuid: Optional[str] = None,
        sign: Optional[str] = None,
        model: str = "auto",
        length: str = "auto",
        style: str = "auto",
        lang: str = "en",
        msg_id: Optional[int] = None,
    ) -> Reply:
        if model not in MODELS:
            model = MODEL_ALIAS.get(model, "auto")
        if length not in LENGS:
            length = "auto"
        if uuid is None:
            uuid, sign = self.new_session()
        elif sign is None:
            sign = f"{uuid}#{int(time.time() * 1000)}"
        ts = int(time.time() * 1000)
        payload = {
            "uuid": uuid,
            "conversation_sign": sign,
            "timestamp": ts,
            "question": question,
            "lang": lang,
            "model": model,
            "length": length,
            "style": style,
        }
        if msg_id is not None:
            payload["id"] = msg_id
        t0 = time.time()
        outer = self._post("v6/chat/common", payload)
        data = outer.get("data") or {}
        trace = (data.get("service_trace") or {}).get("primary") or {}
        content = data.get("content") or ""
        if not trace.get("success", True) and not content:
            raise OpenChatError("upstream_fail", trace.get("error_type") or "server_error", outer)
        return Reply(content=content, model=model, conversation_sign=sign or "",
                     latency=time.time() - t0, raw=outer)

    def image_generate(self, prompt: str, **kw) -> dict:
        return self._post("v6/image/generate", {"question": prompt, **kw})

    def image_result(self, uuid: str, sign: str) -> dict:
        return self._post("v6/image/generate_result", {"uuid": uuid, "conversation_sign": sign})


_default: Optional[Client] = None
_default_lock = threading.Lock()


def default_client() -> Client:
    global _default
    with _default_lock:
        if _default is None:
            _default = Client(use_proxy=os.environ.get("OPENCHAT_PROXY") == "1")
        return _default
