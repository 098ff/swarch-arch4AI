"""Send a burst of reviews through the gateway and measure what happened.

Examples
    python tools/loadtest.py --name baseline
    python tools/loadtest.py --name t1-chaos --hang-rate 0.1
    python tools/loadtest.py --name t2-cascade-0.8 --strategy cascade --threshold 0.8
    python tools/loadtest.py --name t3-cache --strategy cascade --threshold 0.8 --cache on

Before each run it configures the inference service (strategy, threshold,
cache, chaos) and resets all counters, so runs do not affect each other.
Every run prints one result row and appends it to results/runs.csv.

Columns
    p50 / p95    latency seen by the client, in ms (half / 95% of requests were faster)
    errors       requests that failed or got no answer within --client-timeout
    pending      reviews saved without a label (your Task 1 fallback)
    accuracy     correct labels among the reviews that did get a label
    large calls  share of requests that reached the large model (cost)
    cache hits   share of requests answered from the cache
"""
import argparse
import asyncio
import csv
import random
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from common import settings  # noqa: E402
from data.make_data import FREQUENT  # noqa: E402

RESTAURANTS = ["Canteen A", "Som Tam Corner", "Noodle Bar", "Green Kitchen", "Burger Hut"]
COLUMNS = ["name", "strategy", "threshold", "cache", "hang_rate", "n", "p50_ms", "p95_ms",
           "errors", "pending", "accuracy", "large_calls", "cache_hits"]


def workload(n, seed=13):
    """Same sequence of (text, true label) every run: 75% unique reviews, 25% common short ones."""
    with open(ROOT / "data" / "test.csv", encoding="utf-8") as f:
        test = [(r["text"], r["label"]) for r in csv.DictReader(f)]
    rng = random.Random(seed)
    return [rng.choice(FREQUENT) if rng.random() < 0.25 else rng.choice(test) for _ in range(n)]


def percentile(values, p):
    if not values:
        return "n/a"
    values = sorted(values)
    return round(values[min(len(values) - 1, int(round(p / 100 * (len(values) - 1))))])


async def run(args):
    async with httpx.AsyncClient() as c:
        cfg = {"strategy": args.strategy, "threshold": args.threshold, "cache": args.cache == "on",
               "hang_rate": args.hang_rate}
        await c.post(f"{settings.INFERENCE_URL}/admin/config", json=cfg)
        await c.post(f"{settings.INFERENCE_URL}/admin/reset")
        await c.post(f"{settings.REVIEW_URL}/admin/reset")

    jobs = workload(args.n)
    sem = asyncio.Semaphore(args.concurrency)
    results = []
    limits = httpx.Limits(max_connections=args.concurrency + 5)

    async with httpx.AsyncClient(timeout=args.client_timeout, limits=limits) as c:
        async def one(i, text, truth):
            async with sem:
                start = time.perf_counter()
                try:
                    r = await c.post(f"{settings.GATEWAY_URL}/api/reviews",
                                     json={"restaurant": RESTAURANTS[i % len(RESTAURANTS)], "text": text})
                    r.raise_for_status()
                    body = r.json()
                    ok = True
                except httpx.HTTPError:
                    body, ok = {}, False
                results.append({"ms": (time.perf_counter() - start) * 1000, "ok": ok,
                                "label": body.get("label"), "status": body.get("status"), "truth": truth})
                done = len(results)
                if done % 20 == 0 or done == len(jobs):
                    print(f"\r  {done}/{len(jobs)} requests", end="", flush=True)

        t0 = time.perf_counter()
        await asyncio.gather(*(one(i, t, y) for i, (t, y) in enumerate(jobs)))
        wall = time.perf_counter() - t0
        print()
        inf = (await c.get(f"{settings.INFERENCE_URL}/metrics")).json()

    n = len(results)
    ok = [r for r in results if r["ok"]]
    scored = [r for r in ok if r["status"] != "pending" and r["label"] is not None]
    lat = [r["ms"] for r in ok]
    row = {"name": args.name, "strategy": args.strategy,
           "threshold": args.threshold if args.strategy == "cascade" else "",
           "cache": args.cache, "hang_rate": args.hang_rate, "n": n,
           "p50_ms": percentile(lat, 50), "p95_ms": percentile(lat, 95),
           "errors": n - len(ok), "pending": len(ok) - len(scored),
           "accuracy": f"{sum(r['label'] == r['truth'] for r in scored) / len(scored):.1%}" if scored else "n/a",
           "large_calls": f"{inf.get('large_calls', 0) / n:.0%}",
           "cache_hits": f"{inf.get('cache_hits', 0) / n:.0%}"}

    print(f"  finished in {wall:.1f} s\n")
    if not ok:
        print("  Every request failed. Look at the run_all.py terminal: a NotImplementedError means\n"
              "  that task's TODO is not done yet.\n")
    width = {k: max(len(k), len(str(v))) for k, v in row.items()}
    print("  " + "  ".join(k.ljust(width[k]) for k in COLUMNS))
    print("  " + "  ".join(str(row[k]).ljust(width[k]) for k in COLUMNS))

    out = ROOT / "results" / "runs.csv"
    out.parent.mkdir(exist_ok=True)
    new = not out.exists()
    with open(out, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if new:
            w.writeheader()
        w.writerow(row)
    print(f"\n  appended to {out.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True, help="a label for this run, e.g. t2-cascade-0.8")
    ap.add_argument("--strategy", choices=["large", "small", "cascade"], default="large")
    ap.add_argument("--threshold", type=float, default=0.8, help="cascade confidence threshold")
    ap.add_argument("--cache", choices=["on", "off"], default="off")
    ap.add_argument("--hang-rate", type=float, default=0.0, help="chaos: share of large-model calls that hang")
    ap.add_argument("-n", type=int, default=200, help="number of reviews to send")
    ap.add_argument("-c", "--concurrency", type=int, default=10, help="reviews in flight at once")
    ap.add_argument("--client-timeout", type=float, default=10.0, help="seconds before the client gives up")
    args = ap.parse_args()
    try:
        asyncio.run(run(args))
    except httpx.ConnectError:
        print("Cannot reach the services. Is `python run_all.py` running in another terminal?")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
