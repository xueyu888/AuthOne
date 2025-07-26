"""Pydantic 模型定义。

用于对外接口的请求和响应模型，确保输入参数的有效性和输出格式的一致性。
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, validator

__all__ = ["AccessCheckRequest", "AccessCheckResponse"]


class AccessCheckRequest(BaseModel):
    """权限校验请求模型。"""

    account_id: str = Field(..., description="账户 ID")
    resource: str = Field(..., description="资源名称（组件、模块、数据集等）")
    action: str = Field(..., description="操作名称，如 create/read/delete")
    tenant_id: Optional[str] = Field(None, description="租户 ID，可为空")

    @validator("account_id", "resource", "action")
    def _not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("must not be empty")
        return v


class AccessCheckResponse(BaseModel):
    """权限校验响应模型。"""

    allowed: bool = Field(..., description="是否允许访问")
    reason: Optional[str] = Field(None, description="拒绝原因")
