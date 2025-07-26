"""高级权限管理服务。

该模块实现 ``AuthService``，负责协调模型创建、持久化和策略更新。它
同时操作存储层仓库和 Casbin 引擎，实现用户、角色、权限、用户组及
资源的管理与权限校验。对外暴露方法遵循清晰的输入输出契约，确保
调用者无需关心底层实现。

示例::

    from AuthOne.config import Settings
    from AuthOne.service import AuthService
    settings = Settings(db_url="postgresql://user:pass@host:5432/db")
    svc = AuthService(settings)
    user = svc.create_account("alice", "alice@example.com", "t1")
    # ...
    resp = svc.check_access(AccessCheckRequest(...))
"""

from __future__ import annotations

import logging
from typing import Optional

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
from ..storage.interface import (
    AccountRepository,
    GroupRepository,
    PermissionRepository,
    ResourceRepository,
    RoleRepository,
)
from ..storage.postgres import (
    PostgresDatabase,
    PostgresAccountRepository,
    PostgresGroupRepository,
    PostgresPermissionRepository,
    PostgresResourceRepository,
    PostgresRoleRepository,
)

__all__ = ["AuthService"]

logger = logging.getLogger(__name__)


class AuthService:
    """权限管理服务。"""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        # 初始化数据库连接和仓库实现
        db = PostgresDatabase(settings)
        self._perm_repo: PermissionRepository = PostgresPermissionRepository(db)
        self._role_repo: RoleRepository = PostgresRoleRepository(db)
        self._group_repo: GroupRepository = PostgresGroupRepository(db)
        self._account_repo: AccountRepository = PostgresAccountRepository(db)
        self._resource_repo: ResourceRepository = PostgresResourceRepository(db)
        # 初始化 Casbin 引擎
        self._casbin = CasbinEngine(settings)

    # --------------------------- 实体创建 -----------------------------
    def create_permission(self, name: str, description: str = "") -> Permission:
        perm = Permission.create(name, description)
        self._perm_repo.add(perm)
        return perm

    def create_role(self, tenant_id: Optional[str], name: str, description: str = "") -> Role:
        role = Role.create(tenant_id, name, description)
        self._role_repo.add(role)
        return role

    def create_group(self, tenant_id: Optional[str], name: str, description: str = "") -> Group:
        group = Group.create(tenant_id, name, description)
        self._group_repo.add(group)
        return group

    def create_account(self, username: str, email: str, tenant_id: Optional[str] = None) -> Account:
        acc = Account.create(username, email, tenant_id)
        self._account_repo.add(acc)
        return acc

    def create_resource(
        self,
        resource_type: str,
        name: str,
        tenant_id: Optional[str],
        owner_id: Optional[str],
        metadata: Optional[dict] = None,
    ) -> Resource:
        res = Resource.create(resource_type, name, tenant_id, owner_id, metadata)
        self._resource_repo.add(res)
        return res

    # --------------------------- 权限与角色分配 -----------------------
    def assign_permission_to_role(self, role_id: str, permission_id: str) -> None:
        # 更新业务表
        self._role_repo.assign_permission(role_id, permission_id)
        # 获取相关对象以更新 Casbin
        role = self._role_repo.get(role_id)
        perm = self._perm_repo.get(permission_id)
        if not role or not perm:
            raise ValueError("role or permission not found")
        resource, action = perm.parse()
        self._casbin.add_permission_for_user(role.id, role.tenant_id, resource, action)

    def assign_role_to_account(self, account_id: str, role_id: str) -> None:
        acc = self._account_repo.get(account_id)
        role = self._role_repo.get(role_id)
        if not acc or not role:
            raise ValueError("account or role not found")
        # 更新业务表
        self._account_repo.assign_role(account_id, role_id)
        # 更新 Casbin：account 与 role 的 g 关系
        self._casbin.add_role_for_account(acc.id, acc.tenant_id, role.id)

    def assign_role_to_group(self, group_id: str, role_id: str) -> None:
        group = self._group_repo.get(group_id)
        role = self._role_repo.get(role_id)
        if not group or not role:
            raise ValueError("group or role not found")
        self._group_repo.assign_role(group_id, role_id)
        # g 关系：组名作为 user，角色作为 role
        self._casbin.add_role_for_group(group.id, group.tenant_id, role.id)

    def assign_group_to_account(self, account_id: str, group_id: str) -> None:
        acc = self._account_repo.get(account_id)
        group = self._group_repo.get(group_id)
        if not acc or not group:
            raise ValueError("account or group not found")
        self._account_repo.assign_group(account_id, group_id)
        self._casbin.add_group_for_account(acc.id, acc.tenant_id, group.id)

    # --------------------------- 权限校验 -----------------------------
    def check_access(self, req: AccessCheckRequest) -> AccessCheckResponse:
        allowed = self._casbin.enforce(
            account=req.account_id,
            tenant_id=req.tenant_id,
            resource=req.resource,
            action=req.action,
        )
        return AccessCheckResponse(allowed=allowed, reason=None if allowed else "Access denied")
