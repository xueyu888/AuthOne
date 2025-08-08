"""Repository interface definitions.

This module defines abstract base classes describing the operations
required by the AuthOne service layer.  Concrete implementations
using SQLAlchemy can be found in ``sqlalchemy_repository.py``.  By
targeting these interfaces, the service layer remains decoupled from
the underlying persistence mechanism and can be more easily tested.

Each repository raises ``ValueError`` for business-rule violations
such as attempting to create a duplicate entity.  Missing entities
return ``None`` where appropriate rather than raising exceptions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List

from ..db import (
    PermissionModel,
    RoleModel,
    GroupModel,
    AccountModel,
    ResourceModel,
)

__all__ = [
    "PermissionRepository",
    "RoleRepository",
    "GroupRepository",
    "AccountRepository",
    "ResourceRepository",
]


class PermissionRepository(ABC):
    """Repository interface for permissions."""

    @abstractmethod
    async def add(self, name: str, description: str | None = None) -> PermissionModel:
        """Create a new permission.

        :raises ValueError: if a permission with the same name already exists.
        :returns: The created ``PermissionModel`` instance.
        """
        raise NotImplementedError

    @abstractmethod
    async def get(self, permission_id: str) -> Optional[PermissionModel]:
        """Retrieve a permission by its ID.

        :returns: The corresponding permission instance, or ``None`` if not found.
        """
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> List[PermissionModel]:
        """Return a list of all permissions."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, permission_id: str) -> bool:
        """Delete a permission by its ID.

        :returns: ``True`` if a row was deleted, ``False`` otherwise.
        """
        raise NotImplementedError


class RoleRepository(ABC):
    """Repository interface for roles."""

    @abstractmethod
    async def add(self, tenant_id: str | None, name: str, description: str | None = None) -> RoleModel:
        """Create a new role for a tenant.

        :raises ValueError: if a duplicate role name exists within the same tenant.
        :returns: The created ``RoleModel`` instance.
        """
        raise NotImplementedError

    @abstractmethod
    async def get(self, role_id: str) -> Optional[RoleModel]:
        """Retrieve a role by ID."""
        raise NotImplementedError

    @abstractmethod
    async def list(self, tenant_id: str | None = None) -> List[RoleModel]:
        """List all roles, optionally filtered by tenant."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, role_id: str) -> bool:
        """Delete a role by ID."""
        raise NotImplementedError

    @abstractmethod
    async def assign_permission(self, role_id: str, permission_id: str) -> None:
        """Associate a permission with a role.

        The operation is idempotent: adding the same permission twice
        has no effect and does not raise an error.
        """
        raise NotImplementedError

    @abstractmethod
    async def remove_permission(self, role_id: str, permission_id: str) -> None:
        """Remove a permission from a role.

        The operation is idempotent: removing a non-existent association
        has no effect and does not raise an error.
        """
        raise NotImplementedError


class GroupRepository(ABC):
    """Repository interface for groups."""

    @abstractmethod
    async def add(self, tenant_id: str | None, name: str, description: str | None = None) -> GroupModel:
        """Create a new group."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, group_id: str) -> Optional[GroupModel]:
        """Retrieve a group by ID."""
        raise NotImplementedError

    @abstractmethod
    async def list(self, tenant_id: str | None = None) -> List[GroupModel]:
        """List all groups, optionally filtered by tenant."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, group_id: str) -> bool:
        """Delete a group by ID."""
        raise NotImplementedError

    @abstractmethod
    async def assign_role(self, group_id: str, role_id: str) -> None:
        """Associate a role with a group (idempotent)."""
        raise NotImplementedError

    @abstractmethod
    async def remove_role(self, group_id: str, role_id: str) -> None:
        """Remove a role from a group (idempotent)."""
        raise NotImplementedError


class AccountRepository(ABC):
    """Repository interface for accounts."""

    @abstractmethod
    async def add(self, username: str, email: str, tenant_id: str | None) -> AccountModel:
        """Create a new account.

        :raises ValueError: if the username or email already exists within the same tenant.
        """
        raise NotImplementedError

    @abstractmethod
    async def get(self, account_id: str) -> Optional[AccountModel]:
        """Retrieve an account by ID."""
        raise NotImplementedError

    @abstractmethod
    async def list(self, tenant_id: str | None = None) -> List[AccountModel]:
        """List all accounts, optionally filtered by tenant."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, account_id: str) -> bool:
        """Delete an account."""
        raise NotImplementedError

    @abstractmethod
    async def assign_role(self, account_id: str, role_id: str) -> None:
        """Associate a role with an account (idempotent)."""
        raise NotImplementedError

    @abstractmethod
    async def remove_role(self, account_id: str, role_id: str) -> None:
        """Remove a role from an account (idempotent)."""
        raise NotImplementedError

    @abstractmethod
    async def assign_group(self, account_id: str, group_id: str) -> None:
        """Associate a group with an account (idempotent)."""
        raise NotImplementedError

    @abstractmethod
    async def remove_group(self, account_id: str, group_id: str) -> None:
        """Remove a group from an account (idempotent)."""
        raise NotImplementedError


class ResourceRepository(ABC):
    """Repository interface for resources."""

    @abstractmethod
    async def add(
        self,
        resource_type: str,
        name: str,
        tenant_id: str | None,
        owner_id: str | None,
        metadata: dict[str, str] | None = None,
    ) -> ResourceModel:
        """Create a new resource.

        :raises ValueError: if a duplicate resource exists (same name and tenant).
        :returns: The created ``ResourceModel``.
        """
        raise NotImplementedError

    @abstractmethod
    async def get(self, resource_id: str) -> Optional[ResourceModel]:
        """Retrieve a resource by ID."""
        raise NotImplementedError

    @abstractmethod
    async def list(self, tenant_id: str | None = None) -> List[ResourceModel]:
        """List all resources, optionally filtered by tenant."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, resource_id: str) -> bool:
        """Delete a resource."""
        raise NotImplementedError