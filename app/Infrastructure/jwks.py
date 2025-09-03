from __future__ import annotations
import http.client, json
from functools import lru_cache
from urllib.parse import urlparse
from typing import Any
from app.config import settings

def _http_get_json(url: str) -> dict[str, Any]:
    u = urlparse(url)
    conn = http.client.HTTPSConnection(u.netloc)
    path = u.path or "/"
    if u.query:
        path += f"?{u.query}"
    conn.request("GET", path)
    resp = conn.getresponse()
    if resp.status != 200:
        raise RuntimeError(f"JWKS fetch failed: {resp.status}")
    data = resp.read()
    conn.close()
    return json.loads(data.decode("utf-8"))

@lru_cache(maxsize=1)
def get_jwks() -> dict[str, Any]:
    return _http_get_json(settings.SUPABASE_JWKS_URL)
