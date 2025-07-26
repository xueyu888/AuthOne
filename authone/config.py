"""配置模块。

此模块定义了一些配置相关的数据结构和帮助函数，用于管理数据库
连接、Casbin 模型路径等可配置项。通过外部注入 ``Settings`` 实例，可以
方便地替换数据库或调整日志级别等运行参数。

示例::

    from AuthOne.config import Settings
    settings = Settings(db_url="postgresql://user:pass@host:5432/db")
    print(settings.db_url)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

__all__ = ["Settings"]


@dataclass(slots=True)
class Settings:
    """应用配置。

    :param db_url: 数据库连接字符串，使用 SQLAlchemy 或 psycopg 标准格式。
    :param log_level: 日志级别，默认为 ``INFO``。
    :param casbin_model_path: Casbin 模型配置文件路径，用于初始化 Enforcer。
    :param casbin_policy_table: Casbin 策略表名称，在数据库中存储策略行。
    """

    db_url: str = "postgresql://user:password@localhost:5432/authone"
    log_level: str = "INFO"
    casbin_model_path: str = "rbac_model.conf"
    casbin_policy_table: str = "casbin_rules"
    # 未来可以添加更多配置项，如 Redis、缓存过期时间等

    def override(self, **kwargs: object) -> "Settings":
        """复制当前配置并按需覆盖字段。

        该方法返回新的 ``Settings`` 实例，不修改原对象。
        """
        data = self.__dict__.copy()
        data.update(kwargs)
        return Settings(**data)  # type: ignore[arg-type]
