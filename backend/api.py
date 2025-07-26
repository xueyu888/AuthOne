"""FastAPI 应用入口。

此模块定义了一组 RESTful 接口，用于管理权限相关实体及执行权限校验。
客户端（如前端或其他服务）可以通过这些接口完成权限配置和访问判断。
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings
from .models import (
    AccessCheckRequest,
    AccessCheckResponse,
)
from .service import AuthService
from .db import init_db

app = FastAPI(title="AuthOne IAM Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或限制具体来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，包括 OPTIONS
    allow_headers=["*"],  # 允许所有 headers
)

_settings: Settings | None = None
_svc: AuthService | None = None


@app.on_event("startup")
async def on_startup() -> None:
    """初始化数据库并创建服务实例。

    当 FastAPI 应用启动时，先创建数据库表结构，再异步初始化
    ``AuthService``。如果需要自定义配置，可在此修改 ``_settings``。
    """
    global _settings, _svc
    _settings = Settings()
    # 创建数据库表
    await init_db(_settings)
    # 创建服务实例
    _svc = await AuthService.create(_settings)


def _require_service() -> AuthService:
    """获取已经初始化的 AuthService 实例。

    在处理请求之前，确保服务已创建；否则抛出运行时错误。
    """
    if _svc is None:
        raise RuntimeError("Service not initialized")
    return _svc


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")


@app.post("/permissions", response_model=dict)
async def create_permission(name: str, description: str = "") -> dict:
    svc = _require_service()
    perm = await svc.create_permission(name, description)
    return {"id": perm.id, "name": perm.name, "description": perm.description}


@app.get("/permissions", response_model=list[dict])
async def list_permissions(tenant_id: str | None = None) -> list[dict]:
    svc = _require_service()
    perms = await svc.list_permissions(tenant_id)
    return [
        {"id": p.id, "name": p.name, "description": p.description}
        for p in perms
    ]


@app.post("/roles", response_model=dict)
async def create_role(name: str, tenant_id: str | None = None, description: str = "") -> dict:
    svc = _require_service()
    role = await svc.create_role(tenant_id, name, description)
    return {"id": role.id, "name": role.name, "tenant_id": role.tenant_id}


@app.get("/roles", response_model=list[dict])
async def list_roles(tenant_id: str | None = None) -> list[dict]:
    svc = _require_service()
    roles = await svc.list_roles(tenant_id)
    return [
        {
            "id": r.id,
            "name": r.name,
            "tenant_id": r.tenant_id,
            "permissions": r.permissions,
        }
        for r in roles
    ]


@app.post("/groups", response_model=dict)
async def create_group(name: str, tenant_id: str | None = None, description: str = "") -> dict:
    svc = _require_service()
    group = await svc.create_group(tenant_id, name, description)
    return {"id": group.id, "name": group.name, "tenant_id": group.tenant_id}


@app.get("/groups", response_model=list[dict])
async def list_groups(tenant_id: str | None = None) -> list[dict]:
    svc = _require_service()
    groups = await svc.list_groups(tenant_id)
    return [
        {
            "id": g.id,
            "name": g.name,
            "tenant_id": g.tenant_id,
            "roles": g.roles,
        }
        for g in groups
    ]


@app.post("/accounts", response_model=dict)
async def create_account(username: str, email: str, tenant_id: str | None = None) -> dict:
    svc = _require_service()
    acc = await svc.create_account(username, email, tenant_id)
    return {"id": acc.id, "username": acc.username, "tenant_id": acc.tenant_id}


@app.get("/accounts", response_model=list[dict])
async def list_accounts(tenant_id: str | None = None) -> list[dict]:
    svc = _require_service()
    accounts = await svc.list_accounts(tenant_id)
    return [
        {
            "id": a.id,
            "username": a.username,
            "email": a.email,
            "tenant_id": a.tenant_id,
            "roles": a.roles,
            "groups": a.groups,
        }
        for a in accounts
    ]


@app.post("/resources", response_model=dict)
async def create_resource(
    resource_type: str,
    name: str,
    tenant_id: str | None = None,
    owner_id: str | None = None,
) -> dict:
    svc = _require_service()
    res = await svc.create_resource(resource_type, name, tenant_id, owner_id)
    return {"id": res.id, "name": res.name, "type": res.type, "tenant_id": res.tenant_id}


@app.get("/resources", response_model=list[dict])
async def list_resources(tenant_id: str | None = None) -> list[dict]:
    svc = _require_service()
    res = await svc.list_resources(tenant_id)
    return [
        {
            "id": r.id,
            "name": r.name,
            "type": r.type,
            "tenant_id": r.tenant_id,
            "owner_id": r.owner_id,
        }
        for r in res
    ]


@app.post("/roles/{role_id}/permissions/{permission_id}")
async def assign_permission_to_role(
    role_id: str = Path(..., description="角色 ID"),
    permission_id: str = Path(..., description="权限 ID"),
) -> dict:
    svc = _require_service()
    try:
        await svc.assign_permission_to_role(role_id, permission_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok"}


@app.post("/accounts/{account_id}/roles/{role_id}")
async def assign_role_to_account(
    account_id: str = Path(..., description="账户 ID"),
    role_id: str = Path(..., description="角色 ID"),
) -> dict:
    svc = _require_service()
    try:
        await svc.assign_role_to_account(account_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok"}


@app.post("/groups/{group_id}/roles/{role_id}")
async def assign_role_to_group(
    group_id: str = Path(..., description="用户组 ID"),
    role_id: str = Path(..., description="角色 ID"),
) -> dict:
    svc = _require_service()
    try:
        await svc.assign_role_to_group(group_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok"}


@app.post("/accounts/{account_id}/groups/{group_id}")
async def assign_group_to_account(
    account_id: str = Path(..., description="账户 ID"),
    group_id: str = Path(..., description="用户组 ID"),
) -> dict:
    svc = _require_service()
    try:
        await svc.assign_group_to_account(account_id, group_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok"}


@app.post("/access/check", response_model=AccessCheckResponse)
async def check_access(req: AccessCheckRequest) -> AccessCheckResponse:
    svc = _require_service()
    return await svc.check_access(req)
