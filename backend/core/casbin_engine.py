from __future__ import annotations
from dataclasses import dataclass
import casbin

@dataclass(slots=True)
class CasbinEngine:
    _enforcer: casbin.Enforcer
    _use_domain: bool = True

    def add_permission_for_user(self, role_id: str, tenant_id: str | None, resource: str, action: str) -> None:
        self._enforcer.add_policy(role_id, tenant_id or "*", resource, action)

    def remove_permission_from_user(self, role_id: str, tenant_id: str | None, resource: str, action: str) -> None:
        self._enforcer.remove_policy(role_id, tenant_id or "*", resource, action)

    def add_role_for_account(self, account_id: str, tenant_id: str | None, role_id: str) -> None:
        self._enforcer.add_grouping_policy(account_id, role_id, tenant_id or "*")

    def remove_role_for_account(self, account_id: str, tenant_id: str | None, role_id: str) -> None:
        self._enforcer.remove_grouping_policy(account_id, role_id, tenant_id or "*")

    def add_role_for_group(self, group_id: str, tenant_id: str | None, role_id: str) -> None:
        self._enforcer.add_grouping_policy(group_id, role_id, tenant_id or "*")

    def remove_role_for_group(self, group_id: str, tenant_id: str | None, role_id: str) -> None:
        self._enforcer.remove_grouping_policy(group_id, role_id, tenant_id or "*")

    def add_group_for_account(self, account_id: str, tenant_id: str | None, group_id: str) -> None:
        self._enforcer.add_grouping_policy(account_id, group_id, tenant_id or "*")

    def remove_group_for_account(self, account_id: str, tenant_id: str | None, group_id: str) -> None:
        self._enforcer.remove_grouping_policy(account_id, group_id, tenant_id or "*")

    def remove_filtered_policies_for_subject(self, subject_id: str) -> None:
        self._enforcer.remove_filtered_grouping_policy(0, subject_id)
        self._enforcer.remove_filtered_policy(0, subject_id)

    def enforce(self, account_id: str, tenant_id: str | None, resource: str, action: str) -> bool:
        return bool(self._enforcer.enforce(account_id, tenant_id or "*", resource, action))