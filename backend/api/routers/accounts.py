from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from ...service.auth_service import AuthService
from ...db.unit_of_work import UnitOfWork
from ..deps import get_auth_service, get_uow, handle_errors, run_tx
from ..schemas import AccountCreate, AccountResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def create_account(
    body: AccountCreate,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    return await handle_errors(run_tx(uow, lambda: svc.create_account(uow, body.username, body.email, body.tenant_id)))

@router.get("", response_model=List[AccountResponse])
async def list_accounts(
    tenant_id: Optional[str] = Query(default=None),
    username: Optional[str] = Query(default=None),
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    return await handle_errors(svc.list_accounts(uow, tenant_id=tenant_id, username=username))

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    svc: AuthService = Depends(get_auth_service),
    uow: UnitOfWork = Depends(get_uow),
):
    await handle_errors(run_tx(uow, lambda: svc.delete_account(uow, account_id)))
