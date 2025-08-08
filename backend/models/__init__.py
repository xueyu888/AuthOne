"""模型子包。

此包包含应用域内的实体类，包括 ``Permission``、``Role``、``Group``、
``Account``、``Resource`` 以及若干用于接口交互的 Pydantic 模型。

使用 ``from AuthOne.models import Permission`` 导入实体类。
"""
# backend/models/__init__.py

from __future__ import annotations

from .permission import Permission
from .role import Role
from .group import Group
from .account import Account
from .resource import Resource
from .schemas import AccessCheckRequest, AccessCheckResponse

__all__: list[str] = [
    "Permission",
    "Role",
    "Group",
    "Account",
    "Resource",
    "AccessCheckRequest",
    "AccessCheckResponse",
]
