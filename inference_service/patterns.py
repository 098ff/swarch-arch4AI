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
    # TODO (Task 2): about 4 lines.
    raise NotImplementedError("Task 2: implement cascade() in inference_service/patterns.py")


# ---------------------------------------------------------------- Task 3
class PredictionCache:
    """Cached predictions: remember answers for texts we have already seen.

    - Two texts that differ only in upper/lower case or extra spaces are the
      same entry ("Delicious!" and "  delicious! ").
    - Keep at most max_size entries; when full, evict the least recently used.
    - Count hits and misses (the service reports them in /metrics).

    Hint: an OrderedDict remembers insertion order; move_to_end(key) marks a key
    as recently used, and popitem(last=False) removes the oldest one.
    """

    def __init__(self, max_size=1000):
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self._data = OrderedDict()

    @staticmethod
    def key(text):
        # TODO (Task 3): normalise text so "  Delicious! " and "delicious!" give the same key.
        raise NotImplementedError("Task 3: implement PredictionCache.key()")

    def get(self, text):
        """Return the cached Prediction for text, or None. Count a hit or a miss."""
        # TODO (Task 3)
        raise NotImplementedError("Task 3: implement PredictionCache.get()")

    def put(self, text, prediction):
        """Store prediction for text; evict the least recently used entry when over max_size."""
        # TODO (Task 3)
        raise NotImplementedError("Task 3: implement PredictionCache.put()")
