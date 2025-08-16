# backend/api.py

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Optional, List, AsyncGenerator
from uuid import UUID

from casbin.async_enforcer import AsyncEnforcer
from casbin.util import key_match_func, regex_match_func
from casbin_async_sqlalchemy_adapter import Adapter as AsyncCasbinAdapter
from fastapi import FastAPI, HTTPException, status, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from .db.db_models import init_engine, init_db, dispose_engine, get_sessionmaker
from .db.unit_of_work import UnitOfWork
from .service.auth_service import AuthService, DuplicateError, NotFoundError, ConcurrencyError


DB_URL = os.getenv("DB_URL", "postgresql+asyncpg://postgres:123@127.0.0.1:5432/authone")
MODEL_PATH = os.getenv("CASBIN_MODEL_PATH", "rbac_model.conf")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化数据库
    await init_engine(DB_URL)
    # 测试/本地环境干净重建；生产请改为 False 并用迁移
    await init_db(False)

    # 初始化 Casbin（异步 PG 适配器）
    adapter = AsyncCasbinAdapter(DB_URL)
    await adapter.create_table()

    enforcer = AsyncEnforcer(MODEL_PATH, adapter)
    enforcer.add_function("keyMatch", key_match_func)
    enforcer.add_function("regexMatch", regex_match_func)
    await enforcer.load_policy()
    enforcer.enable_auto_save(True)

    # Service
    svc = AuthService(enforcer)
    app.state.svc = svc
    app.state.enforcer = enforcer

    try:
        yield
    finally:
        await dispose_engine()

app = FastAPI(title="AuthOne IAM Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "PUT", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---------------------- Pydantic Schemas ----------------------

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
    # alias: "type" -> resource_type
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: UUID
    name: str
    resource_type: str = Field(alias="type")
    tenant_id: Optional[str] = None
    owner_id: Optional[UUID] = None


class AccessCheckResponse(BaseModel):
    allowed: bool


# ---------------------- Dependencies ----------------------

def get_auth_service(request: Request) -> AuthService:
    return request.app.state.svc


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    uow = UnitOfWork(get_sessionmaker())
    async with uow:
        yield uow


# ---------------------- Error Wrapper ----------------------

async def handle_service_errors(service_call):
    try:
        result = await service_call
        return result
    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConcurrencyError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database integrity error: {e.orig}")


# ====================== CRUD: Permissions ======================

@app.post("/permissions", status_code=status.HTTP_201_CREATED, response_model=PermissionResponse)
async def create_permission(
    body: PermissionCreate,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            new_perm = await svc.create_permission(uow, body.name, body.description)
            await uow.commit()
            return new_perm
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    return await handle_service_errors(task())


@app.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    name: Optional[str] = Query(default=None),
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    rows = await svc.list_permissions(uow, name=name)
    return rows


@app.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.delete_permission(uow, permission_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


# ====================== CRUD: Roles ======================

@app.post("/roles", status_code=status.HTTP_201_CREATED, response_model=RoleResponse)
async def create_role(
    body: RoleCreate,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            new_role = await svc.create_role(uow, body.tenant_id, body.name, body.description)
            await uow.commit()
            return new_role
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    return await handle_service_errors(task())


@app.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    tenant_id: Optional[str] = Query(default=None),
    name: Optional[str] = Query(default=None),
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    rows = await svc.list_roles(uow, tenant_id=tenant_id, name=name)
    return rows


@app.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.delete_role(uow, role_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


# ====================== CRUD: Groups ======================

@app.post("/groups", status_code=status.HTTP_201_CREATED, response_model=GroupResponse)
async def create_group(
    body: GroupCreate,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            grp = await svc.create_group(uow, body.tenant_id, body.name, body.description)
            await uow.commit()
            return grp
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    return await handle_service_errors(task())


@app.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.delete_group(uow, group_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


# ====================== CRUD: Accounts ======================

@app.post("/accounts", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def create_account(
    body: AccountCreate,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            acc = await svc.create_account(uow, body.username, body.email, body.tenant_id)
            await uow.commit()
            return acc
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    return await handle_service_errors(task())


@app.get("/accounts", response_model=List[AccountResponse])
async def list_accounts(
    tenant_id: Optional[str] = Query(default=None),
    username: Optional[str] = Query(default=None),
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    rows = await svc.list_accounts(uow, tenant_id=tenant_id, username=username)
    return rows


@app.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.delete_account(uow, account_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


# ====================== CRUD: Resources ======================

@app.post("/resources", status_code=status.HTTP_201_CREATED, response_model=ResourceResponse)
async def create_resource(
    body: ResourceCreate,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            res = await svc.create_resource(
                uow, body.resource_type, body.name, body.tenant_id, body.owner_id, body.metadata
            )
            await uow.commit()
            return res
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    return await handle_service_errors(task())


@app.get("/resources", response_model=List[ResourceResponse])
async def list_resources(
    tenant_id: Optional[str] = Query(default=None),
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    rows = await svc.list_resources(uow, tenant_id=tenant_id)
    return rows


@app.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.delete_resource(uow, resource_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


# ====================== Relationships ======================

# 角色 ↔ 权限
@app.post("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_permission_to_role(
    role_id: UUID,
    permission_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.assign_permission_to_role(uow, role_id, permission_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


@app.delete("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permission_from_role(
    role_id: UUID,
    permission_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.remove_permission_from_role(uow, role_id, permission_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


# 账号 ↔ 角色
@app.post("/accounts/{account_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role_to_account(
    account_id: UUID,
    role_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.assign_role_to_account(uow, account_id, role_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


@app.delete("/accounts/{account_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role_from_account(
    account_id: UUID,
    role_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.remove_role_from_account(uow, account_id, role_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


# 组 ↔ 角色
@app.post("/groups/{group_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role_to_group(
    group_id: UUID,
    role_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.assign_role_to_group(uow, group_id, role_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


@app.delete("/groups/{group_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role_from_group(
    group_id: UUID,
    role_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.remove_role_from_group(uow, group_id, role_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


# 账号 ↔ 组
@app.post("/accounts/{account_id}/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_group_to_account(
    account_id: UUID,
    group_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.assign_group_to_account(uow, account_id, group_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


@app.delete("/accounts/{account_id}/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_group_from_account(
    account_id: UUID,
    group_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    async def task():
        try:
            await svc.remove_group_from_account(uow, account_id, group_id)
            await uow.commit()
        except StaleDataError:
            await uow.rollback()
            raise ConcurrencyError("This resource was updated by another process. Please try again.")
    await handle_service_errors(task())


# ====================== Access Check ======================

@app.post("/check-access", status_code=status.HTTP_200_OK, response_model=AccessCheckResponse)
async def check_access(access_check: AccessCheck, svc: AuthService = Depends(get_auth_service)):
    try:
        has_access = await svc.check_access(
            access_check.account_id,
            access_check.resource,
            access_check.action,
            access_check.tenant_id,
        )
        return {"allowed": has_access}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
