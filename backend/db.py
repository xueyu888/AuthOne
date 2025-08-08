"""数据库模块。

本模块负责创建 SQLAlchemy 的引擎、会话工厂以及 ORM 模型定义。
我们定义了与领域模型对应的数据库表结构，包括关联表，并提供
初始化和获取会话的便捷函数。
"""

# backend/db.py
from __future__ import annotations
import json
from dataclasses import dataclass
from sqlalchemy import Table, Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

__all__ = [
    "Base", "init_engine", "get_session", "dispose_engine",
    "init_db",
    "PermissionModel", "RoleModel", "GroupModel", "AccountModel", "ResourceModel",
    "AuditLogModel", "CasbinRuleModel",
]

Base = declarative_base()

role_permissions = Table(
    "role_permissions", Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)
group_roles = Table(
    "group_roles", Base.metadata,
    Column("group_id", UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)
user_roles = Table(
    "user_roles", Base.metadata,
    Column("account_id", UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)
user_groups = Table(
    "user_groups", Base.metadata,
    Column("account_id", UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
)

class PermissionModel(Base):
    __tablename__ = "permissions"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    name: str = Column(String(255), unique=True, nullable=False)
    description: str = Column(Text, nullable=True)
    roles = relationship("RoleModel", secondary=role_permissions, back_populates="permissions")

class RoleModel(Base):
    __tablename__ = "roles"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id: str|None = Column(String(255), nullable=True, index=True)
    name: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=True)
    permissions = relationship(PermissionModel, secondary=role_permissions, back_populates="roles")
    groups = relationship("GroupModel", secondary=group_roles, back_populates="roles")
    accounts = relationship("AccountModel", secondary=user_roles, back_populates="roles")

class GroupModel(Base):
    __tablename__ = "groups"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id: str|None = Column(String(255), nullable=True, index=True)
    name: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=True)
    roles = relationship(RoleModel, secondary=group_roles, back_populates="groups")
    # --- THIS IS THE FIX ---
    # It must back-populate the 'groups' property on the AccountModel
    accounts = relationship("AccountModel", secondary=user_groups, back_populates="groups")

class AccountModel(Base):
    __tablename__ = "accounts"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id: str|None = Column(String(255), nullable=True, index=True)
    username: str = Column(String(255), nullable=False)
    email: str = Column(String(255), nullable=False, unique=True)
    roles = relationship(RoleModel, secondary=user_roles, back_populates="accounts")
    groups = relationship(GroupModel, secondary=user_groups, back_populates="accounts")

class ResourceModel(Base):
    __tablename__ = "resources"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    type: str = Column(String(255), nullable=False)
    name: str = Column(String(255), nullable=False)
    tenant_id: str|None = Column(String(255), nullable=True, index=True)
    owner_id: str|None = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    resource_metadata: dict = Column(JSON, nullable=True)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    account_id: str = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    action: str = Column(String(255), nullable=False)
    resource: str = Column(String(255), nullable=True)
    result: bool = Column(Boolean, nullable=False)
    message: str = Column(Text, nullable=True)
    timestamp: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

class CasbinRuleModel(Base):
    __tablename__ = "casbin_rules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ptype = Column(String(255))
    v0 = Column(String(255))
    v1 = Column(String(255))
    v2 = Column(String(255))
    v3 = Column(String(255))
    v4 = Column(String(255))
    v5 = Column(String(255))


# ---------- Engine / Session (单例) ----------
_ENGINE: AsyncEngine | None = None
_SESSION_FACTORY: async_sessionmaker[AsyncSession] | None = None

def init_engine(db_url: str) -> None:
    global _ENGINE, _SESSION_FACTORY
    if _ENGINE is None:
        _ENGINE = create_async_engine(
            db_url,
            future=True,
            json_serializer=json.dumps,
            json_deserializer=json.loads,
        )
        _SESSION_FACTORY = async_sessionmaker(_ENGINE, expire_on_commit=False)

def get_session() -> AsyncSession:
    if _SESSION_FACTORY is None:
        raise RuntimeError("Engine not initialized, call init_engine() first")
    return _SESSION_FACTORY()

async def dispose_engine() -> None:
    global _ENGINE
    if _ENGINE is not None:
        await _ENGINE.dispose()
        _ENGINE = None

# 改：允许传 Settings（测试里就这么用），否则使用既有引擎
async def init_db(settings: "Settings | None" = None, drop_all: bool = False) -> None:
    global _ENGINE
    if settings is not None:
        # 若传入 settings，幂等初始化引擎
        init_engine(settings.db_url)
    if _ENGINE is None:
        raise RuntimeError("Engine not initialized")

    async with _ENGINE.begin() as conn:
        if drop_all:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)