from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from ...service.auth_service import AuthService
from ...db.unit_of_work import UnitOfWork
from ..deps import get_auth_service, get_uow, handle_errors, run_tx
from ..schemas import ResourceCreate, ResourceResponse

router = APIRouter(prefix="/resources", tags=["resources"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=ResourceResponse)
async def create_resource(
    body: ResourceCreate,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    return await handle_errors(run_tx(uow, lambda: svc.create_resource(
        uow, body.resource_type, body.name, body.tenant_id, body.owner_id, body.metadata
    )))

@router.get("", response_model=List[ResourceResponse])
async def list_resources(
    tenant_id: Optional[str] = Query(default=None),
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    return await handle_errors(svc.list_resources(uow, tenant_id=tenant_id))

@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    await handle_errors(run_tx(uow, lambda: svc.delete_resource(uow, resource_id)))
