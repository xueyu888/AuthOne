import { useEffect, useState } from 'react';
import { Plus, Users, UserCheck, Shield, Edit, Trash2, X, Check, Search, MoreHorizontal, Settings } from 'lucide-react';
import { 
  getGroups, 
  getRoles, 
  getAccounts,
  createGroup, 
  assignRoleToGroup, 
  Group, 
  Role,
  Account 
} from '../api';

// 生成用户组图标的颜色
const getGroupColor = (name: string) => {
  const colors = [
    'bg-violet-400', 'bg-purple-400', 'bg-indigo-400', 'bg-blue-400',
    'bg-cyan-400', 'bg-teal-400', 'bg-emerald-400', 'bg-green-400',
    'bg-lime-400', 'bg-yellow-400', 'bg-amber-400', 'bg-orange-400'
  ];
  
  const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
};

export default function GroupsPage() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [groupName, setGroupName] = useState('');
  const [groupDescription, setGroupDescription] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [configGroup, setConfigGroup] = useState<Group | null>(null);
  const [selectedGroups, setSelectedGroups] = useState<string[]>([]);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const [assigningRoles, setAssigningRoles] = useState<{[key: string]: boolean}>({});

  const fetchData = async () => {
    try {
      const [groupsData, rolesData, accountsData] = await Promise.all([
        getGroups(),
        getRoles(),
        getAccounts(),
      ]);
      setGroups(groupsData);
      setRoles(rolesData);
      setAccounts(accountsData);
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
      await createGroup(groupName, groupDescription);
      setGroupName('');
      setGroupDescription('');
      setShowCreateModal(false);
      await fetchData();
    } catch (error) {
      console.error('Failed to create group:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleAssignRole = async (groupId: string, roleId: string) => {
    if (!groupId || !roleId) return;
    
    setAssigningRoles(prev => ({...prev, [groupId]: true}));
    try {
      await assignRoleToGroup(groupId, roleId);
      await fetchData();
    } catch (error) {
      console.error('Failed to assign role:', error);
    } finally {
      setAssigningRoles(prev => ({...prev, [groupId]: false}));
    }
  };

  const openConfigModal = (group: Group) => {
    setConfigGroup(group);
    setShowConfigModal(true);
    setOpenDropdown(null);
  };

  const toggleGroupSelection = (groupId: string) => {
    setSelectedGroups(prev => 
      prev.includes(groupId) 
        ? prev.filter(id => id !== groupId)
        : [...prev, groupId]
    );
  };

  const selectAllGroups = () => {
    if (selectedGroups.length === filteredGroups.length) {
      setSelectedGroups([]);
    } else {
      setSelectedGroups(filteredGroups.map(group => group.id));
    }
  };

  const filteredGroups = groups.filter(group =>
    group.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 获取组的成员数量
  const getGroupMemberCount = (groupId: string) => {
    return accounts.filter(account => account.groups.includes(groupId)).length;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-2xl shadow-lg mb-4">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent"></div>
          </div>
          <p className="text-gray-600 font-medium">加载用户组数据...</p>
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
              <h1 className="text-4xl font-display font-extrabold text-gray-900 mb-3 tracking-tight">用户组管理</h1>
              <p className="text-lg font-medium text-gray-600 tracking-wide">管理用户组和角色分配</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-bold text-base rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 shadow-lg hover:shadow-xl tracking-wide"
            >
              <Plus className="w-5 h-5 mr-2" />
              新建用户组
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
                placeholder="搜索用户组名称..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-base font-medium placeholder:text-gray-400 placeholder:font-normal"
              />
            </div>
            <div className="flex items-center gap-4">
              {selectedGroups.length > 0 && (
                <div className="flex items-center gap-3">
                  <span className="text-base font-medium text-gray-700">
                    已选择 <span className="font-bold text-blue-600">{selectedGroups.length}</span> 个用户组
                  </span>
                  <button className="px-4 py-2 text-base font-semibold text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                    批量配置
                  </button>
                </div>
              )}
              <div className="flex items-center gap-2 text-base font-medium text-gray-700">
                <Users className="w-4 h-4" />
                <span className="font-bold text-gray-900">{filteredGroups.length}</span>
                <span>个用户组</span>
              </div>
            </div>
          </div>
        </div>

        {/* 用户组列表 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          {filteredGroups.length === 0 ? (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-2xl mb-4">
                <Users className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3 tracking-tight">暂无用户组</h3>
              <p className="text-base font-medium text-gray-600 mb-6">创建第一个用户组开始管理用户权限</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold text-base rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4 mr-2" />
                创建用户组
              </button>
            </div>
          ) : (
            <>
              {/* 桌面端表头 */}
              <div className="hidden lg:block bg-gray-50/80 backdrop-blur-sm border-b border-gray-200/60">
                <div className="flex w-full px-6 py-4">
                  {/* 第一列：复选框 */}
                  <div className="w-12 flex items-center">
                    <label className="relative flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedGroups.length === filteredGroups.length && filteredGroups.length > 0}
                        onChange={selectAllGroups}
                        className="sr-only"
                      />
                      <div className={`w-5 h-5 rounded-lg border-2 transition-all duration-200 flex items-center justify-center ${
                        selectedGroups.length === filteredGroups.length && filteredGroups.length > 0
                          ? 'bg-blue-600 border-blue-600' 
                          : 'border-gray-300 hover:border-blue-400'
                      }`}>
                        {selectedGroups.length === filteredGroups.length && filteredGroups.length > 0 && (
                          <Check className="w-3 h-3 text-white" />
                        )}
                      </div>
                    </label>
                  </div>
                  
                  {/* 第二列：用户组 */}
                  <div className="flex-1 min-w-0 px-4">
                    <div className="text-xs font-extrabold text-gray-700 uppercase tracking-widest">
                      用户组
                    </div>
                  </div>
                  
                  {/* 第三列：描述 */}
                  <div className="flex-1 min-w-0 px-4">
                    <div className="text-xs font-extrabold text-gray-700 uppercase tracking-widest">
                      描述
                    </div>
                  </div>
                  
                  {/* 第四列：成员 */}
                  <div className="flex-1 min-w-0 px-4">
                    <div className="text-xs font-extrabold text-gray-700 uppercase tracking-widest">
                      成员
                    </div>
                  </div>
                  
                  {/* 第五列：操作 */}
                  <div className="w-20 flex items-center justify-end">
                    <div className="text-xs font-extrabold text-gray-700 uppercase tracking-widest">
                      操作
                    </div>
                  </div>
                </div>
              </div>

              {/* 用户组列表 */}
              <div className="divide-y divide-gray-100/60">
                {filteredGroups.map((group, index) => (
                  <div key={group.id} className="group hover:bg-gradient-to-r hover:from-blue-50/40 hover:to-indigo-50/20 transition-all duration-300 ease-out border-l-4 border-transparent hover:border-blue-400/30">
                    {/* 桌面端布局 */}
                    <div className="hidden lg:flex w-full px-6 py-5 items-center">
                      {/* 第一列：复选框 */}
                      <div className="w-12 flex items-center">
                        <label className="relative flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={selectedGroups.includes(group.id)}
                            onChange={() => toggleGroupSelection(group.id)}
                            className="sr-only"
                          />
                          <div className={`w-5 h-5 rounded-lg border-2 transition-all duration-200 flex items-center justify-center ${
                            selectedGroups.includes(group.id)
                              ? 'bg-blue-600 border-blue-600 scale-110' 
                              : 'border-gray-300 hover:border-blue-400 group-hover:border-blue-300'
                          }`}>
                            {selectedGroups.includes(group.id) && (
                              <Check className="w-3 h-3 text-white" />
                            )}
                          </div>
                        </label>
                      </div>

                      {/* 第二列：用户组 */}
                      <div className="flex-1 min-w-0 px-4">
                        <div className="flex items-center space-x-3">
                          <div className="flex-shrink-0">
                            <div className={`w-10 h-10 ${getGroupColor(group.name)} rounded-full flex items-center justify-center text-white font-bold text-sm shadow-sm border-2 border-white group-hover:shadow-md transition-all duration-200`}>
                              <Users className="w-5 h-5" />
                            </div>
                          </div>
                          <div className="min-w-0 flex-1">
                            <h3 className="text-base font-bold text-gray-900 truncate">
                              {group.name}
                            </h3>
                            {group.tenant_id && (
                              <div className="text-xs text-gray-500 mt-1">
                                租户: {group.tenant_id}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* 第三列：描述 */}
                      <div className="flex-1 min-w-0 px-4">
                        <span className="text-sm text-gray-500 truncate block">
                          {group.description || '无描述'}
                        </span>
                      </div>

                      {/* 第四列：成员 */}
                      <div className="flex-1 min-w-0 px-4">
                        <div className="flex flex-wrap gap-1 ml-2">
                          <div className="flex items-center space-x-2">
                            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-bold bg-blue-50 text-blue-800 border border-blue-200/60">
                              <Users className="w-3 h-3 mr-1" />
                              {getGroupMemberCount(group.id)} 成员
                            </span>
                            {group.roles.length > 0 && (
                              <>
                                {group.roles.slice(0, 1).map((roleId) => {
                                  const role = roles.find(r => r.id === roleId);
                                  return (
                                    <span
                                      key={roleId}
                                      className="inline-flex items-center px-2 py-1 rounded-md text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200/60"
                                    >
                                      <UserCheck className="w-3 h-3 mr-1" />
                                      {role?.name || roleId}
                                    </span>
                                  );
                                })}
                                {group.roles.length > 1 && (
                                  <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-semibold bg-gray-50 text-gray-700">
                                    +{group.roles.length - 1}
                                  </span>
                                )}
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* 第五列：操作 */}
                      <div className="w-20 flex items-center justify-end">
                        <div className="relative">
                          <button
                            onClick={() => setOpenDropdown(openDropdown === group.id ? null : group.id)}
                            className="p-2.5 text-gray-400 hover:text-gray-600 hover:bg-white/80 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/30 backdrop-blur-sm group-hover:bg-white/60"
                          >
                            <MoreHorizontal className="w-4 h-4" />
                          </button>
                          
                          {openDropdown === group.id && (
                            <>
                              <div 
                                className="fixed inset-0 z-10" 
                                onClick={() => setOpenDropdown(null)}
                              />
                              <div className="absolute right-0 top-full mt-2 w-48 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/60 py-2 z-20 ring-1 ring-black/5">
                                <button
                                  onClick={() => openConfigModal(group)}
                                  className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-blue-50/60 transition-all duration-200 rounded-lg mx-2"
                                >
                                  <Settings className="w-4 h-4 mr-3 text-gray-500" />
                                  配置角色
                                </button>
                                <button
                                  className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-blue-50/60 transition-all duration-200 rounded-lg mx-2"
                                >
                                  <Edit className="w-4 h-4 mr-3 text-gray-500" />
                                  编辑用户组
                                </button>
                                <hr className="my-2 border-gray-100" />
                                <button
                                  className="flex items-center w-full px-4 py-3 text-sm text-red-600 hover:bg-red-50/60 transition-all duration-200 rounded-lg mx-2"
                                >
                                  <Trash2 className="w-4 h-4 mr-3 text-red-400" />
                                  删除用户组
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
                            <div className={`w-10 h-10 ${getGroupColor(group.name)} rounded-xl flex items-center justify-center text-white font-semibold`}>
                              <Users className="w-5 h-5" />
                            </div>
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-semibold text-gray-900 truncate">
                              {group.name}
                            </p>
                            <p className="text-sm text-gray-500 mt-1 truncate">
                              {group.description || '无描述'}
                            </p>
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
                          <p className="text-xs text-gray-500 mb-2">成员数量</p>
                          <div className="space-y-1">
                            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                              <Users className="w-3 h-3 mr-1" />
                              {getGroupMemberCount(group.id)} 成员
                            </span>
                          </div>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-2">关联角色</p>
                          <div className="space-y-1">
                            {group.roles.length > 0 ? (
                              group.roles.slice(0, 2).map((roleId) => {
                                const role = roles.find(r => r.id === roleId);
                                return (
                                  <span
                                    key={roleId}
                                    className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-emerald-100 text-emerald-800"
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
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* 创建用户组弹窗 */}
      {showCreateModal && (
        <>
          <div 
            className="fixed inset-0 bg-black/20 backdrop-blur-md z-40 transition-all duration-300 ease-out"
            onClick={() => setShowCreateModal(false)}
          />
          
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <div 
                className="relative bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 w-full max-w-md transform transition-all duration-300 ease-out scale-100 opacity-100"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-purple-50/50 rounded-3xl" />
                
                <div className="relative p-8">
                  <div className="flex items-center justify-between mb-8">
                    <div>
                      <h3 className="text-3xl font-display font-extrabold text-gray-900 mb-2 tracking-tight">创建新用户组</h3>
                      <p className="text-base font-medium text-gray-600">添加新的用户组到系统中</p>
                    </div>
                    <button
                      onClick={() => setShowCreateModal(false)}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-white/60 rounded-xl transition-all duration-200 backdrop-blur-sm"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  
                  <form onSubmit={handleCreate} className="space-y-6">
                    <div className="space-y-5">
                      <div>
                        <label className="block text-base font-bold text-gray-800 mb-3">
                          用户组名称
                        </label>
                        <input
                          type="text"
                          value={groupName}
                          onChange={(e) => setGroupName(e.target.value)}
                          placeholder="输入用户组名称"
                          className="w-full px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 focus:bg-white transition-all duration-200 placeholder-gray-400 text-base font-medium"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-base font-bold text-gray-800 mb-3">
                          用户组描述 <span className="text-gray-500 font-medium">(可选)</span>
                        </label>
                        <textarea
                          value={groupDescription}
                          onChange={(e) => setGroupDescription(e.target.value)}
                          placeholder="输入用户组描述"
                          rows={3}
                          className="w-full px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 focus:bg-white transition-all duration-200 placeholder-gray-400 text-base font-medium resize-none"
                        />
                      </div>
                    </div>
                    
                    <div className="flex justify-end space-x-4 pt-6">
                      <button
                        type="button"
                        onClick={() => setShowCreateModal(false)}
                        className="px-6 py-3 text-base font-bold text-gray-700 bg-white/60 backdrop-blur-sm border border-gray-200/60 rounded-2xl hover:bg-white/80 hover:border-gray-300/80 focus:outline-none focus:ring-2 focus:ring-gray-400/50 transition-all duration-200"
                      >
                        取消
                      </button>
                      <button 
                        type="submit" 
                        disabled={creating || !groupName.trim()}
                        className="px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold text-base rounded-2xl hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
                      >
                        {creating ? (
                          <div className="flex items-center">
                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white mr-3"></div>
                            创建中...
                          </div>
                        ) : (
                          <div className="flex items-center">
                            <Plus className="w-4 h-4 mr-2" />
                            创建用户组
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

      {/* 角色配置弹窗 */}
      {showConfigModal && configGroup && (
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
                      <div className={`w-14 h-14 ${getGroupColor(configGroup.name)} rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg ring-4 ring-white`}>
                        <Users className="w-8 h-8" />
                      </div>
                      <div>
                        <h3 className="text-3xl font-display font-extrabold text-gray-900 tracking-tight">{configGroup.name}</h3>
                        <p className="text-base font-semibold text-gray-700">{configGroup.description || '无描述'}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowConfigModal(false)}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-white/60 rounded-xl transition-all duration-200 backdrop-blur-sm"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  
                  <div className="space-y-6">
                    <div>
                      <h4 className="text-xl font-bold text-gray-900 flex items-center tracking-tight mb-6">
                        <UserCheck className="w-5 h-5 mr-2 text-emerald-600" />
                        角色配置
                      </h4>
                      
                      <div className="space-y-4">
                        <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-4">
                          <h5 className="text-base font-bold text-gray-800 mb-3">当前角色</h5>
                          <div className="flex flex-wrap gap-2">
                            {configGroup.roles.length > 0 ? (
                              configGroup.roles.map((roleId) => {
                                const role = roles.find(r => r.id === roleId);
                                return (
                                  <span
                                    key={roleId}
                                    className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-bold bg-emerald-100 text-emerald-800 border border-emerald-200"
                                  >
                                    {role?.name || roleId}
                                    <button className="ml-2 text-emerald-600 hover:text-emerald-800">
                                      <X className="w-3 h-3" />
                                    </button>
                                  </span>
                                );
                              })
                            ) : (
                              <span className="text-base font-medium text-gray-600">暂无角色</span>
                            )}
                          </div>
                        </div>
                        
                        <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-4">
                          <h5 className="text-base font-bold text-gray-800 mb-3">可分配角色</h5>
                          <div className="space-y-2 max-h-32 overflow-y-auto">
                            {roles.filter(role => !configGroup.roles.includes(role.id)).map((role) => (
                              <button
                                key={role.id}
                                onClick={() => handleAssignRole(configGroup.id, role.id)}
                                disabled={assigningRoles[configGroup.id]}
                                className="flex items-center justify-between w-full px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors disabled:opacity-50"
                              >
                                <span>{role.name}</span>
                                <Plus className="w-4 h-4 text-gray-400" />
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-xl font-bold text-gray-900 flex items-center tracking-tight mb-6">
                        <Users className="w-5 h-5 mr-2 text-blue-600" />
                        成员信息
                      </h4>
                      
                      <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-6">
                        <div className="text-center">
                          <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                          <h5 className="text-lg font-bold text-gray-800 mb-2">{getGroupMemberCount(configGroup.id)} 个成员</h5>
                          <p className="text-base font-medium text-gray-600">查看和管理用户组成员</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex justify-end mt-8">
                    <button
                      onClick={() => setShowConfigModal(false)}
                      className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold text-base rounded-2xl hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all duration-200 shadow-lg hover:shadow-xl"
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