"""Task 3 self-check:  python -m pytest tests/test_task3_cache.py -v"""
from inference_service.patterns import PredictionCache

P = {"label": "positive", "confidence": 0.9, "model": "large"}
N = {"label": "negative", "confidence": 0.8, "model": "large"}


def test_miss_then_hit():
    c = PredictionCache()
    assert c.get("Delicious!") is None
    c.put("Delicious!", P)
    assert c.get("Delicious!") == P
    assert (c.hits, c.misses) == (1, 1)


def test_case_and_spaces_are_ignored():
    c = PredictionCache()
    c.put("Delicious!", P)
    assert c.get("  delicious!  ") == P
    assert c.get("DELICIOUS!") == P
    c.put("Too   salty", N)
    assert c.get("too salty") == N


def test_different_texts_do_not_collide():
    c = PredictionCache()
    c.put("Delicious!", P)
    assert c.get("Not delicious!") is None


def test_size_limit_evicts_least_recently_used():
    c = PredictionCache(max_size=2)
    c.put("a", P)
    c.put("b", P)
    c.get("a")            # "a" is now the most recently used
    c.put("c", P)         # cache is full: "b" must go
    assert c.get("b") is None
    assert c.get("a") == P and c.get("c") == P
