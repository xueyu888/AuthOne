# backend/service/auth_service.py

from __future__ import annotations

from typing import Optional, Tuple, Sequence, Dict, Any
from uuid import UUID

from casbin.async_enforcer import AsyncEnforcer  
from sqlalchemy import delete, select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from ..db import (
    AccountModel,
    GroupModel,
    RoleModel,
    PermissionModel,
    ResourceModel,
)


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


class AuthService:
    def __init__(self, sm: async_sessionmaker[AsyncSession], enforcer: AsyncEnforcer) -> None:
        self._sm = sm
        self._e = enforcer

    # --------------- Permission Management ---------------

    async def create_permission(self, name: str, description: str = "") -> PermissionModel:
        _parse_perm(name)
        async with self._sm() as s:
            perm = PermissionModel(name=name, description=description or "")
            s.add(perm)
            try:
                await s.commit()
            except IntegrityError:
                await s.rollback()
                raise DuplicateError(f"Permission '{name}' already exists.")
            await s.refresh(perm)
            return perm
            
    async def get_permission_by_name(self, name: str) -> Optional[PermissionModel]:
        async with self._sm() as s:
            q = select(PermissionModel).where(PermissionModel.name == name)
            result = await s.execute(q)
            return result.scalar_one_or_none()

    async def delete_permission(self, perm_id: UUID) -> None:
        async with self._sm() as s:
            result = await s.execute(delete(PermissionModel).where(PermissionModel.id == perm_id))
            if result.rowcount == 0:
                raise NotFoundError(f"Permission with ID '{perm_id}' not found.")
            await s.commit()

    # --------------- Role Management ---------------

    async def create_role(self, tenant_id: Optional[str], name: str, description: str = "") -> RoleModel:
        async with self._sm() as s:
            role = RoleModel(tenant_id=tenant_id, name=name, description=description or "")
            s.add(role)
            try:
                await s.commit()
            except IntegrityError:
                await s.rollback()
                raise DuplicateError(f"Role '{name}' already exists in tenant '{tenant_id}'.")
            await s.refresh(role)
            return role
            
    async def get_role_by_name(self, tenant_id: Optional[str], name: str) -> Optional[RoleModel]:
        async with self._sm() as s:
            q = select(RoleModel).where(and_(RoleModel.tenant_id == tenant_id, RoleModel.name == name))
            result = await s.execute(q)
            return result.scalar_one_or_none()


    async def delete_role(self, role_id: UUID) -> None:
        async with self._sm() as s:
            role = await s.get(RoleModel, role_id)
            if not role:
                raise NotFoundError(f"Role with ID '{role_id}' not found.")
            await s.delete(role)
            await s.commit()

        role_id_str = str(role_id)
        # MODIFIED: Direct await on async enforcer methods
        await self._e.remove_filtered_policy(0, role_id_str)
        await self._e.remove_filtered_grouping_policy(1, role_id_str)

    # --------------- Group Management ---------------

    async def create_group(self, tenant_id: Optional[str], name: str, description: str = "") -> GroupModel:
        async with self._sm() as s:
            grp = GroupModel(tenant_id=tenant_id, name=name, description=description or "")
            s.add(grp)
            try:
                await s.commit()
            except IntegrityError:
                await s.rollback()
                raise DuplicateError(f"Group '{name}' already exists in tenant '{tenant_id}'.")
            await s.refresh(grp)
            return grp

    async def delete_group(self, group_id: UUID) -> None:
        async with self._sm() as s:
            grp = await s.get(GroupModel, group_id)
            if not grp:
                raise NotFoundError(f"Group with ID '{group_id}' not found.")
            await s.delete(grp)
            await s.commit()

        group_id_str = str(group_id)
        # MODIFIED: Direct await on async enforcer methods
        await self._e.remove_filtered_grouping_policy(0, group_id_str)
        await self._e.remove_filtered_named_grouping_policy("g", 1, group_id_str)

    # --------------- Account Management ---------------

    async def create_account(self, username: str, email: str, tenant_id: Optional[str]) -> AccountModel:
        async with self._sm() as s:
            acc = AccountModel(username=username, email=email, tenant_id=tenant_id)
            s.add(acc)
            try:
                await s.commit()
            except IntegrityError:
                await s.rollback()
                raise DuplicateError(f"Account with email '{email}' or username '{username}' already exists.")
            await s.refresh(acc)
            return acc
            
    async def get_account_by_username(self, tenant_id: Optional[str], username: str) -> Optional[AccountModel]:
        async with self._sm() as s:
            q = select(AccountModel).where(and_(AccountModel.tenant_id == tenant_id, AccountModel.username == username))
            result = await s.execute(q)
            return result.scalar_one_or_none()

    async def delete_account(self, account_id: UUID) -> None:
        async with self._sm() as s:
            acc = await s.get(AccountModel, account_id)
            if not acc:
                raise NotFoundError(f"Account with ID '{account_id}' not found.")
            await s.delete(acc)
            await s.commit()

        account_id_str = str(account_id)
        # MODIFIED: Direct await on async enforcer method
        await self._e.remove_filtered_grouping_policy(0, account_id_str)

    # --------------- Resource Management ---------------

    async def create_resource(
            self,
            resource_type: str,
            name: str,
            tenant_id: Optional[str],
            owner_id: Optional[UUID],
            metadata: Optional[Dict[str, Any]] = None,
    ) -> ResourceModel:
        async with self._sm() as s:
            res = ResourceModel(
                type=resource_type, name=name, tenant_id=tenant_id, owner_id=owner_id,
                resource_metadata=metadata or {}
            )
            s.add(res)
            try:
                await s.commit()
            except IntegrityError:
                await s.rollback()
                raise DuplicateError(f"Resource '{name}' already exists in tenant '{tenant_id}'.")
            await s.refresh(res)
            return res

    async def delete_resource(self, resource_id: UUID) -> None:
        async with self._sm() as s:
            result = await s.execute(delete(ResourceModel).where(ResourceModel.id == resource_id))
            if result.rowcount == 0:
                raise NotFoundError(f"Resource with ID '{resource_id}' not found.")
            await s.commit()

    # --------------- Relationship Management ---------------

    async def assign_permission_to_role(self, role_id: UUID, permission_id: UUID) -> None:
        async with self._sm() as s:
            role = await s.get(RoleModel, role_id, options=[selectinload(RoleModel.permissions)])
            perm = await s.get(PermissionModel, permission_id)
            if not role or not perm:
                raise NotFoundError("Role or permission not found.")

            if perm not in role.permissions:
                role.permissions.append(perm)
                await s.commit()

            res, act = _parse_perm(perm.name)
            obj = RESOURCE_TO_PATTERN.get(res, res)
            dom = role.tenant_id or ""

            # MODIFIED: Direct await on async enforcer methods
            has = self._e.has_policy(str(role_id), dom, obj, act)
            if not has:
                ok = await self._e.add_policy(str(role_id), dom, obj, act)
                if not ok:
                    # Optional: Add rollback logic if enforcer fails
                    raise RuntimeError(f"add_policy failed: sub={role_id}, dom={dom}, obj={obj}, act={act}")

    async def remove_permission_from_role(self, role_id: UUID, permission_id: UUID) -> None:
        async with self._sm() as s:
            role = await s.get(RoleModel, role_id, options=[selectinload(RoleModel.permissions)])
            perm = await s.get(PermissionModel, permission_id)
            if not role or not perm:
                raise NotFoundError("Role or permission not found.")

            if perm in role.permissions:
                role.permissions.remove(perm)
                await s.commit()

            resource, action = _parse_perm(perm.name)
            obj = RESOURCE_TO_PATTERN.get(resource, resource)
            domain = role.tenant_id or ""
            # MODIFIED: Direct await on async enforcer method
            await self._e.remove_policy(str(role_id), domain, obj, action)

    async def assign_role_to_account(self, account_id: UUID, role_id: UUID) -> None:
        async with self._sm() as s:
            acc = await s.get(AccountModel, account_id, options=[selectinload(AccountModel.roles)])
            role = await s.get(RoleModel, role_id)
            if not acc or not role:
                raise NotFoundError("Account or role not found.")

            if role not in acc.roles:
                acc.roles.append(role)
                await s.commit()

            domain = role.tenant_id or ""
            # MODIFIED: Direct await on async enforcer method
            await self._e.add_grouping_policy(str(account_id), str(role_id), domain)

    async def remove_role_from_account(self, account_id: UUID, role_id: UUID) -> None:
        async with self._sm() as s:
            acc = await s.get(AccountModel, account_id, options=[selectinload(AccountModel.roles)])
            role = await s.get(RoleModel, role_id)
            if not acc or not role:
                raise NotFoundError("Account or role not found.")

            if role in acc.roles:
                acc.roles.remove(role)
                await s.commit()

            domain = role.tenant_id or ""
            # MODIFIED: Direct await on async enforcer method
            await self._e.remove_grouping_policy(str(account_id), str(role_id), domain)

    async def assign_role_to_group(self, group_id: UUID, role_id: UUID) -> None:
        async with self._sm() as s:
            grp = await s.get(GroupModel, group_id, options=[selectinload(GroupModel.roles)])
            role = await s.get(RoleModel, role_id)
            if not grp or not role:
                raise NotFoundError("Group or role not found.")

            if role not in grp.roles:
                grp.roles.append(role)
                await s.commit()

            domain = role.tenant_id or ""
            # MODIFIED: Direct await on async enforcer method
            await self._e.add_grouping_policy(str(group_id), str(role_id), domain)

    async def remove_role_from_group(self, group_id: UUID, role_id: UUID) -> None:
        async with self._sm() as s:
            grp = await s.get(GroupModel, group_id, options=[selectinload(GroupModel.roles)])
            role = await s.get(RoleModel, role_id)
            if not grp or not role:
                raise NotFoundError("Group or role not found.")

            if role in grp.roles:
                grp.roles.remove(role)
                await s.commit()

            domain = role.tenant_id or ""
            # MODIFIED: Direct await on async enforcer method
            await self._e.remove_grouping_policy(str(group_id), str(role_id), domain)

    async def assign_group_to_account(self, account_id: UUID, group_id: UUID) -> None:
        async with self._sm() as s:
            acc = await s.get(AccountModel, account_id, options=[selectinload(AccountModel.groups)])
            grp = await s.get(GroupModel, group_id)
            if not acc or not grp:
                raise NotFoundError("Account or group not found.")

            if grp not in acc.groups:
                acc.groups.append(grp)
                await s.commit()

            domain = grp.tenant_id or ""
            # MODIFIED: Direct await on async enforcer method
            await self._e.add_named_grouping_policy("g", str(account_id), str(group_id), domain)

    async def remove_group_from_account(self, account_id: UUID, group_id: UUID) -> None:
        async with self._sm() as s:
            acc = await s.get(AccountModel, account_id, options=[selectinload(AccountModel.groups)])
            grp = await s.get(GroupModel, group_id)
            if not acc or not grp:
                raise NotFoundError("Account or group not found.")

            if grp in acc.groups:
                acc.groups.remove(grp)
                await s.commit()

            domain = grp.tenant_id or ""
            # MODIFIED: Direct await on async enforcer method
            await self._e.remove_named_grouping_policy("g", str(account_id), str(group_id), domain)

    # --------------- Authorization Check ---------------

    async def check_access(
            self, account_id: UUID, resource: str, action: str, tenant_id: Optional[str] = None
    ) -> bool:
        sub, dom, obj, act = str(account_id), tenant_id or "", resource, action
        # MODIFIED: Direct await on async enforcer method
        return self._e.enforce(sub, dom, obj, act)

    # --------------- Listing Methods ---------------

    async def list_permissions(self, name: Optional[str] = None) -> Sequence[PermissionModel]:
        async with self._sm() as s:
            q = select(PermissionModel).order_by(PermissionModel.name)
            if name:
                q = q.where(PermissionModel.name == name)
            return (await s.execute(q)).scalars().all()

    async def list_roles(self, tenant_id: Optional[str] = None, name: Optional[str] = None) -> Sequence[RoleModel]:
        async with self._sm() as s:
            q = select(RoleModel).order_by(RoleModel.name)
            if tenant_id is not None:
                q = q.where(RoleModel.tenant_id == tenant_id)
            if name:
                q = q.where(RoleModel.name == name)
            return (await s.execute(q)).scalars().all()

    async def list_groups(self, tenant_id: Optional[str] = None) -> Sequence[GroupModel]:
        async with self._sm() as s:
            q = select(GroupModel).order_by(GroupModel.name)
            if tenant_id is not None:
                q = q.where(GroupModel.tenant_id == tenant_id)
            return (await s.execute(q)).scalars().all()

    async def list_accounts(self, tenant_id: Optional[str] = None, username: Optional[str] = None) -> Sequence[AccountModel]:
        async with self._sm() as s:
            q = select(AccountModel).order_by(AccountModel.username)
            if tenant_id is not None:
                q = q.where(AccountModel.tenant_id == tenant_id)
            if username:
                q = q.where(AccountModel.username == username)
            return (await s.execute(q)).scalars().all()

    async def list_resources(self, tenant_id: Optional[str] = None) -> Sequence[ResourceModel]:
        async with self._sm() as s:
            q = select(ResourceModel).order_by(ResourceModel.type, ResourceModel.name)
            if tenant_id is not None:
                q = q.where(ResourceModel.tenant_id == tenant_id)
            return (await s.execute(q)).scalars().all()