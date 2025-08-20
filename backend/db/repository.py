from __future__ import annotations

from typing import Generic, Protocol, TypeVar, Optional, Sequence
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .db_models import AccountModel, GroupModel, PermissionModel, RoleModel, ResourceModel

# A generic TypeVar to represent the model type (e.g., AccountModel).
T = TypeVar("T")


class Repository(Protocol, Generic[T]):
    """A protocol defining the standard interface for a repository.

    This defines the contract that all repository classes must adhere to,
    enabling static analysis and dependency injection without forcing inheritance.
    """

    async def get(self, id: UUID) -> Optional[T]:
        """Retrieves an entity by its unique identifier."""
        ...

    async def list(self, **filters) -> Sequence[T]:
        """Lists entities, optionally applying filters."""
        ...

    def add(self, entity: T) -> None:
        """Adds a new entity to the session."""
        ...

    async def delete(self, id: UUID) -> bool:
        """Deletes an entity by its unique identifier."""
        ...


# --- Concrete Repository Implementations ---

class PermissionRepository:
    """Repository for PermissionModel operations."""
    _model = PermissionModel

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, id: UUID) -> Optional[PermissionModel]:
        return await self._session.get(self._model, id)

    async def get_by_name(self, name: str) -> Optional[PermissionModel]:
        q = select(self._model).where(self._model.name == name)
        return (await self._session.execute(q)).scalar_one_or_none()

    async def list(self, **filters) -> Sequence[PermissionModel]:
        name = filters.get("name")
        q = select(self._model).order_by(self._model.name)
        if name:
            q = q.where(self._model.name == name)
        return (await self._session.execute(q)).scalars().all()

    def add(self, entity: PermissionModel) -> None:
        self._session.add(entity)

    async def delete(self, id: UUID) -> bool:
        obj = await self._session.get(self._model, id)
        if not obj:
            return False
        await self._session.delete(obj)
        return True


class RoleRepository:
    """Repository for RoleModel operations."""
    _model = RoleModel

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, id: UUID) -> Optional[RoleModel]:
        return await self._session.get(self._model, id)
    
    async def get_with_permissions(self, id: UUID) -> Optional[RoleModel]:
        return await self._session.get(self._model, id, options=[selectinload(RoleModel.permissions)])

    async def get_by_name(self, tenant_id: Optional[str], name: str) -> Optional[RoleModel]:
        q = select(self._model).where(
            and_(self._model.tenant_id == tenant_id, self._model.name == name)
        )
        return (await self._session.execute(q)).scalar_one_or_none()

    async def list(self, **filters) -> Sequence[RoleModel]:
        tenant_id = filters.get("tenant_id")
        name = filters.get("name")
        
        q = select(self._model).order_by(self._model.name)
        if tenant_id is not None:
            q = q.where(self._model.tenant_id == tenant_id)
        if name:
            q = q.where(self._model.name == name)
        return (await self._session.execute(q)).scalars().all()
    
    def add(self, entity: RoleModel) -> None:
        self._session.add(entity)

    async def delete(self, id: UUID) -> bool:
        obj = await self._session.get(self._model, id)
        if not obj:
            return False
        await self._session.delete(obj)
        return True


class GroupRepository:
    """Repository for GroupModel operations."""
    _model = GroupModel

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, id: UUID) -> Optional[GroupModel]:
        return await self._session.get(self._model, id)
    
    async def get_with_roles(self, id: UUID) -> Optional[GroupModel]:
        return await self._session.get(self._model, id, options=[selectinload(GroupModel.roles)])

    async def list(self, **filters) -> Sequence[GroupModel]:
        tenant_id = filters.get("tenant_id")
        q = select(self._model).order_by(self._model.name)
        if tenant_id is not None:
            q = q.where(self._model.tenant_id == tenant_id)
        return (await self._session.execute(q)).scalars().all()

    def add(self, entity: GroupModel) -> None:
        self._session.add(entity)

    async def delete(self, id: UUID) -> bool:
        obj = await self._session.get(self._model, id)
        if not obj:
            return False
        await self._session.delete(obj)
        return True


class AccountRepository:
    """Repository for AccountModel operations."""
    _model = AccountModel

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, id: UUID) -> Optional[AccountModel]:
        return await self._session.get(self._model, id)

    async def get_with_roles(self, id: UUID) -> Optional[AccountModel]:
        return await self._session.get(self._model, id, options=[selectinload(AccountModel.roles)])

    async def get_with_groups(self, id: UUID) -> Optional[AccountModel]:
        return await self._session.get(self._model, id, options=[selectinload(AccountModel.groups)])

    async def get_by_username(self, tenant_id: Optional[str], username: str) -> Optional[AccountModel]:
        q = select(self._model).where(
            and_(self._model.tenant_id == tenant_id, self._model.username == username)
        )
        return (await self._session.execute(q)).scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[AccountModel]:
        q = select(self._model).where(self._model.email == email)
        return (await self._session.execute(q)).scalar_one_or_none()

    async def list(self, **filters) -> Sequence[AccountModel]:
        tenant_id = filters.get("tenant_id")
        username = filters.get("username")
        
        q = select(self._model).order_by(self._model.username)
        if tenant_id is not None:
            q = q.where(self._model.tenant_id == tenant_id)
        if username:
            q = q.where(self._model.username == username)
        return (await self._session.execute(q)).scalars().all()
    
    def add(self, entity: AccountModel) -> None:
        self._session.add(entity)

    async def delete(self, id: UUID) -> bool:
        obj = await self._session.get(self._model, id)
        if not obj:
            return False
        await self._session.delete(obj)
        return True


class ResourceRepository:
    """Repository for ResourceModel operations."""
    _model = ResourceModel

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, id: UUID) -> Optional[ResourceModel]:
        return await self._session.get(self._model, id)

    async def list(self, **filters) -> Sequence[ResourceModel]:
        tenant_id = filters.get("tenant_id")
        q = select(self._model).order_by(self._model.type, self._model.name)
        if tenant_id is not None:
            q = q.where(self._model.tenant_id == tenant_id)
        return (await self._session.execute(q)).scalars().all()
    
    def add(self, entity: ResourceModel) -> None:
        self._session.add(entity)

    async def delete(self, id: UUID) -> bool:
        obj = await self._session.get(self._model, id)
        if not obj:
            return False
        await self._session.delete(obj)
        return True