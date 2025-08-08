"""账户实体定义。

账户（Account）代表一个登录用户，可以直接绑定角色或加入用户组。支持
租户隔离，一个账户只能属于一个租户（或无租户，即平台管理员）。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

__all__ = ["Account"]


@dataclass(slots=True)
class Account:
    _id: str
    _username: str
    _email: str
    _tenant_id: Optional[str]
    _roles: list[str]
    _groups: list[str]

    @classmethod
    def create(cls, username: str, email: str, tenant_id: Optional[str] = None) -> "Account":
        if not username:
            raise ValueError("username must not be empty")
        if not email or "@" not in email:
            raise ValueError("invalid email")
        return cls(
            _id = str(uuid.uuid4()),
            _username = username,
            _email = email,
            _tenant_id = tenant_id,
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def username(self) -> str:
        return self._username

    @property
    def email(self) -> str:
        return self._email

    @property
    def tenant_id(self) -> Optional[str]:
        return self._tenant_id

    @property
    def roles(self) -> list[str]:
        return list(self._roles)

    @property
    def groups(self) -> list[str]:
        return list(self._groups)

    def add_role(self, role_id: str) -> None:
        if role_id not in self._roles:
            self._roles.append(role_id)

    def remove_role(self, role_id: str) -> None:
        if role_id in self._roles:
            self._roles.remove(role_id)

    def add_group(self, group_id: str) -> None:
        if group_id not in self._groups:
            self._groups.append(group_id)

    def remove_group(self, group_id: str) -> None:
        if group_id in self._groups:
            self._groups.remove(group_id)
