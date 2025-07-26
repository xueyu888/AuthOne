"""角色实体定义。

角色用于汇聚一组权限，并可以被多个账户或用户组绑定。支持租户隔离，
一个角色只能属于一个租户（也可以是全局角色，tenant_id 为 None）。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Optional

__all__ = ["Role"]


@dataclass(slots=True)
class Role:
    """角色数据类。"""

    _id: str
    _tenant_id: Optional[str]
    _name: str
    _description: str
    _permissions: List[str] = field(default_factory=list)

    @classmethod
    def create(cls, tenant_id: Optional[str], name: str, description: str) -> "Role":
        if not name:
            raise ValueError("role name must not be empty")
        return cls(
            _id=str(uuid.uuid4()),
            _tenant_id=tenant_id,
            _name=name,
            _description=description or "",
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def tenant_id(self) -> Optional[str]:
        return self._tenant_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def permissions(self) -> List[str]:
        return list(self._permissions)

    def add_permission(self, permission_id: str) -> None:
        if permission_id not in self._permissions:
            self._permissions.append(permission_id)

    def remove_permission(self, permission_id: str) -> None:
        if permission_id in self._permissions:
            self._permissions.remove(permission_id)
