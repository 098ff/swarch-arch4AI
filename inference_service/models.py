"""The two provided models. You do not need to change this file.

SmallModel: a tiny bag-of-words classifier. Fast (well under 1 ms), but it
            misreads negations ("not bad") and contrasts ("... but ...").
LargeModel: a bigger classifier that also sees word pairs and triples. Much
            more accurate, but every call is slow (about LARGE_DELAY_MS) and
            only LARGE_CAPACITY calls run at once, like a GPU-hosted model
            or a paid LLM API. The delay is simulated; the predictions are real.

Both are trained from data/train.csv when the inference service starts
(about a second), so there are no model files to download.
"""
import asyncio
import csv
import random
from pathlib import Path

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from common import settings

DATA = Path(__file__).resolve().parent.parent / "data"


def load(name):
    with open(DATA / name, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [r["text"] for r in rows], [r["label"] for r in rows]


class Prediction(dict):
    """{"label": "positive" | "negative", "confidence": 0.5-1.0, "model": name}"""


class SmallModel:
    name = "small"

    def __init__(self):
        texts, labels = load("train.csv")
        self.pipe = make_pipeline(CountVectorizer(binary=True, max_features=100),
                                  LogisticRegression(max_iter=1000, C=0.5)).fit(texts, labels)

    def predict(self, text: str) -> Prediction:
        probs = self.pipe.predict_proba([text])[0]
        best = probs.argmax()
        return Prediction(label=str(self.pipe.classes_[best]), confidence=round(float(probs[best]), 3),
                          model=self.name)


class LargeModel:
    name = "large"

    def __init__(self):
        texts, labels = load("train.csv")
        self.pipe = make_pipeline(TfidfVectorizer(ngram_range=(1, 3)),
                                  LogisticRegression(max_iter=2000, C=10)).fit(texts, labels)
        self.capacity = asyncio.Semaphore(settings.LARGE_CAPACITY)
        self.delay_ms = settings.LARGE_DELAY_MS
        self.hang_rate = 0.0          # chaos: share of calls that hang
        self._rng = random.Random(7)

    async def predict(self, text: str) -> Prediction:
        if self._rng.random() < self.hang_rate:
            # a stuck call: no error, no log line, it just does not answer for a long time
            await asyncio.sleep(settings.HANG_SECONDS)
        async with self.capacity:
            await asyncio.sleep(self.delay_ms / 1000 * self._rng.uniform(0.7, 1.3))
            probs = self.pipe.predict_proba([text])[0]
        best = probs.argmax()
        return Prediction(label=str(self.pipe.classes_[best]), confidence=round(float(probs[best]), 3),
                          model=self.name)
