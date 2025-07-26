import { useState } from 'react';
import axios from 'axios';

// 默认 API 基础地址，可通过环境变量覆盖
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://199.199.199.8:8000';

/**
 * 管理首页。
 *
 * 本页面提供创建角色和权限的表单示例，演示如何调用后端接口。
 */
export default function IndexPage() {
  const [roleName, setRoleName] = useState('');
  const [permissionName, setPermissionName] = useState('');
  const [message, setMessage] = useState<string | null>(null);

  const handleCreateRole = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/roles`, null, {
        params: { name: roleName }
      });
      setMessage(`角色 ${roleName} 已创建`);
      setRoleName('');
    } catch (error) {
      setMessage('创建角色失败');
    }
  };

  const handleCreatePermission = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/permissions`, null, {
        params: { name: permissionName }
      });
      setMessage(`权限 ${permissionName} 已创建`);
      setPermissionName('');
    } catch (error) {
      setMessage('创建权限失败');
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>AuthOne 管理控制台</h1>
      {message && <p>{message}</p>}
      <section>
        <h2>创建角色</h2>
        <form onSubmit={handleCreateRole} style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            value={roleName}
            onChange={(e) => setRoleName(e.target.value)}
            placeholder="角色名称"
            style={{ marginRight: '0.5rem' }}
          />
          <button type="submit">创建</button>
        </form>
      </section>
      <section>
        <h2>创建权限</h2>
        <form onSubmit={handleCreatePermission}>
          <input
            type="text"
            value={permissionName}
            onChange={(e) => setPermissionName(e.target.value)}
            placeholder="resource:action"
            style={{ marginRight: '0.5rem' }}
          />
          <button type="submit">创建</button>
        </form>
      </section>
    </div>
  );
}