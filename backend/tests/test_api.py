# backend/tests/test_api.py
import os
import httpx
import pytest

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# 只用 asyncio，别让 anyio 去拉 trio
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

async def create_or_get_permission(ac: httpx.AsyncClient, name: str) -> str:
    r = await ac.post("/permissions", json={"name": name})
    if r.status_code in (200, 201):
        return r.json()["id"]
    if r.status_code == 409:
        # 两种后端实现都有可能：/permissions/by-name/{name} 或 query 参数
        r2 = await ac.get(f"/permissions/by-name/{name}")
        if r2.status_code == 200:
            return r2.json()["id"]
        r3 = await ac.get("/permissions", params={"name": name})
        assert r3.status_code == 200 and r3.json(), f"permission {name} not found by query"
        return r3.json()[0]["id"]
    assert False, f"create permission failed: {r.status_code} {r.text}"

async def create_or_get_role(ac: httpx.AsyncClient, tenant_id: str, name: str) -> str:
    r = await ac.post("/roles", json={"tenant_id": tenant_id, "name": name})
    if r.status_code in (200, 201):
        return r.json()["id"]
    if r.status_code == 409:
        r2 = await ac.get("/roles", params={"tenant_id": tenant_id, "name": name})
        assert r2.status_code == 200 and r2.json(), f"role {name} not found"
        return r2.json()[0]["id"]
    assert False, f"create role failed: {r.status_code} {r.text}"

async def create_or_get_account(ac: httpx.AsyncClient, tenant_id: str, username: str, email: str) -> str:
    r = await ac.post("/accounts", json={"username": username, "email": email, "tenant_id": tenant_id})
    if r.status_code in (200, 201):
        return r.json()["id"]
    if r.status_code == 409:
        r2 = await ac.get("/accounts", params={"tenant_id": tenant_id, "username": username})
        assert r2.status_code == 200 and r2.json(), f"account {username} not found"
        return r2.json()[0]["id"]
    assert False, f"create account failed: {r.status_code} {r.text}"

@pytest.mark.anyio
async def test_crud_and_rbac_pg_adapter():
    tenant = "t1"
    perm_name = "doc:read"
    role_name = "reader"
    username  = "alice"
    email     = "alice@example.com"

    async with httpx.AsyncClient(base_url=BASE_URL) as ac:
        # 幂等 create-or-get
        perm_id = await create_or_get_permission(ac, perm_name)
        role_id = await create_or_get_role(ac, tenant, role_name)
        acc_id  = await create_or_get_account(ac, tenant, username, email)

        # 绑定：接受 200/201/204/409
        r = await ac.post(f"/roles/{role_id}/permissions/{perm_id}")
        assert r.status_code in (200, 201, 204, 409), r.text

        r = await ac.post(f"/accounts/{acc_id}/roles/{role_id}")
        assert r.status_code in (200, 201, 204, 409), r.text
        # 授权检查
        # 第一个测试：期望有权限
        r = await ac.post("/check-access", json={"account_id": acc_id, "tenant_id": tenant, "resource": "/docs/1", "action": "read"})

        # 验证状态码，并检查 'has_access' 键的值
        assert r.status_code == 200
        assert r.json()["has_access"] is True, f"Expected access to be True, but got: {r.text}"

        # 第二个测试：期望无权限
        r = await ac.post("/check-access", json={"account_id": acc_id, "tenant_id": tenant, "resource": "/docs/1", "action": "write"})

        # 验证状态码，并检查 'has_access' 键的值
        assert r.status_code == 200
        assert r.json()["has_access"] is False, f"Expected access to be False, but got: {r.text}"
