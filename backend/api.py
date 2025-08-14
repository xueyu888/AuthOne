from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Optional, List
from uuid import UUID

from casbin.async_enforcer import AsyncEnforcer
from casbin.util import key_match_func, regex_match_func
from casbin_async_sqlalchemy_adapter import Adapter as AsyncAdapter
from fastapi import FastAPI, HTTPException, status, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from .db import init_engine, init_db, dispose_engine, get_sessionmaker, _engine
from .service.auth_service import AuthService, DuplicateError, NotFoundError

DB_URL = os.getenv("DB_URL", "postgresql+asyncpg://postgres:123@127.0.0.1:5432/authone")
MODEL_PATH = os.getenv("CASBIN_MODEL_PATH", "rbac_model.conf")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化数据库引擎和会话工厂
    await init_engine(DB_URL)
    await init_db()
    sm = get_sessionmaker()

    # 创建官方异步 Adapter，它直接使用已创建的 _engine
    adapter = AsyncAdapter(_engine)

    # 创建异步 Enforcer
    enforcer = AsyncEnforcer(MODEL_PATH, adapter)
    enforcer.add_function("keyMatch", key_match_func)
    enforcer.add_function("regexMatch", regex_match_func)
    
    # 异步加载策略
    await enforcer.load_policy()

    # 创建 AuthService 实例
    svc = AuthService(sm, enforcer)
    
    # 将实例存储在 app.state 中
    app.state.enforcer = enforcer
    app.state.svc = svc
    
    try:
        yield
    finally:
        # 清理资源
        await dispose_engine()

app = FastAPI(title="AuthOne IAM Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 在生产环境中应改为你的前端域名
    allow_methods=["GET", "POST", "DELETE", "PUT", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- Pydantic 模型定义保持不变 ---

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

class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: Optional[str]

class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    tenant_id: Optional[str] = None

class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    tenant_id: Optional[str] = None

class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    email: EmailStr
    tenant_id: Optional[str] = None

class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: UUID
    name: str
    resource_type: str = Field(alias="type")
    tenant_id: Optional[str] = None
    owner_id: Optional[UUID] = None

class AccessCheckResponse(BaseModel):
    allowed: bool # 字段名从 has_access 改为 allowed 以匹配前端


# ---------- Dependency ----------
def get_auth_service(request: Request) -> AuthService:
    return request.app.state.svc

# ---------- CRUD ----------

@app.post("/permissions", status_code=status.HTTP_201_CREATED, response_model=PermissionResponse)
async def create_permission(body: PermissionCreate, svc: AuthService = Depends(get_auth_service)):
    try:
        # 假设 svc.create_permission 返回完整的 Permission ORM 对象
        new_permission = await svc.create_permission(body.name, body.description)
        return new_permission
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(svc: AuthService = Depends(get_auth_service)):
    rows = await svc.list_permissions()
    return rows

@app.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(permission_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.delete_permission(permission_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/roles", status_code=status.HTTP_201_CREATED, response_model=RoleResponse)
async def create_role(body: RoleCreate, svc: AuthService = Depends(get_auth_service)):
    try:
        # 假设 svc.create_role 返回完整的 Role ORM 对象
        new_role = await svc.create_role(body.tenant_id, body.name, body.description)
        return new_role
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/roles", response_model=List[RoleResponse])
async def list_roles(tenant_id: Optional[str] = Query(default=None), svc: AuthService = Depends(get_auth_service)):
    rows = await svc.list_roles(tenant_id)
    return rows

@app.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.delete_role(role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/groups", status_code=status.HTTP_201_CREATED, response_model=GroupResponse)
async def create_group(body: GroupCreate, svc: AuthService = Depends(get_auth_service)):
    try:
        # 假设 svc.create_group 返回完整的 Group ORM 对象
        new_group = await svc.create_group(body.tenant_id, body.name, body.description)
        return new_group
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/groups", response_model=List[GroupResponse])
async def list_groups(tenant_id: Optional[str] = Query(default=None), svc: AuthService = Depends(get_auth_service)):
    rows = await svc.list_groups(tenant_id)
    return rows

@app.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.delete_group(group_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/accounts", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def create_account(body: AccountCreate, svc: AuthService = Depends(get_auth_service)):
    try:
        # 假设 svc.create_account 返回完整的 Account ORM 对象
        new_account = await svc.create_account(body.username, str(body.email), body.tenant_id)
        return new_account
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/accounts", response_model=List[AccountResponse])
async def list_accounts(tenant_id: Optional[str] = Query(default=None), svc: AuthService = Depends(get_auth_service)):
    rows = await svc.list_accounts(tenant_id)
    return rows

@app.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.delete_account(account_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    
@app.post("/resources", status_code=status.HTTP_201_CREATED, response_model=ResourceResponse)
async def create_resource(body: ResourceCreate, svc: AuthService = Depends(get_auth_service)):
    try:
        # 假设 svc.create_resource 返回完整的 Resource ORM 对象
        new_resource = await svc.create_resource(body.resource_type, body.name, body.tenant_id, body.owner_id, body.metadata)
        return new_resource
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/resources", response_model=List[ResourceResponse])
async def list_resources(tenant_id: Optional[str] = Query(default=None), svc: AuthService = Depends(get_auth_service)):
    rows = await svc.list_resources(tenant_id)
    return rows

@app.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(resource_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try: 
        await svc.delete_resource(resource_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---------- 关系绑定 (这些接口没有响应体，所以不需要 response_model) ----------
# ... (关系绑定部分保持不变) ...
@app.post("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_permission_to_role(role_id: UUID, permission_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.assign_permission_to_role(role_id, permission_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permission_from_role(role_id: UUID, permission_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.remove_permission_from_role(role_id, permission_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/accounts/{account_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role_to_account(account_id: UUID, role_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.assign_role_to_account(account_id, role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/accounts/{account_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role_from_account(account_id: UUID, role_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.remove_role_from_account(account_id, role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/groups/{group_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role_to_group(group_id: UUID, role_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.assign_role_to_group(group_id, role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/groups/{group_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role_from_group(group_id: UUID, role_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.remove_role_from_group(group_id, role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/accounts/{account_id}/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_group_to_account(account_id: UUID, group_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.assign_group_to_account(account_id, group_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/accounts/{account_id}/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_group_from_account(account_id: UUID, group_id: UUID, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.remove_group_from_account(account_id, group_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
        
@app.post("/check-access", status_code=status.HTTP_200_OK, response_model=AccessCheckResponse)
async def check_access(access_check: AccessCheck, svc: AuthService = Depends(get_auth_service)):
    try:
        has_access = await svc.check_access(
            access_check.account_id,
            access_check.resource,
            access_check.action,
            access_check.tenant_id,
        )
        return {"has_access": bool(has_access)}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")