import pytest

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
