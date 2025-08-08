"""Facade for authorisation operations using Casbin.

The ``AuthEngine`` encapsulates the Casbin adapter used by the
application and provides a stable interface for granting and revoking
permissions and roles.  It also exposes a simple ``enforce`` method
for performing access checks.  This abstraction allows future
swap-out of the underlying RBAC implementation without affecting
higher layers.
"""

from __future__ import annotations

from dataclasses import dataclass

from .casbin_adapter import CasbinEngine

__all__ = ["AuthEngine"]


@dataclass(slots=True)
class AuthEngine:
    """Casbin-driven authorisation facade."""

    _casbin: CasbinEngine

    @staticmethod
    def _split(name: str) -> tuple[str, str]:
        """Split a permission name of the form ``resource:action``.

        :param name: Permission name string.
        :raises ValueError: if the name is not in the expected format.
        :returns: A tuple ``(resource, action)``.
        """
        if ":" not in name:
            raise ValueError(
                f"permission must be 'resource:action', got {name!r}"
            )
        res, act = name.split(":", 1)
        if not res or not act:
            raise ValueError(f"invalid permission: {name!r}")
        return res, act

    # Granting and revoking
    def grant_permission_to_role(
        self, role_id: str, tenant_id: str | None, permission_name: str
    ) -> None:
        res, act = self._split(permission_name)
        self._casbin.add_permission_for_user(role_id, tenant_id, res, act)

    def revoke_permission_from_role(
        self, role_id: str, tenant_id: str | None, permission_name: str
    ) -> None:
        res, act = self._split(permission_name)
        self._casbin.remove_permission_from_user(role_id, tenant_id, res, act)

    def grant_role_to_account(
        self, account_id: str, tenant_id: str | None, role_id: str
    ) -> None:
        self._casbin.add_role_for_account(account_id, tenant_id, role_id)

    def revoke_role_from_account(
        self, account_id: str, tenant_id: str | None, role_id: str
    ) -> None:
        self._casbin.remove_role_for_account(account_id, tenant_id, role_id)

    def grant_role_to_group(
        self, group_id: str, tenant_id: str | None, role_id: str
    ) -> None:
        self._casbin.add_role_for_group(group_id, tenant_id, role_id)

    def revoke_role_from_group(
        self, group_id: str, tenant_id: str | None, role_id: str
    ) -> None:
        self._casbin.remove_role_for_group(group_id, tenant_id, role_id)

    def add_group_for_account(
        self, account_id: str, tenant_id: str | None, group_id: str
    ) -> None:
        self._casbin.add_group_for_account(account_id, tenant_id, group_id)

    def remove_group_from_account(
        self, account_id: str, tenant_id: str | None, group_id: str
    ) -> None:
        self._casbin.remove_group_for_account(account_id, tenant_id, group_id)

    def purge_subject(self, subject_id: str) -> None:
        self._casbin.remove_filtered_policies_for_subject(subject_id)

    # Enforcement
    def enforce(
        self, account_id: str, tenant_id: str | None, resource: str, action: str
    ) -> bool:
        return self._casbin.enforce(account_id, tenant_id, resource, action)