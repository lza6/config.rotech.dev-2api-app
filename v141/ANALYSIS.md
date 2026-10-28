# OpenChat 1.4.1 深度逆向分析报告

- 样本：`open.chat.gpt.aichat.bot.free.app_v1.4.1__.apk`（30,042,672 字节，TRUMods 重签，v1+v2 签名）
- 分析时间：2026-10-29
- 方法：jadx 全量反编译（20,263 类）→ 静态定链 → PC 端复现 → 线上实测验证
- 结论：**协议完整还原，可直连，无需设备指纹/无账号体系/实测无额度拦截**

---

## 1. 应用架构

| 层 | 内容 |
|---|---|
| 外壳 | Java/Kotlin（4 个 dex，5.9+6.7+6.7+1.3 MB） |
| 混合 | Flutter 模块（`libapp.so` 2.3MB + `libflutter.so`），仅用于局部页面 |
| 原生 | `librocore.so`（21,848B，`dev.rotech.decode.Decoder` 的 JNI 实现，**密钥种子与签名校验都在这里**） |
| 广告 | Pangle/InMobi/AppLovin/Google Ads（x86 模拟器上 `pag_init_handle` 会 SIGSEGV，无法直接跑 App） |
| 后端 | `*.rotech.dev`（Go + nginx 1.18，同一家还运营 `gpay.rotech.dev`、`config.rotech.dev`、`fcm-chatgpt-api.rotech.dev`） |

主业务链路全在 Java 层：`ChatViewModel` → `m80.c()` → `g61.n()` → `j13.a()`（OkHttp FormBody POST）。

---

## 2. 加密体系（核心）

### 2.1 算法

```java
// defpackage.a6
String seed = ga2.m(a6.m(context));      // md5(签名) —— 表面看是这样
String key  = seed.substring(0,16);      // ASCII
String iv   = seed.substring(16);        // ASCII
Cipher c = Cipher.getInstance("AES/CBC/PKCS5Padding");
c.init(ENCRYPT_MODE, new SecretKeySpec(key.getBytes(UTF_8), "AES"), new IvParameterSpec(iv.getBytes(UTF_8)));
return Base64.encodeToString(c.doFinal(plain.getBytes(UTF_8)), NO_WRAP);
```

`a6.m(context)` 返回 `getPackageInfo(pkg, 64).signatures[last].toCharsString()`（证书 DER 的大写 hex）。

### 2.2 真正的种子（关键突破）

按 Java 层推导（用 APK 实际签名 TRUMods 证书）算出的密钥**全部失败**：25 种派生组合加密后，上游一律返回同一密文响应，且无论如何都解不开。

用 `strings`/二进制扫描 `librocore.so` 后发现：

| 偏移 | 内容 |
|---|---|
| `0x1298` | 2842 字符**小写 hex** = 一张完整 X.509 证书 DER（`CN=Android, O=Google Inc.`，有效期 2023-03-31 → 2053-03-31） |
| `0x1f30` | 字符串 `please put your debug key sign string here`（调试占位） |
| `0x1e69` | 字符串 `signature is error`（native 签名校验） |
| `0x1fc0` | `Gg8ZVznKQqPGvCvSchatgptflyPeriodvYVz5BOudxtB`（字符串解密 key，夹带了 `chatgpt`/`Period` 诱饵片段） |
| `0x1fed` / `0x1ffa` | `EdTQ6AlqYnng` / `az7BxN1dy3cV`（同上） |

用**内嵌证书的小写 hex** 做种子：

```
md5("3082058930820371a00302010202150...72aa71") = 8a678654d587204960f88b97a8896ec5
AES key = "8a678654d5872049"
AES iv  = "60f88b97a8896ec5"
```

立即解开了历史响应密文：

```json
{"code":407,"msg":"decrypt data parameter failed the err is:base64 decode failed: illegal base64 data at input byte 0","data":null}
{"code":10000,"data":{"service_trace":{"primary":{"success":false,"error_type":"server_error"}}},"msg":"param error"}
```

**结论：密钥与 APK 签名无关**，硬编码在 native 里 → mod 版、任意重签版、任意设备通用；官方原版走同样的种子（native 内嵌证书即原作者调试证书）。

### 2.3 请求封装

```java
// defpackage.j13#a
FormBody.Builder b = new FormBody.Builder();
for (entry : params) b.add(key, value);
Request r = new Request.Builder().url(url).post(formBody).build();   // 无任何自定义 Header
```

即 `Content-Type: application/x-www-form-urlencoded`，公共参数见 `cs1.a()`：

```java
hashMap.put("pkg",     context.getPackageName());   // open.chat.gpt.aichat.bot.free.app
hashMap.put("version", versionName);                // 1.4.1
hashMap.put("modetype","1");
hashMap.put("data",    a6.g(context, json.toString()));
```

---

## 3. 接口清单

| 路径 | 用途 | 关键入参 |
|---|---|---|
| `v6/chat/common` | **主聊天** | uuid, conversation_sign, timestamp, question, lang, model, length, style（可选 id/id_list） |
| `v6/chat/role` | 角色扮演聊天 | 同上 + 角色 id |
| `v6/chat/deepseek` | DeepSeek 专用分支 | |
| `v6/chat/email` | 邮件生成 | |
| `v6/web/search` / `v6/web/analysis` / `v6/web/title` | 联网搜索 / 网页分析 / 标题生成 | |
| `v6/video/analysis` / `v6/video/title` | 视频分析 / 标题 | |
| `v6/file/upload` / `v6/file/upload_result` | 文件上传（异步） | |
| `v6/image/generate` / `v6/image/generate_result` | 文生图（异步） | content_text, conversation_id, uuid, preset_id, is_plus, style_id, aspect_ratio |
| `v6/image/edit` / `v6/image/edit_result` | 图生图 | |
| `v6/image/analysis_result` / `v6/image/temp_url` | 图片分析 / 临时链接 | |
| `v6/exchange/code` | 兑换码 | |

辅助域名：

| 域名 | 用途 | 探测结果 |
|---|---|---|
| `config.rotech.dev/chatgpt` | 远程配置 | 需要额外参数（非 `version`），返回 `app is not found` |
| `gpay.rotech.dev/api/v1/subscription/pay`、`/api/v1/android/ack`、`/api/v4/user/subscription/info` | 订阅/支付 | 路由存在，未鉴权返回 404 body |
| `fcm-chatgpt-api.rotech.dev/fcmbull/delaymsg` | FCM 推送排程 | |

---

## 4. 字段语义

| 字段 | 语义 | 实测要点 |
|---|---|---|
| `uuid` | 用户标识，客户端随机生成 | 任意 UUIDv4 可用，**无需注册** |
| `conversation_sign` | 会话标识，格式 `{uuid}#{ms}` | 固定同一值 → 多轮上下文保持；换值 → 新会话 |
| `timestamp` | 毫秒时间戳 | 未见严格校验 |
| `question` | 用户输入 | 多轮需自行拼接历史（上游无 messages 数组） |
| `lang` | 语言（`en`/`zh_CN`/`ja`…来自 `m80.e` 的 27 语言映射） | 影响人设语言 |
| `model` | `auto` / `claude45` / `gemini3` / `gpt4o` / `gpt5` / `grok41` | 6 个全部可用 |
| `length` | `auto` / `detail` / `short` | |
| `style` | `auto`/`academic`/`creativity`/`humor`/`major`/`popular` | |
| `id` | 消息序号 | **有副作用**：带 `id` 会走另一分支，返回通用人设模板并丢失上下文 → 建议不传 |

响应：

```json
{"code":200,"data":{"code":0,"content":"...","id":0,
  "service_trace":{"primary":{"service_type":"a","success":true,"error_type":""}}}}
```

`code==200` 为成功；`service_trace.primary.success=false` 时 `error_type` 给出失败类（如 `server_error`）。

---

## 5. 踩坑与解法（复现必读）

| # | 坑 | 现象 | 解法 |
|---|---|---|---|
| 1 | **JSON 带空格** | 上游返回 `{"code":10000,"msg":"param error"}` | 必须 `separators=(',',':')`，与 Java `JSONObject.toString()` 一致 |
| 2 | **密钥来源** | 用 APK 签名派生 → 请求看似"成功"，但响应恒为同一密文且解不开 | 用 `librocore.so` 内嵌证书 hex 作种子 |
| 3 | **响应密文判读** | 容易把 192 字符/236 字符两种错误响应当成正常 | 统一解密后再看 `code` |
| 4 | **`id` 字段** | 多轮上下文突然消失、回答变通用模板 | 多轮不要传 `id`，只固定 `conversation_sign` |
| 5 | **本机代理并发** | 20 并发全部 `SSLError` | `requests.Session.trust_env=False` 直连；上游本身可直连 |
| 6 | **网关单进程** | 并发 40 时 RPS 只有 2.9 | uvicorn 单 worker + 线程池限制；需要更高吞吐要起多 worker |
| 7 | **App 无法在 x86 模拟器运行** | `pag_init_handle` SIGSEGV（Pangle 广告 SDK） | 动态调试需 ARM 镜像或 patch 广告 SDK；本次未走动态即完成 |

---

## 6. 能力实测（线上真实调用）

| 项目 | 结果 |
|---|---|
| 模型可用性 | 6/6 可用，均返回正确结果 |
| 回答正确性 | 随机两位数加法 20/20 全对 |
| 多轮上下文 | 固定 `conversation_sign` → "你之前说的数字是 4242" ✓ |
| 中文 | `lang=zh_CN` 返回中文人设回答 ✓ |
| 长输入 | 1761 字输入正常处理（1.1s） |
| 免费额度 | **同 uuid 连续 200 次 0 失败**（`quota200.log`，每次答案均正确） |
| 图片生成 | `v6/image/generate` 需 preset/style/aspect 三件套，本轮未标定（返回 `require fail`） |

---

## 7. 压测数据（本机，2026-10-29）

**直连上游**：`stress_test.py -n 200 -w 40`

```
成功 200/200 (100%)   P50 1.74s  P90 5.37s  P99 29.05s  RPS 5.46
模型混合：auto/gpt5/gpt4o/claude45/gemini3/grok41 各 ~33 次
```

**经网关**：`stress_test.py -n 200 -w 40 --gateway http://127.0.0.1:8941`

```
成功 199/200 (99.5%)  P50 2.54s  P90 5.45s  P95 6.69s  P99 22.81s  RPS 2.88
唯一失败：上游 504（HTML 页面被当密文 → decode_error，已归类 upstream_error）
```

**单请求**：冷启 2.5–2.7s，稳定态 0.8–1.2s（`auto` 最快）。

---

## 8. 与旧版（1.4.2 / dialgptapi）对比

| 项 | 1.4.2（dialgptapi） | 1.4.1（本次，rotech.dev） |
|---|---|---|
| 后端 | `dialgptapi` | `gptapi.rotech.dev` |
| 鉴权 | RevenueCat + Firebase 匿名注册 | **无**（uuid 任意） |
| 去重键 | `revenue_cat_app_user_id`（12 次/轮换） | 无，单 uuid 长跑不拦 |
| 免费额度 | 6 次/user_id | **实测 200 次 0 失败** |
| 加密 | 未知（不同体系） | AES-128-CBC，种子硬编码 native |
| 渠道设计 | 需伪造 rc_id 循环 + 代理池兜底 | **单 uuid 直连即可** |

结论：**1.4.1 比 1.4.2 更省事**，无需凭证轮换与代理池。

---

## 9. 对接 new-api 建议

1. 渠道类型：新建 `OpenChat 1.4.1`（或复用 type 自定义），BaseURL `https://gptapi.rotech.dev/api/`
2. 只需一个「协议适配层」：把 OpenAI messages → 单条 question（多轮用固定 `conversation_sign` 保上下文，不传 `id`）
3. 模型映射：`openchat-auto/gpt5/gpt4o/claude45/gemini3/grok41` → 上游代号
4. 无需密钥池、无需代理池（本地实测可直连；若部署在受限网络再加代理）
5. 上游 504/HTML 响应需判为可重试错误（当前已归 `upstream_error`）
6. 建议网关多 worker（`uvicorn --workers 4`）扛并发

---

## 10. 剩余风险

- **上游是免费额度池**，随时可能加风控（设备指纹/IP/频控）；当前无保护措施，建议保留 uuid 轮换能力做降级
- `service_trace.service_model` 恒空 → 无法证明实际后端是 GPT-5/Claude，模型名仅为客户端标签
- 图片/视频/文件类接口未逐个标定（字段已列出，可直接续做）
- 未做「官方原版 APK（非 mod）」对比验证；理论上原生走同一 native 种子，但**待验证**
