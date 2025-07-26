"""资源实体定义。

资源代表 AI 平台中的前端组件、后端模块、数据集或模型等受控对象。
通过 ``Resource`` 可以对不同类型的资源进行统一管理，并在权限检查
中提供必要的信息（如所属租户、拥有者）。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

__all__ = ["Resource"]


@dataclass(slots=True)
class Resource:
    """资源数据类。"""

    _id: str
    _type: str
    _name: str
    _tenant_id: Optional[str]
    _owner_id: Optional[str]
    _metadata: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        resource_type: str,
        name: str,
        tenant_id: Optional[str],
        owner_id: Optional[str],
        metadata: Optional[Dict[str, str]] = None,
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
            _metadata=metadata or {},
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def type(self) -> str:
        return self._type

    @property
    def name(self) -> str:
        return self._name

    @property
    def tenant_id(self) -> Optional[str]:
        return self._tenant_id

    @property
    def owner_id(self) -> Optional[str]:
        return self._owner_id

    @property
    def metadata(self) -> Dict[str, str]:
        return dict(self._metadata)
