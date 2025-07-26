import { useEffect, useState } from 'react';
import { Plus, Key, Edit, Trash2 } from 'lucide-react';
import { getPermissions, createPermission, Permission } from '../api';

export default function PermissionsPage() {
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [permName, setPermName] = useState('');
  const [permDesc, setPermDesc] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const fetchPermissions = async () => {
    try {
      const data = await getPermissions();
      setPermissions(data);
    } catch (error) {
      console.error('Failed to fetch permissions:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPermissions();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!permName.trim()) return;
    
    setCreating(true);
    try {
      await createPermission(permName, permDesc);
      setPermName('');
      setPermDesc('');
      await fetchPermissions();
    } catch (error) {
      console.error('Failed to create permission:', error);
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">权限管理</h1>
          <p className="text-gray-600 mt-1">管理系统权限和操作控制</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">已有权限</h2>
              <span className="text-sm text-gray-500">{permissions.length} 个权限</span>
            </div>
            
            {permissions.length === 0 ? (
              <div className="text-center py-8">
                <Key className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">暂无权限</p>
              </div>
            ) : (
              <div className="space-y-3">
                {permissions.map((permission) => (
                  <div key={permission.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center">
                          <Key className="w-5 h-5 text-purple-600 mr-2" />
                          <h3 className="font-medium text-gray-900">{permission.name}</h3>
                        </div>
                        {permission.description && (
                          <p className="text-sm text-gray-600 mt-1">{permission.description}</p>
                        )}
                        <div className="flex items-center mt-2 text-xs text-gray-500">
                          <span>ID: {permission.id}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button className="p-1 text-gray-400 hover:text-gray-600">
                          <Edit className="w-4 h-4" />
                        </button>
                        <button className="p-1 text-gray-400 hover:text-red-600">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">创建新权限</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  权限名称
                </label>
                <input
                  type="text"
                  value={permName}
                  onChange={(e) => setPermName(e.target.value)}
                  placeholder="resource:action (例如: users:read)"
                  className="input-field"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  格式：资源:操作，如 users:read, posts:write
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  描述 (可选)
                </label>
                <textarea
                  value={permDesc}
                  onChange={(e) => setPermDesc(e.target.value)}
                  placeholder="权限描述"
                  className="input-field"
                  rows={3}
                />
              </div>
              <button 
                type="submit" 
                disabled={creating || !permName.trim()}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {creating ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    创建中...
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <Plus className="w-4 h-4 mr-2" />
                    创建权限
                  </div>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}