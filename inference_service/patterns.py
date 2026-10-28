"""Task 2 (cascade) and Task 3 (cached predictions). Your code goes here.

The inference service calls these when you switch the strategy to "cascade"
or turn the cache on (tools/loadtest.py does that for you).
"""
from collections import OrderedDict


# ---------------------------------------------------------------- Task 2
async def cascade(text, small, large, threshold):
    """Two-phase prediction: ask the small model first, and the large model only
    when the small one is not confident enough.

    small.predict(text)        -> Prediction, fast, call it normally
    await large.predict(text)  -> Prediction, slow, limited capacity
    A Prediction is a dict: {"label": ..., "confidence": 0.5-1.0, "model": ...}

    Return the small model's prediction if its confidence >= threshold,
    otherwise return the large model's prediction.
    """
    # TODO (Task 2): about 4 lines. Delete the raise line below when you start.
    #
    # Step 1. Ask the small model and keep its answer in a variable.
    #   small.predict() is a normal function: call it without await.
    #
    # Step 2. Decide. Read the answer's confidence (a Prediction is a dict,
    #   so use ["confidence"]) and compare it with threshold. Confidence
    #   *equal* to the threshold counts as confident.
    #     - Confident: return the small model's answer, and stop there.
    #       Do not call the large model "just to compare": every large call
    #       costs money, and the tests check that it is not called.
    #     - Not confident: escalate to the large model.
    #
    # Step 3. Escalate. large.predict() is a coroutine (async def), so call it
    #   with await. Without await you get a coroutine object, not a Prediction.
    #   Return its answer as it is: the "model" field tells the load test
    #   which model answered.
    #
    # Check: python -m pytest tests/test_task2_cascade.py -v
    #   (confident -> "small" and 0 large calls; unsure -> "large";
    #    confidence == threshold -> "small"; threshold 1.0 -> always "large")
    prediction = small.predict(text)
    if prediction["confidence"] >= threshold:
        return prediction
    return await large.predict(text)


# ---------------------------------------------------------------- Task 3
class PredictionCache:
    """Cached predictions: remember answers for texts we have already seen.

    - Two texts that differ only in upper/lower case or extra spaces are the
      same entry ("Delicious!" and "  delicious! ").
    - Keep at most max_size entries; when full, evict the least recently used.
    - Count hits and misses (the service reports them in /metrics).

    Hint: an OrderedDict remembers insertion order; move_to_end(key) marks a key
    as recently used, and popitem(last=False) removes the oldest one.

    How the pieces fit: self._data maps key(text) -> Prediction. Keep it in
    order from least recently used (front) to most recently used (back).
    Then the entry to evict is always the one at the front.

        d = OrderedDict()
        d["a"] = 1; d["b"] = 2      # order: a, b
        d.move_to_end("a")          # order: b, a   ("a" was just used)
        d.popitem(last=False)       # removes "b", the least recently used

    Implement the three methods in order (key, get, put); get and put both
    start by calling self.key(text).

    Check: python -m pytest tests/test_task3_cache.py -v
    """

    def __init__(self, max_size=1000):
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self._data = OrderedDict()

    @staticmethod
    def key(text):
        return " ".join(text.lower().split())

    def get(self, text):
        """Return the cached Prediction for text, or None. Count a hit or a miss."""
        k = self.key(text)
        if k in self._data:
            self._data.move_to_end(k)
            self.hits += 1
            return self._data[k]
        self.misses += 1
        return None

    def put(self, text, prediction):
        """Store prediction for text; evict the least recently used entry when over max_size."""
        k = self.key(text)
        self._data[k] = prediction
        self._data.move_to_end(k)
        if len(self._data) > self.max_size:
            self._data.popitem(last=False)
