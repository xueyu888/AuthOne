set -e
BASE=${BASE:-http://127.0.0.1:8000}

# 1) perms
pr=$(curl -sS -X POST $BASE/permissions -H 'Content-Type: application/json' \
  -d '{"name":"doc:read","description":""}')
pw=$(curl -sS -X POST $BASE/permissions -H 'Content-Type: application/json' \
  -d '{"name":"doc:write","description":""}')
PR=$(python - <<'PY';import json,sys;print(json.loads(sys.stdin.read())["id"]);PY <<<"$pr")
PW=$(python - <<'PY';import json,sys;print(json.loads(sys.stdin.read())["id"]);PY <<<"$pw")

# 2) roles
rr=$(curl -sS -X POST $BASE/roles -H 'Content-Type: application/json' \
  -d '{"tenant_id":"t1","name":"reader","description":""}')
re=$(curl -sS -X POST $BASE/roles -H 'Content-Type: application/json' \
  -d '{"tenant_id":"t1","name":"editor","description":""}')
RR=$(python - <<'PY';import json,sys;print(json.loads(sys.stdin.read())["id"]);PY <<<"$rr")
RE=$(python - <<'PY';import json,sys;print(json.loads(sys.stdin.read())["id"]);PY <<<"$re")

# 3) bind role-perm
curl -sS -X POST $BASE/roles/$RR/permissions/$PR -d ''
curl -sS -X POST $BASE/roles/$RE/permissions/$PR -d ''
curl -sS -X POST $BASE/roles/$RE/permissions/$PW -d ''

# 4) accounts
aa=$(curl -sS -X POST $BASE/accounts -H 'Content-Type: application/json' \
  -d '{"username":"alice","email":"alice@example.com","tenant_id":"t1"}')
ab=$(curl -sS -X POST $BASE/accounts -H 'Content-Type: application/json' \
  -d '{"username":"bob","email":"bob@example.com","tenant_id":"t1"}')
at2=$(curl -sS -X POST $BASE/accounts -H 'Content-Type: application/json' \
  -d '{"username":"x","email":"x@example.com","tenant_id":"t2"}')
AA=$(python - <<'PY';import json,sys;print(json.loads(sys.stdin.read())["id"]);PY <<<"$aa")
AB=$(python - <<'PY';import json,sys;print(json.loads(sys.stdin.read())["id"]);PY <<<"$ab")
AT2=$(python - <<'PY';import json,sys;print(json.loads(sys.stdin.read())["id"]);PY <<<"$at2")

# 5) bind account-role（含跨租户软绑定）
curl -sS -X POST $BASE/accounts/$AA/roles/$RR -d ''
curl -sS -X POST $BASE/accounts/$AB/roles/$RE -d ''
curl -sS -X POST $BASE/accounts/$AT2/roles/$RR -d ''

# 6) checks
check(){ curl -sS -X POST $BASE/check_access -H 'Content-Type: application/json' -d "$1"; echo; }

check '{"account_id":"'"$AA"'","tenant_id":"t1","resource":"/docs/1","action":"read"}'   # true
check '{"account_id":"'"$AA"'","tenant_id":"t1","resource":"/docs/1","action":"write"}'  # false
check '{"account_id":"'"$AB"'","tenant_id":"t1","resource":"/docs/1","action":"write"}'  # true
check '{"account_id":"'"$AT2"'","tenant_id":"t2","resource":"/docs/1","action":"read"}'  # false

# 7) cleanup
curl -sS -X DELETE $BASE/accounts/$AA
curl -sS -X DELETE $BASE/accounts/$AB
curl -sS -X DELETE $BASE/accounts/$AT2
curl -sS -X DELETE $BASE/roles/$RR
curl -sS -X DELETE $BASE/roles/$RE
curl -sS -X DELETE $BASE/permissions/$PR
curl -sS -X DELETE $BASE/permissions/$PW
