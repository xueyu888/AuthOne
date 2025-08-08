# backend/core/auth_engine.py
from __future__ import annotations
from dataclasses import dataclass
from .casbin_adapter import CasbinEngine

__all__ = ["AuthEngine"]

@dataclass(slots=True)
class AuthEngine:
    """Casbin 驱动的授权门面：不持有任何内存态 RBAC 数据。"""
    _casbin: CasbinEngine

    @staticmethod
    def _split(name: str) -> tuple[str, str]:
        if ":" not in name:
            raise ValueError(f"permission must be 'resource:action', got {name!r}")
        res, act = name.split(":", 1)
        if not res or not act:
            raise ValueError(f"invalid permission: {name!r}")
        return res, act

    # 写侧（供 Service 调用）
    def grant_permission_to_role(self, role_id: str, tenant_id: str|None, permission_name: str) -> None:
        res, act = self._split(permission_name)
        self._casbin.add_permission_for_user(role_id, tenant_id, res, act)

    def revoke_permission_from_role(self, role_id: str, tenant_id: str|None, permission_name: str) -> None:
        res, act = self._split(permission_name)
        self._casbin.remove_permission_from_user(role_id, tenant_id, res, act)

    def grant_role_to_account(self, account_id: str, tenant_id: str|None, role_id: str) -> None:
        self._casbin.add_role_for_account(account_id, tenant_id, role_id)

    def revoke_role_from_account(self, account_id: str, tenant_id: str|None, role_id: str) -> None:
        self._casbin.remove_role_for_account(account_id, tenant_id, role_id)

    def grant_role_to_group(self, group_id: str, tenant_id: str|None, role_id: str) -> None:
        self._casbin.add_role_for_group(group_id, tenant_id, role_id)

    def revoke_role_from_group(self, group_id: str, tenant_id: str|None, role_id: str) -> None:
        self._casbin.remove_role_for_group(group_id, tenant_id, role_id)

    def add_group_for_account(self, account_id: str, tenant_id: str|None, group_id: str) -> None:
        self._casbin.add_group_for_account(account_id, tenant_id, group_id)

    def remove_group_from_account(self, account_id: str, tenant_id: str|None, group_id: str) -> None:
        self._casbin.remove_group_for_account(account_id, tenant_id, group_id)

    def purge_subject(self, subject_id: str) -> None:
        self._casbin.remove_filtered_policies_for_subject(subject_id)

    # 读侧（鉴权）
    def enforce(self, account_id: str, tenant_id: str|None, resource: str, action: str) -> bool:
        return self._casbin.enforce(account_id, tenant_id, resource, action)
