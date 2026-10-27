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
    predict_small = small.predict(text)
    if predict_small["confidence"] >= threshold:
        return predict_small
    else:
        predict_large = await large.predict(text)
        return predict_large


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
        # TODO (Task 3): normalise text so "  Delicious! " and "delicious!" give the same key.
        #   About 1 line. Return a string that is:
        #     - all lower case (str.lower())
        #     - without spaces at the start and end
        #     - with runs of spaces inside squeezed to one: "Too   salty" -> "too salty"
        #   Hint: text.split() with no argument splits on any run of whitespace
        #   and drops the ends; " ".join(...) glues the words back together.
        #   Keep the punctuation: "Delicious!" and "Delicious" may stay different.
        raise NotImplementedError("Task 3: implement PredictionCache.key()")

    def get(self, text):
        """Return the cached Prediction for text, or None. Count a hit or a miss."""
        # TODO (Task 3): about 7 lines.
        #   1. Turn text into a key with self.key(text).
        #   2. If the key is in self._data (a hit):
        #        - mark it as just used: self._data.move_to_end(key)
        #        - add 1 to self.hits
        #        - return the stored Prediction
        #   3. Otherwise (a miss): add 1 to self.misses and return None.
        #   Without move_to_end, the cache forgets what was used recently, and
        #   test_size_limit_evicts_least_recently_used fails.
        raise NotImplementedError("Task 3: implement PredictionCache.get()")

    def put(self, text, prediction):
        """Store prediction for text; evict the least recently used entry when over max_size."""
        # TODO (Task 3): about 5 lines.
        #   1. Turn text into a key with self.key(text).
        #   2. Store the prediction under that key, and mark it as just used
        #      (move_to_end), in case the key was already there.
        #   3. If the cache now holds more than self.max_size entries, remove
        #      the least recently used one: self._data.popitem(last=False).
        #   put() does not count hits or misses: only get() does.
        raise NotImplementedError("Task 3: implement PredictionCache.put()")
