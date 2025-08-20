# backend/api/routers/groups.py

from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from ...service import AuthService
from ...db import UnitOfWork
from ..deps import RequestHandler
from ..schemas import GroupCreate, GroupResponse

__all__ = ["router"]

router = APIRouter(prefix="/groups", tags=["groups"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=GroupResponse)
async def create_group(
    body: GroupCreate,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """创建一个新用户组。"""
    return await RequestHandler.run_in_transaction(
        uow, 
        lambda: svc.create_group(uow, body.tenant_id, body.name, body.description)
    )

@router.get("", response_model=List[GroupResponse])
async def list_groups(
    tenant_id: Optional[str] = Query(default=None),
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """根据租户ID查询用户组列表。"""
    return await RequestHandler.run_read_operation(
        lambda: svc.list_groups(uow, tenant_id=tenant_id)
    )

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """删除一个用户组。"""
    await RequestHandler.run_in_transaction(
        uow, 
        lambda: svc.delete_group(uow, group_id)
    )