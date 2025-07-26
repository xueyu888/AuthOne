import { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

interface Role {
  id: string;
  tenant_id: string | null;
  name: string;
  permissions: string[];
}

interface Permission {
  id: string;
  name: string;
  description: string;
}

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [roleName, setRoleName] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [permissionId, setPermissionId] = useState('');

  const fetchData = async () => {
    const [rRes, pRes] = await Promise.all([
      axios.get(`${API_BASE}/roles`),
      axios.get(`${API_BASE}/permissions`),
    ]);
    setRoles(rRes.data);
    setPermissions(pRes.data);
  };

  useEffect(() => {
    fetchData().catch(() => {
      // ignore
    });
  }, []);

  const handleCreateRole = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roleName) return;
    await axios.post(`${API_BASE}/roles`, null, { params: { name: roleName } });
    setRoleName('');
    await fetchData();
  };

  const handleAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRole || !permissionId) return;
    await axios.post(
      `${API_BASE}/roles/${selectedRole}/permissions/${permissionId}`
    );
    setPermissionId('');
    await fetchData();
  };

  return (
    <div>
      <h1>角色管理</h1>
      <section>
        <h2>现有角色</h2>
        <ul>
          {roles.map((r) => (
            <li key={r.id}>
              <strong>{r.name}</strong> (id: {r.id})
              {r.permissions.length > 0 && (
                <span>
                  ，权限：
                  {r.permissions.join(', ')}
                </span>
              )}
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2>创建新角色</h2>
        <form onSubmit={handleCreateRole} style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            value={roleName}
            onChange={(e) => setRoleName(e.target.value)}
            placeholder="角色名称"
          />
          <button type="submit" style={{ marginLeft: '0.5rem' }}>
            创建
          </button>
        </form>
      </section>
      <section>
        <h2>分配权限</h2>
        <form onSubmit={handleAssign}>
          <label>
            选择角色：
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
            >
              <option value="">--请选择角色--</option>
              {roles.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          </label>
          <label style={{ marginLeft: '1rem' }}>
            权限：
            <select
              value={permissionId}
              onChange={(e) => setPermissionId(e.target.value)}
            >
              <option value="">--请选择权限--</option>
              {permissions.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
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