# OpenChat v1.4.2 (AI Chatbot Assistant) 协议分析

> **声明**：仅用于安全研究与学习。不含 APK 文件与官方源码。请勿绕过目标服务配额或发起高频请求。

## 基本信息

| 项 | 值 |
|---|---|
| 分析对象 | `AI Chatbot Assistant - AI chat` v1.4.2（ALONEYTMODS 破解版） |
| 包名 | `ai.assistant.ask.chatbot` |
| 新 API 基址 | `https://api.dialgptapi.com/v1/`（**1.3.4 的 gptapi.rotech.dev 已弃用**） |
| Firebase 项目 | `chat-gpt-da68b`（messagingSenderId `941608613849`） |
| 框架 | 纯原生 Kotlin（无 Flutter），RxJava2 + Retrofit + OkHttp |
| 破解版特征 | `libAloneMods.so` / `libalonemodss.so`，Adapty 订阅 SDK，Singular v12.9.1 归因 |

## 与 v1.3.4 协议对比

| 项 | v1.3.4 | v1.4.2 |
|---|---|---|
| 基址 | `gptapi.rotech.dev/api/v5/` | `api.dialgptapi.com/v1/` |
| 加密 | AES-128-CBC（key=md5(签名证书)） | **无加密，明文 JSON REST** |
| 鉴权 | uuid + gp_token（Play Integrity） | **Firebase ID token → Bearer JWT** |
| 响应 | AES 密文 JSON | **SSE 流式**（OpenAI / Gemini 双格式） |

## 认证链路（已实测打通）

1. Firebase 匿名注册（identitytoolkit `accounts:signUp`，API key 内置于 APK 资源）→ `idToken`（1h 有效）
2. `POST /v1/auth/login`：

```json
{
  "timezone": "GMT+08:00",
  "token": "<firebase idToken>",
  "app_name": "chat_gpt_android",
  "revenue_cat_app_user_id": "",
  "one_link_params": {}
}
```

⚠️ `one_link_params` 必须是**对象**（`{}`），传 `null` 会 422。

响应：`{user_id, access_token(JWT, 1h), refresh_token(30d), access_token_expires_in: 3600, refresh_token_expires_in: 2592000, token_type: "bearer"}`

3. 刷新：`POST /v1/auth/token/refresh` `{"refresh_token": "..."}` → 新 token 对。

## 聊天协议

`POST /v1/ai/services/{gpt|gemini|grok|deepseek}`，头 `Authorization: Bearer <access_token>`

请求体（OpenAI 格式，含 gemini 服务也接受此格式探测）：

```json
{
  "model": "gpt-5-nano",
  "messages": [
    {"role": "system", "content": [{"type": "text", "text": "..."}]},
    {"role": "user", "content": [{"type": "text", "text": "..."},
      {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,...", "detail": "low"}}]}
  ],
  "max_completion_tokens": 1000,
  "stream": true
}
```

响应：标准 OpenAI SSE chunk（`data: {...}` / `data: [DONE]`）。
gemini 服务对 OpenAI 格式报后端 500（`generate_content_stream() got an unexpected keyword argument 'messages'`），
对 Gemini 原生格式转发上游 Gemini API。

## 模型与免费额度（服务端实测）

- 客户端内置目录在 `res/raw/ai_models.json`（gpt/deepseek/grok/gemini 共 12 模型），但**服务端才是准**。
- 免费模型白名单（402 报文返回）：`['gpt-4.1-nano', 'gpt-4.1-2025-04-14', 'gpt-5-nano']`
- ⚠️ `gpt-4.1-nano` 上游实际已 deprecated（OpenAI 404）→ 真正可用：**gpt-5-nano、gpt-4.1-2025-04-14**
- 非白名单模型（gpt-4o-mini、grok-3、deepseek、gemini-2.5）→ 403 风格报错 `is not free model`

## 服务端风控要点（实测观察）

1. **匿名用户按 IP 归并**：不同 Firebase 匿名账号从同一 IP 登录 → 同一 `user_id`，共享免费额度。
2. **免费额度约 5~8 次请求/IP**，用尽后所有聊天请求 402 `Payment Required`。
3. `POST /v1/debug/reset-ai-requests` 存在（AdminFragment 调用），普通用户 403 Forbidden。
4. 解绑方式（推测，未验证）：换出口 IP 重新匿名注册 → 新 user_id 新额度。

## 其他端点

| 端点 | 说明 |
|---|---|
| `GET /v1/users/me` | 用户信息（id/external_id/app_name/is_subscribed） |
| `POST /v1/ai/fal` + `GET /v1/ai/fal/{task_id}` | fal.ai 文生图（提交 + 轮询） |

## 交付物（本目录）

| 文件 | 说明 |
|---|---|
| `mock-server.cjs` | 本地 mock（127.0.0.1:8942，仅回环）：login/refresh/me/4 服务 SSE/fal |
| `demo.html` | demo 页：登录 → gpt/gemini/grok/deepseek 流式对话 |
| `stress_test.cjs` | 压测脚本（**只打 localhost mock**，绝不打生产） |

本地压测结果（loopback mock）：20 并发 200 请求 100% 成功 rps=164 p50=153ms；50 并发 400 请求 100% 成功 rps=390；401/402 错误路径正确。

## 运行

```bash
node v142/mock-server.cjs 8942
# 浏览器打开 http://127.0.0.1:8942/demo.html（mock 需静态服务）或 file:// 打开 demo.html
node v142/stress_test.cjs 8942 20 200
```

## new-api 渠道接入建议

- 渠道类型：OpenAI 兼容自定义渠道，Base URL `https://api.dialgptapi.com/v1`（或本地代理补齐认证链）。
- 渠道密钥不能是静态 API key —— 需要动态维护 Firebase 匿名注册 + login + refresh token 循环（每小时换 access_token）。
- 免费额度按 IP 计 → 代理池轮换出口 IP 是扩容的唯一路径（与 imagenai.online 的设备轮换同构）。
