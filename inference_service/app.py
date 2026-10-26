"""Inference service: wraps the models behind a REST API (model as a service).

POST /predict        {"text": "..."} -> {"label", "confidence", "model", "latency_ms"}
GET  /metrics        counters since the last reset
GET  /admin/config   current strategy, threshold, cache and chaos settings
POST /admin/config   change them (tools/loadtest.py does this for you)
POST /admin/reset    reset counters and empty the cache
"""
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from common import settings
from inference_service.models import LargeModel, SmallModel
from inference_service.patterns import PredictionCache, cascade

app = FastAPI(title="Inference service")
small, large = SmallModel(), LargeModel()

config = {"strategy": "large", "threshold": 0.8, "cache": False, "hang_rate": 0.0,
          "large_delay_ms": settings.LARGE_DELAY_MS}
cache = PredictionCache()
counters = {}


def reset():
    global cache
    cache = PredictionCache()
    counters.update(requests=0, small_calls=0, large_calls=0)


reset()


@app.exception_handler(NotImplementedError)
async def not_done(request: Request, exc: NotImplementedError):
    return JSONResponse(status_code=501, content={"detail": str(exc)})


class Review(BaseModel):
    text: str


class Config(BaseModel):
    strategy: str | None = None       # "large", "small" or "cascade"
    threshold: float | None = None    # used by "cascade"
    cache: bool | None = None
    hang_rate: float | None = None    # chaos: share of large-model calls that hang
    large_delay_ms: int | None = None


class CountingSmall:
    def predict(self, text):
        counters["small_calls"] += 1
        return small.predict(text)


class CountingLarge:
    async def predict(self, text):
        counters["large_calls"] += 1
        return await large.predict(text)


async def run_strategy(text):
    if config["strategy"] == "small":
        return CountingSmall().predict(text)
    if config["strategy"] == "cascade":
        return await cascade(text, CountingSmall(), CountingLarge(), config["threshold"])
    return await CountingLarge().predict(text)


@app.post("/predict")
async def predict(review: Review):
    start = time.perf_counter()
    counters["requests"] += 1
    result = cache.get(review.text) if config["cache"] else None
    if result is not None:
        result = {**result, "model": "cache"}
    else:
        result = await run_strategy(review.text)
        if config["cache"]:
            cache.put(review.text, result)
    return {**result, "latency_ms": round((time.perf_counter() - start) * 1000, 1)}


@app.get("/metrics")
def metrics():
    return {**counters, "cache_hits": cache.hits, "cache_misses": cache.misses}


@app.get("/admin/config")
def get_config():
    return config


@app.post("/admin/config")
def set_config(new: Config):
    for k, v in new.model_dump(exclude_none=True).items():
        config[k] = v
    large.hang_rate = config["hang_rate"]
    large.delay_ms = config["large_delay_ms"]
    return config


@app.post("/admin/reset")
def admin_reset():
    reset()
    return {"ok": True}


@app.get("/health")
def health():
    return {"ok": True}
