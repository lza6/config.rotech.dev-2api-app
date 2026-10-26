"""
OpenChat (open.chat.gpt.aichat.bot.free.app) gptapi.rotech.dev 协议客户端 — 单次验证
用法: python test_verify.py "你的问题"
仅用于安全研究验证逆向成果, 单次低频调用, 请勿滥用。
"""
import hashlib, json, sys, base64, urllib.request, urllib.parse, uuid, time, zipfile, subprocess, os, tempfile

APK = r"D:\notrack-2api-app\openchat134\openchat-1.3.4.apk"
CERT_ENTRY = "META-INF/ANDROIDD.RSA"
URL = "https://gptapi.rotech.dev/api/v5/chat/common_question"
PKG = "open.chat.gpt.aichat.bot.free.app"
UA  = "okhttp/4.12.0"

def derive_key_iv():
    """PackageManager signature.toCharsString() = 证书 DER 的 hex (v1 signing, cert from PKCS7)。"""
    with zipfile.ZipFile(APK) as z:
        pkcs7 = z.read(CERT_ENTRY)
    pem = subprocess.run(["openssl", "pkcs7", "-inform", "DER", "-in", "-"],
                         input=pkcs7, capture_output=True)
    # openssl 不支持 stdin with -in -, 用临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".p7") as f:
        f.write(pkcs7); tmp = f.name
    pem = subprocess.run(["openssl", "pkcs7", "-inform", "DER", "-in", tmp, "-print_certs"],
                         capture_output=True).stdout
    der = subprocess.run(["openssl", "x509", "-outform", "DER"], input=pem,
                         capture_output=True).stdout
    os.unlink(tmp)
    hex_str = der.hex()
    digest = hashlib.md5(hex_str.encode()).hexdigest()
    return digest[:16].encode(), digest[16:].encode()

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

def aes_encrypt(key, iv, plaintext: str) -> str:
    padder = PKCS7(128).padder()
    data = padder.update(plaintext.encode()) + padder.finalize()
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return base64.b64encode(enc.update(data) + enc.finalize()).decode()

def aes_decrypt(key, iv, b64data: str) -> str:
    raw = base64.b64decode(b64data)
    dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    padded = dec.update(raw) + dec.finalize()
    unpadder = PKCS7(128).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode()

def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "你好，请用一句话介绍你自己"
    key, iv = derive_key_iv()
    print(f"[+] KEY={key.decode()} IV={iv.decode()}")

    payload = {
        "uuid": str(uuid.uuid4()),
        "gp_token": "",                      # 重打包版拿不到 Play Integrity token, 先置空观察服务端反应
        "conversation_sign": f"conv-{int(time.time()*1000)}",
        "timestamp": int(time.time() * 1000),
        "question": question,
        "id": 0,
        "id_list": "",
        "lang": "zh",
        "model": "1",
        "length": "1",
        "style": "1",
    }
    print(f"[+] 明文请求: {json.dumps(payload, ensure_ascii=False)[:200]}")
    data_enc = aes_encrypt(key, iv, json.dumps(payload, ensure_ascii=False))

    body = urllib.parse.urlencode({
        "pkg": PKG, "modetype": "1", "version": "1.3.4", "data": data_enc,
    }).encode()

    req = urllib.request.Request(URL, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", UA)

    try:
        resp = urllib.request.urlopen(req, timeout=60)
        raw = resp.read().decode(errors="replace")
        print(f"[+] HTTP {resp.status}, 原始响应({len(raw)}B): {raw[:300]}")
        try:
            j = json.loads(raw)
            enc_resp = j.get("data") or j.get("res") or ""
            if enc_resp:
                print("[+] 解密响应:", aes_decrypt(key, iv, enc_resp)[:2000])
            else:
                print("[+] 响应JSON键:", list(j.keys()))
        except json.JSONDecodeError:
            # 响应可能整体是密文 Base64
            try:
                print("[+] 整体解密:", aes_decrypt(key, iv, raw)[:2000])
            except Exception as e:
                print("[-] 非JSON非密文:", e)
    except urllib.error.HTTPError as e:
        print(f"[-] HTTP {e.code}: {e.read()[:500]}")

if __name__ == "__main__":
    main()
