"""SQLAlchemy repository implementations.

This module provides concrete implementations of the repository
interfaces defined in ``backend.storage.interface``.  Each class
operates on the SQLAlchemy models defined in ``backend.db`` using an
``AsyncSession``.  Operations that violate uniqueness constraints
(such as creating an entity that already exists) raise ``ValueError``
with a descriptive message.  Assignment and removal methods are
idempotent; adding an existing association or removing a non-existent
one has no effect and does not raise an exception.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional, List

from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import (
    PermissionModel,
    RoleModel,
    GroupModel,
    AccountModel,
    ResourceModel,
    role_permissions,
    group_roles,
    user_roles,
    user_groups,
    AuditLogModel,
)
from .interface import (
    PermissionRepository,
    RoleRepository,
    GroupRepository,
    AccountRepository,
    ResourceRepository,
)

__all__ = [
    "SQLAlchemyPermissionRepository",
    "SQLAlchemyRoleRepository",
    "SQLAlchemyGroupRepository",
    "SQLAlchemyAccountRepository",
    "SQLAlchemyResourceRepository",
    "AuditLogRepository",
]


class SQLAlchemyPermissionRepository(PermissionRepository):
    """SQLAlchemy implementation of ``PermissionRepository``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, name: str, description: str | None = None) -> PermissionModel:
        # Check for existing permission by unique name
        existing = await self._session.scalar(
            select(PermissionModel.id).where(PermissionModel.name == name)
        )
        if existing:
            raise ValueError(f"permission '{name}' already exists")

        # Create and persist
        perm = PermissionModel(name=name, description=description)
        async with self._session.begin():
            self._session.add(perm)
        return perm

    async def get(self, permission_id: str) -> Optional[PermissionModel]:
        try:
            uuid_obj = uuid.UUID(permission_id)
        except ValueError:
            return None
        return await self._session.get(PermissionModel, uuid_obj)

    async def list(self) -> List[PermissionModel]:
        result = await self._session.execute(select(PermissionModel))
        return list(result.scalars())

    async def delete(self, permission_id: str) -> bool:
        try:
            uuid_obj = uuid.UUID(permission_id)
        except ValueError:
            return False
        async with self._session.begin():
            res = await self._session.execute(
                delete(PermissionModel).where(PermissionModel.id == uuid_obj)
            )
        return res.rowcount > 0


class SQLAlchemyRoleRepository(RoleRepository):
    """SQLAlchemy implementation of ``RoleRepository``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, tenant_id: str | None, name: str, description: str | None = None) -> RoleModel:
        # Duplicate check: roles are unique per (tenant_id, name)
        result = await self._session.scalar(
            select(RoleModel.id).where(
                RoleModel.name == name,
                RoleModel.tenant_id == tenant_id,
            )
        )
        if result:
            raise ValueError(
                f"role '{name}' already exists for tenant '{tenant_id}'"
            )
        role = RoleModel(tenant_id=tenant_id, name=name, description=description)
        async with self._session.begin():
            self._session.add(role)
        return role

    async def get(self, role_id: str) -> Optional[RoleModel]:
        try:
            uuid_obj = uuid.UUID(role_id)
        except ValueError:
            return None
        return await self._session.get(RoleModel, uuid_obj)

    async def list(self, tenant_id: str | None = None) -> List[RoleModel]:
        stmt = select(RoleModel)
        if tenant_id is not None:
            stmt = stmt.where(RoleModel.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def delete(self, role_id: str) -> bool:
        try:
            uuid_obj = uuid.UUID(role_id)
        except ValueError:
            return False
        async with self._session.begin():
            res = await self._session.execute(
                delete(RoleModel).where(RoleModel.id == uuid_obj)
            )
        return res.rowcount > 0

    async def assign_permission(self, role_id: str, permission_id: str) -> None:
        # Always idempotent: no error if the mapping already exists
        try:
            role_uuid = uuid.UUID(role_id)
            perm_uuid = uuid.UUID(permission_id)
        except ValueError:
            return
        stmt = insert(role_permissions).values(role_id=role_uuid, permission_id=perm_uuid)
        # ``on_conflict_do_nothing`` is available on dialect-specific insert; the type checker may
        # not know about this method on a generic ``Insert``, so ignore that attribute.
        stmt = stmt.on_conflict_do_nothing(  # type: ignore[attr-defined]
            index_elements=[role_permissions.c.role_id, role_permissions.c.permission_id]
        )
        async with self._session.begin():
            await self._session.execute(stmt)

    async def remove_permission(self, role_id: str, permission_id: str) -> None:
        try:
            role_uuid = uuid.UUID(role_id)
            perm_uuid = uuid.UUID(permission_id)
        except ValueError:
            return
        # Delete the mapping if it exists.  Do nothing if not present.
        async with self._session.begin():
            await self._session.execute(
                delete(role_permissions).where(
                    role_permissions.c.role_id == role_uuid,
                    role_permissions.c.permission_id == perm_uuid,
                )
            )


class SQLAlchemyGroupRepository(GroupRepository):
    """SQLAlchemy implementation of ``GroupRepository``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, tenant_id: str | None, name: str, description: str | None = None) -> GroupModel:
        # Groups are unique per (tenant_id, name)
        existing = await self._session.scalar(
            select(GroupModel.id).where(
                GroupModel.name == name,
                GroupModel.tenant_id == tenant_id,
            )
        )
        if existing:
            raise ValueError(
                f"group '{name}' already exists for tenant '{tenant_id}'"
            )
        group = GroupModel(tenant_id=tenant_id, name=name, description=description)
        async with self._session.begin():
            self._session.add(group)
        return group

    async def get(self, group_id: str) -> Optional[GroupModel]:
        try:
            uuid_obj = uuid.UUID(group_id)
        except ValueError:
            return None
        return await self._session.get(GroupModel, uuid_obj)

    async def list(self, tenant_id: str | None = None) -> List[GroupModel]:
        stmt = select(GroupModel)
        if tenant_id is not None:
            stmt = stmt.where(GroupModel.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def delete(self, group_id: str) -> bool:
        try:
            uuid_obj = uuid.UUID(group_id)
        except ValueError:
            return False
        async with self._session.begin():
            res = await self._session.execute(
                delete(GroupModel).where(GroupModel.id == uuid_obj)
            )
        return res.rowcount > 0

    async def assign_role(self, group_id: str, role_id: str) -> None:
        try:
            group_uuid = uuid.UUID(group_id)
            role_uuid = uuid.UUID(role_id)
        except ValueError:
            return
        stmt = insert(group_roles).values(group_id=group_uuid, role_id=role_uuid)
        # on_conflict_do_nothing is dialect-specific; silence type checker
        stmt = stmt.on_conflict_do_nothing(index_elements=[group_roles.c.group_id, group_roles.c.role_id])  # type: ignore[attr-defined]
        async with self._session.begin():
            await self._session.execute(stmt)

    async def remove_role(self, group_id: str, role_id: str) -> None:
        try:
            group_uuid = uuid.UUID(group_id)
            role_uuid = uuid.UUID(role_id)
        except ValueError:
            return
        async with self._session.begin():
            await self._session.execute(
                delete(group_roles).where(
                    group_roles.c.group_id == group_uuid,
                    group_roles.c.role_id == role_uuid,
                )
            )


class SQLAlchemyAccountRepository(AccountRepository):
    """SQLAlchemy implementation of ``AccountRepository``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, username: str, email: str, tenant_id: str | None) -> AccountModel:
        # Basic duplicate check: email unique across all tenants; username unique per tenant
        # Check email
        email_exists = await self._session.scalar(
            select(AccountModel.id).where(AccountModel.email == email)
        )
        if email_exists:
            raise ValueError(f"email '{email}' already exists")
        # Check username within tenant
        username_exists = await self._session.scalar(
            select(AccountModel.id).where(
                AccountModel.username == username,
                AccountModel.tenant_id == tenant_id,
            )
        )
        if username_exists:
            raise ValueError(
                f"username '{username}' already exists for tenant '{tenant_id}'"
            )
        account = AccountModel(
            tenant_id=tenant_id,
            username=username,
            email=email,
        )
        async with self._session.begin():
            self._session.add(account)
        return account

    async def get(self, account_id: str) -> Optional[AccountModel]:
        try:
            uuid_obj = uuid.UUID(account_id)
        except ValueError:
            return None
        return await self._session.get(AccountModel, uuid_obj)

    async def list(self, tenant_id: str | None = None) -> List[AccountModel]:
        stmt = select(AccountModel)
        if tenant_id is not None:
            stmt = stmt.where(AccountModel.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def delete(self, account_id: str) -> bool:
        try:
            uuid_obj = uuid.UUID(account_id)
        except ValueError:
            return False
        async with self._session.begin():
            res = await self._session.execute(
                delete(AccountModel).where(AccountModel.id == uuid_obj)
            )
        return res.rowcount > 0

    async def assign_role(self, account_id: str, role_id: str) -> None:
        try:
            acc_uuid = uuid.UUID(account_id)
            role_uuid = uuid.UUID(role_id)
        except ValueError:
            return
        stmt = insert(user_roles).values(account_id=acc_uuid, role_id=role_uuid)
        # on_conflict_do_nothing is dialect-specific; silence type checker
        stmt = stmt.on_conflict_do_nothing(index_elements=[user_roles.c.account_id, user_roles.c.role_id])  # type: ignore[attr-defined]
        async with self._session.begin():
            await self._session.execute(stmt)

    async def remove_role(self, account_id: str, role_id: str) -> None:
        try:
            acc_uuid = uuid.UUID(account_id)
            role_uuid = uuid.UUID(role_id)
        except ValueError:
            return
        async with self._session.begin():
            await self._session.execute(
                delete(user_roles).where(
                    user_roles.c.account_id == acc_uuid,
                    user_roles.c.role_id == role_uuid,
                )
            )

    async def assign_group(self, account_id: str, group_id: str) -> None:
        try:
            acc_uuid = uuid.UUID(account_id)
            group_uuid = uuid.UUID(group_id)
        except ValueError:
            return
        stmt = insert(user_groups).values(account_id=acc_uuid, group_id=group_uuid)
        # on_conflict_do_nothing is dialect-specific; silence type checker
        stmt = stmt.on_conflict_do_nothing(index_elements=[user_groups.c.account_id, user_groups.c.group_id])  # type: ignore[attr-defined]
        async with self._session.begin():
            await self._session.execute(stmt)

    async def remove_group(self, account_id: str, group_id: str) -> None:
        try:
            acc_uuid = uuid.UUID(account_id)
            group_uuid = uuid.UUID(group_id)
        except ValueError:
            return
        async with self._session.begin():
            await self._session.execute(
                delete(user_groups).where(
                    user_groups.c.account_id == acc_uuid,
                    user_groups.c.group_id == group_uuid,
                )
            )


class SQLAlchemyResourceRepository(ResourceRepository):
    """SQLAlchemy implementation of ``ResourceRepository``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        resource_type: str,
        name: str,
        tenant_id: str | None,
        owner_id: str | None,
        metadata: dict[str, str] | None = None,
    ) -> ResourceModel:
        # Duplicate check: resources are unique per (tenant_id, name)
        existing = await self._session.scalar(
            select(ResourceModel.id).where(
                ResourceModel.name == name,
                ResourceModel.tenant_id == tenant_id,
            )
        )
        if existing:
            raise ValueError(
                f"resource '{name}' already exists for tenant '{tenant_id}'"
            )
        kwargs: dict[str, Any] = {
            "type": resource_type,
            "name": name,
            "tenant_id": tenant_id,
            "owner_id": uuid.UUID(owner_id) if owner_id else None,
            "resource_metadata": metadata or {},
        }
        resource = ResourceModel(**kwargs)
        async with self._session.begin():
            self._session.add(resource)
        return resource

    async def get(self, resource_id: str) -> Optional[ResourceModel]:
        try:
            uuid_obj = uuid.UUID(resource_id)
        except ValueError:
            return None
        return await self._session.get(ResourceModel, uuid_obj)

    async def list(self, tenant_id: str | None = None) -> List[ResourceModel]:
        stmt = select(ResourceModel)
        if tenant_id is not None:
            stmt = stmt.where(ResourceModel.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def delete(self, resource_id: str) -> bool:
        try:
            uuid_obj = uuid.UUID(resource_id)
        except ValueError:
            return False
        async with self._session.begin():
            res = await self._session.execute(
                delete(ResourceModel).where(ResourceModel.id == uuid_obj)
            )
        return res.rowcount > 0


class AuditLogRepository:
    """Simplified repository for writing audit log entries.

    The audit log records are append-only and currently no reads are
    implemented.  This repository is deliberately minimal; audit log
    writing is a side-effect of access control operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        *,
        account_id: str,
        action: str,
        resource: str | None,
        result: bool,
        message: str | None = None,
    ) -> None:
        # Convert account_id to UUID if possible; ignore invalid
        try:
            account_uuid = uuid.UUID(account_id)
        except ValueError:
            account_uuid = None  # type: ignore[assignment]
        log = AuditLogModel(
            account_id=account_uuid,
            action=action,
            resource=resource,
            result=result,
            message=message,
        )
        async with self._session.begin():
            self._session.add(log)