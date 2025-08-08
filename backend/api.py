"""HTTP API for AuthOne.

This module exposes a FastAPI application that provides REST
endpoints for creating, deleting and relating permissions, roles,
groups, accounts and resources, as well as checking access via
Casbin.  It uses Pydantic models to validate incoming request bodies
and returns simple JSON responses.  Business logic is delegated to
the ``AuthService``.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

from .config import Settings
from .db import init_engine, init_db, dispose_engine, get_session
from .models import AccessCheckRequest, AccessCheckResponse
from .service import AuthService
from .core.casbin_adapter import CasbinEngine

import casbin
from casbin.util import key_match, regex_match

__all__ = ["app"]


# ---------------------------------------------------------------------------
# Request body models for create endpoints

class PermissionCreate(BaseModel):
    name: str = Field(..., min_length=3)
    description: str | None = Field(default=None)


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1)
    tenant_id: str | None = None
    description: str | None = Field(default=None)


class GroupCreate(BaseModel):
    name: str
    tenant_id: str | None = None
    description: str | None = Field(default=None)


class AccountCreate(BaseModel):
    username: str
    email: EmailStr
    tenant_id: str | None = None


class ResourceCreate(BaseModel):
    resource_type: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    tenant_id: str | None = None
    owner_id: str | None = None
    metadata: dict[str, str] | None = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# FastAPI application and lifespan

app = FastAPI(title="AuthOne IAM Service")

# CORS configuration (allow all origins in development; restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Hold the service instance globally; created in lifespan
_service: AuthService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialise database and service on startup, cleanup on shutdown."""
    global _service
    # Build settings from environment variables
    defaults = Settings()
    settings = defaults.override(
        db_url=os.getenv("DB_URL", defaults.db_url),
        casbin_model_path=os.getenv("CASBIN_MODEL_PATH", defaults.casbin_model_path),
        casbin_policy_table=defaults.casbin_policy_table,
        log_level=os.getenv("LOG_LEVEL", defaults.log_level),
    )
    # Initialise engine and database
    init_engine(settings.db_url)
    await init_db(drop_all=False)
    # Setup Casbin enforcer
    enforcer = casbin.Enforcer(settings.casbin_model_path, "rbac_policy.csv")
    enforcer.add_function("keyMatch", key_match)
    enforcer.add_function("regexMatch", regex_match)
    casbin_engine = CasbinEngine(enforcer)
    # Create service
    _service = await AuthService.create(casbin_engine)
    try:
        yield
    finally:
        await dispose_engine()
        _service = None


app.router.lifespan_context = lifespan  # type: ignore[assignment]


def get_service() -> AuthService:
    if _service is None:
        raise RuntimeError("Service not initialised")
        
    return _service


@app.get("/", include_in_schema=False)
async def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs")


# ---------------------------------------------------------------------------
# CRUD endpoints for permissions, roles, groups, accounts, resources

@app.post("/permissions", status_code=status.HTTP_201_CREATED)
async def create_permission(body: PermissionCreate):
    svc = get_service()
    try:
        perm = await svc.create_permission(name=body.name, description=body.description or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"id": str(perm.id), "name": perm.name, "description": perm.description}


@app.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(permission_id: str):
    svc = get_service()
    if not await svc.delete_permission(permission_id):
        raise HTTPException(status_code=404, detail="permission not found")


@app.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_role(body: RoleCreate):
    svc = get_service()
    try:
        role = await svc.create_role(
            tenant_id=body.tenant_id, name=body.name, description=body.description or ""
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"id": str(role.id), "name": role.name, "tenant_id": role.tenant_id}


@app.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: str):
    svc = get_service()
    if not await svc.delete_role(role_id):
        raise HTTPException(status_code=404, detail="role not found")


@app.post("/groups", status_code=status.HTTP_201_CREATED)
async def create_group(body: GroupCreate):
    svc = get_service()
    try:
        group = await svc.create_group(
            tenant_id=body.tenant_id, name=body.name, description=body.description or ""
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"id": str(group.id), "name": group.name, "tenant_id": group.tenant_id}


@app.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: str):
    svc = get_service()
    if not await svc.delete_group(group_id):
        raise HTTPException(status_code=404, detail="group not found")


@app.post("/accounts", status_code=status.HTTP_201_CREATED)
async def create_account(body: AccountCreate):
    svc = get_service()
    try:
        account = await svc.create_account(
            username=body.username,
            email=str(body.email),
            tenant_id=body.tenant_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"id": str(account.id), "username": account.username, "tenant_id": account.tenant_id}


@app.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: str):
    svc = get_service()
    if not await svc.delete_account(account_id):
        raise HTTPException(status_code=404, detail="account not found")


@app.post("/resources", status_code=status.HTTP_201_CREATED)
async def create_resource(body: ResourceCreate):
    svc = get_service()
    try:
        res = await svc.create_resource(
            resource_type=body.resource_type,
            name=body.name,
            tenant_id=body.tenant_id,
            owner_id=body.owner_id,
            metadata=body.metadata,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {
        "id": str(res.id),
        "name": res.name,
        "type": res.type,
        "tenant_id": res.tenant_id,
    }


@app.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(resource_id: str):
    svc = get_service()
    if not await svc.delete_resource(resource_id):
        raise HTTPException(status_code=404, detail="resource not found")


# ---------------------------------------------------------------------------
# Relationship endpoints

@app.post("/roles/{role_id}/permissions/{permission_id}")
async def assign_permission_to_role(role_id: str, permission_id: str):
    svc = get_service()
    try:
        await svc.assign_permission_to_role(role_id, permission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "ok"}


@app.delete("/roles/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(role_id: str, permission_id: str):
    svc = get_service()
    try:
        await svc.remove_permission_from_role(role_id, permission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "ok"}


@app.post("/accounts/{account_id}/roles/{role_id}")
async def assign_role_to_account(account_id: str, role_id: str):
    svc = get_service()
    try:
        await svc.assign_role_to_account(account_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "ok"}


@app.delete("/accounts/{account_id}/roles/{role_id}")
async def remove_role_from_account(account_id: str, role_id: str):
    svc = get_service()
    try:
        await svc.remove_role_from_account(account_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "ok"}


@app.post("/groups/{group_id}/roles/{role_id}")
async def assign_role_to_group(group_id: str, role_id: str):
    svc = get_service()
    try:
        await svc.assign_role_to_group(group_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "ok"}


@app.delete("/groups/{group_id}/roles/{role_id}")
async def remove_role_from_group(group_id: str, role_id: str):
    svc = get_service()
    try:
        await svc.remove_role_from_group(group_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "ok"}


@app.post("/accounts/{account_id}/groups/{group_id}")
async def assign_group_to_account(account_id: str, group_id: str):
    svc = get_service()
    try:
        await svc.assign_group_to_account(account_id, group_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "ok"}


@app.delete("/accounts/{account_id}/groups/{group_id}")
async def remove_group_from_account(account_id: str, group_id: str):
    svc = get_service()
    try:
        await svc.remove_group_from_account(account_id, group_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Access control endpoint

@app.post("/check_access", response_model=AccessCheckResponse)
async def check_access(req: AccessCheckRequest) -> AccessCheckResponse:
    svc = get_service()
    return await svc.check_access(req)