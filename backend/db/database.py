# backend/db/database.py

from __future__ import annotations
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from .db_models import Base

# 规范 11: 所有模块必须显式声明导出符号 __all__
__all__ = ["DatabaseManager"]


# 规范 3 & 5: 边界清晰 & 逻辑封装为类
class DatabaseManager:
    """
    负责数据库连接和会话的生命周期管理。
    """
    _engine: Optional[AsyncEngine] = None
    _session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    def __init__(self, db_url: str):
        self._db_url = db_url

    async def init_engine(self) -> None:
        """初始化数据库引擎并创建会话工厂。"""
        self._engine = create_async_engine(self._db_url, echo=False, pool_pre_ping=True)
        # 简单连接测试
        async with self._engine.connect() as conn:
            await conn.execute(select(1))
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    async def close_engine(self) -> None:
        """安全地关闭数据库引擎。"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def create_database_and_tables(self, drop_all: bool = False) -> None:
        """根据模型创建所有表，可选择先删除旧表。"""
        if not self._engine:
            raise RuntimeError("Database engine is not initialized. Call init_engine() first.")
        
        async with self._engine.begin() as conn:
            if drop_all:
                await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    def get_async_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        """获取会话工厂实例。"""
        if not self._session_factory:
            raise RuntimeError("Session maker is not available. Call init_engine() first.")
        return self._session_factory



