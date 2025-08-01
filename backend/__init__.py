"""AuthOne 顶层命名空间。

该模块负责对外重新导出核心的接口和类型，使调用方只需
``import AuthOne`` 或 ``from AuthOne import AuthService`` 即可。

公开的符号通过 __all__ 控制，其余均视为内部实现细节。
"""

from __future__ import annotations

from ._version import __version__
# 从模型子包重新导入公开实体
from .models import (
    Permission,
    Role,
    Group,
    Account,
    Resource,
    AccessCheckRequest,
    AccessCheckResponse,
)
from .config import Settings
from .service import AuthService

__all__: list[str] = [
    "__version__",
    "Permission",
    "Role",
    "Group",
    "Account",
    "Resource",
    "AccessCheckRequest",
    "AccessCheckResponse",
    "Settings",
    "AuthService",
]
