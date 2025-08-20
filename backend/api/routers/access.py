# backend/api/routers/access.py

from __future__ import annotations
from fastapi import APIRouter, Depends, status
from ...service import AuthService
from ..deps import RequestHandler
from ..schemas import AccessCheck, AccessCheckResponse

__all__ = ["router"]

router = APIRouter(tags=["access"])

@router.post("/check-access", status_code=status.HTTP_200_OK, response_model=AccessCheckResponse)
async def check_access(
    payload: AccessCheck, 
    svc: AuthService = Depends(RequestHandler.get_auth_service)
):
    """
    检查账户是否有权执行操作。这是一个只读操作。
    """
    allowed = await RequestHandler.run_read_operation(
        lambda: svc.check_access(
            payload.account_id, payload.resource, payload.action, payload.tenant_id
        )
    )
    return {"allowed": allowed}