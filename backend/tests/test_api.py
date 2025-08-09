import os, pytest
from httpx import AsyncClient
from backend.api import app
from backend.db import init_engine, init_db, dispose_engine

DB_URL = os.getenv("DB_URL", "postgresql+asyncpg://authone:authone@localhost:5432/authone")

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    init_engine(DB_URL)
    await init_db(drop_all=True)
    yield
    await dispose_engine()

@pytest.mark.anyio
async def test_crud_and_rbac_pg_adapter():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create permission, role, bind, account, assign, check
        r = await ac.post("/permissions", json={"name": "doc:read"}); assert r.status_code == 201, r.text
        perm_id = r.json()["id"]
        r = await ac.post("/roles", json={"tenant_id": "t1", "name": "reader"}); assert r.status_code == 201, r.text
        role_id = r.json()["id"]
        r = await ac.post(f"/roles/{role_id}/permissions/{perm_id}"); assert r.status_code == 200, r.text
        r = await ac.post("/accounts", json={"username":"alice", "email":"alice@example.com", "tenant_id":"t1"}); assert r.status_code == 201, r.text
        acc_id = r.json()["id"]
        r = await ac.post(f"/accounts/{acc_id}/roles/{role_id}"); assert r.status_code == 200, r.text
        r = await ac.post("/check_access", json={"account_id": acc_id, "tenant_id":"t1", "resource":"/docs/1", "action":"read"})
        assert r.status_code == 200 and r.json()["allowed"] is True
        r = await ac.post("/check_access", json={"account_id": acc_id, "tenant_id":"t1", "resource":"/docs/1", "action":"write"})
        assert r.status_code == 200 and r.json()["allowed"] is False

        # duplicate checks
        assert (await ac.post("/permissions", json={"name": "doc:read"})).status_code == 400
        assert (await ac.post("/roles", json={"tenant_id": "t1", "name": "reader"})).status_code == 400
        assert (await ac.post("/accounts", json={"username":"alice", "email":"alice@example.com", "tenant_id":"t1"})).status_code == 400