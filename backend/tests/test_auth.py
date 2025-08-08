"""AuthService 单元测试。
"""
from __future__ import annotations
import pytest
import pytest_asyncio

# Mark all tests in this file as asyncio, requires pytest-asyncio
pytestmark = pytest.mark.asyncio

try:
    from backend import AuthService, AccessCheckRequest, Settings
    from backend.db import init_db
except ImportError:
    AuthService = None
    AccessCheckRequest = None
    Settings = None
    init_db = None




@pytest_asyncio.fixture
async def auth_service() -> AuthService:
    if any(x is None for x in [AuthService, Settings, init_db]):
        pytest.skip("Required backend dependencies are missing")

    settings = Settings(
        db_url="sqlite+aiosqlite:///./test.db",
        db_url_sync="sqlite:///./test.db",
    )
    
    await init_db(settings, drop_all=True)

    svc = await AuthService.create(settings)
    return svc

    
async def test_account_role_permission(auth_service: AuthService):
    svc = auth_service
    acc = await svc.create_account("alice", "alice@example.com", tenant_id="t1")
    role = await svc.create_role("t1", "admin")
    perm = await svc.create_permission("app:create", "create app")
    await svc.assign_permission_to_role(role.id, perm.id)
    await svc.assign_role_to_account(acc.id, role.id)
    
    req = AccessCheckRequest(account_id=acc.id, resource="app", action="create", tenant_id="t1")
    resp = await svc.check_access(req)
    
    assert resp.allowed is True

async def test_account_group_role_permission(auth_service: AuthService):
    svc = auth_service
    acc = await svc.create_account("bob", "bob@example.com", tenant_id="t1")
    group = await svc.create_group("t1", "devs")
    role = await svc.create_role("t1", "developer")
    perm = await svc.create_permission("module:deploy", "deploy module")
    await svc.assign_permission_to_role(role.id, perm.id)
    await svc.assign_role_to_group(group.id, role.id)
    await svc.assign_group_to_account(acc.id, group.id)
    
    req = AccessCheckRequest(account_id=acc.id, resource="module", action="deploy", tenant_id="t1")
    resp = await svc.check_access(req)
    
    assert resp.allowed is True

async def test_tenant_isolation(auth_service: AuthService):
    svc = auth_service
    acc = await svc.create_account("carol", "carol@example.com", tenant_id="t1")
    role = await svc.create_role("t2", "crossTenantRole")
    perm = await svc.create_permission("app:delete", "delete app")
    await svc.assign_permission_to_role(role.id, perm.id)
    await svc.assign_role_to_account(acc.id, role.id)
    
    req_wrong = AccessCheckRequest(account_id=acc.id, resource="app", action="delete", tenant_id="t1")
    resp_wrong = await svc.check_access(req_wrong)
    assert resp_wrong.allowed is False

    req_no_tenant = AccessCheckRequest(account_id=acc.id, resource="app", action="delete")
    resp_no = await svc.check_access(req_no_tenant)
    assert resp_no.allowed is False

async def test_unauthorized(auth_service: AuthService):
    svc = auth_service
    acc = await svc.create_account("dave", "dave@example.com", tenant_id="t1")
    perm = await svc.create_permission("file:read", "read file")
    role = await svc.create_role("t1", "reader")
    await svc.assign_permission_to_role(role.id, perm.id)
    
    req = AccessCheckRequest(account_id=acc.id, resource="file", action="read", tenant_id="t1")
    resp = await svc.check_access(req)
    
    assert resp.allowed is False
