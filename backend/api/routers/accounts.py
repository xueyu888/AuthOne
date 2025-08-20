# backend/api/routers/accounts.py

from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from ...service import AuthService
from ...db import UnitOfWork
from ..deps import RequestHandler
from ..schemas import AccountCreate, AccountResponse

__all__ = ["router"]

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def create_account(
    body: AccountCreate,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """创建一个新账户。"""
    return await RequestHandler.run_in_transaction(
        uow, 
        lambda: svc.create_account(uow, body.username, body.email, body.tenant_id)
    )

@router.get("", response_model=List[AccountResponse])
async def list_accounts(
    tenant_id: Optional[str] = Query(default=None),
    username: Optional[str] = Query(default=None),
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """根据条件查询账户列表。"""
    return await RequestHandler.run_read_operation(
        lambda: svc.list_accounts(uow, tenant_id=tenant_id, username=username)
    )

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow),
):
    """删除一个账户。"""
    await RequestHandler.run_in_transaction(
        uow, 
        lambda: svc.delete_account(uow, account_id)
    )