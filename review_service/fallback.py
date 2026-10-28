"""Task 1 (fallback prediction). Your code goes here.

The review service calls classify() for every new review. Right now it waits
for the inference service for as long as it takes. When the large model
hangs, every review hangs with it, and so does the user.
"""
import httpx

from common import settings

PENDING = {"label": None, "confidence": None, "model": "fallback", "status": "pending"}


async def classify(client: httpx.AsyncClient, text: str) -> dict:
    """Ask the inference service for a sentiment label.

    Return the inference service's JSON plus "status": "scored".
    If it does not answer within settings.INFERENCE_TIMEOUT_S seconds, or
    answers with an error, return a copy of PENDING instead: the review is
    saved, and a batch job can score it later.
    """
    # TODO (Task 1): add a timeout and a fallback. About 4 lines change.
    #
    # Step 1. Timeout. The client was created with timeout=None, so today
    #   client.post(...) waits forever. Pass a timeout for this one call:
    #       client.post(url, json=..., timeout=<seconds>)
    #   Use settings.INFERENCE_TIMEOUT_S (1 s), not a number typed in here.
    #   When the time runs out, httpx raises httpx.TimeoutException.
    #
    # Step 2. Errors. r.raise_for_status() raises httpx.HTTPStatusError when
    #   the inference service answers with an error (HTTP 4xx or 5xx).
    #   Both exceptions are subclasses of httpx.HTTPError, so one except
    #   clause catches both. Wrap the three lines below like this:
    #       try:
    #           ...the call, raise_for_status() and the return below...
    #       except <which exception class?>:
    #           return <a pending review>
    #
    # Step 3. Fallback. In the except clause, return a *copy* of PENDING
    #   (dict(PENDING)), not PENDING itself. PENDING is one shared dict: if
    #   the caller changes the returned review, every later pending review
    #   would change with it.
    #
    # Check: python -m pytest tests/test_task1_fallback.py -v
    #   (normal answer -> "scored"; hang or HTTP 500 -> "pending" within ~1 s)
    try:
        r = await client.post(
            f"{settings.INFERENCE_URL}/predict",
            json={"text": text},
            timeout=settings.INFERENCE_TIMEOUT_S,
        )
        r.raise_for_status()
        return {**r.json(), "status": "scored"}
    except httpx.HTTPError:
        return dict(PENDING)
