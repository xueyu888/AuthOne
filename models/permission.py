"""权限实体定义。

``Permission`` 用于表示系统中的访问许可，它采用 ``resource:action``
形式标识具体资源与操作，例如 ``app:create`` 或 ``dataset:view``。该
模块提供了权限实体的创建、解析和属性访问功能。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Tuple

__all__ = ["Permission"]


@dataclass(slots=True)
class Permission:
    """权限数据类。

    使用 ``@dataclass`` 定义不可变字段，通过 ``create`` 方法进行实例化并
    进行基础校验。所有字段私有，并通过属性公开，只读访问。
    """

    _id: str
    _name: str
    _description: str

    @classmethod
    def create(cls, name: str, description: str) -> "Permission":
        """创建一个权限。

        :param name: 权限名称，必须包含 ``:`` 分隔资源与动作
        :param description: 描述
        :returns: 权限对象
        :raises ValueError: 当 name 为空或格式不正确
        """
        if not name:
            raise ValueError("permission name must not be empty")
        if ":" not in name:
            raise ValueError("permission name must be in format resource:action")
        return cls(
            _id=str(uuid.uuid4()),
            _name=name,
            _description=description or "",
        )

    @property
    def id(self) -> str:
        """权限的唯一标识符。"""
        return self._id

    @property
    def name(self) -> str:
        """权限的机器可读名称。"""
        return self._name

    @property
    def description(self) -> str:
        """权限的人类可读描述。"""
        return self._description

    def parse(self) -> Tuple[str, str]:
        """解析权限名称为 ``(resource, action)`` 元组。"""
        resource, action = self._name.split(":", 1)
        return resource, action
