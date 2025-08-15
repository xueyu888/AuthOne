# backend/tests/test_api.py

import os
import httpx
import pytest

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


async def create_or_get_permission(ac: httpx.AsyncClient, name: str) -> str:
    r = await ac.post("/permissions", json={"name": name})
    if r.status_code in (200, 201):
        return r.json()["id"]
    if r.status_code == 409:
        # MODIFIED: Use the 'name' query parameter which we added to the API
        r2 = await ac.get("/permissions", params={"name": name})
        assert r2.status_code == 200, f"Failed to get permission by name: {r2.text}"
        data = r2.json()
        assert data, f"Permission '{name}' not found"
        return data[0]["id"]
    assert False, f"create permission failed: {r.status_code} {r.text}"


async def create_or_get_role(ac: httpx.AsyncClient, tenant_id: str, name: str) -> str:
    r = await ac.post("/roles", json={"tenant_id": tenant_id, "name": name})
    if r.status_code in (200, 201):
        return r.json()["id"]
    if r.status_code == 409:
        # MODIFIED: Use the 'name' and 'tenant_id' query parameters
        r2 = await ac.get("/roles", params={"tenant_id": tenant_id, "name": name})
        assert r2.status_code == 200, f"Failed to get role by name: {r2.text}"
        data = r2.json()
        assert data, f"Role '{name}' in tenant '{tenant_id}' not found"
        return data[0]["id"]
    assert False, f"create role failed: {r.status_code} {r.text}"


async def create_or_get_account(ac: httpx.AsyncClient, tenant_id: str, username: str, email: str) -> str:
    r = await ac.post("/accounts", json={"username": username, "email": email, "tenant_id": tenant_id})
    if r.status_code in (200, 201):
        return r.json()["id"]
    if r.status_code == 409:
        # MODIFIED: Use the 'username' and 'tenant_id' query parameters
        r2 = await ac.get("/accounts", params={"tenant_id": tenant_id, "username": username})
        assert r2.status_code == 200, f"Failed to get account by username: {r2.text}"
        data = r2.json()
        assert data, f"Account '{username}' in tenant '{tenant_id}' not found"
        return r2.json()[0]["id"]
    assert False, f"create account failed: {r.status_code} {r.text}"


@pytest.mark.anyio
async def test_crud_and_rbac_flow():
    tenant = "t1"
    perm_name = "doc:read"
    role_name = "reader"
    username = "alice"
    email = "alice@example.com"

    async with httpx.AsyncClient(base_url=BASE_URL) as ac:
        # 幂等 create-or-get
        perm_id = await create_or_get_permission(ac, perm_name)
        role_id = await create_or_get_role(ac, tenant, role_name)
        acc_id = await create_or_get_account(ac, tenant, username, email)

        # 绑定：接受 204 (成功无内容) / 409 (已存在)
        r = await ac.post(f"/roles/{role_id}/permissions/{perm_id}")
        assert r.status_code in (204, 409), r.text

        r = await ac.post(f"/accounts/{acc_id}/roles/{role_id}")
        assert r.status_code in (204, 409), r.text

        # 授权检查
        # 第一个测试：期望有权限
        r = await ac.post("/check-access",
                          json={"account_id": acc_id, "tenant_id": tenant, "resource": "/docs/1", "action": "read"})

        # MODIFIED: Check status code and the 'allowed' key
        assert r.status_code == 200, f"Check-access failed: {r.text}"
        assert r.json()["allowed"] is True, f"Expected access to be True, but got: {r.text}"

        # 第二个测试：期望无权限
        r = await ac.post("/check-access",
                          json={"account_id": acc_id, "tenant_id": tenant, "resource": "/docs/1", "action": "write"})

        # MODIFIED: Check status code and the 'allowed' key
        assert r.status_code == 200, f"Check-access failed: {r.text}"
        assert r.json()["allowed"] is False, f"Expected access to be False, but got: {r.text}"