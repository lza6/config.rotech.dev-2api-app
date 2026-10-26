"""
OpenChat (gptapi.rotech.dev) 协议本地演示代理 — OpenAI 兼容接口
用法:
  set OPENCHAT_AES_KEY=1c1d083bc424270a     (可选, 默认从 APK 证书自动派生)
  set OPENCHAT_AES_IV=7d719764f224e6cd
  python demo_server.py
然后浏览器打开 http://localhost:8901 (demo.html), 或用任意 OpenAI 客户端:
  POST http://localhost:8901/v1/chat/completions  {"model":"openchat","messages":[...]}

仅用于安全研究验证逆向成果, 请勿高频调用。上游若返回拒绝密文会如实转报。
"""
import base64
import hashlib
import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

APK = os.environ.get("OPENCHAT_APK", r"D:\notrack-2api-app\openchat134\openchat-1.3.4.apk")
CHAT_URL = "https://gptapi.rotech.dev/api/v5/chat/common_question"
PKG = "open.chat.gpt.aichat.bot.free.app"
UA = "okhttp/4.12.0"
PORT = 8901

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

_cache = {}


def derive_key_iv(apk_path=APK):
    """从 APK 签名证书派生 AES key/IV: md5hex(cert_DER_hex)[:16]=key, [16:]=IV。"""
    if "key" in _cache:
        return _cache["key"], _cache["iv"]
    key_env = os.environ.get("OPENCHAT_AES_KEY")
    iv_env = os.environ.get("OPENCHAT_AES_IV")
    if key_env and iv_env:
        _cache["key"], _cache["iv"] = key_env.encode(), iv_env.encode()
        return _cache["key"], _cache["iv"]
    with zipfile.ZipFile(apk_path) as z:
        rsa_entry = next(n for n in z.namelist() if n.endswith(".RSA"))
        pkcs7 = z.read(rsa_entry)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".p7") as f:
        f.write(pkcs7)
        tmp = f.name
    try:
        pem = subprocess.run(
            ["openssl", "pkcs7", "-inform", "DER", "-in", tmp, "-print_certs"],
            capture_output=True).stdout
        der = subprocess.run(["openssl", "x509", "-outform", "DER"],
                             input=pem, capture_output=True).stdout
    finally:
        os.unlink(tmp)
    digest = hashlib.md5(der.hex().encode()).hexdigest()
    _cache["key"], _cache["iv"] = digest[:16].encode(), digest[16:].encode()
    return _cache["key"], _cache["iv"]


def aes_enc(plaintext: str) -> str:
    key, iv = derive_key_iv()
    padder = PKCS7(128).padder()
    data = padder.update(plaintext.encode()) + padder.finalize()
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return base64.b64encode(enc.update(data) + enc.finalize()).decode()


def aes_dec(b64data: str) -> str:
    key, iv = derive_key_iv()
    raw = base64.b64decode(b64data)
    dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    padded = dec.update(raw) + dec.finalize()
    unpadder = PKCS7(128).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode()


def upstream_chat(question: str, lang="zh", model="1", length="1", style="1"):
    payload = {
        "uuid": os.environ.get("OPENCHAT_UUID", str(uuid.uuid4())),
        "gp_token": os.environ.get("OPENCHAT_GP_TOKEN", ""),
        "conversation_sign": f"conv-{int(time.time() * 1000)}",
        "timestamp": int(time.time() * 1000),
        "question": question,
        "id": 0,
        "id_list": "",
        "lang": lang,
        "model": model,
        "length": length,
        "style": style,
    }
    body = urllib.parse.urlencode({
        "pkg": PKG, "modetype": "1", "version": "1.3.4",
        "data": aes_enc(json.dumps(payload, ensure_ascii=False)),
    }).encode()
    req = urllib.request.Request(CHAT_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", UA)
    resp = urllib.request.urlopen(req, timeout=120)
    raw = resp.read().decode(errors="replace").strip()
    try:
        plain = aes_dec(raw)
        return {"ok": True, "plain": plain, "raw_b64": raw[:80] + "..."}
    except Exception as e:
        return {"ok": False, "error": f"响应解密失败: {e}", "raw_b64": raw[:80]}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[%s] %s" % (time.strftime("%H:%M:%S"), fmt % args))

    def _json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/demo.html"
        if self.path == "/health":
            return self._json(200, {"status": "ok", "upstream": CHAT_URL})
        return super().do_GET()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n) or b"{}")

        # OpenAI 兼容: /v1/chat/completions
        if self.path == "/v1/chat/completions":
            msgs = req.get("messages", [])
            question = next((m["content"] for m in reversed(msgs)
                             if m.get("role") == "user"), "")
            if not question:
                return self._json(400, {"error": {"message": "no user message"}})
            r = upstream_chat(question)
            if not r["ok"]:
                return self._json(502, {"error": {"message": r["error"],
                                                  "upstream_hint": r["raw_b64"]}})
            try:
                j = json.loads(r["plain"])
                content = j.get("data", {}).get("content", r["plain"])
            except json.JSONDecodeError:
                content = r["plain"]
            return self._json(200, {
                "id": "chatcmpl-openchat-%d" % int(time.time()),
                "object": "chat.completion", "model": req.get("model", "openchat"),
                "choices": [{"index": 0,
                             "message": {"role": "assistant", "content": content},
                             "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            })

        # 原生调试: /api/chat  {question}
        if self.path == "/api/chat":
            r = upstream_chat(req.get("question", ""))
            return self._json(200, r)

        return self._json(404, {"error": "not found"})


if __name__ == "__main__":
    derive_key_iv()
    print(f"[*] AES KEY={_cache['key'].decode()} IV={_cache['iv'].decode()}")
    print(f"[*] demo: http://localhost:{PORT}  OpenAI: POST /v1/chat/completions")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
