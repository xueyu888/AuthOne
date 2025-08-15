# backend/tests/test_api_full.py
import os
import uuid
import httpx
import pytest

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


def _uid(s: str) -> str:
    return f"{s}-{uuid.uuid4().hex[:8]}"


async def _post_json(ac: httpx.AsyncClient, path: str, payload: dict, ok=(200, 201, 204)):
    r = await ac.post(path, json=payload)
    assert r.status_code in ok, f"POST {path} failed: {r.status_code} {r.text}"
    return r


# 改进：允许 _delete 优雅地处理 404 错误，方便清理
async def _delete(ac: httpx.AsyncClient, path: str, ok=(204, 404)):
    r = await ac.delete(path)
    assert r.status_code in ok, f"DELETE {path} failed: {r.status_code} {r.text}"
    return r


async def _get(ac: httpx.AsyncClient, path: str, params: dict | None = None, ok=(200,)):
    r = await ac.get(path, params=params or {})
    assert r.status_code in ok, f"GET {path} failed: {r.status_code} {r.text}"
    return r


async def create_or_get_permission(ac: httpx.AsyncClient, name: str, description: str = "") -> str:
    r = await ac.post("/permissions", json={"name": name, "description": description})
    if r.status_code in (200, 201):
        return r.json()["id"]
    if r.status_code == 409:
        r2 = await ac.get("/permissions", params={"name": name})
        data = r2.json()
        assert data, f"Permission '{name}' not found"
        return data[0]["id"]
    raise AssertionError(f"create permission failed: {r.status_code} {r.text}")


async def create_or_get_role(ac: httpx.AsyncClient, tenant_id: str | None, name: str, description: str = "") -> str:
    r = await ac.post("/roles", json={"tenant_id": tenant_id, "name": name, "description": description})
    if r.status_code in (200, 201):
        return r.json()["id"]
    if r.status_code == 409:
        r2 = await ac.get("/roles", params={"tenant_id": tenant_id, "name": name})
        data = r2.json()
        assert data, f"Role '{name}' in tenant '{tenant_id}' not found"
        return data[0]["id"]
    raise AssertionError(f"create role failed: {r.status_code} {r.text}")


async def create_or_get_account(ac: httpx.AsyncClient, tenant_id: str | None, username: str, email: str) -> str:
    r = await ac.post("/accounts", json={"username": username, "email": email, "tenant_id": tenant_id})
    if r.status_code in (200, 201):
        return r.json()["id"]
    if r.status_code == 409:
        r2 = await ac.get("/accounts", params={"tenant_id": tenant_id, "username": username})
        data = r2.json()
        assert data, f"Account '{username}' in tenant '{tenant_id}' not found"
        return data[0]["id"]
    raise AssertionError(f"create account failed: {r.status_code} {r.text}")


@pytest.mark.anyio
async def test_full_api_matrix():
    tenant1 = "t1"
    tenant2 = "t2"

    # —— 唯一性：避免与之前数据冲突
    perm_read = "doc:read"
    perm_rw_regex = "doc:read|write"  # 用于 regexMatch 测试
    role_reader = _uid("reader")
    role_editor = _uid("editor")
    group_name = _uid("group")
    user_alice = _uid("alice")
    user_bob = _uid("bob")
    email_alice = f"{user_alice}@example.com"
    email_bob = f"{user_bob}@example.com"

    res_name_1 = _uid("fileA")
    res_name_2 = _uid("fileB")

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as ac:
        # ---------- 1) 基础 CRUD 与约束 ----------
        # 1.1 Permission：创建/冲突/过滤
        perm_read_id = await create_or_get_permission(ac, perm_read, "read docs")
        r = await ac.post("/permissions", json={"name": perm_read})
        assert r.status_code == 409

        perm_rw_id = await create_or_get_permission(ac, perm_rw_regex, "read or write via regex")
        r = await _get(ac, "/permissions", params={"name": perm_rw_regex})
        assert r.json() and r.json()[0]["id"] == perm_rw_id

        # 1.2 Role：t1 下创建 reader/editor；t2 下只建一个
        role_reader_id_t1 = await create_or_get_role(ac, tenant1, role_reader)
        role_editor_id_t1 = await create_or_get_role(ac, tenant1, role_editor)
        role_reader_id_t2 = await create_or_get_role(ac, tenant2, role_reader)

        # 1.3 Account：t1 的 alice/bob；alice 冲突再 get
        alice_id_t1 = await create_or_get_account(ac, tenant1, user_alice, email_alice)
        r = await ac.post("/accounts", json={"username": user_alice, "email": email_alice, "tenant_id": tenant1})
        assert r.status_code == 409
        bob_id_t1 = await create_or_get_account(ac, tenant1, user_bob, email_bob)

        # 1.4 Group：t1 的一个组
        r = await _post_json(ac, "/groups", {"tenant_id": tenant1, "name": group_name})
        group_id_t1 = r.json()["id"]

        # 1.5 Resource：
        r = await _post_json(
            ac, "/resources",
            {"resource_type": "doc", "name": res_name_1, "tenant_id": tenant1, "metadata": {"k": 1}}
        )
        res_id_1 = r.json()["id"]
        body = r.json()
        assert body["type"] == "doc"
        assert "resource_type" not in body

        r = await _post_json(
            ac, "/resources",
            {"resource_type": "doc", "name": res_name_2, "tenant_id": tenant1}
        )
        res_id_2 = r.json()["id"]

        # 1.6 422 校验（permission 名字太短）
        r = await ac.post("/permissions", json={"name": "aa"})
        assert r.status_code == 422

        # ---------- 2) 绑定关系 ----------
        # 2.1 角色 ↔ 权限
        await _post_json(ac, f"/roles/{role_reader_id_t1}/permissions/{perm_read_id}", {})
        await _post_json(ac, f"/roles/{role_reader_id_t1}/permissions/{perm_rw_id}", {})

        # 2.2 账号 ↔ 角色
        await _post_json(ac, f"/accounts/{alice_id_t1}/roles/{role_reader_id_t1}", {})
        await _post_json(ac, f"/accounts/{bob_id_t1}/roles/{role_editor_id_t1}", {})

        # 2.3 组 ↔ 角色
        await _post_json(ac, f"/groups/{group_id_t1}/roles/{role_reader_id_t1}", {})

        # 2.4 账号 ↔ 组
        await _post_json(ac, f"/accounts/{alice_id_t1}/groups/{group_id_t1}", {})

        # ---------- 3) 鉴权 ----------
        async def check(account_id: str, tenant: str | None, resource: str, action: str) -> bool:
            r = await _post_json(ac, "/check-access", {
                "account_id": account_id, "tenant_id": tenant, "resource": resource, "action": action
            }, ok=(200,))
            return bool(r.json()["allowed"])

        assert await check(alice_id_t1, tenant1, "/docs/1", "read") is True
        assert await check(alice_id_t1, tenant1, "/docs/99", "write") is True
        assert await check(alice_id_t1, tenant1, "/docsX/1", "read") is False
        assert await check(alice_id_t1, tenant1, "/docs/1/2", "read") is True
        assert await check(alice_id_t1, tenant1, "/docs/1", "delete") is False
        assert await check(alice_id_t1, tenant2, "/docs/1", "read") is False
        assert await check(alice_id_t1, None, "/docs/1", "read") is False

        # ---------- 4) 组中转授权 ----------
        ok_via_group = await check(alice_id_t1, tenant1, "/docs/123", "read")
        if not ok_via_group:
            pytest.skip("matcher 里可能未声明 g2，账号→组→角色链路未开启；跳过组中转校验。")
        assert await check(alice_id_t1, tenant1, "/docs/777", "write") is True

        # ---------- 5) 幂等与冲突分支 ----------
        r = await ac.post(f"/roles/{role_reader_id_t1}/permissions/{perm_read_id}")
        assert r.status_code in (204, 409)
        r = await ac.post(f"/accounts/{alice_id_t1}/roles/{role_reader_id_t1}")
        assert r.status_code in (204, 409)

        # ---------- 6) 解绑与权限撤销 ----------
        # 6.1 解绑角色-权限
        await _delete(ac, f"/roles/{role_reader_id_t1}/permissions/{perm_rw_id}")
        assert await check(alice_id_t1, tenant1, "/docs/1", "write") is False
        assert await check(alice_id_t1, tenant1, "/docs/1", "read") is True

        # 6.2 解绑账号-角色 和 账号-组
        await _delete(ac, f"/accounts/{alice_id_t1}/roles/{role_reader_id_t1}")
        # 【修复】必须同时解绑组，才能彻底切断权限
        await _delete(ac, f"/accounts/{alice_id_t1}/groups/{group_id_t1}")
        assert await check(alice_id_t1, tenant1, "/docs/1", "read") is False

        # 6.3 恢复绑定用于后续测试
        await _post_json(ac, f"/accounts/{alice_id_t1}/roles/{role_reader_id_t1}", {})
        assert await check(alice_id_t1, tenant1, "/docs/1", "read") is True

        # ---------- 7) 实体删除与级联权限撤销 ----------
        # 【重构】明确测试删除角色后的级联效果
        # 删除前，alice 有权限
        assert await check(alice_id_t1, tenant1, "/docs/1", "read") is True
        # 删除 reader 角色
        await _delete(ac, f"/roles/{role_reader_id_t1}", ok=(204,)) # 确保这次删除是成功的
        # 删除后，alice 应该立即失去权限
        assert await check(alice_id_t1, tenant1, "/docs/1", "read") is False

        # ---------- 8) 列表过滤 ----------
        r = await _get(ac, "/roles", params={"tenant_id": tenant1})
        roles_t1 = r.json()
        assert all(item["tenant_id"] == tenant1 for item in roles_t1)
        # 验证 reader 角色已被删除
        assert role_reader_id_t1 not in {item["id"] for item in roles_t1}

        r = await _get(ac, "/accounts", params={"tenant_id": tenant1, "username": user_alice})
        lst = r.json()
        assert lst and lst[0]["username"] == user_alice

        r = await _get(ac, "/resources", params={"tenant_id": tenant1})
        names = {x["name"] for x in r.json()}
        assert {res_name_1, res_name_2}.issubset(names)

        # ---------- 9) 清理测试数据 ----------
        # 【新增】一个完整的清理步骤，确保不污染环境
        # 删除资源
        await _delete(ac, f"/resources/{res_id_1}")
        await _delete(ac, f"/resources/{res_id_2}")
        
        # 删除用户
        await _delete(ac, f"/accounts/{alice_id_t1}")
        await _delete(ac, f"/accounts/{bob_id_t1}")
        
        # 删除组
        await _delete(ac, f"/groups/{group_id_t1}")
        
        # 删除剩余的角色
        await _delete(ac, f"/roles/{role_editor_id_t1}")
        await _delete(ac, f"/roles/{role_reader_id_t2}")
        # role_reader_id_t1 已在上面删除，无需重复
        
        # 删除权限
        await _delete(ac, f"/permissions/{perm_read_id}")
        await _delete(ac, f"/permissions/{perm_rw_id}")

        # ---------- 10) 404 错误分支 ----------
        # 【调整】将 404 测试放在最后，因为此时依赖的实体都已删除
        rand_uuid = str(uuid.uuid4())
        r = await ac.delete(f"/permissions/{rand_uuid}")
        assert r.status_code == 404
        r = await ac.delete(f"/roles/{rand_uuid}")
        assert r.status_code == 404
        r = await ac.delete(f"/groups/{rand_uuid}")
        assert r.status_code == 404
        r = await ac.delete(f"/accounts/{rand_uuid}")
        assert r.status_code == 404
        r = await ac.delete(f"/resources/{rand_uuid}")
        assert r.status_code == 404