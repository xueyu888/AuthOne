"""core 子包：授权引擎。

该子包对外暴露 ``AuthEngine``，用于管理权限模型和执行权限校验。
"""

from __future__ import annotations

from .engine import AuthEngine

__all__: list[str] = ["AuthEngine"]
