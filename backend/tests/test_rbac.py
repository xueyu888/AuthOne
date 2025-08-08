import requests, os

BASE = os.getenv("BASE", "http://127.0.0.1:8000")

def post(p, j=None):
    r = requests.post(BASE + p, json=j)
    assert r.status_code in (200, 201), (p, r.status_code, r.text)
    return r.json() if r.text else {}

def delete(p):
    r = requests.delete(BASE + p)
    assert r.status_code in (200, 204), (p, r.status_code, r.text)

def test_crud_and_rbac_with_groups():
    # perms
    pread  = post("/permissions", {"name":"doc:read","description":""})
    pwrite = post("/permissions", {"name":"doc:write","description":""})

    # roles in t1
    r_reader = post("/roles", {"tenant_id":"t1","name":"reader","description":""})
    r_editor = post("/roles", {"tenant_id":"t1","name":"editor","description":""})

    # bind role->perm
    post(f"/roles/{r_reader['id']}/permissions/{pread['id']}")
    post(f"/roles/{r_editor['id']}/permissions/{pread['id']}")
    post(f"/roles/{r_editor['id']}/permissions/{pwrite['id']}")

    # accounts
    alice = post("/accounts", {"username":"alice","email":"alice@x.com","tenant_id":"t1"})
    bob   = post("/accounts", {"username":"bob","email":"bob@x.com","tenant_id":"t1"})
    x_t2  = post("/accounts", {"username":"x","email":"x@x.com","tenant_id":"t2"})

    # groups
    g_dev = post("/groups", {"tenant_id":"t1","name":"dev-team","description":""})

    # group -> role
    post(f"/groups/{g_dev['id']}/roles/{r_reader['id']}")
    # user -> group
    post(f"/accounts/{alice['id']}/groups/{g_dev['id']}")
    # direct user -> role
    post(f"/accounts/{bob['id']}/roles/{r_editor['id']}")

    # (optional) cross-tenant soft bind: allow bind, later deny on enforce
    post(f"/accounts/{x_t2['id']}/roles/{r_reader['id']}")

    def check(acc, dom, obj, act):
        return post("/check_access", {
            "account_id": acc, "tenant_id": dom, "resource": obj, "action": act
        })["allowed"]

    # alice via group in t1: read allowed, write denied
    assert check(alice["id"], "t1", "/docs/42", "read")  is True
    assert check(alice["id"], "t1", "/docs/42", "write") is False

    # bob direct editor in t1: both allowed
    assert check(bob["id"], "t1", "/docs/7", "read")   is True
    assert check(bob["id"], "t1", "/docs/7", "write")  is True

    # cross-tenant: bound role in t1 but request in t2 -> denied
    assert check(x_t2["id"], "t2", "/docs/1", "read")  is False
    assert check(x_t2["id"], "t1", "/docs/1", "read")  is False

    # cleanup
    delete(f"/accounts/{alice['id']}"); delete(f"/accounts/{bob['id']}"); delete(f"/accounts/{x_t2['id']}")
    delete(f"/groups/{g_dev['id']}");   delete(f"/roles/{r_reader['id']}"); delete(f"/roles/{r_editor['id']}")
    delete(f"/permissions/{pread['id']}"); delete(f"/permissions/{pwrite['id']}")
