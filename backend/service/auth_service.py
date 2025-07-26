"""业务服务层。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import asyncio

from ..config import Settings
from ..core.casbin_adapter import CasbinEngine
from ..models import (
    Account,
    Group,
    Permission,
    Resource,
    Role,
    AccessCheckRequest,
    AccessCheckResponse,
)
from ..db import get_session
from ..storage.sqlalchemy_repository import (
    SQLAlchemyAccountRepository,
    SQLAlchemyGroupRepository,
    SQLAlchemyPermissionRepository,
    SQLAlchemyResourceRepository,
    SQLAlchemyRoleRepository,
    AuditLogRepository,
)

__all__ = ["AuthService"]


@dataclass(slots=True)
class AuthService:
    """权限管理服务。

    使用 ``create`` 类方法创建实例，注入配置。服务内部持有仓库对象、
    Casbin 引擎和审计日志仓库，对外暴露实体管理和权限校验接口。
    """

    _settings: Settings
    _perm_repo: SQLAlchemyPermissionRepository
    _role_repo: SQLAlchemyRoleRepository
    _group_repo: SQLAlchemyGroupRepository
    _account_repo: SQLAlchemyAccountRepository
    _resource_repo: SQLAlchemyResourceRepository
    _audit_repo: AuditLogRepository
    _casbin: CasbinEngine

    @classmethod
    async def create(cls, settings: Settings) -> "AuthService":
        """异步创建 ``AuthService`` 实例并初始化仓库和 Casbin 引擎。

        该方法负责构造所有仓库实例，并确保它们持有同一个异步会话。由于
        ``AsyncSession`` 需要绑定到事件循环，此方法必须使用 ``await`` 调用。
        """
        session = get_session(settings)
        perm_repo = SQLAlchemyPermissionRepository(session)
        role_repo = SQLAlchemyRoleRepository(session)
        group_repo = SQLAlchemyGroupRepository(session)
        account_repo = SQLAlchemyAccountRepository(session)
        resource_repo = SQLAlchemyResourceRepository(session)
        audit_repo = AuditLogRepository(session)
        casbin_engine = CasbinEngine(settings)
        return cls(
            _settings=settings,
            _perm_repo=perm_repo,
            _role_repo=role_repo,
            _group_repo=group_repo,
            _account_repo=account_repo,
            _resource_repo=resource_repo,
            _audit_repo=audit_repo,
            _casbin=casbin_engine,
        )

    # ------------------- 实体创建 -------------------
    async def create_permission(self, name: str, description: str = "") -> Permission:
        perm = Permission.create(name, description)
        await self._perm_repo.add(perm)
        return perm

    async def create_role(self, tenant_id: Optional[str], name: str, description: str = "") -> Role:
        role = Role.create(tenant_id, name, description)
        await self._role_repo.add(role)
        return role

    async def create_group(self, tenant_id: Optional[str], name: str, description: str = "") -> Group:
        group = Group.create(tenant_id, name, description)
        await self._group_repo.add(group)
        return group

    async def create_account(self, username: str, email: str, tenant_id: Optional[str] = None) -> Account:
        acc = Account.create(username, email, tenant_id)
        await self._account_repo.add(acc)
        return acc

    async def create_resource(
        self,
        resource_type: str,
        name: str,
        tenant_id: Optional[str],
        owner_id: Optional[str],
        metadata: Optional[dict] = None,
    ) -> Resource:
        res = Resource.create(resource_type, name, tenant_id, owner_id, metadata)
        await self._resource_repo.add(res)
        return res

    # ------------------- 实体查询 -------------------
    async def list_permissions(self, tenant_id: Optional[str] = None) -> list[Permission]:
        return await self._perm_repo.list(tenant_id)

    async def list_roles(self, tenant_id: Optional[str] = None) -> list[Role]:
        return await self._role_repo.list(tenant_id)

    async def list_groups(self, tenant_id: Optional[str] = None) -> list[Group]:
        return await self._group_repo.list(tenant_id)

    async def list_accounts(self, tenant_id: Optional[str] = None) -> list[Account]:
        return await self._account_repo.list(tenant_id)

    async def list_resources(self, tenant_id: Optional[str] = None) -> list[Resource]:
        return await self._resource_repo.list(tenant_id)

    # ------------------- 关系绑定 -------------------
    async def assign_permission_to_role(self, role_id: str, permission_id: str) -> None:
        # 更新数据库中的关系
        await self._role_repo.assign_permission(role_id, permission_id)
        # 读取角色和权限信息
        role = await self._role_repo.get(role_id)
        perm = await self._perm_repo.get(permission_id)
        if not role or not perm:
            raise ValueError("role or permission not found")
        resource, action = perm.parse()
        # 将策略写入 Casbin（在后台线程执行同步调用）
        await asyncio.to_thread(
            self._casbin.add_permission_for_user,
            role.id,
            role.tenant_id,
            resource,
            action,
        )

    async def assign_role_to_account(self, account_id: str, role_id: str) -> None:
        acc = await self._account_repo.get(account_id)
        role = await self._role_repo.get(role_id)
        if not acc or not role:
            raise ValueError("account or role not found")
        await self._account_repo.assign_role(account_id, role_id)
        await asyncio.to_thread(
            self._casbin.add_role_for_account,
            acc.id,
            acc.tenant_id,
            role.id,
        )

    async def assign_role_to_group(self, group_id: str, role_id: str) -> None:
        group = await self._group_repo.get(group_id)
        role = await self._role_repo.get(role_id)
        if not group or not role:
            raise ValueError("group or role not found")
        await self._group_repo.assign_role(group_id, role_id)
        await asyncio.to_thread(
            self._casbin.add_role_for_group,
            group.id,
            group.tenant_id,
            role.id,
        )

    async def assign_group_to_account(self, account_id: str, group_id: str) -> None:
        acc = await self._account_repo.get(account_id)
        group = await self._group_repo.get(group_id)
        if not acc or not group:
            raise ValueError("account or group not found")
        await self._account_repo.assign_group(account_id, group_id)
        await asyncio.to_thread(
            self._casbin.add_group_for_account,
            acc.id,
            acc.tenant_id,
            group.id,
        )

    # ------------------- 权限校验 -------------------
    async def check_access(self, req: AccessCheckRequest) -> AccessCheckResponse:
        """检查用户是否对资源拥有访问权限，并记录审计日志。"""
        allowed = await asyncio.to_thread(
            self._casbin.enforce,
            req.account_id,
            req.tenant_id,
            req.resource,
            req.action,
        )
        # 记录审计日志
        await self._audit_repo.record(
            account_id=req.account_id,
            action=req.action,
            resource=req.resource,
            result=allowed,
            message="allowed" if allowed else "denied",
        )
        return AccessCheckResponse(allowed=allowed, reason=None if allowed else "Access denied")
