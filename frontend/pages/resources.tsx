import { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

interface Resource {
  id: string;
  name: string;
  type: string;
  tenant_id: string | null;
  owner_id: string | null;
}

export default function ResourcesPage() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [resName, setResName] = useState('');
  const [resType, setResType] = useState('dataset');
  const fetchResources = async () => {
    const res = await axios.get(`${API_BASE}/resources`);
    setResources(res.data);
  };
  useEffect(() => {
    fetchResources().catch(() => {});
  }, []);
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resName) return;
    await axios.post(`${API_BASE}/resources`, null, {
      params: { resource_type: resType, name: resName },
    });
    setResName('');
    await fetchResources();
  };
  return (
    <div>
      <h1>资源管理</h1>
      <section>
        <h2>已有资源</h2>
        <ul>
          {resources.map((r) => (
            <li key={r.id}>
              <strong>{r.name}</strong> ({r.type}) id: {r.id}
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2>创建新资源</h2>
        <form onSubmit={handleCreate}>
          <input
            type="text"
            placeholder="资源名称"
            value={resName}
            onChange={(e) => setResName(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          />
          <select
            value={resType}
            onChange={(e) => setResType(e.target.value)}
            style={{ marginRight: '0.5rem' }}
          >
            <option value="dataset">数据集</option>
            <option value="app">应用</option>
            <option value="model">模型</option>
            <option value="file">文件</option>
          </select>
          <button type="submit">创建</button>
        </form>
      </section>
    </div>
  );
}