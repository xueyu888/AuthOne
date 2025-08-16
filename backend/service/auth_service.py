from __future__ import annotations

import inspect
from typing import Optional, Tuple, Sequence, Dict, Any
from uuid import UUID

from casbin.async_enforcer import AsyncEnforcer

from ..db.db_models import (
    AccountModel,
    GroupModel,
    RoleModel,
    PermissionModel,
    ResourceModel,
)
from ..db.unit_of_work import UnitOfWork
from .exceptions import DuplicateError, NotFoundError

def _parse_perm(name: str) -> Tuple[str, str]:
    if ":" not in name:
        raise ValueError("Permission name must be in 'resource:action' format")
    res, action = name.split(":", 1)
    return res, action

async def _maybe_await(v):
    """Casbin 有的实现是同步，有的是异步；统一一下。"""
    return await v if inspect.isawaitable(v) else v

class AuthService:
    """
    业务服务层：不碰 HTTP、只做领域逻辑。
    resource_to_pattern 可配置注入：{"doc": "/docs/*"} 等
    """
    def __init__(self, enforcer: AsyncEnforcer, resource_to_pattern: Optional[Dict[str, str]] = None) -> None:
        self._e = enforcer
        self.RESOURCE_TO_PATTERN: Dict[str, str] = resource_to_pattern or {}

    # -------- Permissions --------
    async def create_permission(self, uow: UnitOfWork, name: str, description: str = "") -> PermissionModel:
        _parse_perm(name)
        if await uow.permissions.get_by_name(name):
            raise DuplicateError(f"Permission '{name}' already exists.")
        perm = PermissionModel(name=name, description=description or "")
        uow.permissions.add(perm)
        return perm

    async def delete_permission(self, uow: UnitOfWork, perm_id: UUID) -> None:
        if not await uow.permissions.delete(perm_id):
            raise NotFoundError(f"Permission '{perm_id}' not found.")

    async def list_permissions(self, uow: UnitOfWork, name: Optional[str] = None) -> Sequence[PermissionModel]:
        return await uow.permissions.list(name=name)

    # -------- Roles --------
    async def create_role(self, uow: UnitOfWork, tenant_id: Optional[str], name: str, description: str = "") -> RoleModel:
        if await uow.roles.get_by_name(tenant_id, name):
            raise DuplicateError(f"Role '{name}' already exists in tenant '{tenant_id}'.")
        role = RoleModel(tenant_id=tenant_id, name=name, description=description or "")
        uow.roles.add(role)
        return role

    async def delete_role(self, uow: UnitOfWork, role_id: UUID) -> None:
        if not await uow.roles.delete(role_id):
            raise NotFoundError(f"Role '{role_id}' not found.")
        rid = str(role_id)
        await _maybe_await(self._e.remove_filtered_policy(0, rid))
        await _maybe_await(self._e.remove_filtered_grouping_policy(1, rid))

    async def list_roles(self, uow: UnitOfWork, tenant_id: Optional[str] = None, name: Optional[str] = None) -> Sequence[RoleModel]:
        return await uow.roles.list(tenant_id=tenant_id, name=name)

    # -------- Groups --------
    async def create_group(self, uow: UnitOfWork, tenant_id: Optional[str], name: str, description: str = "") -> GroupModel:
        grp = GroupModel(tenant_id=tenant_id, name=name, description=description or "")
        uow.groups.add(grp)
        return grp

    async def delete_group(self, uow: UnitOfWork, group_id: UUID) -> None:
        if not await uow.groups.delete(group_id):
            raise NotFoundError(f"Group '{group_id}' not found.")
        gid = str(group_id)
        await _maybe_await(self._e.remove_filtered_grouping_policy(0, gid))
        await _maybe_await(self._e.remove_filtered_named_grouping_policy("g", 1, gid))

    async def list_groups(self, uow: UnitOfWork, tenant_id: Optional[str] = None) -> Sequence[GroupModel]:
        return await uow.groups.list(tenant_id=tenant_id)

    # -------- Accounts --------
    async def create_account(self, uow: UnitOfWork, username: str, email: str, tenant_id: Optional[str]) -> AccountModel:
        if await uow.accounts.get_by_email(email) or await uow.accounts.get_by_username(tenant_id, username):
            raise DuplicateError(f"Account with email '{email}' or username '{username}' already exists.")
        acc = AccountModel(username=username, email=email, tenant_id=tenant_id)
        uow.accounts.add(acc)
        return acc

    async def delete_account(self, uow: UnitOfWork, account_id: UUID) -> None:
        if not await uow.accounts.delete(account_id):
            raise NotFoundError(f"Account '{account_id}' not found.")
        aid = str(account_id)
        await _maybe_await(self._e.remove_filtered_grouping_policy(0, aid))

    async def list_accounts(self, uow: UnitOfWork, tenant_id: Optional[str] = None, username: Optional[str] = None) -> Sequence[AccountModel]:
        return await uow.accounts.list(tenant_id=tenant_id, username=username)

    # -------- Resources --------
    async def create_resource(
        self, uow: UnitOfWork, resource_type: str, name: str, tenant_id: Optional[str],
        owner_id: Optional[UUID], metadata: Optional[Dict[str, Any]] = None
    ) -> ResourceModel:
        res = ResourceModel(
            type=resource_type, name=name, tenant_id=tenant_id, owner_id=owner_id,
            resource_metadata=metadata or {}
        )
        uow.resources.add(res)
        return res

    async def delete_resource(self, uow: UnitOfWork, resource_id: UUID) -> None:
        if not await uow.resources.delete(resource_id):
            raise NotFoundError(f"Resource '{resource_id}' not found.")

    async def list_resources(self, uow: UnitOfWork, tenant_id: Optional[str] = None) -> Sequence[ResourceModel]:
        return await uow.resources.list(tenant_id=tenant_id)

    # -------- Relationships --------
    async def assign_permission_to_role(self, uow: UnitOfWork, role_id: UUID, permission_id: UUID) -> None:
        role = await uow.roles.get_with_permissions(role_id)
        perm = await uow.permissions.get(permission_id)
        if not role or not perm:
            raise NotFoundError("Role or permission not found.")

        if perm not in role.permissions:
            role.permissions.append(perm)

        res, act = _parse_perm(perm.name)
        obj = self.RESOURCE_TO_PATTERN.get(res, res)
        dom = role.tenant_id or ""
        if not await _maybe_await(self._e.has_policy(str(role_id), dom, obj, act)):
            await _maybe_await(self._e.add_policy(str(role_id), dom, obj, act))

    async def remove_permission_from_role(self, uow: UnitOfWork, role_id: UUID, permission_id: UUID) -> None:
        role = await uow.roles.get_with_permissions(role_id)
        perm = await uow.permissions.get(permission_id)
        if not role or not perm:
            raise NotFoundError("Role or permission not found.")

        if perm in role.permissions:
            role.permissions.remove(perm)

        res, act = _parse_perm(perm.name)
        obj = self.RESOURCE_TO_PATTERN.get(res, res)
        dom = role.tenant_id or ""
        await _maybe_await(self._e.remove_policy(str(role_id), dom, obj, act))

    async def assign_role_to_account(self, uow: UnitOfWork, account_id: UUID, role_id: UUID) -> None:
        acc = await uow.accounts.get_with_roles(account_id)
        role = await uow.roles.get(role_id)
        if not acc or not role:
            raise NotFoundError("Account or role not found.")
        if role not in acc.roles:
            acc.roles.append(role)
        dom = role.tenant_id or ""
        await _maybe_await(self._e.add_grouping_policy(str(account_id), str(role_id), dom))

    async def remove_role_from_account(self, uow: UnitOfWork, account_id: UUID, role_id: UUID) -> None:
        acc = await uow.accounts.get_with_roles(account_id)
        role = await uow.roles.get(role_id)
        if not acc or not role:
            raise NotFoundError("Account or role not found.")
        if role in acc.roles:
            acc.roles.remove(role)
        dom = role.tenant_id or ""
        await _maybe_await(self._e.remove_grouping_policy(str(account_id), str(role_id), dom))

    async def assign_role_to_group(self, uow: UnitOfWork, group_id: UUID, role_id: UUID) -> None:
        grp = await uow.groups.get_with_roles(group_id)
        role = await uow.roles.get(role_id)
        if not grp or not role:
            raise NotFoundError("Group or role not found.")
        if role not in grp.roles:
            grp.roles.append(role)
        dom = role.tenant_id or ""
        await _maybe_await(self._e.add_grouping_policy(str(group_id), str(role_id), dom))

    async def remove_role_from_group(self, uow: UnitOfWork, group_id: UUID, role_id: UUID) -> None:
        grp = await uow.groups.get_with_roles(group_id)
        role = await uow.roles.get(role_id)
        if not grp or not role:
            raise NotFoundError("Group or role not found.")
        if role in grp.roles:
            grp.roles.remove(role)
        dom = role.tenant_id or ""
        await _maybe_await(self._e.remove_grouping_policy(str(group_id), str(role_id), dom))

    async def assign_group_to_account(self, uow: UnitOfWork, account_id: UUID, group_id: UUID) -> None:
        acc = await uow.accounts.get_with_groups(account_id)
        grp = await uow.groups.get(group_id)
        if not acc or not grp:
            raise NotFoundError("Account or group not found.")
        if grp not in acc.groups:
            acc.groups.append(grp)
        dom = grp.tenant_id or ""
        await _maybe_await(self._e.add_named_grouping_policy("g", str(account_id), str(group_id), dom))

    async def remove_group_from_account(self, uow: UnitOfWork, account_id: UUID, group_id: UUID) -> None:
        acc = await uow.accounts.get_with_groups(account_id)
        grp = await uow.groups.get(group_id)
        if not acc or not grp:
            raise NotFoundError("Account or group not found.")
        if grp in acc.groups:
            acc.groups.remove(grp)
        dom = grp.tenant_id or ""
        await _maybe_await(self._e.remove_named_grouping_policy("g", str(account_id), str(group_id), dom))

    # -------- Access Check --------
    async def check_access(self, account_id: UUID, resource: str, action: str, tenant_id: Optional[str] = None) -> bool:
        sub, dom, obj, act = str(account_id), (tenant_id or ""), resource, action
        return bool(await _maybe_await(self._e.enforce(sub, dom, obj, act)))
