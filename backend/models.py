"""Pydantic models used by the AuthOne API.

The service functions operate on SQLAlchemy ORM instances; however the
API layer uses Pydantic models to validate incoming requests and
structure outgoing responses.  These models are deliberately thin
wrappers around primitive types and do not contain any business logic.

``AccessCheckRequest`` encapsulates the parameters required to check
whether an account has permission to perform an action on a resource.
``AccessCheckResponse`` conveys the result of an access check.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

__all__ = ["AccessCheckRequest", "AccessCheckResponse"]


class AccessCheckRequest(BaseModel):
    """Request body for the access check endpoint.

    :param account_id: Identifier of the account performing the action.
    :param tenant_id: Optional tenant/domain associated with the request.
    :param resource: Resource identifier (path or name) being accessed.
    :param action: Action name (create/read/update/delete etc.).
    """

    account_id: str = Field(..., description="User account ID")
    tenant_id: Optional[str] = Field(
        None, description="Tenant/domain ID (optional)"
    )
    resource: str = Field(..., description="Name or path of the resource")
    action: str = Field(..., description="Action to perform on the resource")


class AccessCheckResponse(BaseModel):
    """Response returned by the access check endpoint.

    :param allowed: Whether the requested action is permitted.
    :param reason: Optional reason for denial (``None`` if allowed).
    """

    allowed: bool = Field(..., description="True if access is permitted")
    reason: Optional[str] = Field(
        None, description="Reason for denial if access is not permitted"
    )