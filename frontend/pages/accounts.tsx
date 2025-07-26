import { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://199.199.199.8:8000';

interface Account {
  id: string;
  username: string;
  email: string;
  tenant_id: string | null;
  roles: string[];
  groups: string[];
}

interface Role {
  id: string;
  name: string;
}

interface Group {
  id: string;
  name: string;
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [tenantId, setTenantId] = useState('');
  const [selAccount, setSelAccount] = useState('');
  const [selRole, setSelRole] = useState('');
  const [selGroup, setSelGroup] = useState('');

  const fetchData = async () => {
    const [aRes, rRes, gRes] = await Promise.all([
      axios.get(`${API_BASE}/accounts`),
      axios.get(`${API_BASE}/roles`),
      axios.get(`${API_BASE}/groups`),
    ]);
    setAccounts(aRes.data);
    setRoles(rRes.data);
    setGroups(gRes.data);
  };

  useEffect(() => {
    fetchData().catch(() => {});
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !email) return;
    await axios.post(`${API_BASE}/accounts`, null, {
      params: { username, email, tenant_id: tenantId || undefined },
    });
    setUsername('');
    setEmail('');
    setTenantId('');
    await fetchData();
  };

  const handleAssignRole = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selAccount || !selRole) return;
    await axios.post(`${API_BASE}/accounts/${selAccount}/roles/${selRole}`);
    setSelRole('');
    await fetchData();
  };

  const handleAssignGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selAccount || !selGroup) return;
    await axios.post(`${API_BASE}/accounts/${selAccount}/groups/${selGroup}`);
    setSelGroup('');
    await fetchData();
  };

  return (
    <div>
      <h1>账户管理</h1>
      <section>
        <h2>现有账户</h2>
        <ul>
          {accounts.map((a) => (
            <li key={a.id}>
              <strong>{a.username}</strong> ({a.email}) id:{' '}
              {a.id}
              {a.roles.length > 0 && <span>，角色：{a.roles.join(', ')}</span>}
              {a.groups.length > 0 && <span>，组：{a.groups.join(', ')}</span>}
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2>创建新账户</h2>
        <form onSubmit={handleCreate}>
          <input
            type="text"
            placeholder="用户名"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          />
          <input
            type="email"
            placeholder="邮箱"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          />
          <input
            type="text"
            placeholder="租户ID (可选)"
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          />
          <button type="submit">创建</button>
        </form>
      </section>
      <section>
        <h2>分配角色和用户组</h2>
        <form onSubmit={handleAssignRole} style={{ marginBottom: '0.5rem' }}>
          <label>
            选择账户：
            <select value={selAccount} onChange={(e) => setSelAccount(e.target.value)}>
              <option value="">--账户--</option>
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.username}
                </option>
              ))}
            </select>
          </label>
          <label style={{ marginLeft: '1rem' }}>
            角色：
            <select value={selRole} onChange={(e) => setSelRole(e.target.value)}>
              <option value="">--角色--</option>
              {roles.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" style={{ marginLeft: '0.5rem' }}>
            分配角色
          </button>
        </form>
        <form onSubmit={handleAssignGroup}>
          <label>
            选择账户：
            <select value={selAccount} onChange={(e) => setSelAccount(e.target.value)}>
              <option value="">--账户--</option>
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.username}
                </option>
              ))}
            </select>
          </label>
          <label style={{ marginLeft: '1rem' }}>
            用户组：
            <select value={selGroup} onChange={(e) => setSelGroup(e.target.value)}>
              <option value="">--用户组--</option>
              {groups.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" style={{ marginLeft: '0.5rem' }}>
            分配用户组
          </button>
        </form>
      </section>
    </div>
  );
}