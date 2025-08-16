from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from ...service.auth_service import AuthService
from ...db.unit_of_work import UnitOfWork
from ..deps import get_auth_service, get_uow, handle_errors, run_tx
from ..schemas import GroupCreate, GroupResponse

router = APIRouter(prefix="/groups", tags=["groups"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=GroupResponse)
async def create_group(
    body: GroupCreate,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    return await handle_errors(run_tx(uow, lambda: svc.create_group(uow, body.tenant_id, body.name, body.description)))

@router.get("", response_model=List[GroupResponse])
async def list_groups(
    tenant_id: Optional[str] = Query(default=None),
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    return await handle_errors(svc.list_groups(uow, tenant_id=tenant_id))

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    await handle_errors(run_tx(uow, lambda: svc.delete_group(uow, group_id)))
