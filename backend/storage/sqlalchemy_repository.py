"""SQLAlchemy 仓库实现。

本模块实现了各实体仓库协议，使用 SQLAlchemy ORM 与 PostgreSQL 交互。
仓库负责在领域模型与数据库模型之间转换，所有操作均以事务方式提交。
同时包含审计日志仓库，用于记录每次权限检查的结果。
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import (
    AccountModel,
    AuditLogModel,
    GroupModel,
    PermissionModel,
    ResourceModel,
    RoleModel,
)
from ..models import Account, Group, Permission, Resource, Role
from .interface import (
    AccountRepository,
    GroupRepository,
    PermissionRepository,
    ResourceRepository,
    RoleRepository,
)

__all__ = [
    "SQLAlchemyPermissionRepository",
    "SQLAlchemyRoleRepository",
    "SQLAlchemyGroupRepository",
    "SQLAlchemyAccountRepository",
    "SQLAlchemyResourceRepository",
    "AuditLogRepository",
]


class _BaseRepo:
    """Base repository holding a SQLAlchemy async session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session


class SQLAlchemyPermissionRepository(_BaseRepo, PermissionRepository):
    async def add(self, permission: Permission) -> None:
        model = PermissionModel(id=uuid.UUID(permission.id), name=permission.name, description=permission.description)
        self._session.add(model)
        await self._session.commit()

    async def get(self, permission_id: str) -> Optional[Permission]:
        obj = await self._session.get(PermissionModel, uuid.UUID(permission_id))
        if not obj:
            return None
        return Permission(_id=str(obj.id), _name=obj.name, _description=obj.description or "")

    async def list(self, tenant_id: Optional[str] = None) -> List[Permission]:
        result = await self._session.execute(select(PermissionModel))
        objs = result.scalars().all()
        return [Permission(_id=str(o.id), _name=o.name, _description=o.description or "") for o in objs]


class SQLAlchemyRoleRepository(_BaseRepo, RoleRepository):
    async def add(self, role: Role) -> None:
        model = RoleModel(id=uuid.UUID(role.id), tenant_id=role.tenant_id, name=role.name, description=role.description)
        self._session.add(model)
        await self._session.commit()

    async def get(self, role_id: str) -> Optional[Role]:
        stmt = select(RoleModel).where(RoleModel.id == uuid.UUID(role_id)).options(selectinload(RoleModel.permissions))
        result = await self._session.execute(stmt)
        obj: Optional[RoleModel] = result.scalars().first()

        if not obj:
            return None
        perm_ids = [str(p.id) for p in obj.permissions]
        return Role(
            _id=str(obj.id),
            _tenant_id=obj.tenant_id,
            _name=obj.name,
            _description=obj.description or "",
            _permissions=perm_ids,
        )

    async def list(self, tenant_id: Optional[str] = None) -> List[Role]:
        stmt = select(RoleModel).options(selectinload(RoleModel.permissions))
        if tenant_id is not None:
            stmt = stmt.where(RoleModel.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        roles: List[Role] = []
        for obj in result.scalars().all():
            perm_ids = [str(p.id) for p in obj.permissions]
            roles.append(
                Role(
                    _id=str(obj.id),
                    _tenant_id=obj.tenant_id,
                    _name=obj.name,
                    _description=obj.description or "",
                    _permissions=perm_ids,
                )
            )
        return roles

    async def assign_permission(self, role_id: str, permission_id: str) -> None:
        stmt = select(RoleModel).where(RoleModel.id == uuid.UUID(role_id)).options(selectinload(RoleModel.permissions))
        result = await self._session.execute(stmt)
        role_obj: Optional[RoleModel] = result.scalars().first()

        perm_obj: Optional[PermissionModel] = await self._session.get(PermissionModel, uuid.UUID(permission_id))
        
        if role_obj is None or perm_obj is None:
            raise ValueError("role or permission not found")

        if perm_obj not in role_obj.permissions:
            role_obj.permissions.append(perm_obj)
            await self._session.commit()


class SQLAlchemyGroupRepository(_BaseRepo, GroupRepository):
    async def add(self, group: Group) -> None:
        model = GroupModel(
            id=uuid.UUID(group.id), tenant_id=group.tenant_id, name=group.name, description=group.description
        )
        self._session.add(model)
        await self._session.commit()

    async def get(self, group_id: str) -> Optional[Group]:
        stmt = select(GroupModel).where(GroupModel.id == uuid.UUID(group_id)).options(selectinload(GroupModel.roles))
        result = await self._session.execute(stmt)
        obj: Optional[GroupModel] = result.scalars().first()

        if not obj:
            return None
        role_ids = [str(r.id) for r in obj.roles]
        return Group(
            _id=str(obj.id),
            _tenant_id=obj.tenant_id,
            _name=obj.name,
            _description=obj.description or "",
            _roles=role_ids,
        )

    async def list(self, tenant_id: Optional[str] = None) -> List[Group]:
        stmt = select(GroupModel).options(selectinload(GroupModel.roles))
        if tenant_id is not None:
            stmt = stmt.where(GroupModel.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        groups: List[Group] = []
        for obj in result.scalars().all():
            role_ids = [str(r.id) for r in obj.roles]
            groups.append(
                Group(
                    _id=str(obj.id),
                    _tenant_id=obj.tenant_id,
                    _name=obj.name,
                    _description=obj.description or "",
                    _roles=role_ids,
                )
            )
        return groups

    async def assign_role(self, group_id: str, role_id: str) -> None:
        stmt = select(GroupModel).where(GroupModel.id == uuid.UUID(group_id)).options(selectinload(GroupModel.roles))
        result = await self._session.execute(stmt)
        group_obj: Optional[GroupModel] = result.scalars().first()
        
        role_obj: Optional[RoleModel] = await self._session.get(RoleModel, uuid.UUID(role_id))
        
        if group_obj is None or role_obj is None:
            raise ValueError("group or role not found")
        if role_obj not in group_obj.roles:
            group_obj.roles.append(role_obj)
            await self._session.commit()


class SQLAlchemyAccountRepository(_BaseRepo, AccountRepository):
    async def add(self, account: Account) -> None:
        model = AccountModel(
            id=uuid.UUID(account.id), tenant_id=account.tenant_id, username=account.username, email=account.email
        )
        self._session.add(model)
        await self._session.commit()

    async def get(self, account_id: str) -> Optional[Account]:
        stmt = select(AccountModel).where(AccountModel.id == uuid.UUID(account_id)).options(
            selectinload(AccountModel.roles),
            selectinload(AccountModel.groups)
        )
        result = await self._session.execute(stmt)
        obj: Optional[AccountModel] = result.scalars().first()

        if not obj:
            return None
        role_ids = [str(r.id) for r in obj.roles]
        group_ids = [str(g.id) for g in obj.groups]
        return Account(
            _id=str(obj.id),
            _username=obj.username,
            _email=obj.email,
            _tenant_id=obj.tenant_id,
            _roles=role_ids,
            _groups=group_ids,
        )

    async def list(self, tenant_id: Optional[str] = None) -> List[Account]:
        stmt = select(AccountModel).options(
            selectinload(AccountModel.roles),
            selectinload(AccountModel.groups),
        )
        if tenant_id is not None:
            stmt = stmt.where(AccountModel.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        accounts: List[Account] = []
        for obj in result.scalars().all():
            role_ids = [str(r.id) for r in obj.roles]
            group_ids = [str(g.id) for g in obj.groups]
            accounts.append(
                Account(
                    _id=str(obj.id),
                    _username=obj.username,
                    _email=obj.email,
                    _tenant_id=obj.tenant_id,
                    _roles=role_ids,
                    _groups=group_ids,
                )
            )
        return accounts

    async def assign_role(self, account_id: str, role_id: str) -> None:
        stmt = select(AccountModel).where(AccountModel.id == uuid.UUID(account_id)).options(selectinload(AccountModel.roles))
        result = await self._session.execute(stmt)
        acc_obj: Optional[AccountModel] = result.scalars().first()

        role_obj: Optional[RoleModel] = await self._session.get(RoleModel, uuid.UUID(role_id))
        
        if acc_obj is None or role_obj is None:
            raise ValueError("account or role not found")
        if role_obj not in acc_obj.roles:
            acc_obj.roles.append(role_obj)
            await self._session.commit()

    async def assign_group(self, account_id: str, group_id: str) -> None:
        stmt = select(AccountModel).where(AccountModel.id == uuid.UUID(account_id)).options(selectinload(AccountModel.groups))
        result = await self._session.execute(stmt)
        acc_obj: Optional[AccountModel] = result.scalars().first()
        
        group_obj: Optional[GroupModel] = await self._session.get(GroupModel, uuid.UUID(group_id))
        
        if acc_obj is None or group_obj is None:
            raise ValueError("account or group not found")
        if group_obj not in acc_obj.groups:
            acc_obj.groups.append(group_obj)
            await self._session.commit()


class SQLAlchemyResourceRepository(_BaseRepo, ResourceRepository):
    async def add(self, resource: Resource) -> None:
        model = ResourceModel(
            id=uuid.UUID(resource.id),
            type=resource.type,
            name=resource.name,
            tenant_id=resource.tenant_id,
            owner_id=uuid.UUID(resource.owner_id) if resource.owner_id else None,
            resource_metadata=resource.metadata,
        )
        self._session.add(model)
        await self._session.commit()

    async def get(self, resource_id: str) -> Optional[Resource]:
        obj: Optional[ResourceModel] = await self._session.get(ResourceModel, uuid.UUID(resource_id))
        if not obj:
            return None
        return Resource(
            _id=str(obj.id),
            _type=obj.type,
            _name=obj.name,
            _tenant_id=obj.tenant_id,
            _owner_id=str(obj.owner_id) if obj.owner_id else None,
            _metadata=obj.resource_metadata or {}, # Corrected field name
        )

    async def list(self, tenant_id: Optional[str] = None) -> List[Resource]:
        stmt = select(ResourceModel)
        if tenant_id is not None:
            stmt = stmt.where(ResourceModel.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        resources: List[Resource] = []
        for obj in result.scalars().all():
            resources.append(
                Resource(
                    _id=str(obj.id),
                    _type=obj.type,
                    _name=obj.name,
                    _tenant_id=obj.tenant_id,
                    _owner_id=str(obj.owner_id) if obj.owner_id else None,
                    _metadata=obj.resource_metadata or {}, # Corrected field name
                )
            )
        return resources


class AuditLogRepository(_BaseRepo):
    """审计日志仓库。"""

    async def record(
        self,
        account_id: str,
        action: str,
        resource: str,
        result: bool,
        message: str = "",
    ) -> None:
        log = AuditLogModel(
            id=uuid.uuid4(),
            account_id=uuid.UUID(account_id),
            action=action,
            resource=resource,
            result=result,
            message=message,
            timestamp=datetime.utcnow(),
        )
        self._session.add(log)
        await self._session.commit()
