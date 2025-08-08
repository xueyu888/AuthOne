from __future__ import annotations
import uuid
from dataclasses import dataclass, field

__all__ = ["Resource"]

@dataclass(slots=True)
class Resource:
    _id: str
    _type: str
    _name: str
    _tenant_id: str | None
    _owner_id: str | None
    _resource_metadata: dict[str, str] = field(default_factory=dict) # type: ignore

    @classmethod
    def create(
        cls,
        resource_type: str,
        name: str,
        tenant_id: str | None,
        owner_id: str | None,
        resource_metadata: dict[str, str] | None = None,
    ) -> "Resource":
        if not resource_type:
            raise ValueError("resource type must not be empty")
        if not name:
            raise ValueError("resource name must not be empty")
        return cls(
            _id=str(uuid.uuid4()),
            _type=resource_type,
            _name=name,
            _tenant_id=tenant_id,
            _owner_id=owner_id,
            _resource_metadata=resource_metadata or {},
        )

    @property
    def id(self) -> str: return self._id
    @property
    def type(self) -> str: return self._type
    @property
    def name(self) -> str: return self._name
    @property
    def tenant_id(self) -> str | None: return self._tenant_id
    @property
    def owner_id(self) -> str | None: return self._owner_id
    @property
    def resource_metadata(self) -> dict[str, str]:  # 与仓库/ORM 的 resource_metadata 对齐
        return dict(self._resource_metadata)
