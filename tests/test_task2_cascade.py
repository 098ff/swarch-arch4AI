"""Task 2 self-check:  python -m pytest tests/test_task2_cascade.py -v"""
import asyncio

from inference_service.patterns import cascade


class FakeSmall:
    def __init__(self, confidence):
        self.confidence, self.calls = confidence, 0

    def predict(self, text):
        self.calls += 1
        return {"label": "positive", "confidence": self.confidence, "model": "small"}


class FakeLarge:
    def __init__(self):
        self.calls = 0

    async def predict(self, text):
        self.calls += 1
        await asyncio.sleep(0)
        return {"label": "negative", "confidence": 0.97, "model": "large"}


def run(confidence, threshold):
    small, large = FakeSmall(confidence), FakeLarge()
    result = asyncio.run(cascade("The pad thai was not bad at all.", small, large, threshold))
    return result, small, large


def test_confident_small_model_answers_alone():
    result, small, large = run(confidence=0.92, threshold=0.8)
    assert result["model"] == "small"
    assert small.calls == 1 and large.calls == 0, "the large model must not be called when the small one is confident"


def test_unsure_small_model_escalates_to_large():
    result, small, large = run(confidence=0.61, threshold=0.8)
    assert result["model"] == "large"
    assert small.calls == 1 and large.calls == 1


def test_threshold_is_inclusive():
    result, _, large = run(confidence=0.8, threshold=0.8)
    assert result["model"] == "small" and large.calls == 0, "confidence equal to the threshold counts as confident"


def test_threshold_one_always_escalates():
    result, _, _ = run(confidence=0.99, threshold=1.0)
    assert result["model"] == "large"
