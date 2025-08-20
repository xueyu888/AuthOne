# backend/__init__.py

"""
mypkg 顶层命名空间。只暴露“门脸”级 API。
"""
from __future__ import annotations

from ._version import __version__
from .app import create_app
from .config import get_settings
from .service import AuthService

__all__: list[str] = [
    "__version__",
    "create_app",
    "get_settings",
    "AuthService",
]