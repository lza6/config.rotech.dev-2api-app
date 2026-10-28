# OpenChat 1.4.1 接入 new-api（渠道对接指南）

> 上游：`https://gptapi.rotech.dev/api/` ｜ 无账号体系 ｜ 无额度拦截（实测 ≥100 次单 uuid）

## 方案选择

| 方案 | 说明 | 适用 |
|---|---|---|
| **A. 网关中转（推荐）** | new-api 当 OpenAI 客户端指向 `openchat141-2api/server.py` | 0 改动、立刻可用 |
| B. 原生渠道 | 在 new-api 里新增 `type` 渠道，Go 里复刻 AES 协议 | 需要并发/计费/日志一体化时 |

## 方案 A：网关中转（3 步）

1. 起网关（任意机器，能直连 `gptapi.rotech.dev`）

```bash
cd openchat141-2api
pip install requests pycryptodome fastapi uvicorn
OPENCHAT_PORT=8941 python server.py
# 高并发：uvicorn server:app --host 0.0.0.0 --port 8941 --workers 4
```

2. new-api 后台 → 渠道 → 新增

| 字段 | 值 |
|---|---|
| 类型 | OpenAI |
| 名称 | OpenChat-1.4.1 |
| 代理/BaseURL | `http://<网关IP>:8941` |
| 密钥 | 任意非空（如 `openchat`） |
| 模型 | `openchat-auto,openchat-gpt5,openchat-gpt4o,openchat-claude45,openchat-gemini3,openchat-grok41` |

3. 测试：`/v1/chat/completions` 选 `openchat-auto` 发一条即可。

## 方案 B：原生渠道实现要点（Go）

```go
// 1) 常量
const (
    baseURL = "https://gptapi.rotech.dev/api/"
    pkgName = "open.chat.gpt.aichat.bot.free.app"
    version = "1.4.1"
)
// seed 2842 字符 hex，见 openchat141-2api/seed_native_hex.txt
var aesKey, aesIV = derive(seed) // key=md5(seed)hex[0:16], iv=[16:32]（ASCII 字节）

// 2) 请求
form := url.Values{}
form.Set("pkg", pkgName)
form.Set("modetype", "1")
form.Set("version", version)
form.Set("data", base64.StdEncoding.EncodeToString(aesCBCEncrypt(mustCompactJSON(payload))))

// 3) payload 必须紧凑 JSON（Go 默认 json.Marshal 天然紧凑，可用）
//    {"uuid","conversation_sign","timestamp","question","lang","model","length","style"}
//    uuid 每次请求随机 UUIDv4；conversation_sign = uuid + "#" + 毫秒时间戳
//    多轮上下文：同一会话复用 conversation_sign；不要传 id

// 4) 响应：base64 → AES 解密 → JSON；code==200 才算成功
```

映射到 OpenAI 语义：

| OpenAI | 上游 |
|---|---|
| `messages` | 拼成单条 `question`（system 用 `[System]` 前缀，assistant 用 `[Assistant]`） |
| `model` | `openchat-*` → `auto/gpt5/gpt4o/claude45/gemini3/grok41` |
| 非标准可选项 | `length`(auto/short/detail)、`style`(auto/academic/creativity/humor/major/popular) |
| `usage` | 上游无 usage，按字符估算 |

## 错误处理

| 上游表现 | 归类 | 建议 |
|---|---|---|
| `code != 200`（响应可解密） | 业务错误 | 直接回错误信息 |
| 响应非 base64 / 无法解密（常见上游 504 HTML） | `upstream_error` | 可重试（退避 2 次） |
| 连接超时（timeout 默认 180s） | 网络错误 | 重试 |
| `service_trace.primary.success=false` | 上游服务失败 | 可重试 |

## 配额与限流建议

- 上游未观察到额度消耗，仍建议 new-api 侧设每分钟/每日上限做自保
- 单账号（uuid）可并发，实测 40 并发 100% 成功；更高并发建议先小步压测
- 如遇风控，降级方案：每 N 次请求轮换 uuid（代码里 `Client.new_session()` 直接换）

## 已知限制

1. 上游一次性返回整段文本，无原生 SSE；网关做 12 字符切片伪流式
2. 图片/视频/文件接口未标定（字段清单见 `ANALYSIS.md` 第 3 节）
3. `service_trace.service_model` 恒空，无法验证真实后端模型
4. 上游为免费额度池，随时可能加风控 → 保留切换/轮换能力
