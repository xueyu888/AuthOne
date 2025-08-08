from __future__ import annotations
from dataclasses import dataclass
import asyncio
from typing import List

from ..db import get_session, init_engine
from ..models import Account, Group, Permission, Resource, Role, AccessCheckRequest, AccessCheckResponse
from ..storage.sqlalchemy_repository import (
    SQLAlchemyAccountRepository, SQLAlchemyGroupRepository, SQLAlchemyPermissionRepository,
    SQLAlchemyResourceRepository, SQLAlchemyRoleRepository, AuditLogRepository
)
from ..core.casbin_adapter import CasbinEngine

__all__ = ["AuthService"]

@dataclass(slots=True)
class AuthService:
    _perm_repo: SQLAlchemyPermissionRepository
    _role_repo: SQLAlchemyRoleRepository
    _group_repo: SQLAlchemyGroupRepository
    _account_repo: SQLAlchemyAccountRepository
    _resource_repo: SQLAlchemyResourceRepository
    _audit_repo: AuditLogRepository
    _casbin: CasbinEngine

    @classmethod
    async def create(cls, casbin: CasbinEngine) -> "AuthService":
        session = get_session()
        return cls(
            _perm_repo=SQLAlchemyPermissionRepository(session),
            _role_repo=SQLAlchemyRoleRepository(session),
            _group_repo=SQLAlchemyGroupRepository(session),
            _account_repo=SQLAlchemyAccountRepository(session),
            _resource_repo=SQLAlchemyResourceRepository(session),
            _audit_repo=AuditLogRepository(session),
            _casbin=casbin,
        )

    @staticmethod
    def _tenant_compatible(a: str | None, b: str | None) -> bool:
        return a is None or b is None or a == b

    # ---------- 创建 ----------
    async def create_permission(self, name: str, description: str = "") -> Permission:
        perm = Permission.create(name, description)
        await self._perm_repo.add(perm)
        return perm

    async def create_role(self, tenant_id: str | None, name: str, description: str = "") -> Role:
        role = Role.create(tenant_id, name, description)
        await self._role_repo.add(role)
        return role

    async def create_group(self, tenant_id: str | None, name: str, description: str = "") -> Group:
        grp = Group.create(tenant_id, name, description)
        await self._group_repo.add(grp)
        return grp

    async def create_account(self, username: str, email: str, tenant_id: str | None = None) -> Account:
        acc = Account.create(username, email, tenant_id)
        await self._account_repo.add(acc)
        return acc

    async def create_resource(self, resource_type: str, name: str, tenant_id: str | None, owner_id: str | None, metadata: dict | None = None) -> Resource:
        res = Resource.create(resource_type, name, tenant_id, owner_id, metadata or {})
        await self._resource_repo.add(res)
        return res

    # ---------- 查询 ----------
    async def list_permissions(self) -> List[Permission]:
        return await self._perm_repo.list()

    async def list_roles(self, tenant_id: str | None = None) -> List[Role]:
        return await self._role_repo.list(tenant_id)

    async def list_groups(self, tenant_id: str | None = None) -> List[Group]:
        return await self._group_repo.list(tenant_id)

    async def list_accounts(self, tenant_id: str | None = None) -> List[Account]:
        return await self._account_repo.list(tenant_id)

    async def list_resources(self, tenant_id: str | None = None) -> List[Resource]:
        return await self._resource_repo.list(tenant_id)

    # ---------- 绑定 ----------
    async def assign_permission_to_role(self, role_id: str, permission_id: str) -> None:
        role = await self._role_repo.get(role_id)
        perm = await self._perm_repo.get(permission_id)
        if not role or not perm:
            raise ValueError("role or permission not found")
        await self._role_repo.assign_permission(role.id, perm.id)
        res, act = perm.parse()
        await asyncio.to_thread(self._casbin.add_permission_for_user, role.id, role.tenant_id, res, act)

    async def assign_role_to_account(self, account_id: str, role_id: str) -> None:
        acc = await self._account_repo.get(account_id)
        role = await self._role_repo.get(role_id)
        if not acc or not role:
            raise ValueError("account or role not found")
        # 改：跨租户分配不阻止——只审计，最终由 Casbin 按 domain 拒绝访问
        if not self._tenant_compatible(acc.tenant_id, role.tenant_id):
            await self._audit_repo.record(account_id=acc.id, action="assign_role", resource=role.id, result=False, message="tenant mismatch (soft)")
        await self._account_repo.assign_role(account_id, role_id)
        await asyncio.to_thread(self._casbin.add_role_for_account, acc.id, acc.tenant_id, role.id)

    async def assign_role_to_group(self, group_id: str, role_id: str) -> None:
        grp = await self._group_repo.get(group_id)
        role = await self._role_repo.get(role_id)
        if not grp or not role:
            raise ValueError("group or role not found")
        if not self._tenant_compatible(grp.tenant_id, role.tenant_id):
            await self._audit_repo.record(account_id="system", action="assign_role_to_group", resource=role.id, result=False, message="tenant mismatch (soft)")
        await self._group_repo.assign_role(group_id, role_id)
        await asyncio.to_thread(self._casbin.add_role_for_group, grp.id, grp.tenant_id, role.id)

    async def assign_group_to_account(self, account_id: str, group_id: str) -> None:
        acc = await self._account_repo.get(account_id)
        grp = await self._group_repo.get(group_id)
        if not acc or not grp:
            raise ValueError("account or group not found")
        if not self._tenant_compatible(acc.tenant_id, grp.tenant_id):
            await self._audit_repo.record(account_id=acc.id, action="assign_group", resource=grp.id, result=False, message="tenant mismatch (soft)")
        await self._account_repo.assign_group(account_id, group_id)
        await asyncio.to_thread(self._casbin.add_group_for_account, acc.id, acc.tenant_id, grp.id)

    # ---------- 解绑 ----------
    async def remove_permission_from_role(self, role_id: str, permission_id: str) -> None:
        role = await self._role_repo.get(role_id)
        perm = await self._perm_repo.get(permission_id)
        if not role or not perm:
            raise ValueError("role or permission not found")
        await self._role_repo.remove_permission(role_id, permission_id)
        res, act = perm.parse()
        await asyncio.to_thread(self._casbin.remove_permission_from_user, role.id, role.tenant_id, res, act)

    async def remove_role_from_account(self, account_id: str, role_id: str) -> None:
        acc = await self._account_repo.get(account_id)
        role = await self._role_repo.get(role_id)
        if not acc or not role:
            raise ValueError("account or role not found")
        await self._account_repo.remove_role(account_id, role_id)
        await asyncio.to_thread(self._casbin.remove_role_for_account, acc.id, acc.tenant_id, role.id)

    async def remove_role_from_group(self, group_id: str, role_id: str) -> None:
        grp = await self._group_repo.get(group_id)
        role = await self._role_repo.get(role_id)
        if not grp or not role:
            raise ValueError("group or role not found")
        await self._group_repo.remove_role(group_id, role_id)
        await asyncio.to_thread(self._casbin.remove_role_for_group, grp.id, grp.tenant_id, role.id)

    async def remove_group_from_account(self, account_id: str, group_id: str) -> None:
        acc = await self._account_repo.get(account_id)
        grp = await self._group_repo.get(group_id)
        if not acc or not grp:
            raise ValueError("account or group not found")
        await self._account_repo.remove_group(account_id, group_id)
        await asyncio.to_thread(self._casbin.remove_group_for_account, acc.id, acc.tenant_id, grp.id)

    # ---------- 删除 ----------
    async def delete_permission(self, permission_id: str) -> bool:
        return await self._perm_repo.delete(permission_id)

    async def delete_role(self, role_id: str) -> bool:
        role = await self._role_repo.get(role_id)
        if not role:
            return False
        ok = await self._role_repo.delete(role_id)
        await asyncio.to_thread(self._casbin.remove_filtered_policies_for_subject, role.id)
        return ok

    async def delete_group(self, group_id: str) -> bool:
        grp = await self._group_repo.get(group_id)
        if not grp:
            return False
        ok = await self._group_repo.delete(group_id)
        await asyncio.to_thread(self._casbin.remove_filtered_policies_for_subject, grp.id)
        return ok

    async def delete_account(self, account_id: str) -> bool:
        acc = await self._account_repo.get(account_id)
        if not acc:
            return False
        ok = await self._account_repo.delete(account_id)
        await asyncio.to_thread(self._casbin.remove_filtered_policies_for_subject, acc.id)
        return ok

    async def delete_resource(self, resource_id: str) -> bool:
        return await self._resource_repo.delete(resource_id)

    # ---------- 鉴权 ----------
    async def check_access(self, req: AccessCheckRequest) -> AccessCheckResponse:
        allowed = await asyncio.to_thread(self._casbin.enforce, req.account_id, req.tenant_id, req.resource, req.action)
        await self._audit_repo.record(account_id=req.account_id, action=req.action, resource=req.resource, result=allowed, message="allowed" if allowed else "denied")
        return AccessCheckResponse(allowed=allowed, reason=None if allowed else "Access denied")
