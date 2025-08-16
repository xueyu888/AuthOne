from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status

from ...service.auth_service import AuthService
from ..deps import get_auth_service
from ..schemas import AccessCheck, AccessCheckResponse

router = APIRouter(tags=["access"])

@router.post("/check-access", status_code=status.HTTP_200_OK, response_model=AccessCheckResponse)
async def check_access(payload: AccessCheck, svc: AuthService = Depends(get_auth_service)):
    try:
        allowed = await svc.check_access(payload.account_id, payload.resource, payload.action, payload.tenant_id)
        return {"allowed": allowed}
    except Exception as e:
        # 最外层兜底，避免把内部异常直接抛给客户端
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
