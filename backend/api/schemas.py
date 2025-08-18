from __future__ import annotations
from typing import Optional, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# ---- Requests ----
class PermissionCreate(BaseModel):
    name: str = Field(min_length=3)
    description: str = ""

class RoleCreate(BaseModel):
    name: str = Field(min_length=1)
    tenant_id: Optional[str] = None
    description: str = ""

class GroupCreate(BaseModel):
    name: str
    tenant_id: Optional[str] = None
    description: str = ""

class AccountCreate(BaseModel):
    username: str
    email: EmailStr
    tenant_id: Optional[str] = None

class ResourceCreate(BaseModel):
    resource_type: str = Field(min_length=1)
    name: str = Field(min_length=1)
    tenant_id: Optional[str] = None
    owner_id: Optional[UUID] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class AccessCheck(BaseModel):
    account_id: UUID
    resource: str
    action: str
    tenant_id: Optional[str] = None

# ---- Responses ----
class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: Optional[str]

class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    tenant_id: Optional[str] = None

class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    tenant_id: Optional[str] = None

class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    email: EmailStr
    tenant_id: Optional[str] = None

class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: UUID
    name: str
    resource_type: str = Field(alias="type")
    tenant_id: Optional[str] = None
    owner_id: Optional[UUID] = None

class AccessCheckResponse(BaseModel):
    allowed: bool
