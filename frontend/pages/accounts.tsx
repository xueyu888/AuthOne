import { useEffect, useState } from 'react';
import { Plus, Users, UserCheck, Mail, Shield, Edit, Trash2, X, ChevronDown, Search, Filter, MoreHorizontal, Settings, Check } from 'lucide-react';
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

// 生成高级简约的头像配色
const getAvatarColor = (name: string) => {
  const colors = [
    'bg-slate-500', 'bg-gray-500', 'bg-zinc-500', 'bg-neutral-500', 'bg-stone-500',
    'bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-yellow-500', 'bg-lime-500',
    'bg-green-500', 'bg-emerald-500', 'bg-teal-500', 'bg-cyan-500', 'bg-sky-500',
    'bg-blue-500', 'bg-indigo-500', 'bg-violet-500', 'bg-purple-500', 'bg-fuchsia-500',
    'bg-pink-500', 'bg-rose-500'
  ];
  
  // 更柔和的配色方案
  const subtleColors = [
    'bg-slate-400', 'bg-gray-400', 'bg-zinc-400', 'bg-neutral-400',
    'bg-red-400', 'bg-orange-400', 'bg-amber-400', 'bg-green-400',
    'bg-emerald-400', 'bg-teal-400', 'bg-blue-400', 'bg-indigo-400',
    'bg-violet-400', 'bg-purple-400'
  ];
  
  const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return subtleColors[hash % subtleColors.length];
};

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [tenantId, setTenantId] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [configAccount, setConfigAccount] = useState<Account | null>(null);
  const [selectedAccounts, setSelectedAccounts] = useState<string[]>([]);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const [assigningRoles, setAssigningRoles] = useState<{[key: string]: boolean}>({});
  const [assigningGroups, setAssigningGroups] = useState<{[key: string]: boolean}>({});

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
      setShowCreateModal(false);
      await fetchData();
    } catch (error) {
      console.error('Failed to create account:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleAssignRole = async (accountId: string, roleId: string) => {
    if (!accountId || !roleId) return;
    
    setAssigningRoles(prev => ({...prev, [accountId]: true}));
    try {
      await assignRoleToAccount(accountId, roleId);
      await fetchData();
    } catch (error) {
      console.error('Failed to assign role:', error);
    } finally {
      setAssigningRoles(prev => ({...prev, [accountId]: false}));
    }
  };

  const handleAssignGroup = async (accountId: string, groupId: string) => {
    if (!accountId || !groupId) return;
    
    setAssigningGroups(prev => ({...prev, [accountId]: true}));
    try {
      await assignGroupToAccount(accountId, groupId);
      await fetchData();
    } catch (error) {
      console.error('Failed to assign group:', error);
    } finally {
      setAssigningGroups(prev => ({...prev, [accountId]: false}));
    }
  };

  const openConfigModal = (account: Account) => {
    setConfigAccount(account);
    setShowConfigModal(true);
    setOpenDropdown(null);
  };

  const toggleAccountSelection = (accountId: string) => {
    setSelectedAccounts(prev => 
      prev.includes(accountId) 
        ? prev.filter(id => id !== accountId)
        : [...prev, accountId]
    );
  };

  const selectAllAccounts = () => {
    if (selectedAccounts.length === filteredAccounts.length) {
      setSelectedAccounts([]);
    } else {
      setSelectedAccounts(filteredAccounts.map(account => account.id));
    }
  };

  const filteredAccounts = accounts.filter(account =>
    account.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    account.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-2xl shadow-lg mb-4">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent"></div>
          </div>
          <p className="text-gray-600 font-medium">加载账户数据...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页面头部 */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">账户管理</h1>
              <p className="text-gray-600">管理用户账户、角色和权限分配</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <Plus className="w-5 h-5 mr-2" />
              新建账户
            </button>
          </div>
        </div>

        {/* 搜索和批量操作栏 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="搜索用户名或邮箱..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              />
            </div>
            <div className="flex items-center gap-4">
              {selectedAccounts.length > 0 && (
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-600">
                    已选择 <span className="font-semibold text-blue-600">{selectedAccounts.length}</span> 个用户
                  </span>
                  <button className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                    批量配置
                  </button>
                </div>
              )}
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Users className="w-4 h-4" />
                <span className="font-medium">{filteredAccounts.length}</span>
                <span>个账户</span>
              </div>
            </div>
          </div>
        </div>

        {/* 账户列表 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          {filteredAccounts.length === 0 ? (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-2xl mb-4">
                <Users className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">暂无账户</h3>
              <p className="text-gray-500 mb-6">创建第一个账户开始管理用户</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4 mr-2" />
                创建账户
              </button>
            </div>
          ) : (
            <>
              {/* 桌面端表头 */}
              <div className="hidden lg:block bg-gray-50/80 backdrop-blur-sm border-b border-gray-200/60">
                <div className="grid grid-cols-12 gap-3 px-8 py-4">
                  <div className="col-span-1 flex items-center">
                    <label className="relative flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedAccounts.length === filteredAccounts.length && filteredAccounts.length > 0}
                        onChange={selectAllAccounts}
                        className="sr-only"
                      />
                      <div className={`w-5 h-5 rounded-lg border-2 transition-all duration-200 flex items-center justify-center ${
                        selectedAccounts.length === filteredAccounts.length && filteredAccounts.length > 0
                          ? 'bg-blue-600 border-blue-600' 
                          : 'border-gray-300 hover:border-blue-400'
                      }`}>
                        {selectedAccounts.length === filteredAccounts.length && filteredAccounts.length > 0 && (
                          <Check className="w-3 h-3 text-white" />
                        )}
                      </div>
                    </label>
                  </div>
                  <div className="col-span-4 text-xs font-bold text-gray-600 uppercase tracking-wider">
                    用户信息
                  </div>
                  <div className="col-span-3 text-xs font-bold text-gray-600 uppercase tracking-wider">
                    权限与分组
                  </div>
                  <div className="col-span-3 text-xs font-bold text-gray-600 uppercase tracking-wider">
                    邮箱地址
                  </div>
                  <div className="col-span-1 text-xs font-bold text-gray-600 uppercase tracking-wider text-center">
                    操作
                  </div>
                </div>
              </div>

              {/* 账户列表 */}
              <div className="divide-y divide-gray-100/60">
                {filteredAccounts.map((account, index) => (
                  <div key={account.id} className="group hover:bg-gradient-to-r hover:from-blue-50/40 hover:to-indigo-50/20 transition-all duration-300 ease-out border-l-4 border-transparent hover:border-blue-400/30">
                    {/* 桌面端布局 */}
                    <div className="hidden lg:grid grid-cols-12 gap-3 px-8 py-5 items-center">
                      {/* 选择框 */}
                      <div className="col-span-1 flex items-center">
                        <label className="relative flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={selectedAccounts.includes(account.id)}
                            onChange={() => toggleAccountSelection(account.id)}
                            className="sr-only"
                          />
                          <div className={`w-5 h-5 rounded-lg border-2 transition-all duration-200 flex items-center justify-center ${
                            selectedAccounts.includes(account.id)
                              ? 'bg-blue-600 border-blue-600 scale-110' 
                              : 'border-gray-300 hover:border-blue-400 group-hover:border-blue-300'
                          }`}>
                            {selectedAccounts.includes(account.id) && (
                              <Check className="w-3 h-3 text-white" />
                            )}
                          </div>
                        </label>
                      </div>

                      {/* 用户信息 - 紧凑布局 */}
                      <div className="col-span-4">
                        <div className="flex items-center space-x-3">
                          <div className="flex-shrink-0">
                            <div className={`w-11 h-11 ${getAvatarColor(account.username)} rounded-xl flex items-center justify-center text-white font-bold text-base shadow-sm ring-2 ring-white group-hover:shadow-md transition-all duration-200`}>
                              {account.username.charAt(0).toUpperCase()}
                            </div>
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center space-x-2">
                              <h3 className="text-sm font-bold text-gray-900 truncate">
                                {account.username}
                              </h3>
                              <div className="group/tooltip relative">
                                <div className="w-1.5 h-1.5 bg-gray-300 rounded-full cursor-help opacity-60 hover:opacity-100 transition-opacity"></div>
                                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover/tooltip:opacity-100 transition-opacity whitespace-nowrap z-20 shadow-xl">
                                  <div className="font-medium">ID: {account.id}</div>
                                  {account.tenant_id && <div className="text-gray-300 mt-1">租户: {account.tenant_id}</div>}
                                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2 mt-1">
                              <Mail className="w-3 h-3 text-gray-400 flex-shrink-0" />
                              <span className="text-xs text-gray-600 truncate font-medium">
                                {account.email}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* 权限与分组 - 合并列 */}
                      <div className="col-span-3">
                        <div className="space-y-2">
                          {/* 角色 */}
                          <div className="flex flex-wrap gap-1">
                            {account.roles.length > 0 ? (
                              <>
                                {account.roles.slice(0, 2).map((roleId) => {
                                  const role = roles.find(r => r.id === roleId);
                                  return (
                                    <span
                                      key={roleId}
                                      className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200/60"
                                    >
                                      <UserCheck className="w-3 h-3 mr-1" />
                                      {role?.name || roleId}
                                    </span>
                                  );
                                })}
                                {account.roles.length > 2 && (
                                  <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-50 text-gray-600">
                                    +{account.roles.length - 2}
                                  </span>
                                )}
                              </>
                            ) : (
                              <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-50 text-gray-500">
                                无角色
                              </span>
                            )}
                          </div>
                          
                          {/* 用户组 */}
                          <div className="flex flex-wrap gap-1">
                            {account.groups.length > 0 ? (
                              <>
                                {account.groups.slice(0, 2).map((groupId) => {
                                  const group = groups.find(g => g.id === groupId);
                                  return (
                                    <span
                                      key={groupId}
                                      className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-violet-50 text-violet-700 border border-violet-200/60"
                                    >
                                      <Shield className="w-3 h-3 mr-1" />
                                      {group?.name || groupId}
                                    </span>
                                  );
                                })}
                                {account.groups.length > 2 && (
                                  <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-50 text-gray-600">
                                    +{account.groups.length - 2}
                                  </span>
                                )}
                              </>
                            ) : (
                              <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-50 text-gray-500">
                                无分组
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* 邮箱详情 */}
                      <div className="col-span-3">
                        <div className="text-sm font-semibold text-gray-800 truncate">
                          {account.email}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {account.tenant_id ? `租户: ${account.tenant_id}` : '默认租户'}
                        </div>
                      </div>

                      {/* 操作菜单 */}
                      <div className="col-span-1 flex justify-center">
                        <div className="relative">
                          <button
                            onClick={() => setOpenDropdown(openDropdown === account.id ? null : account.id)}
                            className="p-2.5 text-gray-400 hover:text-gray-600 hover:bg-white/80 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/30 backdrop-blur-sm group-hover:bg-white/60"
                          >
                            <MoreHorizontal className="w-4 h-4" />
                          </button>
                          
                          {openDropdown === account.id && (
                            <>
                              <div 
                                className="fixed inset-0 z-10" 
                                onClick={() => setOpenDropdown(null)}
                              />
                              <div className="absolute right-0 top-full mt-2 w-48 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/60 py-2 z-20 ring-1 ring-black/5">
                                <button
                                  onClick={() => openConfigModal(account)}
                                  className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-blue-50/60 transition-all duration-200 rounded-lg mx-2"
                                >
                                  <Settings className="w-4 h-4 mr-3 text-gray-500" />
                                  配置权限
                                </button>
                                <button
                                  className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-blue-50/60 transition-all duration-200 rounded-lg mx-2"
                                >
                                  <Edit className="w-4 h-4 mr-3 text-gray-500" />
                                  编辑用户
                                </button>
                                <hr className="my-2 border-gray-100" />
                                <button
                                  className="flex items-center w-full px-4 py-3 text-sm text-red-600 hover:bg-red-50/60 transition-all duration-200 rounded-lg mx-2"
                                >
                                  <Trash2 className="w-4 h-4 mr-3 text-red-400" />
                                  删除用户
                                </button>
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* 移动端布局 */}
                    <div className="lg:hidden p-6 space-y-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-3 flex-1 min-w-0">
                          <div className="flex-shrink-0">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-semibold">
                              {account.username.charAt(0).toUpperCase()}
                            </div>
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-semibold text-gray-900 truncate">
                              {account.username}
                            </p>
                            <div className="flex items-center text-sm text-gray-500 mt-1">
                              <Mail className="w-3 h-3 mr-1 flex-shrink-0" />
                              <span className="truncate">{account.email}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-1 ml-4">
                          <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200">
                            <Edit className="w-4 h-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs text-gray-500 mb-2">角色权限</p>
                          <div className="space-y-1">
                            {account.roles.length > 0 ? (
                              account.roles.slice(0, 2).map((roleId) => {
                                const role = roles.find(r => r.id === roleId);
                                return (
                                  <span
                                    key={roleId}
                                    className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-100 text-green-800"
                                  >
                                    <UserCheck className="w-3 h-3 mr-1" />
                                    {role?.name || roleId}
                                  </span>
                                );
                              })
                            ) : (
                              <span className="text-xs text-gray-400">暂无角色</span>
                            )}
                          </div>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-2">用户组</p>
                          <div className="space-y-1">
                            {account.groups.length > 0 ? (
                              account.groups.slice(0, 2).map((groupId) => {
                                const group = groups.find(g => g.id === groupId);
                                return (
                                  <span
                                    key={groupId}
                                    className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-purple-100 text-purple-800"
                                  >
                                    <Shield className="w-3 h-3 mr-1" />
                                    {group?.name || groupId}
                                  </span>
                                );
                              })
                            ) : (
                              <span className="text-xs text-gray-400">暂无分组</span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <select
                          className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          value=""
                          onChange={(e) => {
                            if (e.target.value) {
                              handleAssignRole(account.id, e.target.value);
                              e.target.value = '';
                            }
                          }}
                          disabled={assigningRoles[account.id]}
                        >
                          <option value="">+ 分配角色</option>
                          {roles.filter(role => !account.roles.includes(role.id)).map((role) => (
                            <option key={role.id} value={role.id}>
                              {role.name}
                            </option>
                          ))}
                        </select>
                        <select
                          className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          value=""
                          onChange={(e) => {
                            if (e.target.value) {
                              handleAssignGroup(account.id, e.target.value);
                              e.target.value = '';
                            }
                          }}
                          disabled={assigningGroups[account.id]}
                        >
                          <option value="">+ 分配用户组</option>
                          {groups.filter(group => !account.groups.includes(group.id)).map((group) => (
                            <option key={group.id} value={group.id}>
                              {group.name}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* 创建账户弹窗 - 高级悬浮设计 */}
      {showCreateModal && (
        <>
          {/* 遮罩层 */}
          <div 
            className="fixed inset-0 bg-black/20 backdrop-blur-md z-40 transition-all duration-300 ease-out"
            onClick={() => setShowCreateModal(false)}
          />
          
          {/* 弹窗容器 */}
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <div 
                className="relative bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 w-full max-w-md transform transition-all duration-300 ease-out scale-100 opacity-100"
                onClick={(e) => e.stopPropagation()}
              >
                {/* 装饰性渐变背景 */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-purple-50/50 rounded-3xl" />
                
                {/* 弹窗内容 */}
                <div className="relative p-8">
                  {/* 头部 */}
                  <div className="flex items-center justify-between mb-8">
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900 mb-1">创建新账户</h3>
                      <p className="text-sm text-gray-600">添加新的用户账户到系统中</p>
                    </div>
                    <button
                      onClick={() => setShowCreateModal(false)}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-white/60 rounded-xl transition-all duration-200 backdrop-blur-sm"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  
                  {/* 表单 */}
                  <form onSubmit={handleCreate} className="space-y-6">
                    <div className="space-y-5">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3">
                          用户名
                        </label>
                        <input
                          type="text"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          placeholder="输入用户名"
                          className="w-full px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 focus:bg-white transition-all duration-200 placeholder-gray-400"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3">
                          邮箱地址
                        </label>
                        <input
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="输入邮箱地址"
                          className="w-full px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 focus:bg-white transition-all duration-200 placeholder-gray-400"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3">
                          租户ID <span className="text-gray-400 font-normal">(可选)</span>
                        </label>
                        <input
                          type="text"
                          value={tenantId}
                          onChange={(e) => setTenantId(e.target.value)}
                          placeholder="输入租户ID"
                          className="w-full px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 focus:bg-white transition-all duration-200 placeholder-gray-400"
                        />
                      </div>
                    </div>
                    
                    {/* 按钮组 */}
                    <div className="flex justify-end space-x-4 pt-6">
                      <button
                        type="button"
                        onClick={() => setShowCreateModal(false)}
                        className="px-6 py-3 text-sm font-semibold text-gray-700 bg-white/60 backdrop-blur-sm border border-gray-200/60 rounded-2xl hover:bg-white/80 hover:border-gray-300/80 focus:outline-none focus:ring-2 focus:ring-gray-400/50 transition-all duration-200"
                      >
                        取消
                      </button>
                      <button 
                        type="submit" 
                        disabled={creating || !username.trim() || !email.trim()}
                        className="px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-2xl hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
                      >
                        {creating ? (
                          <div className="flex items-center">
                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white mr-3"></div>
                            创建中...
                          </div>
                        ) : (
                          <div className="flex items-center">
                            <Plus className="w-4 h-4 mr-2" />
                            创建账户
                          </div>
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* 权限配置弹窗 */}
      {showConfigModal && configAccount && (
        <>
          <div 
            className="fixed inset-0 bg-black/20 backdrop-blur-md z-40 transition-all duration-300 ease-out"
            onClick={() => setShowConfigModal(false)}
          />
          
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <div 
                className="relative bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 w-full max-w-2xl transform transition-all duration-300 ease-out scale-100 opacity-100"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-purple-50/50 rounded-3xl" />
                
                <div className="relative p-8">
                  <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center space-x-4">
                      <div className={`w-14 h-14 ${getAvatarColor(configAccount.username)} rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg ring-4 ring-white`}>
                        {configAccount.username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-gray-900">{configAccount.username}</h3>
                        <p className="text-sm text-gray-600">{configAccount.email}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowConfigModal(false)}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-white/60 rounded-xl transition-all duration-200 backdrop-blur-sm"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* 角色管理 */}
                    <div className="space-y-4">
                      <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                        <UserCheck className="w-5 h-5 mr-2 text-emerald-600" />
                        角色权限
                      </h4>
                      
                      <div className="space-y-3">
                        <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-4">
                          <h5 className="text-sm font-semibold text-gray-700 mb-3">当前角色</h5>
                          <div className="flex flex-wrap gap-2">
                            {configAccount.roles.length > 0 ? (
                              configAccount.roles.map((roleId) => {
                                const role = roles.find(r => r.id === roleId);
                                return (
                                  <span
                                    key={roleId}
                                    className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200"
                                  >
                                    {role?.name || roleId}
                                    <button className="ml-2 text-emerald-600 hover:text-emerald-800">
                                      <X className="w-3 h-3" />
                                    </button>
                                  </span>
                                );
                              })
                            ) : (
                              <span className="text-sm text-gray-500">暂无角色</span>
                            )}
                          </div>
                        </div>
                        
                        <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-4">
                          <h5 className="text-sm font-semibold text-gray-700 mb-3">可分配角色</h5>
                          <div className="space-y-2 max-h-32 overflow-y-auto">
                            {roles.filter(role => !configAccount.roles.includes(role.id)).map((role) => (
                              <button
                                key={role.id}
                                onClick={() => handleAssignRole(configAccount.id, role.id)}
                                disabled={assigningRoles[configAccount.id]}
                                className="flex items-center justify-between w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors disabled:opacity-50"
                              >
                                <span>{role.name}</span>
                                <Plus className="w-4 h-4 text-gray-400" />
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* 用户组管理 */}
                    <div className="space-y-4">
                      <h4 className="text-lg font-semibold text-gray-900 flex items-center">
                        <Shield className="w-5 h-5 mr-2 text-violet-600" />
                        用户组
                      </h4>
                      
                      <div className="space-y-3">
                        <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-4">
                          <h5 className="text-sm font-semibold text-gray-700 mb-3">当前分组</h5>
                          <div className="flex flex-wrap gap-2">
                            {configAccount.groups.length > 0 ? (
                              configAccount.groups.map((groupId) => {
                                const group = groups.find(g => g.id === groupId);
                                return (
                                  <span
                                    key={groupId}
                                    className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-violet-100 text-violet-800 border border-violet-200"
                                  >
                                    {group?.name || groupId}
                                    <button className="ml-2 text-violet-600 hover:text-violet-800">
                                      <X className="w-3 h-3" />
                                    </button>
                                  </span>
                                );
                              })
                            ) : (
                              <span className="text-sm text-gray-500">暂无分组</span>
                            )}
                          </div>
                        </div>
                        
                        <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-4">
                          <h5 className="text-sm font-semibold text-gray-700 mb-3">可分配分组</h5>
                          <div className="space-y-2 max-h-32 overflow-y-auto">
                            {groups.filter(group => !configAccount.groups.includes(group.id)).map((group) => (
                              <button
                                key={group.id}
                                onClick={() => handleAssignGroup(configAccount.id, group.id)}
                                disabled={assigningGroups[configAccount.id]}
                                className="flex items-center justify-between w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors disabled:opacity-50"
                              >
                                <span>{group.name}</span>
                                <Plus className="w-4 h-4 text-gray-400" />
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex justify-end mt-8">
                    <button
                      onClick={() => setShowConfigModal(false)}
                      className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-2xl hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                      完成配置
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}