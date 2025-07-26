import { useEffect, useState } from 'react';
import { Plus, UserCheck, Key, Edit, Trash2 } from 'lucide-react';
import { getRoles, getPermissions, createRole, assignPermissionToRole, Role, Permission } from '../api';

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [roleName, setRoleName] = useState('');
  const [roleDescription, setRoleDescription] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [permissionId, setPermissionId] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [assigning, setAssigning] = useState(false);

  const fetchData = async () => {
    try {
      const [rolesData, permissionsData] = await Promise.all([
        getRoles(),
        getPermissions(),
      ]);
      setRoles(rolesData);
      setPermissions(permissionsData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateRole = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roleName.trim()) return;
    
    setCreating(true);
    try {
      await createRole(roleName, undefined, roleDescription);
      setRoleName('');
      setRoleDescription('');
      await fetchData();
    } catch (error) {
      console.error('Failed to create role:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleAssignPermission = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRole || !permissionId) return;
    
    setAssigning(true);
    try {
      await assignPermissionToRole(selectedRole, permissionId);
      setPermissionId('');
      await fetchData();
    } catch (error) {
      console.error('Failed to assign permission:', error);
    } finally {
      setAssigning(false);
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
          <h1 className="text-2xl font-bold text-gray-900">角色管理</h1>
          <p className="text-gray-600 mt-1">管理系统角色和权限分配</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">现有角色</h2>
              <span className="text-sm text-gray-500">{roles.length} 个角色</span>
            </div>
            
            {roles.length === 0 ? (
              <div className="text-center py-8">
                <UserCheck className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">暂无角色</p>
              </div>
            ) : (
              <div className="space-y-3">
                {roles.map((role) => (
                  <div key={role.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center">
                          <UserCheck className="w-5 h-5 text-green-600 mr-2" />
                          <h3 className="font-medium text-gray-900">{role.name}</h3>
                        </div>
                        {role.description && (
                          <p className="text-sm text-gray-600 mt-1">{role.description}</p>
                        )}
                        <div className="flex items-center mt-2 text-xs text-gray-500">
                          <span>ID: {role.id}</span>
                          {role.tenant_id && <span className="ml-4">租户: {role.tenant_id}</span>}
                        </div>
                        {role.permissions.length > 0 && (
                          <div className="mt-2">
                            <div className="flex flex-wrap gap-1">
                              {role.permissions.slice(0, 3).map((permId) => {
                                const perm = permissions.find(p => p.id === permId);
                                return (
                                  <span key={permId} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-700">
                                    <Key className="w-3 h-3 mr-1" />
                                    {perm?.name || permId}
                                  </span>
                                );
                              })}
                              {role.permissions.length > 3 && (
                                <span className="text-xs text-gray-500">+{role.permissions.length - 3} 更多</span>
                              )}
                            </div>
                          </div>
                        )}
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

        <div className="space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">创建新角色</h2>
            <form onSubmit={handleCreateRole} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  角色名称
                </label>
                <input
                  type="text"
                  value={roleName}
                  onChange={(e) => setRoleName(e.target.value)}
                  placeholder="输入角色名称"
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  描述 (可选)
                </label>
                <textarea
                  value={roleDescription}
                  onChange={(e) => setRoleDescription(e.target.value)}
                  placeholder="输入角色描述"
                  className="input-field"
                  rows={3}
                />
              </div>
              <button 
                type="submit" 
                disabled={creating || !roleName.trim()}
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
                    创建角色
                  </div>
                )}
              </button>
            </form>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">分配权限</h2>
            <form onSubmit={handleAssignPermission} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  选择角色
                </label>
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="input-field"
                  required
                >
                  <option value="">-- 请选择角色 --</option>
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>
                      {role.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  选择权限
                </label>
                <select
                  value={permissionId}
                  onChange={(e) => setPermissionId(e.target.value)}
                  className="input-field"
                  required
                >
                  <option value="">-- 请选择权限 --</option>
                  {permissions.map((permission) => (
                    <option key={permission.id} value={permission.id}>
                      {permission.name}
                    </option>
                  ))}
                </select>
              </div>
              <button 
                type="submit" 
                disabled={assigning || !selectedRole || !permissionId}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {assigning ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    分配中...
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <Key className="w-4 h-4 mr-2" />
                    分配权限
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