import { useEffect, useState } from 'react';
import { Plus, Users, UserCheck, Shield, Edit, Trash2 } from 'lucide-react';
import { 
  getGroups, 
  getRoles, 
  createGroup, 
  assignRoleToGroup, 
  Group, 
  Role 
} from '../api';

export default function GroupsPage() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [groupName, setGroupName] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [assigning, setAssigning] = useState(false);

  const fetchData = async () => {
    try {
      const [groupsData, rolesData] = await Promise.all([
        getGroups(),
        getRoles(),
      ]);
      setGroups(groupsData);
      setRoles(rolesData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!groupName.trim()) return;
    
    setCreating(true);
    try {
      await createGroup(groupName);
      setGroupName('');
      await fetchData();
    } catch (error) {
      console.error('Failed to create group:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGroup || !selectedRole) return;
    
    setAssigning(true);
    try {
      await assignRoleToGroup(selectedGroup, selectedRole);
      setSelectedRole('');
      await fetchData();
    } catch (error) {
      console.error('Failed to assign role:', error);
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
          <h1 className="text-2xl font-bold text-gray-900">用户组管理</h1>
          <p className="text-gray-600 mt-1">管理用户组和角色分配</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">现有用户组</h2>
              <span className="text-sm text-gray-500">{groups.length} 个用户组</span>
            </div>
            
            {groups.length === 0 ? (
              <div className="text-center py-8">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">暂无用户组</p>
              </div>
            ) : (
              <div className="space-y-3">
                {groups.map((group) => (
                  <div key={group.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center">
                          <Users className="w-5 h-5 text-purple-600 mr-2" />
                          <h3 className="font-medium text-gray-900">{group.name}</h3>
                        </div>
                        <div className="flex items-center mt-2 text-xs text-gray-500">
                          <span>ID: {group.id}</span>
                          {group.tenant_id && <span className="ml-4">租户: {group.tenant_id}</span>}
                        </div>
                        {group.roles.length > 0 && (
                          <div className="mt-2">
                            <div className="flex flex-wrap gap-1">
                              {group.roles.slice(0, 3).map((roleId) => {
                                const role = roles.find(r => r.id === roleId);
                                return (
                                  <span key={roleId} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-700">
                                    <UserCheck className="w-3 h-3 mr-1" />
                                    {role?.name || roleId}
                                  </span>
                                );
                              })}
                              {group.roles.length > 3 && (
                                <span className="text-xs text-gray-500">+{group.roles.length - 3} 更多</span>
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
            <h2 className="text-lg font-semibold text-gray-900 mb-4">创建新用户组</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  用户组名称
                </label>
                <input
                  type="text"
                  value={groupName}
                  onChange={(e) => setGroupName(e.target.value)}
                  placeholder="输入用户组名称"
                  className="input-field"
                  required
                />
              </div>
              <button 
                type="submit" 
                disabled={creating || !groupName.trim()}
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
                    创建用户组
                  </div>
                )}
              </button>
            </form>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">分配角色</h2>
            <form onSubmit={handleAssign} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  选择用户组
                </label>
                <select
                  value={selectedGroup}
                  onChange={(e) => setSelectedGroup(e.target.value)}
                  className="input-field"
                  required
                >
                  <option value="">-- 请选择用户组 --</option>
                  {groups.map((group) => (
                    <option key={group.id} value={group.id}>
                      {group.name}
                    </option>
                  ))}
                </select>
              </div>
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
              <button 
                type="submit" 
                disabled={assigning || !selectedGroup || !selectedRole}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {assigning ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    分配中...
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <Shield className="w-4 h-4 mr-2" />
                    分配角色
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