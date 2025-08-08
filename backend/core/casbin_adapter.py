# backend/core/casbin_adapter.py
from __future__ import annotations
from dataclasses import dataclass
import casbin


__all__ = ["CasbinEngine"]

@dataclass(slots=True)
class CasbinEngine:
    """Casbin 包装。
    注意：这里假设内部已构建好 enforcer（model+adapter），仅提供调用外观。
    """
    _enforcer: "casbin.Enforcer"  # 运行期注入
    _domain_enabled: bool = True  # 租户隔离作为 domain

    # ---- 授权策略录入 ----
    def add_permission_for_user(self, role_id: str, tenant_id: str|None, resource: str, action: str) -> None:
        if self._domain_enabled:
            self._enforcer.add_policy(role_id, tenant_id or "*", resource, action)

    def add_role_for_account(self, account_id: str, tenant_id: str|None, role_id: str) -> None:
        if self._domain_enabled:
            self._enforcer.add_grouping_policy(account_id, role_id, tenant_id or "*")

    def add_role_for_group(self, group_id: str, tenant_id: str|None, role_id: str) -> None:
        if self._domain_enabled:
            self._enforcer.add_grouping_policy(group_id, role_id, tenant_id or "*")

    def add_group_for_account(self, account_id: str, tenant_id: str|None, group_id: str) -> None:
        if self._domain_enabled:
            self._enforcer.add_grouping_policy(account_id, group_id, tenant_id or "*")

    # ---- 回收/解绑 ----
    def remove_permission_from_user(self, role_id: str, tenant_id: str|None, resource: str, action: str) -> None:
        self._enforcer.remove_policy(role_id, tenant_id or "*", resource, action)

    def remove_role_for_account(self, account_id: str, tenant_id: str|None, role_id: str) -> None:
        self._enforcer.remove_grouping_policy(account_id, role_id, tenant_id or "*")

    def remove_role_for_group(self, group_id: str, tenant_id: str|None, role_id: str) -> None:
        self._enforcer.remove_grouping_policy(group_id, role_id, tenant_id or "*")

    def remove_group_for_account(self, account_id: str, tenant_id: str|None, group_id: str) -> None:
        self._enforcer.remove_grouping_policy(account_id, group_id, tenant_id or "*")

    def remove_filtered_policies_for_subject(self, subject_id: str) -> None:
        # 删除 subject 相关的所有分组与策略（用于彻底删除账号/组/角色时清理）
        self._enforcer.remove_filtered_grouping_policy(0, subject_id)
        self._enforcer.remove_filtered_policy(0, subject_id)

    # ---- 决策 ----
    def enforce(self, account_id: str, tenant_id: str|None, resource: str, action: str) -> bool:
        if self._domain_enabled:
            return bool(self._enforcer.enforce(account_id, tenant_id or "*", resource, action))
        return bool(self._enforcer.enforce(account_id, resource, action))
