"""IAMService 的单元测试，使用 Python 内置的 unittest 进行。"""

from __future__ import annotations

import unittest

from iam_service import IAMService, AccessCheckRequest


class TestIAMService(unittest.TestCase):
    """针对 IAMService 功能的测试用例。"""

    def test_direct_role_permission(self) -> None:
        service = IAMService()
        user = service.create_user("alice", "alice@example.com")
        role = service.create_role("admin")
        perm = service.create_permission(action="read", resource_type="dataset", scope="all")
        service.assign_permission_to_role(role.id, perm.id)
        service.assign_role_to_user(user.id, role.id)

        req = AccessCheckRequest(user_id=user.id, resource_type="dataset", resource_id=None, action="read")
        resp = service.check_access(req)
        self.assertTrue(resp.allowed)

    def test_group_role_permission(self) -> None:
        service = IAMService()
        user = service.create_user("bob", "bob@example.com")
        group = service.create_group("editors")
        role = service.create_role("editor_role")
        perm = service.create_permission(action="write", resource_type="dataset", scope="all")
        service.assign_permission_to_role(role.id, perm.id)
        service.assign_role_to_group(group.id, role.id)
        service.assign_user_to_group(user.id, group.id)

        req = AccessCheckRequest(user_id=user.id, resource_type="dataset", resource_id=None, action="write")
        resp = service.check_access(req)
        self.assertTrue(resp.allowed)

    def test_scope_own_permission(self) -> None:
        service = IAMService()
        user = service.create_user("carol", "carol@example.com")
        other = service.create_user("dave", "dave@example.com")
        role = service.create_role("owner_role")
        perm = service.create_permission(action="delete", resource_type="dataset", scope="own")
        service.assign_permission_to_role(role.id, perm.id)
        service.assign_role_to_user(user.id, role.id)

        # Carol owns the resource
        resource = service.create_resource(resource_type="dataset", owner_id=user.id)
        req1 = AccessCheckRequest(user_id=user.id, resource_type="dataset", resource_id=resource.id, action="delete")
        resp1 = service.check_access(req1)
        self.assertTrue(resp1.allowed)

        # Dave tries to delete Carol's resource
        req2 = AccessCheckRequest(user_id=other.id, resource_type="dataset", resource_id=resource.id, action="delete")
        resp2 = service.check_access(req2)
        self.assertFalse(resp2.allowed)


if __name__ == "__main__":
    unittest.main()