"""服务子包。

提供应用层服务类，如 ``AuthService``，封装业务逻辑。"""

from __future__ import annotations

from .auth_service import AuthService

__all__: list[str] = ["AuthService"]
