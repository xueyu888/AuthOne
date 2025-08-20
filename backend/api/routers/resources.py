# backend/api/routers/resources.py

from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from ...service import AuthService
from ...db import UnitOfWork
from ..deps import RequestHandler
from ..schemas import ResourceCreate, ResourceResponse

__all__ = ["router"]

router = APIRouter(prefix="/resources", tags=["resources"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=ResourceResponse)
async def create_resource(
    body: ResourceCreate,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """创建一个新资源。"""
    return await RequestHandler.run_in_transaction(
        uow, 
        lambda: svc.create_resource(
            uow, body.resource_type, body.name, body.tenant_id, body.owner_id, body.metadata
        )
    )

@router.get("", response_model=List[ResourceResponse])
async def list_resources(
    tenant_id: Optional[str] = Query(default=None),
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """根据租户ID查询资源列表。"""
    return await RequestHandler.run_read_operation(
        lambda: svc.list_resources(uow, tenant_id=tenant_id)
    )

@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """删除一个资源。"""
    await RequestHandler.run_in_transaction(
        uow, 
        lambda: svc.delete_resource(uow, resource_id)
    )





