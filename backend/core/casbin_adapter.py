"""Casbin engine adapter used by AuthOne.

This module wraps a ``casbin.Enforcer`` and provides convenience
methods for working with domains (tenants) and grouping policies.
The methods defined here are thin wrappers around the underlying
Casbin API.  They are invoked by the service layer to keep the
authorisation engine state in sync with the database.
"""

from __future__ import annotations

from dataclasses import dataclass
import casbin

__all__ = ["CasbinEngine"]


@dataclass(slots=True)
class CasbinEngine:
    """A light wrapper around a Casbin ``Enforcer``.

    This wrapper exposes methods for adding and removing permissions,
    roles and groups using the Casbin API.  It also delegates access
    checks to the underlying enforcer.  The ``_domain_enabled`` flag
    determines whether tenant/domain support is enabled; when true,
    the tenant ID is passed as the second argument to Casbin calls.
    """

    _enforcer: casbin.Enforcer
    _domain_enabled: bool = True

    # Policy management
    def add_permission_for_user(
        self, role_id: str, tenant_id: str | None, resource: str, action: str
    ) -> None:
        if self._domain_enabled:
            self._enforcer.add_policy(role_id, tenant_id or "*", resource, action)

    def add_role_for_account(
        self, account_id: str, tenant_id: str | None, role_id: str
    ) -> None:
        if self._domain_enabled:
            self._enforcer.add_grouping_policy(account_id, role_id, tenant_id or "*")

    def add_role_for_group(
        self, group_id: str, tenant_id: str | None, role_id: str
    ) -> None:
        if self._domain_enabled:
            self._enforcer.add_grouping_policy(group_id, role_id, tenant_id or "*")

    def add_group_for_account(
        self, account_id: str, tenant_id: str | None, group_id: str
    ) -> None:
        if self._domain_enabled:
            self._enforcer.add_grouping_policy(account_id, group_id, tenant_id or "*")

    def remove_permission_from_user(
        self, role_id: str, tenant_id: str | None, resource: str, action: str
    ) -> None:
        self._enforcer.remove_policy(role_id, tenant_id or "*", resource, action)

    def remove_role_for_account(
        self, account_id: str, tenant_id: str | None, role_id: str
    ) -> None:
        self._enforcer.remove_grouping_policy(account_id, role_id, tenant_id or "*")

    def remove_role_for_group(
        self, group_id: str, tenant_id: str | None, role_id: str
    ) -> None:
        self._enforcer.remove_grouping_policy(group_id, role_id, tenant_id or "*")

    def remove_group_for_account(
        self, account_id: str, tenant_id: str | None, group_id: str
    ) -> None:
        self._enforcer.remove_grouping_policy(account_id, group_id, tenant_id or "*")

    def remove_filtered_policies_for_subject(self, subject_id: str) -> None:
        # Remove all grouping policies and permissions associated with the subject
        self._enforcer.remove_filtered_grouping_policy(0, subject_id)
        self._enforcer.remove_filtered_policy(0, subject_id)

    def enforce(
        self, account_id: str, tenant_id: str | None, resource: str, action: str
    ) -> bool:
        if self._domain_enabled:
            return bool(
                self._enforcer.enforce(account_id, tenant_id or "*", resource, action)
            )
        return bool(self._enforcer.enforce(account_id, resource, action))