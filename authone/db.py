"""数据库模块。

本模块负责创建 SQLAlchemy 的引擎、会话工厂以及 ORM 模型定义。
我们定义了与领域模型对应的数据库表结构，包括关联表，并提供
初始化和获取会话的便捷函数。
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Text,
    JSON,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

from .config import Settings

__all__ = [
    "Base",
    "get_engine",
    "get_session",
    "init_db",
    "PermissionModel",
    "RoleModel",
    "GroupModel",
    "AccountModel",
    "ResourceModel",
    "AuditLogModel",
]


# 基础类
Base = declarative_base()

# 关联表定义
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

group_roles = Table(
    "group_roles",
    Base.metadata,
    Column("group_id", UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
)

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("account_id", UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

user_groups = Table(
    "user_groups",
    Base.metadata,
    Column(
        "account_id", UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("group_id", UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
)


class PermissionModel(Base):
    __tablename__ = "permissions"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    name: str = Column(String(255), unique=True, nullable=False)
    description: str = Column(Text, nullable=True)

    roles = relationship(
        "RoleModel", secondary=role_permissions, back_populates="permissions", cascade="all"
    )


class RoleModel(Base):
    __tablename__ = "roles"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Optional[str] = Column(UUID(as_uuid=True), nullable=True)
    name: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=True)

    permissions = relationship(
        PermissionModel, secondary=role_permissions, back_populates="roles", cascade="all"
    )
    groups = relationship("GroupModel", secondary=group_roles, back_populates="roles", cascade="all")
    accounts = relationship(
        "AccountModel", secondary=user_roles, back_populates="roles", cascade="all"
    )


class GroupModel(Base):
    __tablename__ = "groups"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Optional[str] = Column(UUID(as_uuid=True), nullable=True)
    name: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=True)

    roles = relationship(RoleModel, secondary=group_roles, back_populates="groups", cascade="all")
    accounts = relationship(
        "AccountModel", secondary=user_groups, back_populates="groups", cascade="all"
    )


class AccountModel(Base):
    __tablename__ = "accounts"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Optional[str] = Column(UUID(as_uuid=True), nullable=True)
    username: str = Column(String(255), nullable=False)
    email: str = Column(String(255), nullable=False, unique=True)

    roles = relationship(RoleModel, secondary=user_roles, back_populates="accounts", cascade="all")
    groups = relationship(GroupModel, secondary=user_groups, back_populates="accounts", cascade="all")


class ResourceModel(Base):
    __tablename__ = "resources"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    type: str = Column(String(255), nullable=False)
    name: str = Column(String(255), nullable=False)
    tenant_id: Optional[str] = Column(UUID(as_uuid=True), nullable=True)
    owner_id: Optional[str] = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    metadata: dict = Column(JSON, nullable=True)


class AuditLogModel(Base):
    __tablename__ = "audit_logs"
    id: str = Column(UUID(as_uuid=True), primary_key=True)
    account_id: str = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    action: str = Column(String(255), nullable=False)
    resource: str = Column(String(255), nullable=True)
    result: bool = Column(Boolean, nullable=False)
    message: str = Column(Text, nullable=True)
    timestamp: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)


def get_engine(settings: Settings):
    return create_engine(settings.db_url, future=True)


def get_session(settings: Settings) -> Session:
    engine = get_engine(settings)
    return sessionmaker(bind=engine, future=True)()


def init_db(settings: Settings) -> None:
    """创建所有表结构。"""
    engine = get_engine(settings)
    Base.metadata.create_all(engine)
