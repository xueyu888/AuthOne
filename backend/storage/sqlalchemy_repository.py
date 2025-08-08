# backend/storage/sqlalchemy_repository.py
from __future__ import annotations
import uuid
from typing import list, optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import AccountModel, GroupModel, PermissionModel, ResourceModel, RoleModel
from ..models import Account, Group, Permission, Resource, Role
from .interface import AccountRepository, GroupRepository, PermissionRepository, ResourceRepository, RoleRepository

__all__ = [
    "SQLAlchemyPermissionRepository", "SQLAlchemyRoleRepository", "SQLAlchemyGroupRepository",
    "SQLAlchemyAccountRepository", "SQLAlchemyResourceRepository", "AuditLogRepository",
]

class _BaseRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

# ---- Permission ----
class SQLAlchemyPermissionRepository(_BaseRepo, PermissionRepository):
    async def add(self, permission: Permission) -> None:
        self._session.add(PermissionModel(id=uuid.UUID(permission.id), name=permission.name, description=permission.description))
        await self._session.commit()

    async def get(self, permission_id: str) -> optional[Permission]:
        obj = await self._session.get(PermissionModel, uuid.UUID(permission_id))
        return None if not obj else Permission(_id=str(obj.id), _name=obj.name, _description=obj.description or "")

    async def list(self, tenant_id: optional[str] = None) -> list[Permission]:
        res = await self._session.execute(select(PermissionModel))
        return [Permission(_id=str(o.id), _name=o.name, _description=o.description or "") for o in res.scalars().all()]

    async def delete(self, permission_id: str) -> bool:
        obj = await self._session.get(PermissionModel, uuid.UUID(permission_id))
        if not obj:
            return False
        await self._session.delete(obj)
        await self._session.commit()
        return True

# ---- Role ----
class SQLAlchemyRoleRepository(_BaseRepo, RoleRepository):
    async def add(self, role: Role) -> None:
        self._session.add(RoleModel(id=uuid.UUID(role.id), tenant_id=role.tenant_id, name=role.name, description=role.description))
        await self._session.commit()

    async def get(self, role_id: str) -> optional[Role]:
        stmt = select(RoleModel).where(RoleModel.id == uuid.UUID(role_id)).options(selectinload(RoleModel.permissions))
        obj = (await self._session.execute(stmt)).scalars().first()
        if not obj:
            return None
        return Role(_id=str(obj.id), _tenant_id=obj.tenant_id, _name=obj.name, _description=obj.description or "",
                    _permissions=[str(p.id) for p in obj.permissions])

    async def list(self, tenant_id: optional[str] = None) -> list[Role]:
        stmt = select(RoleModel).options(selectinload(RoleModel.permissions))
        if tenant_id is not None:
            stmt = stmt.where(RoleModel.tenant_id == tenant_id)
        res = await self._session.execute(stmt)
        out: list[Role] = []
        for obj in res.scalars().all():
            out.append(Role(_id=str(obj.id), _tenant_id=obj.tenant_id, _name=obj.name,
                            _description=obj.description or "", _permissions=[str(p.id) for p in obj.permissions]))
        return out

    async def delete(self, role_id: str) -> bool:
        obj = await self._session.get(RoleModel, uuid.UUID(role_id))
        if not obj:
            return False
        await self._session.delete(obj)
        await self._session.commit()
        return True

    async def assign_permission(self, role_id: str, permission_id: str) -> None:
        role = await self._session.get(RoleModel, uuid.UUID(role_id), options=[selectinload(RoleModel.permissions)])
        perm = await self._session.get(PermissionModel, uuid.UUID(permission_id))
        if not role or not perm:
            raise ValueError("role or permission not found")
        if perm not in role.permissions:
            role.permissions.append(perm)
            await self._session.commit()

    async def remove_permission(self, role_id: str, permission_id: str) -> None:
        role = await self._session.get(RoleModel, uuid.UUID(role_id), options=[selectinload(RoleModel.permissions)])
        perm = await self._session.get(PermissionModel, uuid.UUID(permission_id))
        if not role or not perm:
            raise ValueError("role or permission not found")
        if perm in role.permissions:
            role.permissions.remove(perm)
            await self._session.commit()

# ---- Group ----
class SQLAlchemyGroupRepository(_BaseRepo, GroupRepository):
    async def add(self, group: Group) -> None:
        self._session.add(GroupModel(id=uuid.UUID(group.id), tenant_id=group.tenant_id, name=group.name, description=group.description))
        await self._session.commit()

    async def get(self, group_id: str) -> optional[Group]:
        stmt = select(GroupModel).where(GroupModel.id == uuid.UUID(group_id)).options(selectinload(GroupModel.roles))
        obj = (await self._session.execute(stmt)).scalars().first()
        if not obj:
            return None
        return Group(_id=str(obj.id), _tenant_id=obj.tenant_id, _name=obj.name,
                     _description=obj.description or "", _roles=[str(r.id) for r in obj.roles])

    async def list(self, tenant_id: optional[str] = None) -> list[Group]:
        stmt = select(GroupModel).options(selectinload(GroupModel.roles))
        if tenant_id is not None:
            stmt = stmt.where(GroupModel.tenant_id == tenant_id)
        res = await self._session.execute(stmt)
        out: list[Group] = []
        for obj in res.scalars().all():
            out.append(Group(_id=str(obj.id), _tenant_id=obj.tenant_id, _name=obj.name,
                             _description=obj.description or "", _roles=[str(r.id) for r in obj.roles]))
        return out

    async def delete(self, group_id: str) -> bool:
        obj = await self._session.get(GroupModel, uuid.UUID(group_id))
        if not obj:
            return False
        await self._session.delete(obj)
        await self._session.commit()
        return True

    async def assign_role(self, group_id: str, role_id: str) -> None:
        grp = await self._session.get(GroupModel, uuid.UUID(group_id), options=[selectinload(GroupModel.roles)])
        role = await self._session.get(RoleModel, uuid.UUID(role_id))
        if not grp or not role:
            raise ValueError("group or role not found")
        if role not in grp.roles:
            grp.roles.append(role)
            await self._session.commit()

    async def remove_role(self, group_id: str, role_id: str) -> None:
        grp = await self._session.get(GroupModel, uuid.UUID(group_id), options=[selectinload(GroupModel.roles)])
        role = await self._session.get(RoleModel, uuid.UUID(role_id))
        if not grp or not role:
            raise ValueError("group or role not found")
        if role in grp.roles:
            grp.roles.remove(role)
            await self._session.commit()

# ---- Account ----
class SQLAlchemyAccountRepository(_BaseRepo, AccountRepository):
    async def add(self, account: Account) -> None:
        self._session.add(AccountModel(id=uuid.UUID(account.id), tenant_id=account.tenant_id, username=account.username, email=account.email))
        await self._session.commit()

    async def get(self, account_id: str) -> optional[Account]:
        stmt = select(AccountModel).where(AccountModel.id == uuid.UUID(account_id)).options(selectinload(AccountModel.roles), selectinload(AccountModel.groups))
        obj = (await self._session.execute(stmt)).scalars().first()
        if not obj:
            return None
        return Account(_id=str(obj.id), _username=obj.username, _email=obj.email, _tenant_id=obj.tenant_id,
                       _roles=[str(r.id) for r in obj.roles], _groups=[str(g.id) for g in obj.groups])

    async def list(self, tenant_id: optional[str] = None) -> list[Account]:
        stmt = select(AccountModel).options(selectinload(AccountModel.roles), selectinload(AccountModel.groups))
        if tenant_id is not None:
            stmt = stmt.where(AccountModel.tenant_id == tenant_id)
        res = await self._session.execute(stmt)
        out: list[Account] = []
        for obj in res.scalars().all():
            out.append(Account(_id=str(obj.id), _username=obj.username, _email=obj.email, _tenant_id=obj.tenant_id,
                               _roles=[str(r.id) for r in obj.roles], _groups=[str(g.id) for g in obj.groups]))
        return out

    async def delete(self, account_id: str) -> bool:
        obj = await self._session.get(AccountModel, uuid.UUID(account_id))
        if not obj:
            return False
        await self._session.delete(obj)
        await self._session.commit()
        return True

    async def assign_role(self, account_id: str, role_id: str) -> None:
        acc = await self._session.get(AccountModel, uuid.UUID(account_id), options=[selectinload(AccountModel.roles)])
        role = await self._session.get(RoleModel, uuid.UUID(role_id))
        if not acc or not role:
            raise ValueError("account or role not found")
        if role not in acc.roles:
            acc.roles.append(role)
            await self._session.commit()

    async def remove_role(self, account_id: str, role_id: str) -> None:
        acc = await self._session.get(AccountModel, uuid.UUID(account_id), options=[selectinload(AccountModel.roles)])
        role = await self._session.get(RoleModel, uuid.UUID(role_id))
        if not acc or not role:
            raise ValueError("account or role not found")
        if role in acc.roles:
            acc.roles.remove(role)
            await self._session.commit()

    async def assign_group(self, account_id: str, group_id: str) -> None:
        acc = await self._session.get(AccountModel, uuid.UUID(account_id), options=[selectinload(AccountModel.groups)])
        grp = await self._session.get(GroupModel, uuid.UUID(group_id))
        if not acc or not grp:
            raise ValueError("account or group not found")
        if grp not in acc.groups:
            acc.groups.append(grp)
            await self._session.commit()

    async def remove_group(self, account_id: str, group_id: str) -> None:
        acc = await self._session.get(AccountModel, uuid.UUID(account_id), options=[selectinload(AccountModel.groups)])
        grp = await self._session.get(GroupModel, uuid.UUID(group_id))
        if not acc or not grp:
            raise ValueError("account or group not found")
        if grp in acc.groups:
            acc.groups.remove(grp)
            await self._session.commit()

# ---- Resource ----
class SQLAlchemyResourceRepository(_BaseRepo, ResourceRepository):
    async def add(self, resource: Resource) -> None:
        self._session.add(ResourceModel(
            id=uuid.UUID(resource.id),
            type=resource.type,
            name=resource.name,
            tenant_id=resource.tenant_id,
            owner_id=uuid.UUID(resource.owner_id) if resource.owner_id else None,
            resource_metadata=resource.metadata,   # ✅ 修复字段名
        ))
        await self._session.commit()

    async def get(self, resource_id: str) -> optional[Resource]:
        obj = await self._session.get(ResourceModel, uuid.UUID(resource_id))
        if not obj:
            return None
        return Resource(_id=str(obj.id), _type=obj.type, _name=obj.name, _tenant_id=obj.tenant_id,
                        _owner_id=str(obj.owner_id) if obj.owner_id else None,
                        _metadata=obj.resource_metadata or {})

    async def list(self, tenant_id: optional[str] = None) -> list[Resource]:
        stmt = select(ResourceModel)
        if tenant_id is not None:
            stmt = stmt.where(ResourceModel.tenant_id == tenant_id)
        res = await self._session.execute(stmt)
        return [Resource(_id=str(o.id), _type=o.type, _name=o.name, _tenant_id=o.tenant_id,
                         _owner_id=str(o.owner_id) if o.owner_id else None,
                         _metadata=o.resource_metadata or {}) for o in res.scalars().all()]

    async def delete(self, resource_id: str) -> bool:
        obj = await self._session.get(ResourceModel, uuid.UUID(resource_id))
        if not obj:
            return False
        await self._session.delete(obj)
        await self._session.commit()
        return True
