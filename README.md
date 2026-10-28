# OpenChat (rotech.dev) 逆向分析报告

> **声明**：本项目仅用于**安全研究与学习目的**。分析对象为公开分发的 APK，不包含任何官方源码与原始 APK 文件。请勿利用本报告内容绕过目标服务的配额与风控，或对目标服务器发起高频请求。如有侵权请联系删除。

## 基本信息

| 项 | 值 |
|---|---|
| 分析对象 | OpenChat `open.chat.gpt.aichat.bot.free.app` v1.3.4 (versionCode 52) |
| 出品方 | rotech.dev（`dev.rotech.*` SDK，站点 chatgpt.rotech.dev） |
| 框架 | **Flutter（libapp.so, Dart AOT）+ 原生 Android（Kotlin）混合** |
| 网络栈 | 原生层 OkHttp 4（form-urlencoded + AES 加密）；Flutter 层 Dart AOT |
| 商业化 | Google Play 订阅 + AdMob / InMobi / Pangle(穿山甲) / Facebook Audience 广告 |
| 分析工具 | jadx 1.5.6、openssl、Python (cryptography) |

## ⚠️ 重打包警示

本次分析的 APK（社区流传的"高级版"）使用 **`CN=Android Debug` 调试证书重签名**（2026-07-02 签发），
**并非官方 release 签名**。关键影响：

- 应用内通过 Google Play Integrity 获取的 `gp_token`（`Ya.G` / `PlaySafeManager`）在重打包版上不可用；
- 服务端请求体中携带 `gp_token`，说明存在设备完整性风控；
- `classes5.dex` 为后加入的 HuaLuo 插件框架 + 腾讯分享 SDK，**未发现破解 hook**。

## 核心 API 协议（从混淆代码中恢复）

App 采用 **瘦客户端 + 自建网关** 架构：模型全部在服务端。

### 端点清单（v5）

| 端点 (`https://gptapi.rotech.dev/api/v5/`) | 功能 |
|---|---|
| `chat/common_question` | 主聊天入口 |
| `chat/role_question` | 角色扮演聊天 |
| `chat/web_search` / `web_analysis` / `web_analysis_title` | 联网搜索 / 网页解析 |
| `chat/images/analysis` (+`_pull`) | 图片理解（轮询式） |
| `chat/images/edit` (+`_pull`) / `exchange_url` | 图片编辑 |
| `chat/file/analysis` (+`_pull`) / `get_upload_url` / `upload_server` (+`_pull`) | 文件分析 |
| `chat/video_analysis` / `video_analysis_title` | 视频分析 |
| `chat/question-dp` / `email-assistant` | 追问 / 邮件助手 |
| `text2img/gen_image` / `get_task_by_id` | 文生图（任务式） |
| `exchange/code` | 兑换码 |

辅助域名：

| 域名 | 用途 |
|---|---|
| `config.rotech.dev/chatgpt` | 配置/更新下发（POST `version=2&data={loc,tzo,lan,...}`） |
| `gpay.rotech.dev/api/v1/subscription/pay`、`v4/user/subscription/info` | 订阅支付 |
| `fcm-chatgpt-api.rotech.dev/fcmbull/{closemsg,delaymsg}` | 推送管理 |
| `chatgpt.rotech.dev/terms.html` / `privacypolicy.html` | 条款/隐私 |
| `st.rotech.dev/yAZFju` | 短链 |

### 请求格式

`POST application/x-www-form-urlencoded`：

```
pkg=open.chat.gpt.aichat.bot.free.app
modetype=1
version=1.3.4
data=<Base64(AES 密文)>
```

### 加密层（关键，`Z3/a.java` + `N7/a.k()` 还原）

```
sigHex  = MD5hex( 签名证书 DER 的 hex 字符串 )    # PackageManager signature.toCharsString()
KEY     = sigHex[0:16]     # AES-128 密钥 (ASCII)
IV      = sigHex[16:32]    # CBC IV     (ASCII)
data    = Base64( AES-128-CBC-PKCS5( 明文JSON ) )
```

请求明文 JSON（`S9/b.c()` 还原）：

```json
{
  "uuid": "设备 uuid",
  "gp_token": "Play Integrity token",
  "conversation_sign": "会话标识",
  "timestamp": 1793042479193,
  "question": "用户问题",
  "id": 0,
  "id_list": "",
  "lang": "zh",
  "model": "1",
  "length": "1",
  "style": "1"
}
```

**响应同为 AES 密文**，同一 key/IV 解密后为 JSON：
`{"code": 0, "data": {"content": "回答文本", "id": <answerId>}}`
（`code` 0=成功 1/2=业务错误；`S9/b$C0093a.d()` 还原）

### 资产加密

assets 内角色/引导 JSON 由 `librocore.so` 的 native `getAllJsonNative(AssetManager, name)` 解密
（`dev.rotech.decode.Decoder`）。

## 实测验证记录（✅ 已完全打通）

**最终结论（动态分析验证）**：加密 key 来自 **PackageManager 运行时返回的签名**，
而非 APK 内嵌证书（这是本项目最大的坑）。

```
sig_hex = PackageManager.getPackageInfo(pkg, GET_SIGNATURES).signatures[0].toCharsString()
md5hex  = MD5_hex( sig_hex )        # 对签名 hex 字符串本身做 MD5
KEY     = md5hex[0:16]              # 16 字节 ASCII
IV      = md5hex[16:32]             # 16 字节 ASCII
请求/响应共用同一对 KEY/IV, AES-128-CBC-PKCS5
```

验证记录（Android 11 x86_64 模拟器 + Frida hook `javax.crypto.Cipher`）：

1. App 真实请求明文：`{"uuid","gp_token","conversation_sign":"{uuid}_{ms}","timestamp","question","lang","model":"auto","length":"auto","style":"auto"}`
2. 服务端响应明文：`{"code":200,"data":{"code":0,"content":"...","id":0,"service_trace":...}}`
3. **本地 Python 独立实现相同协议 → 服务端返回真实 AI 回复 `"PONG"`** ✅
4. `gp_token` 传空字符串也能通过（Play Integrity 校验未强制）

### 打通路线（已走通的可复现路径）

1. Android 官方 Emulator + google_apis x86_64 镜像（`D:/android-sdk`）；
2. Frida server + hook 脚本 `tools/hook_init.js`（`Cipher.init` 抓 key）+
   `tools/hook_cipher2.js`（`Cipher.doFinal` 抓明密文对）；
3. 从 hook 输出取得运行时签名 hex → 派生 KEY/IV → 本地实现协议。

完整结论请看 `README.md` 底部"打通路线"。

## 🆕 v1.4.1（v6 API）：种子来自 native 内嵌证书（2026-10-29 补完）

v1.3.4 的结论是「key 来自 PackageManager 运行时签名」。**在 v1.4.1 上这条不成立**：

- 用 mod 版（`CN=TRUMods`）实际签名派生出的 25 种组合**全部失败**（响应恒为同一密文且解不开）
- 真正的种子硬编码在 `librocore.so` 偏移 `0x1298`：一张 **X.509 证书 DER 的小写 hex（2842 字符）**，
  同段还留有 `please put your debug key sign string here` 占位串与 `signature is error` 校验提示
- 用该 hex 做 `md5 → key/iv` 后，**请求与响应双向立刻打通**，且与 APK 签名无关（任意重签 / 任意设备通用）

```
md5(seed) = 8a678654d587204960f88b97a8896ec5
KEY = 8a678654d5872049   IV = 60f88b97a8896ec5   (ASCII, AES-128-CBC-PKCS5)
```

v6 接口与 v5 的其他差异：

| 项 | v5（v1.3.4） | v6（v1.4.1，本仓库 `v141/`） |
|---|---|---|
| 端点 | `chat/common_question` 等 | `v6/chat/common`、`v6/chat/role`、`v6/image/generate` … |
| `gp_token` | 需要（可传空） | **完全不需要** |
| `conversation_sign` | `{uuid}_{ms}` | `{uuid}#{ms}` |
| 额外坑 | — | **JSON 必须紧凑**（带空格 → `param error`）；`id` 字段会破坏多轮上下文 |
| 额度 | — | 同 uuid 连续 **200 次 0 失败** |

完整报告、可运行客户端、OpenAI 网关、Demo 与压测见 **[`v141/`](v141/)**；
1.4.2（dialgptapi，Firebase JWT 体系）见 [`v142/`](v142/)。

---

## 文件说明

```
├── README.md             # 本报告
├── demo.html             # 本地网页 demo（对话界面）
├── demo_server.py        # 本地代理（AES 加解密 + OpenAI 兼容 /v1/chat/completions + 原生 /api/chat）
├── tools/
│   ├── test_verify.py    # 单次验证脚本（协议端到端验证）
│   └── hook_z3.js        # Frida hook 脚本（动态分析用）
└── sources-key-files/    # 关键还原源码（混淆原样摘录）
    ├── Z3/a.java         # AES 加解密（核心）
    ├── N7/a.java         # MD5 派生
    ├── T9/c.java         # OkHttp 封装 + 响应解密调用点
    ├── S9/b.java         # 请求构造（端点/参数）
    └── dev/rotech/decode/Decoder.java  # 资产解密 native 入口
```

## Demo 使用

```bash
pip install cryptography
python demo_server.py        # 需要本机存在分析用 APK 路径, 或设置 OPENCHAT_AES_KEY/IV
# 浏览器打开 http://localhost:8901
# 或 OpenAI 客户端: POST http://localhost:8901/v1/chat/completions
```

> 注意：截至本报告，上游对话功能对重打包签名返回加密拒绝消息（见"实测验证记录"）。
> demo 的加密/解密/协议封装已完整实现，打通最后一环（官方 release 证书派生 key 或有效 gp_token）
> 后即可直接出真实回复，无需再改代码结构。

## 打通路线（给后续研究者）

1. **动态 hook**：Android 模拟器（Android Studio Emulator + AOSP 镜像即可）安装 APK，
   Frida hook `Z3.a.a()`（解密）与 `Z3.a.b()`（加密），直接 dump 明文请求/响应；
2. 或抓取 **Play 官方签名版**流量，用官方证书派生 key；
3. `gp_token` 为 Play Integrity token，重打包版需评估服务端校验强度。
