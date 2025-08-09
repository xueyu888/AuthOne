from __future__ import annotations
import uuid
from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert

from ..db import (
    PermissionModel, RoleModel, GroupModel, AccountModel, ResourceModel,
    RolePermission, GroupRole, UserRole, UserGroup, AuditLogModel,
)
from .interface import (
    PermissionRepository, RoleRepository, GroupRepository, AccountRepository, ResourceRepository
)

class SQLAlchemyPermissionRepository(PermissionRepository):
    def __init__(self, sf: async_sessionmaker[AsyncSession]) -> None:
        self._sf = sf

    async def add(self, *, name: str, description: str | None = None) -> PermissionModel:
        async with self._sf() as s:
            exists = await s.scalar(select(PermissionModel.id).where(PermissionModel.name == name))
            if exists:
                raise ValueError(f"permission '{name}' already exists")
            obj = PermissionModel(name=name, description=description)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return obj

    async def get(self, permission_id: str) -> Optional[PermissionModel]:
        try:
            pid = uuid.UUID(permission_id)
        except ValueError:
            return None
        async with self._sf() as s:
            return await s.get(PermissionModel, pid)

    async def list(self) -> List[PermissionModel]:
        async with self._sf() as s:
            res = await s.execute(select(PermissionModel))
            return list(res.scalars())

    async def delete(self, permission_id: str) -> bool:
        try:
            pid = uuid.UUID(permission_id)
        except ValueError:
            return False
        async with self._sf() as s:
            res = await s.execute(delete(PermissionModel).where(PermissionModel.id == pid))
            await s.commit()
            return res.rowcount > 0

class SQLAlchemyRoleRepository(RoleRepository):
    def __init__(self, sf: async_sessionmaker[AsyncSession]) -> None:
        self._sf = sf

    async def add(self, *, tenant_id: str | None, name: str, description: str | None = None) -> RoleModel:
        async with self._sf() as s:
            exists = await s.scalar(select(RoleModel.id).where(RoleModel.tenant_id == tenant_id, RoleModel.name == name))
            if exists:
                raise ValueError(f"role '{name}' already exists for tenant '{tenant_id}'")
            obj = RoleModel(tenant_id=tenant_id, name=name, description=description)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return obj

    async def get(self, role_id: str) -> Optional[RoleModel]:
        try:
            rid = uuid.UUID(role_id)
        except ValueError:
            return None
        async with self._sf() as s:
            return await s.get(RoleModel, rid)

    async def list(self, tenant_id: str | None = None) -> List[RoleModel]:
        async with self._sf() as s:
            stmt = select(RoleModel)
            if tenant_id is not None:
                stmt = stmt.where(RoleModel.tenant_id == tenant_id)
            res = await s.execute(stmt)
            return list(res.scalars())

    async def delete(self, role_id: str) -> bool:
        try:
            rid = uuid.UUID(role_id)
        except ValueError:
            return False
        async with self._sf() as s:
            res = await s.execute(delete(RoleModel).where(RoleModel.id == rid))
            await s.commit()
            return res.rowcount > 0

    async def assign_permission(self, role_id: str, permission_id: str) -> None:
        try:
            rid = uuid.UUID(role_id); pid = uuid.UUID(permission_id)
        except ValueError:
            return
        async with self._sf() as s:
            stmt = pg_insert(RolePermission.__table__).values(role_id=rid, permission_id=pid)
            stmt = stmt.on_conflict_do_nothing(index_elements=[RolePermission.__table__.c.role_id, RolePermission.__table__.c.permission_id])
            await s.execute(stmt); await s.commit()

    async def remove_permission(self, role_id: str, permission_id: str) -> None:
        try:
            rid = uuid.UUID(role_id); pid = uuid.UUID(permission_id)
        except ValueError:
            return
        async with self._sf() as s:
            await s.execute(delete(RolePermission).where(RolePermission.role_id == rid, RolePermission.permission_id == pid))
            await s.commit()

class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, sf: async_sessionmaker[AsyncSession]) -> None:
        self._sf = sf

    async def add(self, *, tenant_id: str | None, name: str, description: str | None = None) -> GroupModel:
        async with self._sf() as s:
            exists = await s.scalar(select(GroupModel.id).where(GroupModel.tenant_id == tenant_id, GroupModel.name == name))
            if exists:
                raise ValueError(f"group '{name}' already exists for tenant '{tenant_id}'")
            obj = GroupModel(tenant_id=tenant_id, name=name, description=description)
            s.add(obj); await s.commit(); await s.refresh(obj); return obj

    async def get(self, group_id: str) -> Optional[GroupModel]:
        try:
            gid = uuid.UUID(group_id)
        except ValueError:
            return None
        async with self._sf() as s:
            return await s.get(GroupModel, gid)

    async def list(self, tenant_id: str | None = None) -> List[GroupModel]:
        async with self._sf() as s:
            stmt = select(GroupModel)
            if tenant_id is not None:
                stmt = stmt.where(GroupModel.tenant_id == tenant_id)
            res = await s.execute(stmt); return list(res.scalars())

    async def delete(self, group_id: str) -> bool:
        try:
            gid = uuid.UUID(group_id)
        except ValueError:
            return False
        async with self._sf() as s:
            res = await s.execute(delete(GroupModel).where(GroupModel.id == gid)); await s.commit(); return res.rowcount > 0

    async def assign_role(self, group_id: str, role_id: str) -> None:
        try:
            gid = uuid.UUID(group_id); rid = uuid.UUID(role_id)
        except ValueError:
            return
        async with self._sf() as s:
            stmt = pg_insert(GroupRole.__table__).values(group_id=gid, role_id=rid)
            stmt = stmt.on_conflict_do_nothing(index_elements=[GroupRole.__table__.c.group_id, GroupRole.__table__.c.role_id])
            await s.execute(stmt); await s.commit()

    async def remove_role(self, group_id: str, role_id: str) -> None:
        try:
            gid = uuid.UUID(group_id); rid = uuid.UUID(role_id)
        except ValueError:
            return
        async with self._sf() as s:
            await s.execute(delete(GroupRole).where(GroupRole.group_id == gid, GroupRole.role_id == rid)); await s.commit()

class SQLAlchemyAccountRepository(AccountRepository):
    def __init__(self, sf: async_sessionmaker[AsyncSession]) -> None:
        self._sf = sf

    async def add(self, *, username: str, email: str, tenant_id: str | None) -> AccountModel:
        async with self._sf() as s:
            e1 = await s.scalar(select(AccountModel.id).where(AccountModel.email == email))
            if e1: raise ValueError(f"email '{email}' already exists")
            e2 = await s.scalar(select(AccountModel.id).where(AccountModel.username == username, AccountModel.tenant_id == tenant_id))
            if e2: raise ValueError(f"username '{username}' already exists for tenant '{tenant_id}'")
            obj = AccountModel(username=username, email=email, tenant_id=tenant_id)
            s.add(obj); await s.commit(); await s.refresh(obj); return obj

    async def get(self, account_id: str) -> Optional[AccountModel]:
        try: aid = uuid.UUID(account_id)
        except ValueError: return None
        async with self._sf() as s: return await s.get(AccountModel, aid)

    async def list(self, tenant_id: str | None = None) -> List[AccountModel]:
        async with self._sf() as s:
            from sqlalchemy import select
            stmt = select(AccountModel)
            if tenant_id is not None: stmt = stmt.where(AccountModel.tenant_id == tenant_id)
            res = await s.execute(stmt); return list(res.scalars())

    async def delete(self, account_id: str) -> bool:
        try: aid = uuid.UUID(account_id)
        except ValueError: return False
        async with self._sf() as s:
            res = await s.execute(delete(AccountModel).where(AccountModel.id == aid)); await s.commit(); return res.rowcount > 0

    async def assign_role(self, account_id: str, role_id: str) -> None:
        try: aid = uuid.UUID(account_id); rid = uuid.UUID(role_id)
        except ValueError: return
        async with self._sf() as s:
            stmt = pg_insert(UserRole.__table__).values(account_id=aid, role_id=rid)
            stmt = stmt.on_conflict_do_nothing(index_elements=[UserRole.__table__.c.account_id, UserRole.__table__.c.role_id])
            await s.execute(stmt); await s.commit()

    async def remove_role(self, account_id: str, role_id: str) -> None:
        try: aid = uuid.UUID(account_id); rid = uuid.UUID(role_id)
        except ValueError: return
        async with self._sf() as s:
            await s.execute(delete(UserRole).where(UserRole.account_id == aid, UserRole.role_id == rid)); await s.commit()

    async def assign_group(self, account_id: str, group_id: str) -> None:
        try: aid = uuid.UUID(account_id); gid = uuid.UUID(group_id)
        except ValueError: return
        async with self._sf() as s:
            stmt = pg_insert(UserGroup.__table__).values(account_id=aid, group_id=gid)
            stmt = stmt.on_conflict_do_nothing(index_elements=[UserGroup.__table__.c.account_id, UserGroup.__table__.c.group_id])
            await s.execute(stmt); await s.commit()

    async def remove_group(self, account_id: str, group_id: str) -> None:
        try: aid = uuid.UUID(account_id); gid = uuid.UUID(group_id)
        except ValueError: return
        async with self._sf() as s:
            await s.execute(delete(UserGroup).where(UserGroup.account_id == aid, UserGroup.group_id == gid)); await s.commit()

class SQLAlchemyResourceRepository(ResourceRepository):
    def __init__(self, sf: async_sessionmaker[AsyncSession]) -> None:
        self._sf = sf

    async def add(self, *, resource_type: str, name: str, tenant_id: str | None, owner_id: str | None, metadata: dict | None = None) -> ResourceModel:
        async with self._sf() as s:
            exists = await s.scalar(select(ResourceModel.id).where(ResourceModel.tenant_id == tenant_id, ResourceModel.name == name))
            if exists: raise ValueError(f"resource '{name}' already exists for tenant '{tenant_id}'")
            obj = ResourceModel(type=resource_type, name=name, tenant_id=tenant_id, owner_id=(uuid.UUID(owner_id) if owner_id else None), resource_metadata=(metadata or {}))
            s.add(obj); await s.commit(); await s.refresh(obj); return obj

    async def get(self, resource_id: str) -> Optional[ResourceModel]:
        try: rid = uuid.UUID(resource_id)
        except ValueError: return None
        async with self._sf() as s: return await s.get(ResourceModel, rid)

    async def list(self, tenant_id: str | None = None) -> List[ResourceModel]:
        async with self._sf() as s:
            from sqlalchemy import select
            stmt = select(ResourceModel)
            if tenant_id is not None: stmt = stmt.where(ResourceModel.tenant_id == tenant_id)
            res = await s.execute(stmt); return list(res.scalars())

    async def delete(self, resource_id: str) -> bool:
        try: rid = uuid.UUID(resource_id)
        except ValueError: return False
        async with self._sf() as s:
            res = await s.execute(delete(ResourceModel).where(ResourceModel.id == rid)); await s.commit(); return res.rowcount > 0

class AuditLogRepository:
    def __init__(self, sf: async_sessionmaker[AsyncSession]) -> None:
        self._sf = sf

    async def record(self, *, account_id: str, action: str, resource: str | None, result: bool, message: str | None = None) -> None:
        async with self._sf() as s:
            try: aid = uuid.UUID(account_id)
            except ValueError: aid = None  # type: ignore[assignment]
            s.add(AuditLogModel(account_id=aid, action=action, resource=resource, result=result, message=message))
            await s.commit()