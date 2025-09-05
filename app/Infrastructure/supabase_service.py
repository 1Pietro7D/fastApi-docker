# app/Infrastructure/supabase_service.py

from __future__ import annotations
import httpx
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from app.config import settings

"""
Service async per Supabase Auth (GoTrue).
⚠️ Tutte le chiamate (anche login/password grant) usano la SERVICE KEY.
"""

# --------- Header ---------

def _service_headers() -> dict[str, str]:
    k = settings.SUPABASE_KEY
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "apikey": k,
        "Authorization": f"Bearer {k}",
    }

# --------- HTTP helper ---------

async def _request(
    method: str,
    path: str,
    json: Optional[dict] = None,
) -> Dict[str, Any]:
    base = settings.SUPABASE_PROJECT_URL.rstrip("/")
    url = f"{base}{path}"
    timeout = httpx.Timeout(30.0, connect=8.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.request(method, url, headers=_service_headers(), json=json)

    try:
        data: Dict[str, Any] = resp.json() if resp.content else {}
    except Exception:
        data = {"message": "Invalid JSON response from Supabase"}

    if resp.status_code >= 400:
        return {
            "error": "auth",
            "message": data.get("msg")
            or data.get("error_description")
            or data.get("message")
            or "error",
            "http_status": resp.status_code,
            "error_code": data.get("error") or "ERROR",
            "raw": data,
        }

    data["http_status"] = resp.status_code
    data["error"] = None
    return data

# --------- API ---------

async def sign_up(email: str, password: str, user_meta: Optional[dict] = None) -> Dict[str, Any]:
    payload = {"email": email, "password": password}
    if user_meta:
        payload["data"] = user_meta
    return await _request("POST", "/auth/v1/signup", payload)

async def sign_in(email: str, password: str) -> Dict[str, Any]:
    """
    Effettua login (password grant) usando la service key.
    """
    payload = {"email": email, "password": password}
    return await _request("POST", "/auth/v1/token?grant_type=password", payload)

async def update_user(user_id: str, patch: dict) -> Dict[str, Any]:
    return await _request("PUT", f"/auth/v1/admin/users/{user_id}", patch)

async def admin_logout_user(user_id: str) -> Dict[str, Any]:
    return await _request("POST", f"/auth/v1/admin/users/{user_id}/logout", json={})

async def admin_confirm_user(user_id: str) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    patch = {"email_confirmed_at": now_iso}
    return await update_user(user_id, patch)

async def register_user(
    email: str,
    password: str,
    user_meta: Optional[dict] = None,
    app_meta: Optional[dict] = None,
    banned_until: Optional[str] = None,
    phone: Optional[str] = None,
) -> Dict[str, Any]:
    res = await sign_up(email, password, user_meta or {})
    if res.get("error"):
        return res

    user = (res.get("user") or {})
    user_id = user.get("id")
    if not user_id:
        return res

    patch: dict = {}
    if app_meta is not None:
        patch["app_metadata"] = app_meta
    if banned_until is not None:
        patch["banned_until"] = banned_until
    if phone is not None:
        patch["phone"] = phone

    if patch:
        upd = await update_user(user_id, patch)
        if not upd.get("error") and isinstance(upd.get("user"), dict):
            res["user"] = upd["user"]

    if settings.ENV == "dev" and settings.AUTH_AUTO_CONFIRM_DEV:
        conf = await admin_confirm_user(user_id)
        if not conf.get("error") and isinstance(conf.get("user"), dict):
            res["user"] = conf["user"]

    return res
