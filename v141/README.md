# OpenChat v1.4.1（rotech.dev v6 API）协议全还原 — **已打通**

> **声明**：仅用于安全研究与学习。不含 APK 文件与官方源码。请勿利用本内容绕过目标服务配额或发起高频请求。

## TL;DR

v1.3.4 的分析卡在「AES key = md5(APK 签名证书)，重打包版签名不同 → 上游拒绝」。**v1.4.1 把这一环彻底解开了**：

- 真正的密钥种子**不在 APK 签名里**，而是硬编码在 `librocore.so` 偏移 `0x1298` 的**内嵌 X.509 证书 DER 小写 hex**（2842 字符）→ **与签名无关，任意重签/mod 版/任意设备通用**
- 因此这一版**无需真机、无需 Play Integrity `gp_token`、无需动态 hook**，纯静态 + HTTP 即可拿到真实回复
- 免费额度实测：**同一 `uuid` 连续 200 次调用 0 失败**（v1.3.4 时代担心的配额风控在 v6 接口上未观察到）

```
md5(seed)  = 8a678654d587204960f88b97a8896ec5
AES key    = 8a678654d5872049   (ASCII)
AES iv     = 60f88b97a8896ec5   (ASCII)
```

## 基本信息

| 项 | 值 |
|---|---|
| 分析对象 | `open.chat.gpt.aichat.bot.free.app` v1.4.1（TRUMods 重签修改版，`CN=TRUMods`） |
| API 基址 | `https://gptapi.rotech.dev/api/v6/`（v5 → **v6**，端点已改名） |
| 鉴权 | **无账号体系**，`uuid` 客户端随机生成即可 |
| 加密 | AES-128-CBC-PKCS5，Key/IV 由 native 内嵌证书 hex 派生（详见下节） |
| 框架 | Java/Kotlin 主体 + Flutter 局部模块（`libapp.so`） |
| 原生 | `librocore.so` 21,848B（`dev.rotech.decode.Decoder`，密钥种子 + 签名校验都在此） |
| 分析工具 | jadx（20,263 类全量）、Python(pycryptodome)、Playwright |

## 密钥体系（核心突破）

Java 层 `defpackage.a6` 长这样：

```java
String m = ga2.m(a6.m(context));   // md5(签名) —— 表面看是签名派生
String key = m.substring(0, 16);   // ASCII
String iv  = m.substring(16);      // ASCII
Cipher c = Cipher.getInstance("AES/CBC/PKCS5Padding");
c.init(ENCRYPT_MODE, new SecretKeySpec(key.getBytes(UTF_8), "AES"),
                     new IvParameterSpec(iv.getBytes(UTF_8)));
return Base64.encodeToString(c.doFinal(plain.getBytes(UTF_8)), NO_WRAP);
```

按「APK 实际签名（TRUMods 证书 DER 大写 hex）」派生的 25 种组合**全部失败**：上游响应恒为同一段密文、且任何候选 key 都解不开 —— 说明服务端用的根本不是这个种子。

扫描 `librocore.so` 得到：

| 偏移 | 内容 |
|---|---|
| `0x1298` | 2842 字符小写 hex = 完整 X.509 证书 DER（`CN=Android, O=Google Inc.`，2023-03-31 → 2053-03-31） |
| `0x1f30` | `please put your debug key sign string here`（调试占位） |
| `0x1e69` | `signature is error`（native 签名校验提示） |
| `0x1fc0` | `Gg8ZVznKQqPGvCvSchatgptflyPeriodvYVz5BOudxtB`（字符串解密 key，夹带 `chatgpt`/`Period` 诱饵片段） |
| `0x1fed` / `0x1ffa` | `EdTQ6AlqYnng` / `az7BxN1dy3cV`（同上） |

用内嵌证书 hex 当种子后，历史响应密文立刻解密成功：

```json
{"code":407,"msg":"decrypt data parameter failed the err is:base64 decode failed: illegal base64 data at input byte 0"}
{"code":10000,"data":{"service_trace":{"primary":{"success":false,"error_type":"server_error"}}},"msg":"param error"}
```

> 完整种子见 `seed_native_hex.txt`（或 `openchat.py` 内 `SEED` 常量）。

## 请求协议

```
POST https://gptapi.rotech.dev/api/v6/chat/common
Content-Type: application/x-www-form-urlencoded   （无任何自定义 Header）

pkg=open.chat.gpt.aichat.bot.free.app
modetype=1
version=1.4.1
data=<Base64_NO_WRAP( AES-128-CBC-PKCS5( 紧凑JSON ) )>
```

`v6/chat/common` 明文结构（`defpackage.m80#b`）：

```json
{"uuid":"<UUIDv4>","conversation_sign":"<uuid>#<毫秒时间戳>","timestamp":<ms>,
 "question":"...","lang":"en","model":"auto","length":"auto","style":"auto"}
```

响应（同样 AES 加密的 Base64）：

```json
{"code":200,"data":{"code":0,"content":"...","id":0,
  "service_trace":{"primary":{"service_type":"a","service_model":"","service_plat":"","success":true,"error_type":""}}}}
```

## 三个致命坑（复现必读）

| # | 坑 | 现象 | 解法 |
|---|---|---|---|
| 1 | **JSON 带空格** | 上游恒返回 `{"code":10000,"msg":"param error"}` | 必须紧凑 JSON（`separators=(',',':')`），与 Java `JSONObject.toString()` 一致 |
| 2 | **`id` 字段有副作用** | 多轮上下文突然丢失、回答变成通用人设模板 | 多轮只固定 `conversation_sign`，**不要传 `id`** |
| 3 | **本机代理并发** | 20 并发全部 `SSLError` | `requests.Session.trust_env=False` 直连（上游可直连） |

## 端点清单（v6）

| 路径 | 功能 | 关键入参 |
|---|---|---|
| `v6/chat/common` | **主聊天** | uuid, conversation_sign, timestamp, question, lang, model, length, style |
| `v6/chat/role` | 角色扮演 | 同上 + 角色 id |
| `v6/chat/deepseek` | DeepSeek 分支 | |
| `v6/chat/email` | 邮件助手 | |
| `v6/web/search` / `v6/web/analysis` / `v6/web/title` | 联网搜索 / 解析 / 标题 | |
| `v6/video/analysis` / `v6/video/title` | 视频分析 / 标题 | |
| `v6/file/upload` / `v6/file/upload_result` | 文件上传（异步） | |
| `v6/image/generate` / `v6/image/generate_result` | 文生图（异步） | content_text, conversation_id, uuid, preset_id, is_plus, style_id, aspect_ratio |
| `v6/image/edit` / `v6/image/edit_result` / `v6/image/analysis_result` / `v6/image/temp_url` | 图片编辑 / 分析 / 临时链接 | |
| `v6/exchange/code` | 兑换码 | |

辅助域名：`config.rotech.dev/chatgpt`（远程配置，需额外参数）、`gpay.rotech.dev/api/v1/subscription/pay`、`fcm-chatgpt-api.rotech.dev/fcmbull/delaymsg`。

## 模型与参数

| 上游代号 | 说明 |
|---|---|
| `auto` | App 默认（界面标注 GPT-5-nano） |
| `gpt5` / `gpt4o` / `claude45` / `gemini3` / `grok41` | 6 个代号全部实测可用 |

| 参数 | 取值 |
|---|---|
| `length` | `auto` / `short` / `detail` |
| `style` | `auto` / `academic` / `creativity` / `humor` / `major` / `popular` |
| `lang` | `en` / `zh_CN` / `zh_TW` / `ja` / `ko` / `de` / `fr` / `es` / `ru` / `ar` …（`m80.e` 共 27 语言映射） |

⚠️ `service_trace.service_model` 恒为空 → **无法证明**实际后端模型，模型名仅为客户端标签。

## 实测验证（2026-10-29）

| 项目 | 结果 |
|---|---|
| 模型可用性 | 6/6 |
| 回答正确性 | 随机两位数加法 20/20 全对 |
| 多轮上下文 | 固定 `conversation_sign` → 正确回忆前文（"你之前说的数字是 4242"） |
| 中文 | `lang=zh_CN` 返回中文人设 |
| 长输入 | 1761 字正常（1.1s） |
| 免费额度 | **同 uuid 200 次 0 失败**（`quota200.log`） |
| 浏览器 E2E | Playwright 真实点击/输入/等待/截图（`ui_demo.png`） |

## 压测

| 场景 | 并发 | 请求 | 成功率 | P50 | P90 | RPS |
|---|---|---|---|---|---|---|
| 直连上游 | 40 | 200 | **100%** | 1.74s | 5.37s | 5.46 |
| 经本机网关 | 40 | 200 | 99.5% | 2.54s | 5.45s | 2.88 |

唯一失败为上游 504（HTML 页面被当密文 → 归类 `upstream_error`，可重试）。网关单 worker 是瓶颈，多 worker 可提升。

## 与 v1.3.4 / v1.4.2 对比

| 项 | v1.3.4（v5 API） | v1.4.1（v6 API，本目录） | v1.4.2（dialgptapi） |
|---|---|---|---|
| 基址 | `gptapi.rotech.dev/api/v5/` | `gptapi.rotech.dev/api/v6/` | `api.dialgptapi.com/v1/` |
| 加密 | AES-128-CBC，key=md5(签名) | AES-128-CBC，**key=md5(native 内嵌证书 hex)** | 无（明文 REST + SSE） |
| 鉴权 | uuid + `gp_token`(Play Integrity) | **仅 uuid**（任意） | Firebase 匿名 → Bearer JWT |
| 额度 | 未打通（签名不符 → 拒绝） | **200 次 0 失败** | 6 次/user_id，需轮换 rc_id |
| 可复现性 | 需官方签名版证书或真机 gp_token | **纯静态可复现** | 需 Firebase 注册 + 轮换逻辑 |
| 目录 | 仓库根（v1.3.4） | `v141/` | `v142/` |

## 文件

| 文件 | 说明 |
|---|---|
| `openchat.py` | 核心协议库（AES / 会话 / 6 模型 / 错误分类） |
| `seed_native_hex.txt` | 密钥种子（2842 字符，取自 `librocore.so` 0x1298） |
| `server.py` | OpenAI 兼容网关（FastAPI `:8941`，流式伪 SSE） |
| `demo.html` | 浏览器 Demo |
| `stress_test.py` | 压测（直连 / 压网关） |
| `verify_ui.py` | Playwright 真实浏览器端到端验证 |
| `ANALYSIS.md` | 深度分析报告（11 节） |
| `docs/NEW-API-INTEGRATION.md` | 接入 new-api 的两套方案（网关中转 / 原生 Go 渠道） |
| `stress_gateway.json` / `quota200.log` / `ui_demo.png` | 压测与验证证据 |

## 快速开始

```bash
pip install requests pycryptodome fastapi uvicorn
python server.py          # http://127.0.0.1:8941/  Demo 页 + /v1/chat/completions
```

```python
import openchat
print(openchat.Client().chat("hello", model="auto").content)
```

## 剩余风险与未完成项

1. `service_trace.service_model` 恒空，无法验证真实后端模型
2. 上游是免费额度池，随时可能加设备指纹/IP 频控（当前零防护），建议保留 uuid 轮换降级
3. 图片/视频/文件接口字段已列出但未逐个标定（`v6/image/generate` 仍返回 `require fail`）
4. App 在 x86 模拟器上因 Pangle 广告 SDK（`pag_init_handle` SIGSEGV）无法运行 → 本报告全程纯静态 + 线上实测完成；官方原版 APK 是否同种子 **未验证**
