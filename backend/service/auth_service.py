# backend/service/auth_service.py

from __future__ import annotations

from typing import Optional, Tuple, Sequence, Dict, Any
from uuid import UUID

from casbin.async_enforcer import AsyncEnforcer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from ..db.db_models import (
    AccountModel,
    GroupModel,
    RoleModel,
    PermissionModel,
    ResourceModel,
)
from ..db.unit_of_work import UnitOfWork


# ---- Utilities and Custom Exceptions ----
RESOURCE_TO_PATTERN = {
    "doc": "/docs/*",
}


def _parse_perm(name: str) -> Tuple[str, str]:
    if ":" not in name:
        raise ValueError("Permission name must be in 'resource:action' format")
    res, action = name.split(":", 1)
    return res, action


class DuplicateError(RuntimeError):
    pass


class NotFoundError(RuntimeError):
    pass


class ConcurrencyError(RuntimeError):
    pass


class AuthService:
    def __init__(self, enforcer: AsyncEnforcer) -> None:
        self._e = enforcer

    # --------------- Permission Management ---------------

    async def create_permission(self, uow: UnitOfWork, name: str, description: str = "") -> PermissionModel:
        _parse_perm(name)
        if await uow.permissions.get_by_name(name):
            raise DuplicateError(f"Permission '{name}' already exists.")
        
        perm = PermissionModel(name=name, description=description or "")
        uow.permissions.add(perm)
        return perm

    async def delete_permission(self, uow: UnitOfWork, perm_id: UUID) -> None:
        if not await uow.permissions.delete(perm_id):
            raise NotFoundError(f"Permission with ID '{perm_id}' not found.")

    async def list_permissions(self, uow: UnitOfWork, name: Optional[str] = None) -> Sequence[PermissionModel]:
        return await uow.permissions.list(name=name)

    # --------------- Role Management ---------------

    async def create_role(self, uow: UnitOfWork, tenant_id: Optional[str], name: str, description: str = "") -> RoleModel:
        if await uow.roles.get_by_name(tenant_id, name):
            raise DuplicateError(f"Role '{name}' already exists in tenant '{tenant_id}'.")
            
        role = RoleModel(tenant_id=tenant_id, name=name, description=description or "")
        uow.roles.add(role)
        return role

    async def delete_role(self, uow: UnitOfWork, role_id: UUID) -> None:
        if not await uow.roles.delete(role_id):
            raise NotFoundError(f"Role with ID '{role_id}' not found.")
        
        # Also clean up casbin policies
        role_id_str = str(role_id)
        await self._e.remove_filtered_policy(0, role_id_str)
        await self._e.remove_filtered_grouping_policy(1, role_id_str)

    async def list_roles(self, uow: UnitOfWork, tenant_id: Optional[str] = None, name: Optional[str] = None) -> Sequence[RoleModel]:
        return await uow.roles.list(tenant_id=tenant_id, name=name)

    # --------------- Group Management ---------------

    async def create_group(self, uow: UnitOfWork, tenant_id: Optional[str], name: str, description: str = "") -> GroupModel:
        # NOTE: Logic to check for duplicates would be similar to create_role
        grp = GroupModel(tenant_id=tenant_id, name=name, description=description or "")
        uow.groups.add(grp)
        return grp

    async def delete_group(self, uow: UnitOfWork, group_id: UUID) -> None:
        if not await uow.groups.delete(group_id):
            raise NotFoundError(f"Group with ID '{group_id}' not found.")
            
        group_id_str = str(group_id)
        await self._e.remove_filtered_grouping_policy(0, group_id_str)
        await self._e.remove_filtered_named_grouping_policy("g", 1, group_id_str)

    async def list_groups(self, uow: UnitOfWork, tenant_id: Optional[str] = None) -> Sequence[GroupModel]:
        return await uow.groups.list(tenant_id=tenant_id)

    # --------------- Account Management ---------------

    async def create_account(self, uow: UnitOfWork, username: str, email: str, tenant_id: Optional[str]) -> AccountModel:
        if await uow.accounts.get_by_email(email) or await uow.accounts.get_by_username(tenant_id, username):
             raise DuplicateError(f"Account with email '{email}' or username '{username}' already exists.")

        acc = AccountModel(username=username, email=email, tenant_id=tenant_id)
        uow.accounts.add(acc)
        return acc

    async def delete_account(self, uow: UnitOfWork, account_id: UUID) -> None:
        if not await uow.accounts.delete(account_id):
            raise NotFoundError(f"Account with ID '{account_id}' not found.")
            
        account_id_str = str(account_id)
        await self._e.remove_filtered_grouping_policy(0, account_id_str)

    async def list_accounts(self, uow: UnitOfWork, tenant_id: Optional[str] = None, username: Optional[str] = None) -> Sequence[AccountModel]:
        return await uow.accounts.list(tenant_id=tenant_id, username=username)

    # --------------- Resource Management ---------------
    
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
            raise NotFoundError(f"Resource with ID '{resource_id}' not found.")

    async def list_resources(self, uow: UnitOfWork, tenant_id: Optional[str] = None) -> Sequence[ResourceModel]:
        return await uow.resources.list(tenant_id=tenant_id)


    # --------------- Relationship Management ---------------

    async def assign_permission_to_role(self, uow: UnitOfWork, role_id: UUID, permission_id: UUID) -> None:
        role = await uow.roles.get_with_permissions(role_id)
        perm = await uow.permissions.get(permission_id)
        if not role or not perm:
            raise NotFoundError("Role or permission not found.")

        if perm not in role.permissions:
            role.permissions.append(perm)

        res, act = _parse_perm(perm.name)
        obj = RESOURCE_TO_PATTERN.get(res, res)
        dom = role.tenant_id or ""
        
        if not self._e.has_policy(str(role_id), dom, obj, act):
            await self._e.add_policy(str(role_id), dom, obj, act)

    async def remove_permission_from_role(self, uow: UnitOfWork, role_id: UUID, permission_id: UUID) -> None:
        role = await uow.roles.get_with_permissions(role_id)
        perm = await uow.permissions.get(permission_id)
        if not role or not perm:
            raise NotFoundError("Role or permission not found.")

        if perm in role.permissions:
            role.permissions.remove(perm)

        resource, action = _parse_perm(perm.name)
        obj = RESOURCE_TO_PATTERN.get(resource, resource)
        domain = role.tenant_id or ""
        await self._e.remove_policy(str(role_id), domain, obj, action)

    async def assign_role_to_account(self, uow: UnitOfWork, account_id: UUID, role_id: UUID) -> None:
        acc = await uow.accounts.get_with_roles(account_id)
        role = await uow.roles.get(role_id)
        if not acc or not role:
            raise NotFoundError("Account or role not found.")

        if role not in acc.roles:
            acc.roles.append(role)
        
        domain = role.tenant_id or ""
        await self._e.add_grouping_policy(str(account_id), str(role_id), domain)

    async def remove_role_from_account(self, uow: UnitOfWork, account_id: UUID, role_id: UUID) -> None:
        acc = await uow.accounts.get_with_roles(account_id)
        role = await uow.roles.get(role_id)
        if not acc or not role:
            raise NotFoundError("Account or role not found.")

        if role in acc.roles:
            acc.roles.remove(role)

        domain = role.tenant_id or ""
        await self._e.remove_grouping_policy(str(account_id), str(role_id), domain)

    # ... (implement other relationship methods similarly) ...
    async def assign_role_to_group(self, uow: UnitOfWork, group_id: UUID, role_id: UUID) -> None:
        grp = await uow.groups.get_with_roles(group_id)
        role = await uow.roles.get(role_id)
        if not grp or not role:
            raise NotFoundError("Group or role not found.")

        if role not in grp.roles:
            grp.roles.append(role)

        domain = role.tenant_id or ""
        await self._e.add_grouping_policy(str(group_id), str(role_id), domain)


    async def remove_role_from_group(self, uow: UnitOfWork, group_id: UUID, role_id: UUID) -> None:
        grp = await uow.groups.get_with_roles(group_id)
        role = await uow.roles.get(role_id)
        if not grp or not role:
            raise NotFoundError("Group or role not found.")

        if role in grp.roles:
            grp.roles.remove(role)

        domain = role.tenant_id or ""
        await self._e.remove_grouping_policy(str(group_id), str(role_id), domain)


    async def assign_group_to_account(self, uow: UnitOfWork, account_id: UUID, group_id: UUID) -> None:
        acc = await uow.accounts.get_with_groups(account_id)
        grp = await uow.groups.get(group_id)
        if not acc or not grp:
            raise NotFoundError("Account or group not found.")

        if grp not in acc.groups:
            acc.groups.append(grp)

        domain = grp.tenant_id or ""
        await self._e.add_named_grouping_policy("g", str(account_id), str(group_id), domain)


    async def remove_group_from_account(self, uow: UnitOfWork, account_id: UUID, group_id: UUID) -> None:
        acc = await uow.accounts.get_with_groups(account_id)
        grp = await uow.groups.get(group_id)
        if not acc or not grp:
            raise NotFoundError("Account or group not found.")

        if grp in acc.groups:
            acc.groups.remove(grp)

        domain = grp.tenant_id or ""
        await self._e.remove_named_grouping_policy("g", str(account_id), str(group_id), domain)
        
    # --------------- Authorization Check ---------------

    async def check_access(
        self, account_id: UUID, resource: str, action: str, tenant_id: Optional[str] = None
    ) -> bool:
        sub, dom, obj, act = str(account_id), tenant_id or "", resource, action
        return self._e.enforce(sub, dom, obj, act)