"""Ports, URLs and tunable numbers shared by all services.

Every value can be overridden with an environment variable of the same name.
"""
import os


def _env(name, default, cast=str):
    return cast(os.environ.get(name, default))


HOST = _env("HOST", "127.0.0.1")
GATEWAY_PORT = _env("GATEWAY_PORT", 8000, int)
REVIEW_PORT = _env("REVIEW_PORT", 8001, int)
INFERENCE_PORT = _env("INFERENCE_PORT", 8002, int)

REVIEW_URL = _env("REVIEW_URL", f"http://{HOST}:{REVIEW_PORT}")
INFERENCE_URL = _env("INFERENCE_URL", f"http://{HOST}:{INFERENCE_PORT}")
GATEWAY_URL = _env("GATEWAY_URL", f"http://{HOST}:{GATEWAY_PORT}")

# The large model stands in for an expensive model (a GPU model or an LLM API):
# each call takes LARGE_DELAY_MS, and only LARGE_CAPACITY calls run at once.
LARGE_DELAY_MS = _env("LARGE_DELAY_MS", 200, int)
LARGE_CAPACITY = _env("LARGE_CAPACITY", 4, int)
# When chaos is on, a "hung" call takes this long before it answers.
HANG_SECONDS = _env("HANG_SECONDS", 20, float)

# Task 1: how long the review service waits for the inference service.
INFERENCE_TIMEOUT_S = _env("INFERENCE_TIMEOUT_S", 1.0, float)
