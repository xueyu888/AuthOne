from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from ...service.auth_service import AuthService
from ...db.unit_of_work import UnitOfWork
from ..deps import get_auth_service, get_uow, handle_errors, run_tx
from ..schemas import PermissionCreate, PermissionResponse

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=PermissionResponse)
async def create_permission(
    body: PermissionCreate,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    return await handle_errors(run_tx(uow, lambda: svc.create_permission(uow, body.name, body.description)))

@router.get("", response_model=List[PermissionResponse])
async def list_permissions(
    name: Optional[str] = Query(default=None),
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    return await handle_errors(svc.list_permissions(uow, name=name))

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    await handle_errors(run_tx(uow, lambda: svc.delete_permission(uow, permission_id)))
