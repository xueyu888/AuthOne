# backend/api/routers/relations.py

from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, status

from ...service import AuthService
from ...db import UnitOfWork
from ..deps import RequestHandler

__all__ = ["router"]

router = APIRouter(tags=["relations"])

# --- Role <-> Permission ---
@router.post("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_permission_to_role(
    role_id: UUID, 
    permission_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow)
):
    await RequestHandler.run_in_transaction(
        uow, lambda: svc.assign_permission_to_role(uow, role_id, permission_id)
    )

@router.delete("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permission_from_role(
    role_id: UUID, 
    permission_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow)
):
    await RequestHandler.run_in_transaction(
        uow, lambda: svc.remove_permission_from_role(uow, role_id, permission_id)
    )

# --- Account <-> Role ---
@router.post("/accounts/{account_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role_to_account(
    account_id: UUID, 
    role_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow)
):
    await RequestHandler.run_in_transaction(
        uow, lambda: svc.assign_role_to_account(uow, account_id, role_id)
    )

@router.delete("/accounts/{account_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role_from_account(
    account_id: UUID, 
    role_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow)
):
    await RequestHandler.run_in_transaction(
        uow, lambda: svc.remove_role_from_account(uow, account_id, role_id)
    )

# --- Group <-> Role ---
@router.post("/groups/{group_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role_to_group(
    group_id: UUID, 
    role_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow)
):
    await RequestHandler.run_in_transaction(
        uow, lambda: svc.assign_role_to_group(uow, group_id, role_id)
    )

@router.delete("/groups/{group_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role_from_group(
    group_id: UUID, 
    role_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow)
):
    await RequestHandler.run_in_transaction(
        uow, lambda: svc.remove_role_from_group(uow, group_id, role_id)
    )

# --- Account <-> Group ---
@router.post("/accounts/{account_id}/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_group_to_account(
    account_id: UUID, 
    group_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow)
):
    await RequestHandler.run_in_transaction(
        uow, lambda: svc.assign_group_to_account(uow, account_id, group_id)
    )

@router.delete("/accounts/{account_id}/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_group_from_account(
    account_id: UUID, 
    group_id: UUID,
    svc: AuthService = Depends(RequestHandler.get_auth_service),
    uow: UnitOfWork = Depends(RequestHandler.get_uow)
):
    await RequestHandler.run_in_transaction(
        uow, lambda: svc.remove_group_from_account(uow, account_id, group_id)
    )