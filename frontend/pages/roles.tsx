import { useEffect, useState } from 'react';
import { Plus, UserCheck, Key, Edit, Trash2, X, Check, Search, Filter, MoreHorizontal, Settings, Mail, Shield } from 'lucide-react';
import { getRoles, getPermissions, createRole, assignPermissionToRole, Role, Permission } from '../api';

// 生成角色标识的颜色
const getRoleColor = (name: string) => {
  const colors = [
    'bg-emerald-400', 'bg-blue-400', 'bg-indigo-400', 'bg-purple-400',
    'bg-pink-400', 'bg-red-400', 'bg-orange-400', 'bg-yellow-400',
    'bg-green-400', 'bg-teal-400', 'bg-cyan-400', 'bg-sky-400'
  ];
  
  const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
};

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [roleName, setRoleName] = useState('');
  const [roleDescription, setRoleDescription] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [permissionId, setPermissionId] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [assigning, setAssigning] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [configRole, setConfigRole] = useState<Role | null>(null);
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

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
      setShowCreateModal(false);
      await fetchData();
    } catch (error) {
      console.error('Failed to create role:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleAssignPermission = async (roleId: string, permissionId: string) => {
    if (!roleId || !permissionId) return;
    
    setAssigning(true);
    try {
      await assignPermissionToRole(roleId, permissionId);
      await fetchData();
    } catch (error) {
      console.error('Failed to assign permission:', error);
    } finally {
      setAssigning(false);
    }
  };

  const openConfigModal = (role: Role) => {
    setConfigRole(role);
    setShowConfigModal(true);
    setOpenDropdown(null);
  };

  const toggleRoleSelection = (roleId: string) => {
    setSelectedRoles(prev => 
      prev.includes(roleId) 
        ? prev.filter(id => id !== roleId)
        : [...prev, roleId]
    );
  };

  const selectAllRoles = () => {
    if (selectedRoles.length === filteredRoles.length) {
      setSelectedRoles([]);
    } else {
      setSelectedRoles(filteredRoles.map(role => role.id));
    }
  };

  const filteredRoles = roles.filter(role =>
    role.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (role.description && role.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-2xl shadow-lg mb-4">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent"></div>
          </div>
          <p className="text-gray-600 font-medium">加载角色数据...</p>
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
              <h1 className="text-4xl font-display font-extrabold text-gray-900 mb-3 tracking-tight">角色管理</h1>
              <p className="text-lg font-medium text-gray-600 tracking-wide">管理系统角色和权限分配</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-bold text-base rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 shadow-lg hover:shadow-xl tracking-wide"
            >
              <Plus className="w-5 h-5 mr-2" />
              新建角色
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
                placeholder="搜索角色名称或描述..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-base font-medium placeholder:text-gray-400 placeholder:font-normal"
              />
            </div>
            <div className="flex items-center gap-4">
              {selectedRoles.length > 0 && (
                <div className="flex items-center gap-3">
                  <span className="text-base font-medium text-gray-700">
                    已选择 <span className="font-bold text-blue-600">{selectedRoles.length}</span> 个角色
                  </span>
                  <button className="px-4 py-2 text-base font-semibold text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                    批量配置
                  </button>
                </div>
              )}
              <div className="flex items-center gap-2 text-base font-medium text-gray-700">
                <UserCheck className="w-4 h-4" />
                <span className="font-bold text-gray-900">{filteredRoles.length}</span>
                <span>个角色</span>
              </div>
            </div>
          </div>
        </div>

        {/* 角色列表 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          {filteredRoles.length === 0 ? (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-2xl mb-4">
                <UserCheck className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3 tracking-tight">暂无角色</h3>
              <p className="text-base font-medium text-gray-600 mb-6">创建第一个角色开始管理权限</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold text-base rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4 mr-2" />
                创建角色
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
                        checked={selectedRoles.length === filteredRoles.length && filteredRoles.length > 0}
                        onChange={selectAllRoles}
                        className="sr-only"
                      />
                      <div className={`w-5 h-5 rounded-lg border-2 transition-all duration-200 flex items-center justify-center ${
                        selectedRoles.length === filteredRoles.length && filteredRoles.length > 0
                          ? 'bg-blue-600 border-blue-600' 
                          : 'border-gray-300 hover:border-blue-400'
                      }`}>
                        {selectedRoles.length === filteredRoles.length && filteredRoles.length > 0 && (
                          <Check className="w-3 h-3 text-white" />
                        )}
                      </div>
                    </label>
                  </div>
                  
                  {/* 第二列：角色 */}
                  <div className="flex-1 min-w-0 px-4">
                    <div className="text-xs font-extrabold text-gray-700 uppercase tracking-widest">
                      角色
                    </div>
                  </div>
                  
                  {/* 第三列：描述 */}
                  <div className="flex-1 min-w-0 px-4">
                    <div className="text-xs font-extrabold text-gray-700 uppercase tracking-widest">
                      描述
                    </div>
                  </div>
                  
                  {/* 第四列：权限 */}
                  <div className="flex-1 min-w-0 px-4">
                    <div className="text-xs font-extrabold text-gray-700 uppercase tracking-widest">
                      权限
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

              {/* 角色列表 */}
              <div className="divide-y divide-gray-100/60">
                {filteredRoles.map((role, index) => (
                  <div key={role.id} className="group hover:bg-gradient-to-r hover:from-blue-50/40 hover:to-indigo-50/20 transition-all duration-300 ease-out border-l-4 border-transparent hover:border-blue-400/30">
                    {/* 桌面端布局 */}
                    <div className="hidden lg:flex w-full px-6 py-5 items-center">
                      {/* 第一列：复选框 */}
                      <div className="w-12 flex items-center">
                        <label className="relative flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={selectedRoles.includes(role.id)}
                            onChange={() => toggleRoleSelection(role.id)}
                            className="sr-only"
                          />
                          <div className={`w-5 h-5 rounded-lg border-2 transition-all duration-200 flex items-center justify-center ${
                            selectedRoles.includes(role.id)
                              ? 'bg-blue-600 border-blue-600 scale-110' 
                              : 'border-gray-300 hover:border-blue-400 group-hover:border-blue-300'
                          }`}>
                            {selectedRoles.includes(role.id) && (
                              <Check className="w-3 h-3 text-white" />
                            )}
                          </div>
                        </label>
                      </div>

                      {/* 第二列：角色 */}
                      <div className="flex-1 min-w-0 px-4">
                        <div className="flex items-center space-x-3">
                          <div className="flex-shrink-0">
                            <div className={`w-10 h-10 ${getRoleColor(role.name)} rounded-full flex items-center justify-center text-white font-bold text-sm shadow-sm border-2 border-white group-hover:shadow-md transition-all duration-200`}>
                              {role.name.charAt(0).toUpperCase()}
                            </div>
                          </div>
                          <div className="min-w-0 flex-1">
                            <h3 className="text-base font-bold text-gray-900 truncate">
                              {role.name}
                            </h3>
                            {role.tenant_id && (
                              <div className="text-xs text-gray-500 mt-1">
                                租户: {role.tenant_id}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* 第三列：描述 */}
                      <div className="flex-1 min-w-0 px-4">
                        <span className="text-sm text-gray-500 truncate">
                          {role.description || '无描述'}
                        </span>
                      </div>

                      {/* 第四列：权限 */}
                      <div className="flex-1 min-w-0 px-4">
                        <div className="flex flex-wrap gap-1 ml-2">
                          {role.permissions.length > 0 ? (
                            <>
                              {role.permissions.slice(0, 2).map((permissionId) => {
                                const permission = permissions.find(p => p.id === permissionId);
                                return (
                                  <span
                                    key={permissionId}
                                    className="inline-flex items-center px-2 py-1 rounded-md text-xs font-bold bg-amber-50 text-amber-800 border border-amber-200/60"
                                  >
                                    <Key className="w-3 h-3 mr-1" />
                                    {permission?.name || permissionId}
                                  </span>
                                );
                              })}
                              {role.permissions.length > 2 && (
                                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-semibold bg-gray-50 text-gray-700">
                                  +{role.permissions.length - 2}
                                </span>
                              )}
                            </>
                          ) : (
                            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-50 text-gray-500 border border-gray-200">
                              无权限
                            </span>
                          )}
                        </div>
                      </div>

                      {/* 第五列：操作 */}
                      <div className="w-20 flex items-center justify-end">
                        <div className="relative">
                          <button
                            onClick={() => setOpenDropdown(openDropdown === role.id ? null : role.id)}
                            className="p-2.5 text-gray-400 hover:text-gray-600 hover:bg-white/80 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/30 backdrop-blur-sm group-hover:bg-white/60"
                          >
                            <MoreHorizontal className="w-4 h-4" />
                          </button>
                          
                          {openDropdown === role.id && (
                            <>
                              <div 
                                className="fixed inset-0 z-10" 
                                onClick={() => setOpenDropdown(null)}
                              />
                              <div className="absolute right-0 top-full mt-2 w-48 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/60 py-2 z-20 ring-1 ring-black/5">
                                <button
                                  onClick={() => openConfigModal(role)}
                                  className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-blue-50/60 transition-all duration-200 rounded-lg mx-2"
                                >
                                  <Settings className="w-4 h-4 mr-3 text-gray-500" />
                                  配置权限
                                </button>
                                <button
                                  className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-blue-50/60 transition-all duration-200 rounded-lg mx-2"
                                >
                                  <Edit className="w-4 h-4 mr-3 text-gray-500" />
                                  编辑角色
                                </button>
                                <hr className="my-2 border-gray-100" />
                                <button
                                  className="flex items-center w-full px-4 py-3 text-sm text-red-600 hover:bg-red-50/60 transition-all duration-200 rounded-lg mx-2"
                                >
                                  <Trash2 className="w-4 h-4 mr-3 text-red-400" />
                                  删除角色
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
                            <div className={`w-10 h-10 ${getRoleColor(role.name)} rounded-full flex items-center justify-center text-white font-semibold`}>
                              {role.name.charAt(0).toUpperCase()}
                            </div>
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-semibold text-gray-900 truncate">
                              {role.name}
                            </p>
                            <p className="text-sm text-gray-500 mt-1 truncate">
                              {role.description || '无描述'}
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

                      <div>
                        <p className="text-xs text-gray-500 mb-2">关联权限</p>
                        <div className="flex flex-wrap gap-1">
                          {role.permissions.length > 0 ? (
                            role.permissions.slice(0, 3).map((permissionId) => {
                              const permission = permissions.find(p => p.id === permissionId);
                              return (
                                <span
                                  key={permissionId}
                                  className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-amber-100 text-amber-800"
                                >
                                  <Key className="w-3 h-3 mr-1" />
                                  {permission?.name || permissionId}
                                </span>
                              );
                            })
                          ) : (
                            <span className="text-xs text-gray-400">暂无权限</span>
                          )}
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

      {/* 创建角色弹窗 */}
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
                      <h3 className="text-3xl font-display font-extrabold text-gray-900 mb-2 tracking-tight">创建新角色</h3>
                      <p className="text-base font-medium text-gray-600">添加新的角色到系统中</p>
                    </div>
                    <button
                      onClick={() => setShowCreateModal(false)}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-white/60 rounded-xl transition-all duration-200 backdrop-blur-sm"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  
                  <form onSubmit={handleCreateRole} className="space-y-6">
                    <div className="space-y-5">
                      <div>
                        <label className="block text-base font-bold text-gray-800 mb-3">
                          角色名称
                        </label>
                        <input
                          type="text"
                          value={roleName}
                          onChange={(e) => setRoleName(e.target.value)}
                          placeholder="输入角色名称"
                          className="w-full px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 focus:bg-white transition-all duration-200 placeholder-gray-400 text-base font-medium"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-base font-bold text-gray-800 mb-3">
                          角色描述 <span className="text-gray-500 font-medium">(可选)</span>
                        </label>
                        <textarea
                          value={roleDescription}
                          onChange={(e) => setRoleDescription(e.target.value)}
                          placeholder="输入角色描述"
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
                        disabled={creating || !roleName.trim()}
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
                            创建角色
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
      {showConfigModal && configRole && (
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
                      <div className={`w-14 h-14 ${getRoleColor(configRole.name)} rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg border-4 border-white`}>
                        {configRole.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h3 className="text-3xl font-display font-extrabold text-gray-900 tracking-tight">{configRole.name}</h3>
                        <p className="text-base font-semibold text-gray-700">{configRole.description || '无描述'}</p>
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
                        <Key className="w-5 h-5 mr-2 text-amber-600" />
                        权限配置
                      </h4>
                      
                      <div className="space-y-4">
                        <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-4">
                          <h5 className="text-base font-bold text-gray-800 mb-3">当前权限</h5>
                          <div className="flex flex-wrap gap-2">
                            {configRole.permissions.length > 0 ? (
                              configRole.permissions.map((permissionId) => {
                                const permission = permissions.find(p => p.id === permissionId);
                                return (
                                  <span
                                    key={permissionId}
                                    className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-bold bg-amber-100 text-amber-800 border border-amber-200"
                                  >
                                    {permission?.name || permissionId}
                                    <button className="ml-2 text-amber-600 hover:text-amber-800">
                                      <X className="w-3 h-3" />
                                    </button>
                                  </span>
                                );
                              })
                            ) : (
                              <span className="text-base font-medium text-gray-600">暂无权限</span>
                            )}
                          </div>
                        </div>
                        
                        <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-4">
                          <h5 className="text-base font-bold text-gray-800 mb-3">可分配权限</h5>
                          <div className="space-y-2 max-h-32 overflow-y-auto">
                            {permissions.filter(permission => !configRole.permissions.includes(permission.id)).map((permission) => (
                              <button
                                key={permission.id}
                                onClick={() => handleAssignPermission(configRole.id, permission.id)}
                                disabled={assigning}
                                className="flex items-center justify-between w-full px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors disabled:opacity-50"
                              >
                                <span>{permission.name}</span>
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