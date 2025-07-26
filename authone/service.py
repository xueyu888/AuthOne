"""服务层封装。

``AuthService`` 封装了 ``AuthEngine`` 的实例，提供创建实体、绑定关系和
权限校验的对外接口。调用方应使用该服务类而非直接操作引擎。
"""

from __future__ import annotations

from typing import Optional

from .models import (
    Permission,
    Role,
    Group,
    Account,
    AccessCheckRequest,
    AccessCheckResponse,
)
from .core import AuthEngine

__all__ = ["AuthService"]


class AuthService:
    """权限管理服务类。"""

    def __init__(self) -> None:
        self._engine = AuthEngine()

    # ------------------------- 创建实体 -------------------------------
    def create_permission(self, name: str, description: str = "") -> Permission:
        """创建并注册一个权限。"""
        perm = Permission.create(name, description)
        self._engine.add_permission(perm)
        return perm

    def create_role(self, tenant_id: Optional[str], name: str, description: str = "") -> Role:
        """创建并注册一个角色。"""
        role = Role.create(tenant_id, name, description)
        self._engine.add_role(role)
        return role

    def create_group(self, tenant_id: Optional[str], name: str, description: str = "") -> Group:
        """创建并注册一个用户组。"""
        group = Group.create(tenant_id, name, description)
        self._engine.add_group(group)
        return group

    def create_account(self, username: str, email: str, tenant_id: Optional[str] = None) -> Account:
        """创建并注册一个账户。"""
        account = Account.create(username, email, tenant_id)
        self._engine.add_account(account)
        return account

    # ------------------------- 关系绑定 -------------------------------
    def assign_permission_to_role(self, role_id: str, permission_id: str) -> None:
        self._engine.assign_permission_to_role(role_id, permission_id)

    def assign_role_to_account(self, account_id: str, role_id: str) -> None:
        self._engine.assign_role_to_account(account_id, role_id)

    def assign_role_to_group(self, group_id: str, role_id: str) -> None:
        self._engine.assign_role_to_group(group_id, role_id)

    def assign_group_to_account(self, account_id: str, group_id: str) -> None:
        self._engine.assign_group_to_account(account_id, group_id)

    # ------------------------- 权限校验 -------------------------------
    def check_access(self, req: AccessCheckRequest) -> AccessCheckResponse:
        """根据访问请求判断是否允许。

        :param req: 访问请求模型
        :returns: 访问结果模型
        """
        allowed = self._engine.enforce(
            account_id=req.account_id,
            resource=req.resource,
            action=req.action,
            tenant_id=req.tenant_id,
        )
        return AccessCheckResponse(
            allowed=allowed,
            reason=None if allowed else "Access denied",
        )
