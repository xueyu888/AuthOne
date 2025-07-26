import { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

interface Permission {
  id: string;
  name: string;
  description: string;
}

export default function PermissionsPage() {
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [permName, setPermName] = useState('');
  const [permDesc, setPermDesc] = useState('');

  const fetchPermissions = async () => {
    const res = await axios.get(`${API_BASE}/permissions`);
    setPermissions(res.data);
  };

  useEffect(() => {
    fetchPermissions().catch(() => {});
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!permName) return;
    await axios.post(`${API_BASE}/permissions`, null, {
      params: { name: permName, description: permDesc },
    });
    setPermName('');
    setPermDesc('');
    await fetchPermissions();
  };

  return (
    <div>
      <h1>权限管理</h1>
      <section>
        <h2>已有权限</h2>
        <ul>
          {permissions.map((p) => (
            <li key={p.id}>
              <strong>{p.name}</strong>：{p.description || '无描述'} (id: {p.id})
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2>创建新权限</h2>
        <form onSubmit={handleCreate}>
          <input
            type="text"
            placeholder="resource:action"
            value={permName}
            onChange={(e) => setPermName(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          />
          <input
            type="text"
            placeholder="描述"
            value={permDesc}
            onChange={(e) => setPermDesc(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          />
          <button type="submit">创建</button>
        </form>
      </section>
    </div>
  );
}