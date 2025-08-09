from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

__all__ = ["AccessCheckRequest", "AccessCheckResponse"]

class AccessCheckRequest(BaseModel):
    account_id: str = Field(..., description="User account UUID")
    tenant_id: Optional[str] = Field(None, description="Tenant/domain ID")
    resource: str = Field(..., description="Resource name or path")
    action: str = Field(..., description="Action (create/read/update/delete)")

class AccessCheckResponse(BaseModel):
    allowed: bool = Field(..., description="Allowed or not")
    reason: Optional[str] = Field(None, description="Why denied")