"""Casbin PostgreSQL/SQLite 适配器和引擎封装。

支持 Casbin 策略持久化至数据库，兼容 PostgreSQL 与 SQLite。
实现了 `DatabaseAdapter`（符合 `casbin.persist.Adapter` 接口）和 `CasbinEngine`
（封装 `casbin.Enforcer` 的常用操作）。

依赖：`casbin`、`sqlalchemy`
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional, Sequence

import casbin
from casbin import persist
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Row

from ..config import Settings

__all__ = ["CasbinRule", "DatabaseAdapter", "CasbinEngine"]

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CasbinRule:
    """表示一条 Casbin 策略行。"""

    id: str
    ptype: str
    v0: Optional[str] = None
    v1: Optional[str] = None
    v2: Optional[str] = None
    v3: Optional[str] = None
    v4: Optional[str] = None
    v5: Optional[str] = None


class DatabaseAdapter(persist.Adapter):
    """Casbin 通用持久化适配器，支持 PostgreSQL 和 SQLite。"""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._engine: Engine = create_engine(settings.db_url_sync, future=True)
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Create policy table if it does not exist.

        This is primarily useful for test environments where an in-memory
        SQLite database is used. Production databases are expected to manage
        migrations separately. The table schema matches the ``CasbinRuleModel``
        defined in :mod:`backend.db`.
        """
        ddl = text(
            f"""
            CREATE TABLE IF NOT EXISTS {self._settings.casbin_policy_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ptype TEXT,
                v0 TEXT, v1 TEXT, v2 TEXT, v3 TEXT, v4 TEXT, v5 TEXT
            )
            """
        )
        with self._engine.begin() as conn:
            conn.execute(ddl)

    def _save_policy_line(self, ptype: str, rule: Sequence[str]) -> None:
        vals: List[Optional[str]] = list(rule) + [None] * (6 - len(rule))
        sql = text(f"""
            INSERT INTO {self._settings.casbin_policy_table}
            (ptype, v0, v1, v2, v3, v4, v5)
            VALUES (:ptype, :v0, :v1, :v2, :v3, :v4, :v5)
        """)
        with self._engine.begin() as conn:
            conn.execute(sql, {
                "ptype": ptype,
                "v0": vals[0], "v1": vals[1], "v2": vals[2],
                "v3": vals[3], "v4": vals[4], "v5": vals[5],
            })

    def load_policy(self, model: casbin.Model) -> None:
        sql = text(f"SELECT ptype, v0, v1, v2, v3, v4, v5 FROM {self._settings.casbin_policy_table}")
        with self._engine.connect() as conn:
            rows = conn.execute(sql).mappings().all()
            for row in rows:
                ptype = row["ptype"]
                rule = [row[f"v{i}"] for i in range(6) if row[f"v{i}"] is not None]
                line = ptype + ", " + ", ".join(rule)
                persist.load_policy_line(line, model)

    def save_policy(self, model: casbin.Model) -> bool:
        with self._engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {self._settings.casbin_policy_table}"))
        for sec in ["p", "g"]:
            if sec not in model.model:
                continue
            for ptype, ast in model.model[sec].items():
                for rule in ast.policy:
                    self._save_policy_line(ptype, rule)
        return True

    def add_policy(self, sec: str, ptype: str, rule: Sequence[str]) -> None:
        self._save_policy_line(ptype, list(rule))

    def remove_policy(self, sec: str, ptype: str, rule: Sequence[str]) -> None:
        conds = [f"v{i} = :v{i}" for i in range(len(rule))]
        params = {f"v{i}": v for i, v in enumerate(rule)}
        sql = f"DELETE FROM {self._settings.casbin_policy_table} WHERE ptype = :ptype"
        if conds:
            sql += " AND " + " AND ".join(conds)
        with self._engine.begin() as conn:
            conn.execute(text(sql), {"ptype": ptype, **params})

    def remove_filtered_policy(
        self,
        sec: str,
        ptype: str,
        field_index: int,
        *field_values: str,
    ) -> None:
        conditions: List[str] = []
        params: dict = {"ptype": ptype}
        for idx, val in enumerate(field_values):
            if val:
                key = f"v{field_index + idx}"
                conditions.append(f"{key} = :{key}")
                params[key] = val
        sql = f"DELETE FROM {self._settings.casbin_policy_table} WHERE ptype = :ptype"
        if conditions:
            sql += " AND " + " AND ".join(conditions)
        with self._engine.begin() as conn:
            conn.execute(text(sql), params)


class CasbinEngine:
    """Casbin 引擎封装。"""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        adapter = DatabaseAdapter(settings)
        self._enforcer = casbin.Enforcer(self._settings.casbin_model_path, adapter)
        self._enforcer.load_policy()

    def enforce(
        self,
        account: str,
        tenant_id: Optional[str],
        resource: str,
        action: str,
    ) -> bool:
        domain = tenant_id or "public"
        return bool(self._enforcer.enforce(account, domain, resource, action))

    def add_permission_for_user(
        self, subject: str, tenant_id: Optional[str], resource: str, action: str
    ) -> None:
        domain = tenant_id or "public"
        self._enforcer.add_policy(subject, domain, resource, action)
        self._enforcer.save_policy()

    def add_role_for_account(
        self, account: str, tenant_id: Optional[str], role_name: str
    ) -> None:
        domain = tenant_id or "public"
        self._enforcer.add_role_for_user_in_domain(account, role_name, domain)
        self._enforcer.save_policy()

    def add_role_for_group(
        self, group_name: str, tenant_id: Optional[str], role_name: str
    ) -> None:
        domain = tenant_id or "public"
        self._enforcer.add_role_for_user_in_domain(group_name, role_name, domain)
        self._enforcer.save_policy()

    def add_group_for_account(
        self, account: str, tenant_id: Optional[str], group_name: str
    ) -> None:
        domain = tenant_id or "public"
        self._enforcer.add_role_for_user_in_domain(account, group_name, domain)
        self._enforcer.save_policy()