"""FastAPI 应用入口。

此模块定义了一组 RESTful 接口，用于管理权限相关实体及执行权限校验。
客户端（如前端或其他服务）可以通过这些接口完成权限配置和访问判断。
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Path

from .config import Settings
from .models import (
    AccessCheckRequest,
    AccessCheckResponse,
)
from .service import AuthService

app = FastAPI(title="AuthOne IAM Service")

_settings = Settings()  # 默认配置，可根据需要替换
_svc = AuthService.create(_settings)


@app.post("/permissions", response_model=dict)
def create_permission(name: str, description: str = "") -> dict:
    perm = _svc.create_permission(name, description)
    return {"id": perm.id, "name": perm.name, "description": perm.description}


@app.post("/roles", response_model=dict)
def create_role(name: str, tenant_id: str | None = None, description: str = "") -> dict:
    role = _svc.create_role(tenant_id, name, description)
    return {"id": role.id, "name": role.name, "tenant_id": role.tenant_id}


@app.post("/groups", response_model=dict)
def create_group(name: str, tenant_id: str | None = None, description: str = "") -> dict:
    group = _svc.create_group(tenant_id, name, description)
    return {"id": group.id, "name": group.name, "tenant_id": group.tenant_id}


@app.post("/accounts", response_model=dict)
def create_account(username: str, email: str, tenant_id: str | None = None) -> dict:
    acc = _svc.create_account(username, email, tenant_id)
    return {"id": acc.id, "username": acc.username, "tenant_id": acc.tenant_id}


@app.post("/resources", response_model=dict)
def create_resource(
    resource_type: str,
    name: str,
    tenant_id: str | None = None,
    owner_id: str | None = None,
) -> dict:
    res = _svc.create_resource(resource_type, name, tenant_id, owner_id)
    return {"id": res.id, "name": res.name, "type": res.type, "tenant_id": res.tenant_id}


@app.post("/roles/{role_id}/permissions/{permission_id}")
def assign_permission_to_role(
    role_id: str = Path(..., description="角色 ID"),
    permission_id: str = Path(..., description="权限 ID"),
) -> dict:
    try:
        _svc.assign_permission_to_role(role_id, permission_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok"}


@app.post("/accounts/{account_id}/roles/{role_id}")
def assign_role_to_account(
    account_id: str = Path(..., description="账户 ID"),
    role_id: str = Path(..., description="角色 ID"),
) -> dict:
    try:
        _svc.assign_role_to_account(account_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok"}


@app.post("/groups/{group_id}/roles/{role_id}")
def assign_role_to_group(
    group_id: str = Path(..., description="用户组 ID"),
    role_id: str = Path(..., description="角色 ID"),
) -> dict:
    try:
        _svc.assign_role_to_group(group_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok"}


@app.post("/accounts/{account_id}/groups/{group_id}")
def assign_group_to_account(
    account_id: str = Path(..., description="账户 ID"),
    group_id: str = Path(..., description="用户组 ID"),
) -> dict:
    try:
        _svc.assign_group_to_account(account_id, group_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok"}


@app.post("/access/check", response_model=AccessCheckResponse)
def check_access(req: AccessCheckRequest) -> AccessCheckResponse:
    return _svc.check_access(req)
