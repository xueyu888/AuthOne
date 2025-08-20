# backend/api/routers/permissions.py

from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from ...service import AuthService
from ...db import UnitOfWork
from ..deps import RequestHandler
from ..schemas import PermissionCreate, PermissionResponse

__all__ = ["router"]

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=PermissionResponse)
async def create_permission(
    body: PermissionCreate,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """创建一个新权限。"""
    return await RequestHandler.run_in_transaction(
        uow, 
        lambda: svc.create_permission(uow, body.name, body.description)
    )

@router.get("", response_model=List[PermissionResponse])
async def list_permissions(
    name: Optional[str] = Query(default=None),
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """根据名称查询权限列表。"""
    return await RequestHandler.run_read_operation(
        lambda: svc.list_permissions(uow, name=name)
    )

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """删除一个权限。"""
    await RequestHandler.run_in_transaction(
        uow, 
        lambda: svc.delete_permission(uow, permission_id)
    )