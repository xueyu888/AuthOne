"""SQLAlchemy 仓库实现。

该模块根据 ``storage.interface`` 中定义的协议实现仓库类，使用
SQLAlchemy ORM 进行数据持久化。由于篇幅限制，这些实现主要展示
方法签名和整体结构，具体 SQLAlchemy 模型和字段映射应根据实际
数据库结构补充。
"""

from __future__ import annotations

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from ..config import Settings
from ..db import get_session
from ..models import Account, Group, Permission, Resource, Role
from .interface import (
    AccountRepository,
    GroupRepository,
    PermissionRepository,
    ResourceRepository,
    RoleRepository,
)

__all__ = [
    "SQLAlchemyPermissionRepository",
    "SQLAlchemyRoleRepository",
    "SQLAlchemyGroupRepository",
    "SQLAlchemyAccountRepository",
    "SQLAlchemyResourceRepository",
]

logger = logging.getLogger(__name__)


class _SQLAlchemyBaseRepository:
    """基类，注入会话。"""

    def __init__(self, session: Session) -> None:
        self._session = session


class SQLAlchemyPermissionRepository(_SQLAlchemyBaseRepository, PermissionRepository):
    def add(self, permission: Permission) -> None:
        # TODO: 将 Permission 映射到 ORM Model 并保存
        self._session.add(permission)  # type: ignore[arg-type]
        self._session.commit()

    def get(self, permission_id: str) -> Optional[Permission]:
        # TODO: 根据 ID 查询 ORM 模型并转换为领域对象
        raise NotImplementedError

    def list(self, tenant_id: Optional[str] = None) -> List[Permission]:
        # TODO: 查询所有权限
        raise NotImplementedError


class SQLAlchemyRoleRepository(_SQLAlchemyBaseRepository, RoleRepository):
    def add(self, role: Role) -> None:
        self._session.add(role)  # type: ignore[arg-type]
        self._session.commit()

    def get(self, role_id: str) -> Optional[Role]:
        raise NotImplementedError

    def list(self, tenant_id: Optional[str] = None) -> List[Role]:
        raise NotImplementedError

    def assign_permission(self, role_id: str, permission_id: str) -> None:
        # TODO: 插入关联表并提交
        raise NotImplementedError


class SQLAlchemyGroupRepository(_SQLAlchemyBaseRepository, GroupRepository):
    def add(self, group: Group) -> None:
        self._session.add(group)  # type: ignore[arg-type]
        self._session.commit()

    def get(self, group_id: str) -> Optional[Group]:
        raise NotImplementedError

    def list(self, tenant_id: Optional[str] = None) -> List[Group]:
        raise NotImplementedError

    def assign_role(self, group_id: str, role_id: str) -> None:
        raise NotImplementedError


class SQLAlchemyAccountRepository(_SQLAlchemyBaseRepository, AccountRepository):
    def add(self, account: Account) -> None:
        self._session.add(account)  # type: ignore[arg-type]
        self._session.commit()

    def get(self, account_id: str) -> Optional[Account]:
        raise NotImplementedError

    def list(self, tenant_id: Optional[str] = None) -> List[Account]:
        raise NotImplementedError

    def assign_role(self, account_id: str, role_id: str) -> None:
        raise NotImplementedError

    def assign_group(self, account_id: str, group_id: str) -> None:
        raise NotImplementedError


class SQLAlchemyResourceRepository(_SQLAlchemyBaseRepository, ResourceRepository):
    def add(self, resource: Resource) -> None:
        self._session.add(resource)  # type: ignore[arg-type]
        self._session.commit()

    def get(self, resource_id: str) -> Optional[Resource]:
        raise NotImplementedError

    def list(self, tenant_id: Optional[str] = None) -> List[Resource]:
        raise NotImplementedError
