"""SQLAlchemy 仓库实现。

本模块实现了各实体仓库协议，使用 SQLAlchemy ORM 与 PostgreSQL 交互。
仓库负责在领域模型与数据库模型之间转换，所有操作均以事务方式提交。
同时包含审计日志仓库，用于记录每次权限检查的结果。
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Account, Group, Permission, Resource, Role
from ..db import (
    AccountModel,
    AuditLogModel,
    GroupModel,
    PermissionModel,
    ResourceModel,
    RoleModel,
)
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
    def __init__(self, session: Session) -> None:
        self._session = session


class SQLAlchemyPermissionRepository(_BaseRepo, PermissionRepository):
    def add(self, permission: Permission) -> None:
        model = PermissionModel(id=permission.id, name=permission.name, description=permission.description)
        self._session.add(model)
        self._session.commit()

    def get(self, permission_id: str) -> Optional[Permission]:
        obj = self._session.get(PermissionModel, permission_id)
        if not obj:
            return None
        return Permission(_id=str(obj.id), _name=obj.name, _description=obj.description)

    def list(self, tenant_id: Optional[str] = None) -> List[Permission]:  # tenant_id ignored
        objs = self._session.query(PermissionModel).all()
        return [Permission(_id=str(o.id), _name=o.name, _description=o.description) for o in objs]


class SQLAlchemyRoleRepository(_BaseRepo, RoleRepository):
    def add(self, role: Role) -> None:
        model = RoleModel(id=role.id, tenant_id=role.tenant_id, name=role.name, description=role.description)
        self._session.add(model)
        self._session.commit()

    def get(self, role_id: str) -> Optional[Role]:
        obj: Optional[RoleModel] = self._session.get(RoleModel, role_id)
        if not obj:
            return None
        # collect permission ids
        perm_ids = [str(p.id) for p in obj.permissions]
        return Role(
            _id=str(obj.id),
            _tenant_id=obj.tenant_id,
            _name=obj.name,
            _description=obj.description or "",
            _permissions=perm_ids,
        )

    def list(self, tenant_id: Optional[str] = None) -> List[Role]:
        q = self._session.query(RoleModel)
        if tenant_id is not None:
            q = q.filter(RoleModel.tenant_id == tenant_id)
        roles: List[Role] = []
        for obj in q:
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

    def assign_permission(self, role_id: str, permission_id: str) -> None:
        role_obj: RoleModel = self._session.get(RoleModel, role_id)  # type: ignore[assignment]
        perm_obj: PermissionModel = self._session.get(PermissionModel, permission_id)  # type: ignore[assignment]
        if role_obj is None or perm_obj is None:
            raise ValueError("role or permission not found")
        if perm_obj not in role_obj.permissions:
            role_obj.permissions.append(perm_obj)
            self._session.commit()


class SQLAlchemyGroupRepository(_BaseRepo, GroupRepository):
    def add(self, group: Group) -> None:
        model = GroupModel(
            id=group.id, tenant_id=group.tenant_id, name=group.name, description=group.description
        )
        self._session.add(model)
        self._session.commit()

    def get(self, group_id: str) -> Optional[Group]:
        obj: Optional[GroupModel] = self._session.get(GroupModel, group_id)
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

    def list(self, tenant_id: Optional[str] = None) -> List[Group]:
        q = self._session.query(GroupModel)
        if tenant_id is not None:
            q = q.filter(GroupModel.tenant_id == tenant_id)
        groups: List[Group] = []
        for obj in q:
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

    def assign_role(self, group_id: str, role_id: str) -> None:
        group_obj: GroupModel = self._session.get(GroupModel, group_id)  # type: ignore[assignment]
        role_obj: RoleModel = self._session.get(RoleModel, role_id)  # type: ignore[assignment]
        if group_obj is None or role_obj is None:
            raise ValueError("group or role not found")
        if role_obj not in group_obj.roles:
            group_obj.roles.append(role_obj)
            self._session.commit()


class SQLAlchemyAccountRepository(_BaseRepo, AccountRepository):
    def add(self, account: Account) -> None:
        model = AccountModel(
            id=account.id, tenant_id=account.tenant_id, username=account.username, email=account.email
        )
        self._session.add(model)
        self._session.commit()

    def get(self, account_id: str) -> Optional[Account]:
        obj: Optional[AccountModel] = self._session.get(AccountModel, account_id)
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

    def list(self, tenant_id: Optional[str] = None) -> List[Account]:
        q = self._session.query(AccountModel)
        if tenant_id is not None:
            q = q.filter(AccountModel.tenant_id == tenant_id)
        accounts: List[Account] = []
        for obj in q:
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

    def assign_role(self, account_id: str, role_id: str) -> None:
        acc_obj: AccountModel = self._session.get(AccountModel, account_id)  # type: ignore[assignment]
        role_obj: RoleModel = self._session.get(RoleModel, role_id)  # type: ignore[assignment]
        if acc_obj is None or role_obj is None:
            raise ValueError("account or role not found")
        if role_obj not in acc_obj.roles:
            acc_obj.roles.append(role_obj)
            self._session.commit()

    def assign_group(self, account_id: str, group_id: str) -> None:
        acc_obj: AccountModel = self._session.get(AccountModel, account_id)  # type: ignore[assignment]
        group_obj: GroupModel = self._session.get(GroupModel, group_id)  # type: ignore[assignment]
        if acc_obj is None or group_obj is None:
            raise ValueError("account or group not found")
        if group_obj not in acc_obj.groups:
            acc_obj.groups.append(group_obj)
            self._session.commit()


class SQLAlchemyResourceRepository(_BaseRepo, ResourceRepository):
    def add(self, resource: Resource) -> None:
        model = ResourceModel(
            id=resource.id,
            type=resource.type,
            name=resource.name,
            tenant_id=resource.tenant_id,
            owner_id=resource.owner_id,
            metadata=resource.metadata,
        )
        self._session.add(model)
        self._session.commit()

    def get(self, resource_id: str) -> Optional[Resource]:
        obj: Optional[ResourceModel] = self._session.get(ResourceModel, resource_id)
        if not obj:
            return None
        return Resource(
            _id=str(obj.id),
            _type=obj.type,
            _name=obj.name,
            _tenant_id=obj.tenant_id,
            _owner_id=obj.owner_id,
            _metadata=obj.metadata or {},
        )

    def list(self, tenant_id: Optional[str] = None) -> List[Resource]:
        q = self._session.query(ResourceModel)
        if tenant_id is not None:
            q = q.filter(ResourceModel.tenant_id == tenant_id)
        resources: List[Resource] = []
        for obj in q:
            resources.append(
                Resource(
                    _id=str(obj.id),
                    _type=obj.type,
                    _name=obj.name,
                    _tenant_id=obj.tenant_id,
                    _owner_id=obj.owner_id,
                    _metadata=obj.metadata or {},
                )
            )
        return resources


class AuditLogRepository(_BaseRepo):
    """审计日志仓库。"""

    def record(
        self,
        account_id: str,
        action: str,
        resource: str,
        result: bool,
        message: str = "",
    ) -> None:
        log = AuditLogModel(
            id=str(uuid.uuid4()),
            account_id=account_id,
            action=action,
            resource=resource,
            result=result,
            message=message,
            timestamp=datetime.utcnow(),
        )
        self._session.add(log)
        self._session.commit()
