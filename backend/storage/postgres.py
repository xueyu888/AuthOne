"""PostgreSQL 仓库实现。

本模块提供各实体的 PostgreSQL 持久化实现，满足 ``storage.interface``
中定义的各仓库协议。使用 psycopg2 驱动连接数据库，所有 SQL 都
遵循参数化语法以防止 SQL 注入。数据库连接通过 ``Settings`` 中的
``db_url`` 进行配置，支持动态替换。

注意：此实现仅作为示例，并未对连接池、事务等高级特性做完整封装。
在生产环境中建议使用 ``asyncpg``、``sqlalchemy`` 等库来管理连接池。
"""

from __future__ import annotations

import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Sequence

from ..config import Settings
from ..models import Account, Group, Permission, Resource, Role
from .interface import (
    AccountRepository,
    GroupRepository,
    PermissionRepository,
    ResourceRepository,
    RoleRepository,
)

__all__ = [
    "PostgresDatabase",
    "PostgresPermissionRepository",
    "PostgresRoleRepository",
    "PostgresGroupRepository",
    "PostgresAccountRepository",
    "PostgresResourceRepository",
]

logger = logging.getLogger(__name__)


class PostgresDatabase:
    """管理 PostgreSQL 连接。

    该类封装了创建连接和获取游标的逻辑，使仓库实现可以专注于业务
    SQL 而无需关心连接细节。连接配置通过 ``Settings`` 提供，初始化
    后即可复用。如果需要连接池，请在此处扩展。
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._conn = psycopg2.connect(self._settings.db_url, cursor_factory=RealDictCursor)
        self._conn.autocommit = True  # 简化示例，不建议在生产中使用 autocommit

    def cursor(self):  # type: ignore[no-untyped-def]
        return self._conn.cursor()

    def close(self) -> None:
        self._conn.close()


class _BaseRepository:
    """Repository 基类，提供通用初始化和日志。"""

    def __init__(self, db: PostgresDatabase) -> None:
        self._db = db

    def _log(self, message: str) -> None:
        logger.debug(message)


class PostgresPermissionRepository(_BaseRepository, PermissionRepository):
    def add(self, permission: Permission) -> None:
        sql = """
            INSERT INTO permissions (id, name, description)
            VALUES (%s, %s, %s)
        """
        self._log(f"Adding permission {permission.id}")
        with self._db.cursor() as cur:
            cur.execute(sql, (permission.id, permission.name, permission.description))

    def get(self, permission_id: str) -> Optional[Permission]:
        sql = """
            SELECT id, name, description
            FROM permissions
            WHERE id = %s
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (permission_id,))
            row = cur.fetchone()
            if row:
                return Permission(_id=row["id"], _name=row["name"], _description=row["description"])  # type: ignore[call-arg]
            return None

    def list(self, tenant_id: Optional[str] = None) -> List[Permission]:
        # 权限表不区分租户，此处忽略 tenant_id
        sql = """
            SELECT id, name, description
            FROM permissions
        """
        with self._db.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return [
                Permission(_id=row["id"], _name=row["name"], _description=row["description"])  # type: ignore[call-arg]
                for row in rows
            ]


class PostgresRoleRepository(_BaseRepository, RoleRepository):
    def add(self, role: Role) -> None:
        sql = """
            INSERT INTO roles (id, tenant_id, name, description)
            VALUES (%s, %s, %s, %s)
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (role.id, role.tenant_id, role.name, role.description))

    def get(self, role_id: str) -> Optional[Role]:
        sql = """
            SELECT id, tenant_id, name, description
            FROM roles
            WHERE id = %s
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (role_id,))
            row = cur.fetchone()
            if row:
                return Role(
                    _id=row["id"],
                    _tenant_id=row["tenant_id"],
                    _name=row["name"],
                    _description=row["description"],
                    _permissions=self._fetch_role_permissions(role_id),
                )
            return None

    def list(self, tenant_id: Optional[str] = None) -> List[Role]:
        sql = """
            SELECT id, tenant_id, name, description
            FROM roles
        """
        params: Sequence[object] = []
        if tenant_id is not None:
            sql += " WHERE tenant_id = %s"
            params = [tenant_id]
        with self._db.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            roles: List[Role] = []
            for row in rows:
                role_id = row["id"]
                perms = self._fetch_role_permissions(role_id)
                roles.append(
                    Role(
                        _id=row["id"],
                        _tenant_id=row["tenant_id"],
                        _name=row["name"],
                        _description=row["description"],
                        _permissions=perms,
                    )
                )
            return roles

    def assign_permission(self, role_id: str, permission_id: str) -> None:
        sql = """
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (role_id, permission_id))

    def _fetch_role_permissions(self, role_id: str) -> List[str]:
        sql = """
            SELECT permission_id
            FROM role_permissions
            WHERE role_id = %s
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (role_id,))
            rows = cur.fetchall()
            return [row["permission_id"] for row in rows]


class PostgresGroupRepository(_BaseRepository, GroupRepository):
    def add(self, group: Group) -> None:
        sql = """
            INSERT INTO groups (id, tenant_id, name, description)
            VALUES (%s, %s, %s, %s)
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (group.id, group.tenant_id, group.name, group.description))

    def get(self, group_id: str) -> Optional[Group]:
        sql = """
            SELECT id, tenant_id, name, description
            FROM groups
            WHERE id = %s
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (group_id,))
            row = cur.fetchone()
            if row:
                roles = self._fetch_group_roles(group_id)
                return Group(
                    _id=row["id"],
                    _tenant_id=row["tenant_id"],
                    _name=row["name"],
                    _description=row["description"],
                    _roles=roles,
                )
            return None

    def list(self, tenant_id: Optional[str] = None) -> List[Group]:
        sql = """
            SELECT id, tenant_id, name, description
            FROM groups
        """
        params: Sequence[object] = []
        if tenant_id is not None:
            sql += " WHERE tenant_id = %s"
            params = [tenant_id]
        with self._db.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            groups: List[Group] = []
            for row in rows:
                group_id = row["id"]
                roles = self._fetch_group_roles(group_id)
                groups.append(
                    Group(
                        _id=row["id"],
                        _tenant_id=row["tenant_id"],
                        _name=row["name"],
                        _description=row["description"],
                        _roles=roles,
                    )
                )
            return groups

    def assign_role(self, group_id: str, role_id: str) -> None:
        sql = """
            INSERT INTO group_roles (group_id, role_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (group_id, role_id))

    def _fetch_group_roles(self, group_id: str) -> List[str]:
        sql = """
            SELECT role_id
            FROM group_roles
            WHERE group_id = %s
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (group_id,))
            rows = cur.fetchall()
            return [row["role_id"] for row in rows]


class PostgresAccountRepository(_BaseRepository, AccountRepository):
    def add(self, account: Account) -> None:
        sql = """
            INSERT INTO accounts (id, tenant_id, username, email)
            VALUES (%s, %s, %s, %s)
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (account.id, account.tenant_id, account.username, account.email))

    def get(self, account_id: str) -> Optional[Account]:
        sql = """
            SELECT id, tenant_id, username, email
            FROM accounts
            WHERE id = %s
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (account_id,))
            row = cur.fetchone()
            if row:
                roles = self._fetch_account_roles(account_id)
                groups = self._fetch_account_groups(account_id)
                return Account(
                    _id=row["id"],
                    _username=row["username"],
                    _email=row["email"],
                    _tenant_id=row["tenant_id"],
                    _roles=roles,
                    _groups=groups,
                )
            return None

    def list(self, tenant_id: Optional[str] = None) -> List[Account]:
        sql = """
            SELECT id, tenant_id, username, email
            FROM accounts
        """
        params: Sequence[object] = []
        if tenant_id is not None:
            sql += " WHERE tenant_id = %s"
            params = [tenant_id]
        with self._db.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            accounts: List[Account] = []
            for row in rows:
                account_id = row["id"]
                roles = self._fetch_account_roles(account_id)
                groups = self._fetch_account_groups(account_id)
                accounts.append(
                    Account(
                        _id=row["id"],
                        _username=row["username"],
                        _email=row["email"],
                        _tenant_id=row["tenant_id"],
                        _roles=roles,
                        _groups=groups,
                    )
                )
            return accounts

    def assign_role(self, account_id: str, role_id: str) -> None:
        sql = """
            INSERT INTO user_roles (account_id, role_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (account_id, role_id))

    def assign_group(self, account_id: str, group_id: str) -> None:
        sql = """
            INSERT INTO user_groups (account_id, group_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (account_id, group_id))

    def _fetch_account_roles(self, account_id: str) -> List[str]:
        sql = """
            SELECT role_id
            FROM user_roles
            WHERE account_id = %s
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (account_id,))
            return [row["role_id"] for row in cur.fetchall()]

    def _fetch_account_groups(self, account_id: str) -> List[str]:
        sql = """
            SELECT group_id
            FROM user_groups
            WHERE account_id = %s
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (account_id,))
            return [row["group_id"] for row in cur.fetchall()]


class PostgresResourceRepository(_BaseRepository, ResourceRepository):
    def add(self, resource: Resource) -> None:
        sql = """
            INSERT INTO resources (id, type, name, tenant_id, owner_id, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        metadata_str = json.dumps(resource.metadata)  # type: ignore[name-defined]
        with self._db.cursor() as cur:
            cur.execute(
                sql,
                (
                    resource.id,
                    resource.type,
                    resource.name,
                    resource.tenant_id,
                    resource.owner_id,
                    metadata_str,
                ),
            )

    def get(self, resource_id: str) -> Optional[Resource]:
        sql = """
            SELECT id, type, name, tenant_id, owner_id, metadata
            FROM resources
            WHERE id = %s
        """
        with self._db.cursor() as cur:
            cur.execute(sql, (resource_id,))
            row = cur.fetchone()
            if row:
                meta = row["metadata"]
                if isinstance(meta, str):
                    try:
                        import json
                        metadata_dict = json.loads(meta)
                    except Exception:
                        metadata_dict = {}
                else:
                    metadata_dict = meta or {}
                return Resource(
                    _id=row["id"],
                    _type=row["type"],
                    _name=row["name"],
                    _tenant_id=row["tenant_id"],
                    _owner_id=row["owner_id"],
                    _metadata=metadata_dict,
                )
            return None

    def list(self, tenant_id: Optional[str] = None) -> List[Resource]:
        sql = """
            SELECT id, type, name, tenant_id, owner_id, metadata
            FROM resources
        """
        params: Sequence[object] = []
        if tenant_id is not None:
            sql += " WHERE tenant_id = %s"
            params = [tenant_id]
        with self._db.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            resources: List[Resource] = []
            for row in rows:
                meta = row["metadata"]
                if isinstance(meta, str):
                    try:
                        import json
                        metadata_dict = json.loads(meta)
                    except Exception:
                        metadata_dict = {}
                else:
                    metadata_dict = meta or {}
                resources.append(
                    Resource(
                        _id=row["id"],
                        _type=row["type"],
                        _name=row["name"],
                        _tenant_id=row["tenant_id"],
                        _owner_id=row["owner_id"],
                        _metadata=metadata_dict,
                    )
                )
            return resources
