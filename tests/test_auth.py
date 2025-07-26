"""AuthService 单元测试。

这些测试验证了 ``AuthService`` 的基本功能，包括：
 - 直接为账户分配角色并继承权限；
 - 通过用户组分配角色给账户；
 - 租户隔离逻辑；
 - 拒绝未授权访问。

测试使用标准库 ``unittest``，只依赖公开 API，避免耦合内部实现。
"""

from __future__ import annotations

import unittest

try:
    from authone import AuthService, AccessCheckRequest, Settings
except Exception:
    AuthService = None  # type: ignore[assignment]
    AccessCheckRequest = None  # type: ignore[assignment]
    Settings = None  # type: ignore[assignment]


class TestAuthService(unittest.TestCase):
    def test_account_role_permission(self) -> None:
        """账户直接绑定角色并继承权限。"""
        if AuthService is None or Settings is None or AccessCheckRequest is None:
            self.skipTest("Required dependencies are missing")
        settings = Settings()
        svc = AuthService(settings)
        acc = svc.create_account("alice", "alice@example.com", tenant_id="t1")
        role = svc.create_role("t1", "admin")
        perm = svc.create_permission("app:create", "create app")
        svc.assign_permission_to_role(role.id, perm.id)
        svc.assign_role_to_account(acc.id, role.id)
        req = AccessCheckRequest(account_id=acc.id, resource="app", action="create", tenant_id="t1")
        resp = svc.check_access(req)
        self.assertTrue(resp.allowed)

    def test_account_group_role_permission(self) -> None:
        """账户通过用户组继承角色权限。"""
        if AuthService is None or Settings is None or AccessCheckRequest is None:
            self.skipTest("Required dependencies are missing")
        settings = Settings()
        svc = AuthService(settings)
        acc = svc.create_account("bob", "bob@example.com", tenant_id="t1")
        group = svc.create_group("t1", "devs")
        role = svc.create_role("t1", "developer")
        perm = svc.create_permission("module:deploy", "deploy module")
        svc.assign_permission_to_role(role.id, perm.id)
        svc.assign_role_to_group(group.id, role.id)
        svc.assign_group_to_account(acc.id, group.id)
        req = AccessCheckRequest(account_id=acc.id, resource="module", action="deploy", tenant_id="t1")
        resp = svc.check_access(req)
        self.assertTrue(resp.allowed)

    def test_tenant_isolation(self) -> None:
        """租户隔离应阻止不同租户的角色。"""
        if AuthService is None or Settings is None or AccessCheckRequest is None:
            self.skipTest("Required dependencies are missing")
        settings = Settings()
        svc = AuthService(settings)
        acc = svc.create_account("carol", "carol@example.com", tenant_id="t1")
        role = svc.create_role("t2", "crossTenantRole")
        perm = svc.create_permission("app:delete", "delete app")
        svc.assign_permission_to_role(role.id, perm.id)
        svc.assign_role_to_account(acc.id, role.id)
        # 提供 tenant_id 时，应阻止跨租户角色
        req_wrong = AccessCheckRequest(account_id=acc.id, resource="app", action="delete", tenant_id="t1")
        resp_wrong = svc.check_access(req_wrong)
        self.assertFalse(resp_wrong.allowed)
        # 如果不提供 tenant_id，则不检查租户
        req_no_tenant = AccessCheckRequest(account_id=acc.id, resource="app", action="delete")
        resp_no = svc.check_access(req_no_tenant)
        self.assertTrue(resp_no.allowed)

    def test_unauthorized(self) -> None:
        """未授权访问应被拒绝。"""
        if AuthService is None or Settings is None or AccessCheckRequest is None:
            self.skipTest("Required dependencies are missing")
        settings = Settings()
        svc = AuthService(settings)
        acc = svc.create_account("dave", "dave@example.com", tenant_id="t1")
        perm = svc.create_permission("file:read", "read file")
        role = svc.create_role("t1", "reader")
        svc.assign_permission_to_role(role.id, perm.id)
        # 未将角色赋予账户
        req = AccessCheckRequest(account_id=acc.id, resource="file", action="read", tenant_id="t1")
        resp = svc.check_access(req)
        self.assertFalse(resp.allowed)


if __name__ == "__main__":
    unittest.main()
