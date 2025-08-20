# backend/db/__init__.py

"""
规范 12: 包结构 - __init__.py + __all__ 的出口管理。
集中导出 db 子包的公共 API。
"""
from __future__ import annotations

from .database import DatabaseManager
from .db_models import (
    AccountModel, GroupModel, PermissionModel, ResourceModel, RoleModel
)
from .repository import (
    AccountRepository, GroupRepository, PermissionRepository, ResourceRepository, RoleRepository
)
from .unit_of_work import UnitOfWork

# 规范 11: 显式声明 __all__
__all__ = [
    "DatabaseManager",
    "UnitOfWork",
    "AccountRepository",
    "GroupRepository",
    "PermissionRepository",
    "ResourceRepository",
    "RoleRepository",
    "AccountModel",
    "GroupModel",
    "PermissionModel",
    "ResourceModel",
    "RoleModel",
]