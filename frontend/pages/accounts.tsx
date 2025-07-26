import { useEffect, useState } from 'react';
import { Plus, Users, UserCheck, Mail, Shield, Edit, Trash2 } from 'lucide-react';
import { 
  getAccounts, 
  getRoles, 
  getGroups, 
  createAccount, 
  assignRoleToAccount, 
  assignGroupToAccount, 
  Account, 
  Role, 
  Group 
} from '../api';

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
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [assigning, setAssigning] = useState(false);

  const fetchData = async () => {
    try {
      const [accountsData, rolesData, groupsData] = await Promise.all([
        getAccounts(),
        getRoles(),
        getGroups(),
      ]);
      setAccounts(accountsData);
      setRoles(rolesData);
      setGroups(groupsData);
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
    if (!username.trim() || !email.trim()) return;
    
    setCreating(true);
    try {
      await createAccount(username, email, tenantId || undefined);
      setUsername('');
      setEmail('');
      setTenantId('');
      await fetchData();
    } catch (error) {
      console.error('Failed to create account:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleAssignRole = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selAccount || !selRole) return;
    
    setAssigning(true);
    try {
      await assignRoleToAccount(selAccount, selRole);
      setSelRole('');
      await fetchData();
    } catch (error) {
      console.error('Failed to assign role:', error);
    } finally {
      setAssigning(false);
    }
  };

  const handleAssignGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selAccount || !selGroup) return;
    
    setAssigning(true);
    try {
      await assignGroupToAccount(selAccount, selGroup);
      setSelGroup('');
      await fetchData();
    } catch (error) {
      console.error('Failed to assign group:', error);
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
          <h1 className="text-2xl font-bold text-gray-900">账户管理</h1>
          <p className="text-gray-600 mt-1">管理用户账户和权限分配</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">现有账户</h2>
              <span className="text-sm text-gray-500">{accounts.length} 个账户</span>
            </div>
            
            {accounts.length === 0 ? (
              <div className="text-center py-8">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">暂无账户</p>
              </div>
            ) : (
              <div className="space-y-3">
                {accounts.map((account) => (
                  <div key={account.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center">
                          <Users className="w-5 h-5 text-blue-600 mr-2" />
                          <h3 className="font-medium text-gray-900">{account.username}</h3>
                        </div>
                        <div className="flex items-center mt-1 text-sm text-gray-600">
                          <Mail className="w-4 h-4 mr-1" />
                          {account.email}
                        </div>
                        <div className="flex items-center mt-2 text-xs text-gray-500">
                          <span>ID: {account.id}</span>
                          {account.tenant_id && <span className="ml-4">租户: {account.tenant_id}</span>}
                        </div>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {account.roles.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {account.roles.slice(0, 3).map((roleId) => {
                                const role = roles.find(r => r.id === roleId);
                                return (
                                  <span key={roleId} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-700">
                                    <UserCheck className="w-3 h-3 mr-1" />
                                    {role?.name || roleId}
                                  </span>
                                );
                              })}
                              {account.roles.length > 3 && (
                                <span className="text-xs text-gray-500">+{account.roles.length - 3} 更多角色</span>
                              )}
                            </div>
                          )}
                          {account.groups.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {account.groups.slice(0, 3).map((groupId) => {
                                const group = groups.find(g => g.id === groupId);
                                return (
                                  <span key={groupId} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-700">
                                    <Shield className="w-3 h-3 mr-1" />
                                    {group?.name || groupId}
                                  </span>
                                );
                              })}
                              {account.groups.length > 3 && (
                                <span className="text-xs text-gray-500">+{account.groups.length - 3} 更多组</span>
                              )}
                            </div>
                          )}
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

        <div className="space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">创建新账户</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  用户名
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="输入用户名"
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  邮箱
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="输入邮箱地址"
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  租户ID (可选)
                </label>
                <input
                  type="text"
                  value={tenantId}
                  onChange={(e) => setTenantId(e.target.value)}
                  placeholder="输入租户ID"
                  className="input-field"
                />
              </div>
              <button 
                type="submit" 
                disabled={creating || !username.trim() || !email.trim()}
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
                    创建账户
                  </div>
                )}
              </button>
            </form>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">分配角色</h2>
            <form onSubmit={handleAssignRole} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  选择账户
                </label>
                <select
                  value={selAccount}
                  onChange={(e) => setSelAccount(e.target.value)}
                  className="input-field"
                  required
                >
                  <option value="">-- 请选择账户 --</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.username}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  选择角色
                </label>
                <select
                  value={selRole}
                  onChange={(e) => setSelRole(e.target.value)}
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
                disabled={assigning || !selAccount || !selRole}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {assigning ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    分配中...
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <UserCheck className="w-4 h-4 mr-2" />
                    分配角色
                  </div>
                )}
              </button>
            </form>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">分配用户组</h2>
            <form onSubmit={handleAssignGroup} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  选择账户
                </label>
                <select
                  value={selAccount}
                  onChange={(e) => setSelAccount(e.target.value)}
                  className="input-field"
                  required
                >
                  <option value="">-- 请选择账户 --</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.username}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  选择用户组
                </label>
                <select
                  value={selGroup}
                  onChange={(e) => setSelGroup(e.target.value)}
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
              <button 
                type="submit" 
                disabled={assigning || !selAccount || !selGroup}
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
                    分配用户组
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