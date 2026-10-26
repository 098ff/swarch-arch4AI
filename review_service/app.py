"""Review service: the business service of CampusEats.

Customers post reviews of campus restaurants. Each review gets a sentiment
label from the inference service so that restaurant owners see unhappy
customers quickly.

POST /reviews                {"restaurant": "...", "text": "..."}
GET  /restaurants/{name}     review counts for one restaurant
GET  /reviews/pending        reviews saved without a label (Task 1)
GET  /metrics                counters since the last reset
POST /admin/reset            reset counters and delete all reviews
"""
import itertools
from collections import Counter

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from review_service.fallback import classify

app = FastAPI(title="Review service")
client = httpx.AsyncClient(timeout=None, limits=httpx.Limits(max_connections=200))
reviews = []
ids = itertools.count(1)
counters = Counter()


class NewReview(BaseModel):
    restaurant: str
    text: str


@app.post("/reviews")
async def post_review(new: NewReview):
    counters["requests"] += 1
    result = await classify(client, new.text)
    if result.get("status") == "pending":
        counters["pending"] += 1
    review = {"id": next(ids), "restaurant": new.restaurant, "text": new.text, **result}
    reviews.append(review)
    return review


@app.get("/restaurants/{name}")
def restaurant(name: str):
    mine = [r for r in reviews if r["restaurant"] == name]
    return {"restaurant": name, "reviews": len(mine),
            "positive": sum(r["label"] == "positive" for r in mine),
            "negative": sum(r["label"] == "negative" for r in mine),
            "pending": sum(r.get("status") == "pending" for r in mine)}


@app.get("/reviews/pending")
def pending():
    return [r for r in reviews if r.get("status") == "pending"]


@app.get("/metrics")
def metrics():
    return {"requests": counters["requests"], "pending": counters["pending"]}


@app.post("/admin/reset")
def admin_reset():
    reviews.clear()
    counters.clear()
    return {"ok": True}


@app.get("/health")
def health():
    return {"ok": True}
