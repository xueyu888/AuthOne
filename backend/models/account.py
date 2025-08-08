from __future__ import annotations
import uuid
from dataclasses import dataclass, field

__all__ = ["Account"]

@dataclass(slots=True)
class Account:
    _id: str
    _username: str
    _email: str
    _tenant_id: str | None
    _roles: list[str] = field(default_factory=list)      # type: ignore 
    _groups: list[str] = field(default_factory=list)     # type: ignore 默认空列表

    @classmethod
    def create(cls, username: str, email: str, tenant_id: str | None = None) -> "Account":
        if not username:
            raise ValueError("username must not be empty")
        if not email or "@" not in email:
            raise ValueError("invalid email")
        return cls(
            _id=str(uuid.uuid4()),
            _username=username,
            _email=email,
            _tenant_id=tenant_id,
        )

    @property
    def id(self) -> str: return self._id
    @property
    def username(self) -> str: return self._username
    @property
    def email(self) -> str: return self._email
    @property
    def tenant_id(self) -> str | None: return self._tenant_id
    @property
    def roles(self) -> list[str]: return list(self._roles)
    @property
    def groups(self) -> list[str]: return list(self._groups)

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
