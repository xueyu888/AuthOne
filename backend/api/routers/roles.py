from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from ...service.auth_service import AuthService
from ...db.unit_of_work import UnitOfWork
from ..deps import get_auth_service, get_uow, handle_errors, run_tx
from ..schemas import RoleCreate, RoleResponse

router = APIRouter(prefix="/roles", tags=["roles"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=RoleResponse)
async def create_role(
    body: RoleCreate,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    return await handle_errors(run_tx(uow, lambda: svc.create_role(uow, body.tenant_id, body.name, body.description)))

@router.get("", response_model=List[RoleResponse])
async def list_roles(
    tenant_id: Optional[str] = Query(default=None),
    name: Optional[str] = Query(default=None),
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    return await handle_errors(svc.list_roles(uow, tenant_id=tenant_id, name=name))

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    await handle_errors(run_tx(uow, lambda: svc.delete_role(uow, role_id)))
