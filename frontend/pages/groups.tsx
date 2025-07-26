import { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://199.199.199.8:8000';

interface Group {
  id: string;
  name: string;
  tenant_id: string | null;
  roles: string[];
}

interface Role {
  id: string;
  name: string;
}

export default function GroupsPage() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [groupName, setGroupName] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');
  const [selectedRole, setSelectedRole] = useState('');

  const fetchData = async () => {
    const [gRes, rRes] = await Promise.all([
      axios.get(`${API_BASE}/groups`),
      axios.get(`${API_BASE}/roles`),
    ]);
    setGroups(gRes.data);
    setRoles(rRes.data);
  };

  useEffect(() => {
    fetchData().catch(() => {});
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!groupName) return;
    await axios.post(`${API_BASE}/groups`, null, { params: { name: groupName } });
    setGroupName('');
    await fetchData();
  };

  const handleAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGroup || !selectedRole) return;
    await axios.post(`${API_BASE}/groups/${selectedGroup}/roles/${selectedRole}`);
    setSelectedRole('');
    await fetchData();
  };

  return (
    <div>
      <h1>用户组管理</h1>
      <section>
        <h2>现有用户组</h2>
        <ul>
          {groups.map((g) => (
            <li key={g.id}>
              <strong>{g.name}</strong> (id: {g.id})
              {g.roles.length > 0 && <span>，角色：{g.roles.join(', ')}</span>}
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2>创建新用户组</h2>
        <form onSubmit={handleCreate} style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            placeholder="用户组名称"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
          />
          <button type="submit" style={{ marginLeft: '0.5rem' }}>
            创建
          </button>
        </form>
      </section>
      <section>
        <h2>为用户组分配角色</h2>
        <form onSubmit={handleAssign}>
          <label>
            选择用户组：
            <select
              value={selectedGroup}
              onChange={(e) => setSelectedGroup(e.target.value)}
            >
              <option value="">--用户组--</option>
              {groups.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name}
                </option>
              ))}
            </select>
          </label>
          <label style={{ marginLeft: '1rem' }}>
            角色：
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
            >
              <option value="">--角色--</option>
              {roles.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" style={{ marginLeft: '0.5rem' }}>
            分配
          </button>
        </form>
      </section>
    </div>
  );
}