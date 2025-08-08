# backend/api.py
from __future__ import annotations
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Path, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

from .db import init_engine, init_db, dispose_engine
from .service import AuthService
from .core.casbin_adapter import CasbinEngine

# --------- Settings & CORS 来源（生产不要 *）---------
ALLOWED_ORIGINS = []  # 从环境或配置加载
app = FastAPI(title="AuthOne IAM Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],  # dev 时可 *
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# --------- 请求体模型（契约化）---------
class PermissionCreate(BaseModel):
    name: str = Field(min_length=3)
    description: str = Field(default="")

class RoleCreate(BaseModel):
    name: str = Field(min_length=1)
    tenant_id: Optional[str] = None
    description: str = Field(default="")

class GroupCreate(BaseModel):
    name: str
    tenant_id: Optional[str] = None
    description: str = Field(default="")

class AccountCreate(BaseModel):
    username: str
    email: EmailStr
    tenant_id: Optional[str] = None

class ResourceCreate(BaseModel):
    resource_type: str = Field(min_length=1)
    name: str = Field(min_length=1)
    tenant_id: Optional[str] = None
    owner_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

# --------- 生命周期：引擎与服务 ---------
_svc: Optional[AuthService] = None

@app.on_event("startup")
async def startup() -> None:
    global _svc
    init_engine(db_url="sqlite+aiosqlite:///./app.db")  # 生产从环境读取
    await init_db()
    # 这里示意注入一个已构造好的 enforcer
    import casbin
    enforcer = casbin.Enforcer("rbac_model.conf", "rbac_policy.csv")  # 生产使用 adapter
    _svc = await AuthService.create(CasbinEngine(enforcer))

@app.on_event("shutdown")
async def shutdown() -> None:
    await dispose_engine()

def _svc_required() -> AuthService:
    if _svc is None:
        raise RuntimeError("Service not initialized")
    return _svc

@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")

# --------- 基础 CRUD ---------
@app.post("/permissions", status_code=status.HTTP_201_CREATED)
async def create_permission(body: PermissionCreate):
    svc = _svc_required()
    p = await svc.create_permission(body.name, body.description)
    return {"id": p.id, "name": p.name, "description": p.description}

@app.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(permission_id: str):
    svc = _svc_required()
    ok = await svc.delete_permission(permission_id)
    if not ok:
        raise HTTPException(status_code=404, detail="permission not found")

@app.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_role(body: RoleCreate):
    svc = _svc_required()
    r = await svc.create_role(body.tenant_id, body.name, body.description)
    return {"id": r.id, "name": r.name, "tenant_id": r.tenant_id}

@app.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: str):
    svc = _svc_required()
    ok = await svc.delete_role(role_id)
    if not ok:
        raise HTTPException(status_code=404, detail="role not found")

@app.post("/groups", status_code=status.HTTP_201_CREATED)
async def create_group(body: GroupCreate):
    svc = _svc_required()
    g = await svc.create_group(body.tenant_id, body.name, body.description)
    return {"id": g.id, "name": g.name, "tenant_id": g.tenant_id}

@app.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: str):
    svc = _svc_required()
    ok = await svc.delete_group(group_id)
    if not ok:
        raise HTTPException(status_code=404, detail="group not found")

@app.post("/accounts", status_code=status.HTTP_201_CREATED)
async def create_account(body: AccountCreate):
    svc = _svc_required()
    a = await svc.create_account(body.username, str(body.email), body.tenant_id)
    return {"id": a.id, "username": a.username, "tenant_id": a.tenant_id}

@app.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: str):
    svc = _svc_required()
    ok = await svc.delete_account(account_id)
    if not ok:
        raise HTTPException(status_code=404, detail="account not found")

@app.post("/resources", status_code=status.HTTP_201_CREATED)
async def create_resource(body: ResourceCreate):
    svc = _svc_required()
    r = await svc.create_resource(body.resource_type, body.name, body.tenant_id, body.owner_id, body.metadata)
    return {"id": r.id, "name": r.name, "type": r.type, "tenant_id": r.tenant_id}

@app.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(resource_id: str):
    svc = _svc_required()
    ok = await svc.delete_resource(resource_id)
    if not ok:
        raise HTTPException(status_code=404, detail="resource not found")

# --------- 关系绑定 / 解绑 ---------
@app.post("/roles/{role_id}/permissions/{permission_id}")
async def assign_permission_to_role(role_id: str, permission_id: str):
    svc = _svc_required()
    try:
        await svc.assign_permission_to_role(role_id, permission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}

@app.delete("/roles/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(role_id: str, permission_id: str):
    svc = _svc_required()
    try:
        await svc.remove_permission_from_role(role_id, permission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}

@app.post("/accounts/{account_id}/roles/{role_id}")
async def assign_role_to_account(account_id: str, role_id: str):
    svc = _svc_required()
    try:
        await svc.assign_role_to_account(account_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}

@app.delete("/accounts/{account_id}/roles/{role_id}")
async def remove_role_from_account(account_id: str, role_id: str):
    svc = _svc_required()
    try:
        await svc.remove_role_from_account(account_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}

@app.post("/groups/{group_id}/roles/{role_id}")
async def assign_role_to_group(group_id: str, role_id: str):
    svc = _svc_required()
    try:
        await svc.assign_role_to_group(group_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}

@app.delete("/groups/{group_id}/roles/{role_id}")
async def remove_role_from_group(group_id: str, role_id: str):
    svc = _svc_required()
    try:
        await svc.remove_role_from_group(group_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}

@app.post("/accounts/{account_id}/groups/{group_id}")
async def assign_group_to_account(account_id: str, group_id: str):
    svc = _svc_required()
    try:
        await svc.assign_group_to_account(account_id, group_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}

@app.delete("/accounts/{account_id}/groups/{group_id}")
async def remove_group_from_account(account_id: str, group_id: str):
    svc = _svc_required()
    try:
        await svc.remove_group_from_account(account_id, group_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}
