# backend/storage/sqlalchemy_repository.py
from __future__ import annotations
from uuid import UUID, uuid4
from sqlalchemy import select, insert, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from ..models import Account, Group, Role, Permission, Resource
from ..db import (
    AccountModel, GroupModel, RoleModel, PermissionModel, ResourceModel,
    AuditLogModel,
    role_permissions, group_roles, user_roles, user_groups,
)
from ..storage.interface import (
    PermissionRepository, RoleRepository, GroupRepository, AccountRepository, ResourceRepository
)

# ---------- 工具：模型 ↔ 领域对象 ----------

def _to_permission(m: PermissionModel) -> Permission:
    return Permission(_id=str(m.id), _name=m.name, _description=m.description or "")

def _to_role(m: RoleModel) -> Role:
    perm_ids = [str(p.id) for p in m.permissions] if hasattr(m, "permissions") and m.permissions else []
    return Role(_id=str(m.id), _tenant_id=m.tenant_id, _name=m.name, _description=m.description or "", _permissions=perm_ids)

def _to_group(m: GroupModel) -> Group:
    role_ids = [str(r.id) for r in m.roles] if hasattr(m, "roles") and m.roles else []
    return Group(_id=str(m.id), _tenant_id=m.tenant_id, _name=m.name, _description=m.description or "", _roles=role_ids)

def _to_account(m: AccountModel) -> Account:
    role_ids = [str(r.id) for r in m.roles] if hasattr(m, "roles") and m.roles else []
    group_ids = [str(g.id) for g in m.groups] if hasattr(m, "groups") and m.groups else []
    return Account(_id=str(m.id), _username=m.username, _email=m.email, _tenant_id=m.tenant_id, _roles=role_ids, _groups=group_ids)

def _to_resource(m: ResourceModel) -> Resource:
    md = m.resource_metadata or {}
    return Resource(_id=str(m.id), _type=m.type, _name=m.name, _tenant_id=m.tenant_id, _owner_id=(str(m.owner_id) if m.owner_id else None), _resource_metadata=md)

# ---------- 仓库实现 ----------

class SQLAlchemyPermissionRepository(PermissionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.s = session

    async def add(self, permission: Permission) -> None:
        async with self.s.begin():
            stmt = (
                pg_insert(PermissionModel)
                .values(
                    id = UUID(permission.id),
                    name = permission.name,
                    description = permission.description,
                )
                .on_conflict_do_nothing(index_elements=[PermissionModel.name])
                .returning(PermissionModel.id) #type: ignore[no-any-return]
            )

        rid = await self.s.scalar(stmt) #type: ignore[no-any-return]
        if rid is None:
            raise ValueError(f"Permission with name '{permission.name}' already exists.")
        
        permission._id = str(rid)  # 更新领域对象的 ID

    async def get(self, permission_id: str) -> Permission | None:
        m = await self.s.get(PermissionModel, UUID(permission_id))
        return _to_permission(m) if m else None

    async def list(self, tenant_id: str | None = None) -> list[Permission]:
        # 权限不分租户
        res = await self.s.execute(select(PermissionModel))
        return [_to_permission(m) for m in res.scalars().all()]

    async def delete(self, permission_id: str) -> bool:
        res = await self.s.execute(delete(PermissionModel).where(PermissionModel.id == UUID(permission_id)))
        await self.s.commit()
        return res.rowcount > 0

class SQLAlchemyRoleRepository(RoleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.s = session

    async def add(self, role: Role) -> None:
        obj = RoleModel(id=UUID(role.id), tenant_id=role.tenant_id, name=role.name, description=role.description)
        self.s.add(obj)
        await self.s.commit()

    async def get(self, role_id: str) -> Role | None:
        res = await self.s.execute(
            select(RoleModel).options(selectinload(RoleModel.permissions)).where(RoleModel.id == UUID(role_id))
        )
        m = res.scalars().first()
        return _to_role(m) if m else None

    async def list(self, tenant_id: str | None = None) -> list[Role]:
        stmt = select(RoleModel).options(selectinload(RoleModel.permissions))
        if tenant_id is not None:
            stmt = stmt.where(RoleModel.tenant_id == tenant_id)
        res = await self.s.execute(stmt)
        return [_to_role(m) for m in res.scalars().all()]

    async def delete(self, role_id: str) -> bool:
        res = await self.s.execute(delete(RoleModel).where(RoleModel.id == UUID(role_id)))
        await self.s.commit()
        return res.rowcount > 0

    async def assign_permission(self, role_id: str, permission_id: str) -> None:
        stmt = (
            pg_insert(role_permissions)
            .values(role_id=UUID(role_id), permission_id=UUID(permission_id))
            .on_conflict_do_nothing(
                index_elements=[role_permissions.c.role_id, role_permissions.c.permission_id]
            )
        )
        await self.s.execute(stmt)
        await self.s.commit()

    async def remove_permission(self, role_id: str, permission_id: str) -> None:
        await self.s.execute(
            delete(role_permissions).where(
                role_permissions.c.role_id == UUID(role_id),
                role_permissions.c.permission_id == UUID(permission_id)
            )
        )
        await self.s.commit()

class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.s = session

    async def add(self, group: Group) -> None:
        obj = GroupModel(id=UUID(group.id), tenant_id=group.tenant_id, name=group.name, description=group.description)
        self.s.add(obj)
        await self.s.commit()

    async def get(self, group_id: str) -> Group | None:
        res = await self.s.execute(
            select(GroupModel).options(selectinload(GroupModel.roles)).where(GroupModel.id == UUID(group_id))
        )
        m = res.scalars().first()
        return _to_group(m) if m else None

    async def list(self, tenant_id: str | None = None) -> list[Group]:
        stmt = select(GroupModel).options(selectinload(GroupModel.roles))
        if tenant_id is not None:
            stmt = stmt.where(GroupModel.tenant_id == tenant_id)
        res = await self.s.execute(stmt)
        return [_to_group(m) for m in res.scalars().all()]

    async def delete(self, group_id: str) -> bool:
        res = await self.s.execute(delete(GroupModel).where(GroupModel.id == UUID(group_id)))
        await self.s.commit()
        return res.rowcount > 0

    async def assign_role(self, group_id: str, role_id: str) -> None:
        stmt = (
            pg_insert(group_roles)
            .values(group_id=UUID(group_id), role_id=UUID(role_id))
            .on_conflict_do_nothing(
                index_elements=[group_roles.c.group_id, group_roles.c.role_id]
            )
        )
        await self.s.execute(stmt)
        await self.s.commit()

    async def remove_role(self, group_id: str, role_id: str) -> None:
        await self.s.execute(
            delete(group_roles).where(group_roles.c.group_id == UUID(group_id), group_roles.c.role_id == UUID(role_id))
        )
        await self.s.commit()

class SQLAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.s = session

    async def add(self, account: Account) -> None:
        obj = AccountModel(id=UUID(account.id), tenant_id=account.tenant_id, username=account.username, email=account.email)
        self.s.add(obj)
        await self.s.commit()

    async def get(self, account_id: str) -> Account | None:
        res = await self.s.execute(
            select(AccountModel).options(selectinload(AccountModel.roles), selectinload(AccountModel.groups)).where(AccountModel.id == UUID(account_id))
        )
        m = res.scalars().first()
        return _to_account(m) if m else None

    async def list(self, tenant_id: str | None = None) -> list[Account]:
        stmt = select(AccountModel).options(selectinload(AccountModel.roles), selectinload(AccountModel.groups))
        if tenant_id is not None:
            stmt = stmt.where(AccountModel.tenant_id == tenant_id)
        res = await self.s.execute(stmt)
        return [_to_account(m) for m in res.scalars().all()]

    async def delete(self, account_id: str) -> bool:
        res = await self.s.execute(delete(AccountModel).where(AccountModel.id == UUID(account_id)))
        await self.s.commit()
        return res.rowcount > 0

    async def assign_role(self, account_id: str, role_id: str) -> None:
        stmt = (
            pg_insert(user_roles)
            .values(account_id=UUID(account_id), role_id=UUID(role_id))
            .on_conflict_do_nothing(
                index_elements=[user_roles.c.account_id, user_roles.c.role_id]
            )
        )
        await self.s.execute(stmt)
        await self.s.commit()

    async def remove_role(self, account_id: str, role_id: str) -> None:
        await self.s.execute(
            delete(user_roles).where(user_roles.c.account_id == UUID(account_id), user_roles.c.role_id == UUID(role_id))
        )
        await self.s.commit()

    async def assign_group(self, account_id: str, group_id: str) -> None:
        stmt = (
            pg_insert(user_groups)
            .values(account_id=UUID(account_id), group_id=UUID(group_id))
            .on_conflict_do_nothing(
                index_elements=[user_groups.c.account_id, user_groups.c.group_id]
            )
        )
        await self.s.execute(stmt)
        await self.s.commit()

    async def remove_group(self, account_id: str, group_id: str) -> None:
        await self.s.execute(
            delete(user_groups).where(user_groups.c.account_id == UUID(account_id), user_groups.c.group_id == UUID(group_id))
        )
        await self.s.commit()

class SQLAlchemyResourceRepository(ResourceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.s = session

    async def add(self, res: Resource) -> None:
        obj = ResourceModel(
            id=UUID(res.id),
            type=res.type,
            name=res.name,
            tenant_id=res.tenant_id,
            owner_id=UUID(res.owner_id) if res.owner_id else None,
            resource_metadata=res.resource_metadata,
        )
        self.s.add(obj)
        await self.s.commit()

    async def get(self, res_id: str) -> Resource | None:
        m = await self.s.get(ResourceModel, UUID(res_id))
        return _to_resource(m) if m else None

    async def list(self, tenant_id: str | None = None) -> list[Resource]:
        stmt = select(ResourceModel)
        if tenant_id is not None:
            stmt = stmt.where(ResourceModel.tenant_id == tenant_id)
        res = await self.s.execute(stmt)
        return [_to_resource(m) for m in res.scalars().all()]

    async def delete(self, res_id: str) -> bool:
        res = await self.s.execute(
            delete(ResourceModel).where(ResourceModel.id == UUID(res_id))
        )
        await self.s.commit()
        return res.rowcount > 0


class AuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.s = session

    async def record(self, *, account_id: str, action: str, resource: str | None, result: bool, message: str | None = None) -> None:
        obj = AuditLogModel(
            id=uuid4(),  
            account_id=UUID(account_id),
            action=action,
            resource=resource,
            result=result,
            message=message,
        )
        self.s.add(obj)
        await self.s.commit()
