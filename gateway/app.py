"""API gateway: the single entry point for clients (as in W11).

/api/reviews...      -> review service
/api/restaurants...  -> review service
"""
import httpx
from fastapi import FastAPI, Request, Response

from common import settings

app = FastAPI(title="API gateway")
client = httpx.AsyncClient(timeout=60, limits=httpx.Limits(max_connections=200))
ROUTES = {"reviews": settings.REVIEW_URL, "restaurants": settings.REVIEW_URL}


@app.api_route("/api/{path:path}", methods=["GET", "POST"])
async def proxy(path: str, request: Request):
    target = ROUTES.get(path.split("/")[0])
    if target is None:
        return Response(status_code=404, content=b'{"detail": "no route"}', media_type="application/json")
    r = await client.request(request.method, f"{target}/{path}", content=await request.body(),
                             headers={"content-type": request.headers.get("content-type", "application/json")})
    return Response(status_code=r.status_code, content=r.content, media_type="application/json")


@app.get("/health")
def health():
    return {"ok": True}
