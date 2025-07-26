"""存储接口定义。

为了支持不同的数据库后端（如 PostgreSQL、MySQL 等），这里定义了
一系列 repository 协议（Protocol），描述各实体的持久化操作。具体
实现可放在 ``storage/postgres.py`` 等文件中。调用方应依赖接口而非
具体实现，以便在运行时灵活替换数据库。
"""

from __future__ import annotations

from typing import List, Optional, Protocol, runtime_checkable

from ..models import Account, Group, Permission, Resource, Role

__all__ = [
    "PermissionRepository",
    "RoleRepository",
    "GroupRepository",
    "AccountRepository",
    "ResourceRepository",
]


@runtime_checkable
class PermissionRepository(Protocol):
    """权限仓库接口。"""

    def add(self, permission: Permission) -> None:
        """保存权限。"""

    def get(self, permission_id: str) -> Optional[Permission]:
        """根据 ID 获取权限。"""

    def list(self, tenant_id: Optional[str] = None) -> List[Permission]:
        """列出指定租户的权限，``tenant_id`` 为 None 时返回所有权限。"""


@runtime_checkable
class RoleRepository(Protocol):
    """角色仓库接口。"""

    def add(self, role: Role) -> None:
        ...

    def get(self, role_id: str) -> Optional[Role]:
        ...

    def list(self, tenant_id: Optional[str] = None) -> List[Role]:
        ...

    def assign_permission(self, role_id: str, permission_id: str) -> None:
        """将权限分配给角色。"""


@runtime_checkable
class GroupRepository(Protocol):
    """用户组仓库接口。"""

    def add(self, group: Group) -> None:
        ...

    def get(self, group_id: str) -> Optional[Group]:
        ...

    def list(self, tenant_id: Optional[str] = None) -> List[Group]:
        ...

    def assign_role(self, group_id: str, role_id: str) -> None:
        ...


@runtime_checkable
class AccountRepository(Protocol):
    """账户仓库接口。"""

    def add(self, account: Account) -> None:
        ...

    def get(self, account_id: str) -> Optional[Account]:
        ...

    def list(self, tenant_id: Optional[str] = None) -> List[Account]:
        ...

    def assign_role(self, account_id: str, role_id: str) -> None:
        ...

    def assign_group(self, account_id: str, group_id: str) -> None:
        ...


@runtime_checkable
class ResourceRepository(Protocol):
    """资源仓库接口。"""

    def add(self, resource: Resource) -> None:
        ...

    def get(self, resource_id: str) -> Optional[Resource]:
        ...

    def list(self, tenant_id: Optional[str] = None) -> List[Resource]:
        ...
