# backend/api.py
from __future__ import annotations
import os

from fastapi import FastAPI, HTTPException, Path, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

from .service import AuthService
from .core.casbin_adapter import CasbinEngine

from contextlib import asynccontextmanager
from backend.config import Settings
from backend.db import init_engine, init_db, get_session, dispose_engine
import casbin
from casbin.util import key_match, regex_match

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _svc

    defaults = Settings()
    s = Settings(
        db_url=os.getenv("DB_URL", defaults.db_url),
        casbin_model_path=os.getenv("CASBIN_MODEL_PATH", defaults.casbin_model_path),
        casbin_policy_table=defaults.casbin_policy_table,
        log_level=defaults.log_level,
    )

    # 只在这里初始化一次（不要再有 on_event 二次初始化）
    init_engine(s.db_url)
    await init_db(drop_all=False)

    # Casbin：文件版最简单；如果你有 adapter，就换成 adapter
    e = casbin.Enforcer(s.casbin_model_path, "rbac_policy.csv")
    e.add_function("keyMatch", key_match)
    e.add_function("regexMatch", regex_match)

    _svc = await AuthService.create(CasbinEngine(e))

    # 打印确认
    sess = get_session()
    bind = sess.get_bind()
    print(f"[DB] dialect={bind.dialect.name}, url={bind.engine.url}")
    await sess.close()

    try:
        yield
    finally:
        await dispose_engine()
        _svc = None  # 可选，确保优雅关闭

# --------- Settings & CORS 来源（生产不要 *）---------
ALLOWED_ORIGINS = []  # 从环境或配置加载
app = FastAPI(title="AuthOne IAM Service", lifespan=lifespan)

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
    tenant_id: str | None = None
    description: str = Field(default="")

class GroupCreate(BaseModel):
    name: str
    tenant_id: str | None = None
    description: str = Field(default="")

class AccountCreate(BaseModel):
    username: str
    email: EmailStr
    tenant_id: str | None = None

class ResourceCreate(BaseModel):
    resource_type: str = Field(min_length=1)
    name: str = Field(min_length=1)
    tenant_id: str | None = None
    owner_id: str | None = None
    metadata: dict = Field(default_factory=dict)

# --------- 生命周期：引擎与服务 ---------
_svc: AuthService|None = None

# @app.on_event("startup")
# async def startup() -> None:
#     global _svc
#     init_engine(db_url="sqlite+aiosqlite:///./app.db")  # 生产从环境读取
#     await init_db()
#     # 这里示意注入一个已构造好的 enforcer
#     import casbin
#     enforcer = casbin.Enforcer("rbac_model.conf", "rbac_policy.csv" )  # 生产使用 adapter
#     _svc = await AuthService.create(CasbinEngine(enforcer))

# @app.on_event("shutdown")
# async def shutdown() -> None:
#     await dispose_engine()

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

# ----- 访问校验 -----
class AccessCheckBody(BaseModel):
    account_id: str
    tenant_id: str | None = None
    resource: str
    action: str

class AccessCheckResult(BaseModel):
    allowed: bool
    reason: str | None = None

@app.post("/check_access", response_model=AccessCheckResult)
async def check_access(body: AccessCheckBody):
    svc = _svc_required()
    resp = await svc.check_access(
        account_id=body.account_id,
        tenant_id=body.tenant_id,
        resource=body.resource,
        action=body.action,
    )
    # resp 应该是你 service 层的 AccessCheckResponse
    return {"allowed": resp.allowed, "reason": resp.reason}



