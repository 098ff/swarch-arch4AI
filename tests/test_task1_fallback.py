"""Task 1 self-check:  python -m pytest tests/test_task1_fallback.py -v

Each test starts a fake inference service on a free local port: one that
answers normally, one that never answers, and one that returns HTTP 500.
"""
import asyncio
import json
import time

import httpx
import pytest

from common import settings
from review_service import fallback


async def _fake_server(behaviour):
    async def handle(reader, writer):
        await reader.read(65536)
        if behaviour == "hang":
            await asyncio.sleep(30)
            return
        if behaviour == "error":
            body, status = b'{"detail": "boom"}', "500 Internal Server Error"
        else:
            body = json.dumps({"label": "positive", "confidence": 0.9, "model": "large"}).encode()
            status = "200 OK"
        writer.write(f"HTTP/1.1 {status}\r\nContent-Type: application/json\r\n"
                     f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode() + body)
        await writer.drain()
        writer.close()

    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    return server, f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}"


async def _classify_against(behaviour, monkeypatch):
    server, url = await _fake_server(behaviour)
    monkeypatch.setattr(settings, "INFERENCE_URL", url)
    monkeypatch.setattr(settings, "INFERENCE_TIMEOUT_S", 0.5)
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            start = time.perf_counter()
            try:
                result = await asyncio.wait_for(fallback.classify(client, "Delicious!"), timeout=5)
            except asyncio.TimeoutError:
                pytest.fail("classify() was still waiting after 5 s: it needs a timeout")
            except httpx.HTTPError as e:
                pytest.fail(f"classify() raised {type(e).__name__}: it should return a pending review instead")
            return result, time.perf_counter() - start
    finally:
        server.close()


def test_normal_answer_is_scored(monkeypatch):
    result, _ = asyncio.run(_classify_against("ok", monkeypatch))
    assert result["label"] == "positive"
    assert result["status"] == "scored"


def test_hang_falls_back_within_timeout(monkeypatch):
    result, seconds = asyncio.run(_classify_against("hang", monkeypatch))
    assert result["status"] == "pending", "a hanging inference service must give a pending review"
    assert result["label"] is None
    assert seconds < 1.5, f"took {seconds:.1f} s; the fallback should kick in after INFERENCE_TIMEOUT_S"


def test_server_error_falls_back(monkeypatch):
    result, _ = asyncio.run(_classify_against("error", monkeypatch))
    assert result["status"] == "pending", "an HTTP 500 must also give a pending review"


def test_fallback_does_not_share_the_pending_dict(monkeypatch):
    result, _ = asyncio.run(_classify_against("error", monkeypatch))
    result["label"] = "changed"
    assert fallback.PENDING["label"] is None, "return a copy of PENDING, not PENDING itself"
