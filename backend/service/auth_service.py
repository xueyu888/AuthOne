"""Service layer for AuthOne.

This module orchestrates operations across repositories and the
authorisation engine (Casbin).  The service layer performs
application-level validation (such as cross-tenant checks) and
translates lower-level exceptions into domain-appropriate ones.  It
does not directly expose SQLAlchemy sessions or models to calling
code but instead returns the ORM instances, allowing the API layer to
serialise them as necessary.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import List, Optional, Tuple

from ..db import (
    PermissionModel,
    RoleModel,
    GroupModel,
    AccountModel,
    ResourceModel,
)
from ..models import AccessCheckRequest, AccessCheckResponse
from ..storage.interface import (
    PermissionRepository,
    RoleRepository,
    GroupRepository,
    AccountRepository,
    ResourceRepository,
)
from ..storage.sqlalchemy_repository import (
    SQLAlchemyPermissionRepository,
    SQLAlchemyRoleRepository,
    SQLAlchemyGroupRepository,
    SQLAlchemyAccountRepository,
    SQLAlchemyResourceRepository,
    AuditLogRepository,
)
from ..db import get_session
from ..core.casbin_adapter import CasbinEngine

__all__ = ["AuthService"]


class AuthService:
    """Application-level service managing permissions, roles, groups, accounts and resources."""

    def __init__(
        self,
        perm_repo: PermissionRepository,
        role_repo: RoleRepository,
        group_repo: GroupRepository,
        account_repo: AccountRepository,
        resource_repo: ResourceRepository,
        audit_repo: AuditLogRepository,
        casbin_engine: CasbinEngine,
    ) -> None:
        self._perm_repo = perm_repo
        self._role_repo = role_repo
        self._group_repo = group_repo
        self._account_repo = account_repo
        self._resource_repo = resource_repo
        self._audit_repo = audit_repo
        self._casbin = casbin_engine

    @classmethod
    async def create(cls, casbin: CasbinEngine) -> "AuthService":
        """Factory method to create an ``AuthService`` with a new session.

        This method obtains a new session via ``get_session`` and
        constructs concrete repository instances bound to that session.
        The returned service instance shares a single session across all
        repository instances; callers should not reuse it across
        multiple concurrent requests.
        """
        session = get_session()
        return cls(
            perm_repo=SQLAlchemyPermissionRepository(session),
            role_repo=SQLAlchemyRoleRepository(session),
            group_repo=SQLAlchemyGroupRepository(session),
            account_repo=SQLAlchemyAccountRepository(session),
            resource_repo=SQLAlchemyResourceRepository(session),
            audit_repo=AuditLogRepository(session),
            casbin_engine=casbin,
        )

    # ------------------------------------------------------------------
    # Internal utilities
    @staticmethod
    def _parse_permission_name(name: str) -> Tuple[str, str]:
        """Split a permission name of the form ``resource:action``.

        :param name: The permission name string.
        :returns: A tuple ``(resource, action)``.
        :raises ValueError: if the string does not contain a colon or any
            side is empty.
        """
        if ":" not in name:
            raise ValueError(
                f"permission name must be in format 'resource:action', got {name!r}"
            )
        resource, action = name.split(":", 1)
        if not resource or not action:
            raise ValueError(f"invalid permission name: {name!r}")
        return resource, action

    @staticmethod
    def _tenant_compatible(a: Optional[str], b: Optional[str]) -> bool:
        """Return True if two tenant IDs are compatible for association.

        Associations across different tenants are allowed but recorded
        as soft errors in the audit log; the Casbin domain check
        ultimately enforces isolation.
        """
        return a is None or b is None or a == b

    # ------------------------------------------------------------------
    # Creation methods
    async def create_permission(self, name: str, description: str = "") -> PermissionModel:
        return await self._perm_repo.add(name=name, description=description)

    async def create_role(self, tenant_id: str | None, name: str, description: str = "") -> RoleModel:
        return await self._role_repo.add(tenant_id=tenant_id, name=name, description=description)

    async def create_group(self, tenant_id: str | None, name: str, description: str = "") -> GroupModel:
        return await self._group_repo.add(tenant_id=tenant_id, name=name, description=description)

    async def create_account(self, username: str, email: str, tenant_id: str | None = None) -> AccountModel:
        return await self._account_repo.add(username=username, email=email, tenant_id=tenant_id)

    async def create_resource(
        self,
        resource_type: str,
        name: str,
        tenant_id: str | None,
        owner_id: str | None,
        metadata: dict[str, str] | None = None,
    ) -> ResourceModel:
        return await self._resource_repo.add(
            resource_type=resource_type,
            name=name,
            tenant_id=tenant_id,
            owner_id=owner_id,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Listing methods
    async def list_permissions(self) -> List[PermissionModel]:
        return await self._perm_repo.list()

    async def list_roles(self, tenant_id: str | None = None) -> List[RoleModel]:
        return await self._role_repo.list(tenant_id)

    async def list_groups(self, tenant_id: str | None = None) -> List[GroupModel]:
        return await self._group_repo.list(tenant_id)

    async def list_accounts(self, tenant_id: str | None = None) -> List[AccountModel]:
        return await self._account_repo.list(tenant_id)

    async def list_resources(self, tenant_id: str | None = None) -> List[ResourceModel]:
        return await self._resource_repo.list(tenant_id)

    # ------------------------------------------------------------------
    # Assignment methods
    async def assign_permission_to_role(self, role_id: str, permission_id: str) -> None:
        role = await self._role_repo.get(role_id)
        perm = await self._perm_repo.get(permission_id)
        if not role or not perm:
            raise ValueError("role or permission not found")
        # Persist association
        await self._role_repo.assign_permission(role.id.hex if isinstance(role.id, uuid.UUID) else str(role.id), perm.id.hex if isinstance(perm.id, uuid.UUID) else str(perm.id))
        # Update Casbin
        res, act = self._parse_permission_name(perm.name)
        await asyncio.to_thread(
            self._casbin.add_permission_for_user,
            str(role.id),
            role.tenant_id,
            res,
            act,
        )

    async def assign_role_to_account(self, account_id: str, role_id: str) -> None:
        acc = await self._account_repo.get(account_id)
        role = await self._role_repo.get(role_id)
        if not acc or not role:
            raise ValueError("account or role not found")
        # Soft tenant mismatch detection
        if not self._tenant_compatible(acc.tenant_id, role.tenant_id):
            await self._audit_repo.record(
                account_id=str(acc.id),
                action="assign_role",
                resource=str(role.id),
                result=False,
                message="tenant mismatch (soft)",
            )
        await self._account_repo.assign_role(account_id=str(acc.id), role_id=str(role.id))
        await asyncio.to_thread(
            self._casbin.add_role_for_account,
            str(acc.id),
            acc.tenant_id,
            str(role.id),
        )

    async def assign_role_to_group(self, group_id: str, role_id: str) -> None:
        grp = await self._group_repo.get(group_id)
        role = await self._role_repo.get(role_id)
        if not grp or not role:
            raise ValueError("group or role not found")
        if not self._tenant_compatible(grp.tenant_id, role.tenant_id):
            await self._audit_repo.record(
                account_id="system",
                action="assign_role_to_group",
                resource=str(role.id),
                result=False,
                message="tenant mismatch (soft)",
            )
        await self._group_repo.assign_role(group_id=str(grp.id), role_id=str(role.id))
        await asyncio.to_thread(
            self._casbin.add_role_for_group,
            str(grp.id),
            grp.tenant_id,
            str(role.id),
        )

    async def assign_group_to_account(self, account_id: str, group_id: str) -> None:
        acc = await self._account_repo.get(account_id)
        grp = await self._group_repo.get(group_id)
        if not acc or not grp:
            raise ValueError("account or group not found")
        if not self._tenant_compatible(acc.tenant_id, grp.tenant_id):
            await self._audit_repo.record(
                account_id=str(acc.id),
                action="assign_group",
                resource=str(grp.id),
                result=False,
                message="tenant mismatch (soft)",
            )
        await self._account_repo.assign_group(account_id=str(acc.id), group_id=str(grp.id))
        await asyncio.to_thread(
            self._casbin.add_group_for_account,
            str(acc.id),
            acc.tenant_id,
            str(grp.id),
        )

    # ------------------------------------------------------------------
    # Removal methods
    async def remove_permission_from_role(self, role_id: str, permission_id: str) -> None:
        role = await self._role_repo.get(role_id)
        perm = await self._perm_repo.get(permission_id)
        if not role or not perm:
            raise ValueError("role or permission not found")
        await self._role_repo.remove_permission(role_id=str(role.id), permission_id=str(perm.id))
        res, act = self._parse_permission_name(perm.name)
        await asyncio.to_thread(
            self._casbin.remove_permission_from_user,
            str(role.id),
            role.tenant_id,
            res,
            act,
        )

    async def remove_role_from_account(self, account_id: str, role_id: str) -> None:
        acc = await self._account_repo.get(account_id)
        role = await self._role_repo.get(role_id)
        if not acc or not role:
            raise ValueError("account or role not found")
        await self._account_repo.remove_role(account_id=str(acc.id), role_id=str(role.id))
        await asyncio.to_thread(
            self._casbin.remove_role_for_account,
            str(acc.id),
            acc.tenant_id,
            str(role.id),
        )

    async def remove_role_from_group(self, group_id: str, role_id: str) -> None:
        grp = await self._group_repo.get(group_id)
        role = await self._role_repo.get(role_id)
        if not grp or not role:
            raise ValueError("group or role not found")
        await self._group_repo.remove_role(group_id=str(grp.id), role_id=str(role.id))
        await asyncio.to_thread(
            self._casbin.remove_role_for_group,
            str(grp.id),
            grp.tenant_id,
            str(role.id),
        )

    async def remove_group_from_account(self, account_id: str, group_id: str) -> None:
        acc = await self._account_repo.get(account_id)
        grp = await self._group_repo.get(group_id)
        if not acc or not grp:
            raise ValueError("account or group not found")
        await self._account_repo.remove_group(account_id=str(acc.id), group_id=str(grp.id))
        await asyncio.to_thread(
            self._casbin.remove_group_for_account,
            str(acc.id),
            acc.tenant_id,
            str(grp.id),
        )

    # ------------------------------------------------------------------
    # Deletion methods
    async def delete_permission(self, permission_id: str) -> bool:
        return await self._perm_repo.delete(permission_id)

    async def delete_role(self, role_id: str) -> bool:
        role = await self._role_repo.get(role_id)
        if not role:
            return False
        ok = await self._role_repo.delete(role_id)
        await asyncio.to_thread(
            self._casbin.remove_filtered_policies_for_subject,
            str(role.id),
        )
        return ok

    async def delete_group(self, group_id: str) -> bool:
        grp = await self._group_repo.get(group_id)
        if not grp:
            return False
        ok = await self._group_repo.delete(group_id)
        await asyncio.to_thread(
            self._casbin.remove_filtered_policies_for_subject,
            str(grp.id),
        )
        return ok

    async def delete_account(self, account_id: str) -> bool:
        acc = await self._account_repo.get(account_id)
        if not acc:
            return False
        ok = await self._account_repo.delete(account_id)
        await asyncio.to_thread(
            self._casbin.remove_filtered_policies_for_subject,
            str(acc.id),
        )
        return ok

    async def delete_resource(self, resource_id: str) -> bool:
        return await self._resource_repo.delete(resource_id)

    # ------------------------------------------------------------------
    # Access check
    async def check_access(self, req: AccessCheckRequest) -> AccessCheckResponse:
        allowed = await asyncio.to_thread(
            self._casbin.enforce,
            req.account_id,
            req.tenant_id,
            req.resource,
            req.action,
        )
        # Record audit
        await self._audit_repo.record(
            account_id=req.account_id,
            action=req.action,
            resource=req.resource,
            result=allowed,
            message="allowed" if allowed else "denied",
        )
        return AccessCheckResponse(
            allowed=bool(allowed),
            reason=None if allowed else "Access denied",
        )