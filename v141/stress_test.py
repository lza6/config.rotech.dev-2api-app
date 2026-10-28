"""OpenChat 1.4.1 通道压测

用法:
    python stress_test.py                     # 默认 200 请求 / 并发 40
    python stress_test.py -n 500 -w 60        # 自定义
    python stress_test.py -n 200 -w 40 --gateway http://127.0.0.1:8941   # 压网关而非直连上游

输出: 控制台摘要 + stress_report.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import threading
import time
import uuid as _uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import openchat

MODELS = list(openchat.MODELS.keys())
LOCK = threading.Lock()
RES: list[dict] = []


def one_direct(i: int) -> dict:
    model = MODELS[i % len(MODELS)]
    uid, sign = openchat.Client.new_session()
    q = f"Reply with exactly: PONG{i}"
    t0 = time.time()
    try:
        reply = openchat.default_client().chat(q, uuid=uid, sign=sign, model=model, length="short")
        return {
            "i": i, "ok": bool(reply.content), "latency": time.time() - t0,
            "model": model, "content": reply.content[:40], "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "i": i, "ok": False, "latency": time.time() - t0,
            "model": model, "content": None, "error": f"{type(exc).__name__}: {exc}"[:200],
        }


def one_gateway(i: int, gateway: str) -> dict:
    import requests

    model = openchat.MODELS[MODELS[i % len(MODELS)]]
    t0 = time.time()
    try:
        r = requests.post(
            gateway.rstrip("/") + "/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": f"Reply with exactly: PONG{i}"}],
                "length": "short",
            },
            timeout=180,
        )
        j = r.json()
        content = (j.get("choices") or [{}])[0].get("message", {}).get("content", "")
        return {
            "i": i, "ok": r.status_code == 200 and bool(content),
            "latency": time.time() - t0, "model": model,
            "content": (content or "")[:40],
            "error": None if r.status_code == 200 else str(j)[:200],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "i": i, "ok": False, "latency": time.time() - t0,
            "model": model, "content": None, "error": f"{type(exc).__name__}: {exc}"[:200],
        }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--requests", type=int, default=200)
    ap.add_argument("-w", "--workers", type=int, default=40)
    ap.add_argument("--gateway", default=None, help="压网关地址（不指定则直连上游）")
    ap.add_argument("--proxy", action="store_true", help="直连时走系统代理")
    ap.add_argument("-o", "--out", default="stress_report.json")
    args = ap.parse_args()

    if args.proxy:
        openchat._default = openchat.Client(use_proxy=True)

    fn = (lambda i: one_gateway(i, args.gateway)) if args.gateway else one_direct
    target = args.gateway or openchat.BASE + "v6/chat/common"
    print(f"目标: {target}\n并发={args.workers} 总请求={args.requests}\n")

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for rec in ex.map(fn, range(args.requests)):
            with LOCK:
                RES.append(rec)
            if (rec["i"] + 1) % 20 == 0:
                done = len(RES)
                okc = sum(1 for r in RES if r["ok"])
                print(f"  {done}/{args.requests}  成功 {okc} ({okc/done*100:.1f}%)")
    elapsed = time.time() - t0

    ok = [r for r in RES if r["ok"]]
    lat = sorted(r["latency"] for r in RES)
    q = lambda p: lat[min(len(lat) - 1, int(len(lat) * p))]
    summary = {
        "target": target,
        "requests": len(RES),
        "workers": args.workers,
        "success": len(ok),
        "success_rate": round(len(ok) / len(RES) * 100, 2),
        "elapsed_s": round(elapsed, 2),
        "rps": round(len(RES) / elapsed, 2),
        "latency_s": {
            "p50": round(statistics.median(lat), 2),
            "p90": round(q(0.9), 2),
            "p95": round(q(0.95), 2),
            "p99": round(q(0.99), 2),
            "max": round(lat[-1], 2),
        },
        "models": dict(Counter(r["model"] for r in RES)),
        "errors": dict(Counter((r["error"] or "").split(":")[0] for r in RES if not r["ok"])),
        "fail_samples": [r for r in RES if not r["ok"]][:5],
    }
    print("\n===== 汇总 =====")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "records": RES}, f, ensure_ascii=False, indent=1)
    print(f"\n明细已写入 {args.out}")


if __name__ == "__main__":
    main()
