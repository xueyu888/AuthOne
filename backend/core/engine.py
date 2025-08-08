"""核心访问控制引擎。

该引擎实现了基于角色的访问控制（RBAC），包括用户账户、角色、权限、
用户组以及它们之间的映射关系。支持租户隔离，通过 ``tenant_id``
区分不同租户的权限与角色。所有数据存储于内存中，适用于最小可用
产品（MVP）阶段。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import Permission, Role, Group, Account

__all__ = ["AuthEngine"]


@dataclass(slots=True)
class AuthEngine:
    """内存型访问控制引擎。

    该引擎管理权限、角色、用户组和账户实体，以及它们之间的关系。它
    提供将权限分配给角色、将角色分配给账户或用户组，以及将用户组
    分配给账户的方法，并提供权限检查（enforce）方法。
    """

    _permissions: dict[str, Permission] = field(default_factory=dict)
    _roles: Dict[str, Role] = field(default_factory=dict)
    _groups: Dict[str, Group] = field(default_factory=dict)
    _accounts: Dict[str, Account] = field(default_factory=dict)

    # ------------------------- 实体管理 -----------------------------------
    def add_permission(self, permission: Permission) -> None:
        """注册一个权限。

        :param permission: 权限实例
        :raises ValueError: 当权限 ID 已存在
        """
        if permission.id in self._permissions:
            raise ValueError(f"permission {permission.id} already exists")
        self._permissions[permission.id] = permission

    def add_role(self, role: Role) -> None:
        if role.id in self._roles:
            raise ValueError(f"role {role.id} already exists")
        self._roles[role.id] = role

    def add_group(self, group: Group) -> None:
        if group.id in self._groups:
            raise ValueError(f"group {group.id} already exists")
        self._groups[group.id] = group

    def add_account(self, account: Account) -> None:
        if account.id in self._accounts:
            raise ValueError(f"account {account.id} already exists")
        self._accounts[account.id] = account

    # ------------------------- 关系绑定 -----------------------------------
    def assign_permission_to_role(self, role_id: str, permission_id: str) -> None:
        role = self._roles.get(role_id)
        perm = self._permissions.get(permission_id)
        if not role:
            raise ValueError(f"role {role_id} not found")
        if not perm:
            raise ValueError(f"permission {permission_id} not found")
        role.add_permission(permission_id)

    def assign_role_to_account(self, account_id: str, role_id: str) -> None:
        account = self._accounts.get(account_id)
        role = self._roles.get(role_id)
        if not account:
            raise ValueError(f"account {account_id} not found")
        if not role:
            raise ValueError(f"role {role_id} not found")
        account.add_role(role_id)

    def assign_role_to_group(self, group_id: str, role_id: str) -> None:
        group = self._groups.get(group_id)
        role = self._roles.get(role_id)
        if not group:
            raise ValueError(f"group {group_id} not found")
        if not role:
            raise ValueError(f"role {role_id} not found")
        group.add_role(role_id)

    def assign_group_to_account(self, account_id: str, group_id: str) -> None:
        account = self._accounts.get(account_id)
        group = self._groups.get(group_id)
        if not account:
            raise ValueError(f"account {account_id} not found")
        if not group:
            raise ValueError(f"group {group_id} not found")
        account.add_group(group_id)

    # ------------------------- 权限检查 -----------------------------------
    def enforce(
        self,
        account_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """检查账户是否拥有指定资源操作的权限。

        :param account_id: 账户 ID
        :param resource: 资源名称，如组件或模块
        :param action: 操作名称
        :param tenant_id: 租户 ID，用于强制租户隔离
        :returns: ``True`` 表示允许访问，``False`` 表示拒绝
        """
        account = self._accounts.get(account_id)
        if not account:
            return False

        # 租户隔离：当提供 tenant_id 时，账户必须属于该租户或账户无租户属性
        if tenant_id is not None and account.tenant_id is not None and account.tenant_id != tenant_id:
            return False

        target = f"{resource}:{action}"

        # 1. 检查账户直接分配的角色
        for role_id in account.roles:
            role = self._roles.get(role_id)
            if not role:
                continue
            # 租户检查：角色所属租户必须匹配（或角色为全局）
            if tenant_id is not None and role.tenant_id is not None and role.tenant_id != tenant_id:
                continue
            if self._role_has_permission(role, target):
                return True

        # 2. 检查账户所属用户组继承的角色
        for group_id in account.groups:
            group = self._groups.get(group_id)
            if not group:
                continue
            # 租户检查：用户组所属租户必须匹配
            if tenant_id is not None and group.tenant_id is not None and group.tenant_id != tenant_id:
                continue
            for role_id in group.roles:
                role = self._roles.get(role_id)
                if not role:
                    continue
                if tenant_id is not None and role.tenant_id is not None and role.tenant_id != tenant_id:
                    continue
                if self._role_has_permission(role, target):
                    return True

        return False

    # ------------------------- 私有帮助方法 ---------------------------------
    def _role_has_permission(self, role: Role, target: str) -> bool:
        """判断角色是否包含名称为 ``target`` 的权限。"""
        for perm_id in role.permissions:
            perm = self._permissions.get(perm_id)
            if perm and perm.name == target:
                return True
        return False
