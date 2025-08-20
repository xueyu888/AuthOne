# backend/api/routers/roles.py

from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from ...service import AuthService
from ...db import UnitOfWork
from ..deps import RequestHandler
from ..schemas import RoleCreate, RoleResponse

__all__ = ["router"]

router = APIRouter(prefix="/roles", tags=["roles"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=RoleResponse)
async def create_role(
    body: RoleCreate,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """创建一个新角色。"""
    return await RequestHandler.run_in_transaction(
        uow, 
        lambda: svc.create_role(uow, body.tenant_id, body.name, body.description)
    )

@router.get("", response_model=List[RoleResponse])
async def list_roles(
    tenant_id: Optional[str] = Query(default=None),
    name: Optional[str] = Query(default=None),
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """根据条件查询角色列表。"""
    return await RequestHandler.run_read_operation(
        lambda: svc.list_roles(uow, tenant_id=tenant_id, name=name)
    )

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """删除一个角色。"""
    await RequestHandler.run_in_transaction(
        uow, 
        lambda: svc.delete_role(uow, role_id)
    )