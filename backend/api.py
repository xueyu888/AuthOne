from __future__ import annotations

import os
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from uuid import UUID

import casbin
from casbin.util import key_match_func, regex_match_func
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

from .db import init_engine, init_db, dispose_engine, get_sessionmaker
from .service.auth_service import AuthService, DuplicateError, NotFoundError
from .core.casbin_pg_adapter import AsyncPGAdapter


DB_URL = os.getenv("DB_URL", "postgresql+asyncpg://postgres:123@127.0.0.1:5432/authone")
MODEL_PATH = os.getenv("CASBIN_MODEL_PATH", "rbac_model.conf")



@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1) DB
    await init_engine(DB_URL)
    await init_db()
    sm = get_sessionmaker()

    # 2) Casbin（后台线程适配器）
    adapter = AsyncPGAdapter(DB_URL)
    def _build() -> casbin.Enforcer:
        e = casbin.Enforcer(MODEL_PATH, adapter)
        e.add_function("keyMatch", key_match_func)
        e.add_function("regexMatch", regex_match_func)
        e.enable_auto_save(True)
        return e

    enforcer = await asyncio.to_thread(_build)
    svc = AuthService(sm, enforcer)

    app.state.adapter = adapter
    app.state.enforcer = enforcer
    app.state.svc = svc

    try:
        yield
    finally:
        adapter.close()
        await dispose_engine()



app = FastAPI(title="AuthOne IAM Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产请精确配置
    # allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

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
    owner_id: Optional[UUID] = None
    metadata: dict = Field(default_factory=dict)

class AccessCheck(BaseModel):
    account_id: UUID
    resource: str
    action: str
    tenant_id: Optional[str] = None


# ---------- Dependency ----------


def _svc() -> AuthService:
    svc: AuthService = app.state.svc
    return svc

# ---------- CRUD ----------
@app.post("/permissions", status_code=status.HTTP_201_CREATED)
async def create_permission(body: PermissionCreate):
    try:
        pid = await _svc().create_permission(body.name, body.description)
        return {"id": str(pid), "name": body.name, "description": body.description}
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/permissions")
async def list_permissions():
    rows = await _svc().list_permissions()
    return [{"id": str(r.id), "name": r.name, "description": r.description or ""} for r in rows]

@app.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(permission_id: UUID):
    try:
        await _svc().delete_permission(permission_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_role(body: RoleCreate):
    try:
        rid = await _svc().create_role(body.tenant_id, body.name, body.description)
        return {"id": str(rid), "name": body.name, "tenant_id": body.tenant_id}
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/roles")
async def list_roles(tenant_id: Optional[str] = Query(default=None)):
    rows = await _svc().list_roles(tenant_id)
    return [{"id": str(r.id), "name": r.name, "tenant_id": r.tenant_id} for r in rows]

@app.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: UUID):
    try:
        await _svc().delete_role(role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/groups", status_code=status.HTTP_201_CREATED)
async def create_group(body: GroupCreate):
    try:
        gid = await _svc().create_group(body.tenant_id, body.name, body.description)
        return {"id": str(gid), "name": body.name, "tenant_id": body.tenant_id}
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/groups")
async def list_groups(tenant_id: Optional[str] = Query(default=None)):
    rows = await _svc().list_groups(tenant_id)
    return [{"id": str(r.id), "name": r.name, "tenant_id": r.tenant_id} for r in rows]

@app.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: UUID):
    try:
        await _svc().delete_group(group_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/accounts", status_code=status.HTTP_201_CREATED)
async def create_account(body: AccountCreate):
    try:
        aid = await _svc().create_account(body.username, str(body.email), body.tenant_id)
        return {"id": str(aid), "username": body.username, "tenant_id": body.tenant_id}
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/accounts")
async def list_accounts(tenant_id: Optional[str] = Query(default=None)):
    rows = await _svc().list_accounts(tenant_id)
    return [{"id": str(r.id), "username": r.username, "tenant_id": r.tenant_id} for r in rows]

@app.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: UUID):
    try:
        await _svc().delete_account(account_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    
@app.post("/resources", status_code=status.HTTP_201_CREATED)
async def create_resource(body: ResourceCreate):
    try:
        rid = await _svc().create_resource(body.resource_type, body.name, body.tenant_id, body.owner_id, body.metadata)
        return {"id": str(rid), "name": body.name, "type": body.resource_type, "tenant_id": body.tenant_id}
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/resources")
async def list_resources(tenant_id: Optional[str] = Query(default=None)):
    rows = await _svc().list_resources(tenant_id)
    return [{"id": str(r.id), "name": r.name, "type": r.type, "tenant_id": r.tenant_id} for r in rows]

@app.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(resource_id: UUID):
    try: 
        await _svc().delete_resource(resource_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---------- 关系绑定 ----------
@app.post("/roles/{role_id}/permissions/{permission_id}")
async def assign_permission_to_role(role_id: UUID, permission_id: UUID):
    try:
        await _svc().assign_permission_to_role(role_id, permission_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/roles/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(role_id: UUID, permission_id: UUID):
    try:
        await _svc().remove_permission_from_role(role_id, permission_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/accounts/{account_id}/roles/{role_id}")
async def assign_role_to_account(account_id: UUID, role_id: UUID):
    try:
        await _svc().assign_role_to_account(account_id, role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/accounts/{account_id}/roles/{role_id}")
async def remove_role_from_account(account_id: UUID, role_id: UUID):
    try:
        await _svc().remove_role_from_account(account_id, role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/groups/{group_id}/roles/{role_id}")
async def assign_role_to_group(group_id: UUID, role_id: UUID):
    try:
        await _svc().assign_role_to_group(group_id, role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/groups/{group_id}/roles/{role_id}")
async def remove_role_from_group(group_id: UUID, role_id: UUID):
    try:
        await _svc().remove_role_from_group(group_id, role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/accounts/{account_id}/groups/{group_id}")
async def assign_group_to_account(account_id: UUID, group_id: UUID):
    try:
        await _svc().assign_group_to_account(account_id, group_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/accounts/{account_id}/groups/{group_id}")
async def remove_group_from_account(account_id: UUID, group_id: UUID):
    try:
        await _svc().remove_group_from_account(account_id, group_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/check-access", status_code=status.HTTP_200_OK)
async def check_access(access_check: AccessCheck):
    try:
        has_access = await _svc().check_access(
            access_check.account_id,
            access_check.resource,
            access_check.action,
            access_check.tenant_id,
        )
        # 查询语义：一律 200，带布尔
        return {"has_access": bool(has_access)}
    except NotFoundError as e:
        # 真正的不存在类错误，4xx
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        # 不要把已成型的 HTTP 错误改写成 500
        raise
    except Exception:
        # 隐藏内部异常细节
        raise HTTPException(status_code=500, detail="Internal Server Error")
