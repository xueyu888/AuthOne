import { useEffect, useState } from 'react';
import { Plus, Archive, Database, FileText, Smartphone, Cpu, Edit, Trash2, X, Check, Search, MoreHorizontal, Settings } from 'lucide-react';
import { 
  getResources, 
  createResource, 
  Resource 
} from '../api';

const resourceTypeIcons = {
  dataset: Database,
  app: Smartphone,
  model: Cpu,
  file: FileText,
};

const resourceTypeLabels = {
  dataset: '数据集',
  app: '应用',
  model: '模型',
  file: '文件',
};

// 生成资源图标的颜色
const getResourceColor = (type: string) => {
  const colors = {
    dataset: 'bg-blue-400',
    app: 'bg-green-400', 
    model: 'bg-purple-400',
    file: 'bg-orange-400',
  };
  
  return colors[type as keyof typeof colors] || 'bg-gray-400';
};

export default function ResourcesPage() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [resName, setResName] = useState('');
  const [resType, setResType] = useState('dataset');
  const [resDescription, setResDescription] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [configResource, setConfigResource] = useState<Resource | null>(null);
  const [selectedResources, setSelectedResources] = useState<string[]>([]);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  const fetchResources = async () => {
    try {
      const resourcesData = await getResources();
      setResources(resourcesData);
    } catch (error) {
      console.error('Failed to fetch resources:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResources();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resName.trim()) return;
    
    setCreating(true);
    try {
      await createResource(resType, resName);
      setResName('');
      setResType('dataset');
      setResDescription('');
      setShowCreateModal(false);
      await fetchResources();
    } catch (error) {
      console.error('Failed to create resource:', error);
    } finally {
      setCreating(false);
    }
  };

  const openConfigModal = (resource: Resource) => {
    setConfigResource(resource);
    setShowConfigModal(true);
    setOpenDropdown(null);
  };

  const toggleResourceSelection = (resourceId: string) => {
    setSelectedResources(prev => 
      prev.includes(resourceId) 
        ? prev.filter(id => id !== resourceId)
        : [...prev, resourceId]
    );
  };

  const selectAllResources = () => {
    if (selectedResources.length === filteredResources.length) {
      setSelectedResources([]);
    } else {
      setSelectedResources(filteredResources.map(resource => resource.id));
    }
  };

  const filteredResources = resources.filter(resource =>
    resource.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    resource.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-2xl shadow-lg mb-4">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent"></div>
          </div>
          <p className="text-gray-600 font-medium">加载资源数据...</p>
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
              <h1 className="text-4xl font-display font-extrabold text-gray-900 mb-3 tracking-tight">资源管理</h1>
              <p className="text-lg font-medium text-gray-600 tracking-wide">管理系统资源和访问控制</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-bold text-base rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 shadow-lg hover:shadow-xl tracking-wide"
            >
              <Plus className="w-5 h-5 mr-2" />
              新建资源
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
                placeholder="搜索资源名称或类型..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-base font-medium placeholder:text-gray-400 placeholder:font-normal"
              />
            </div>
            <div className="flex items-center gap-4">
              {selectedResources.length > 0 && (
                <div className="flex items-center gap-3">
                  <span className="text-base font-medium text-gray-700">
                    已选择 <span className="font-bold text-blue-600">{selectedResources.length}</span> 个资源
                  </span>
                  <button className="px-4 py-2 text-base font-semibold text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                    批量配置
                  </button>
                </div>
              )}
              <div className="flex items-center gap-2 text-base font-medium text-gray-700">
                <Archive className="w-4 h-4" />
                <span className="font-bold text-gray-900">{filteredResources.length}</span>
                <span>个资源</span>
              </div>
            </div>
          </div>
        </div>

        {/* 资源列表 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          {filteredResources.length === 0 ? (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-2xl mb-4">
                <Archive className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3 tracking-tight">暂无资源</h3>
              <p className="text-base font-medium text-gray-600 mb-6">创建第一个资源开始管理系统访问控制</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-semibold text-base rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4 mr-2" />
                创建资源
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
                        checked={selectedResources.length === filteredResources.length && filteredResources.length > 0}
                        onChange={selectAllResources}
                        className="sr-only"
                      />
                      <div className={`w-5 h-5 rounded-lg border-2 transition-all duration-200 flex items-center justify-center ${
                        selectedResources.length === filteredResources.length && filteredResources.length > 0
                          ? 'bg-blue-600 border-blue-600' 
                          : 'border-gray-300 hover:border-blue-400'
                      }`}>
                        {selectedResources.length === filteredResources.length && filteredResources.length > 0 && (
                          <Check className="w-3 h-3 text-white" />
                        )}
                      </div>
                    </label>
                  </div>
                  
                  {/* 第二列：资源 */}
                  <div className="flex-1 min-w-0 px-4">
                    <div className="text-xs font-extrabold text-gray-700 uppercase tracking-widest">
                      资源
                    </div>
                  </div>
                  
                  {/* 第三列：描述 */}
                  <div className="flex-1 min-w-0 px-4">
                    <div className="text-xs font-extrabold text-gray-700 uppercase tracking-widest">
                      描述
                    </div>
                  </div>
                  
                  {/* 第四列：类型 */}
                  <div className="flex-1 min-w-0 px-4">
                    <div className="text-xs font-extrabold text-gray-700 uppercase tracking-widest">
                      类型
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

              {/* 资源列表 */}
              <div className="divide-y divide-gray-100/60">
                {filteredResources.map((resource, index) => {
                  const IconComponent = resourceTypeIcons[resource.type as keyof typeof resourceTypeIcons] || Archive;
                  const typeLabel = resourceTypeLabels[resource.type as keyof typeof resourceTypeLabels] || resource.type;
                  
                  return (
                    <div key={resource.id} className="group hover:bg-gradient-to-r hover:from-blue-50/40 hover:to-indigo-50/20 transition-all duration-300 ease-out border-l-4 border-transparent hover:border-blue-400/30">
                      {/* 桌面端布局 */}
                      <div className="hidden lg:flex w-full px-6 py-5 items-center">
                        {/* 第一列：复选框 */}
                        <div className="w-12 flex items-center">
                          <label className="relative flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={selectedResources.includes(resource.id)}
                              onChange={() => toggleResourceSelection(resource.id)}
                              className="sr-only"
                            />
                            <div className={`w-5 h-5 rounded-lg border-2 transition-all duration-200 flex items-center justify-center ${
                              selectedResources.includes(resource.id)
                                ? 'bg-blue-600 border-blue-600 scale-110' 
                                : 'border-gray-300 hover:border-blue-400 group-hover:border-blue-300'
                            }`}>
                              {selectedResources.includes(resource.id) && (
                                <Check className="w-3 h-3 text-white" />
                              )}
                            </div>
                          </label>
                        </div>

                        {/* 第二列：资源 */}
                        <div className="flex-1 min-w-0 px-4">
                          <div className="flex items-center space-x-3">
                            <div className="flex-shrink-0">
                              <div className={`w-10 h-10 ${getResourceColor(resource.type)} rounded-full flex items-center justify-center text-white font-bold text-sm shadow-sm border-2 border-white group-hover:shadow-md transition-all duration-200`}>
                                <IconComponent className="w-5 h-5" />
                              </div>
                            </div>
                            <div className="min-w-0 flex-1">
                              <h3 className="text-base font-bold text-gray-900 truncate">
                                {resource.name}
                              </h3>
                              <div className="text-xs text-gray-500 mt-1 space-x-2">
                                <span>ID: {resource.id}</span>
                                {resource.tenant_id && <span>• 租户: {resource.tenant_id}</span>}
                                {resource.owner_id && <span>• 所有者: {resource.owner_id}</span>}
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* 第三列：描述 */}
                        <div className="flex-1 min-w-0 px-4">
                          <span className="text-sm text-gray-500 truncate block">
                            {resource.description || '无描述'}
                          </span>
                        </div>

                        {/* 第四列：类型 */}
                        <div className="flex-1 min-w-0 px-4">
                          <div className="flex flex-wrap gap-1 ml-2">
                            <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-bold border ${
                              resource.type === 'dataset' ? 'bg-blue-50 text-blue-800 border-blue-200/60' :
                              resource.type === 'app' ? 'bg-green-50 text-green-800 border-green-200/60' :
                              resource.type === 'model' ? 'bg-purple-50 text-purple-800 border-purple-200/60' :
                              resource.type === 'file' ? 'bg-orange-50 text-orange-800 border-orange-200/60' :
                              'bg-gray-50 text-gray-800 border-gray-200/60'
                            }`}>
                              <IconComponent className="w-3 h-3 mr-1" />
                              {typeLabel}
                            </span>
                          </div>
                        </div>

                        {/* 第五列：操作 */}
                        <div className="w-20 flex items-center justify-end">
                          <div className="relative">
                            <button
                              onClick={() => setOpenDropdown(openDropdown === resource.id ? null : resource.id)}
                              className="p-2.5 text-gray-400 hover:text-gray-600 hover:bg-white/80 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/30 backdrop-blur-sm group-hover:bg-white/60"
                            >
                              <MoreHorizontal className="w-4 h-4" />
                            </button>
                            
                            {openDropdown === resource.id && (
                              <>
                                <div 
                                  className="fixed inset-0 z-10" 
                                  onClick={() => setOpenDropdown(null)}
                                />
                                <div className="absolute right-0 top-full mt-2 w-48 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/60 py-2 z-20 ring-1 ring-black/5">
                                  <button
                                    onClick={() => openConfigModal(resource)}
                                    className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-blue-50/60 transition-all duration-200 rounded-lg mx-2"
                                  >
                                    <Settings className="w-4 h-4 mr-3 text-gray-500" />
                                    配置访问控制
                                  </button>
                                  <button
                                    className="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-blue-50/60 transition-all duration-200 rounded-lg mx-2"
                                  >
                                    <Edit className="w-4 h-4 mr-3 text-gray-500" />
                                    编辑资源
                                  </button>
                                  <hr className="my-2 border-gray-100" />
                                  <button
                                    className="flex items-center w-full px-4 py-3 text-sm text-red-600 hover:bg-red-50/60 transition-all duration-200 rounded-lg mx-2"
                                  >
                                    <Trash2 className="w-4 h-4 mr-3 text-red-400" />
                                    删除资源
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
                              <div className={`w-10 h-10 ${getResourceColor(resource.type)} rounded-xl flex items-center justify-center text-white font-semibold`}>
                                <IconComponent className="w-5 h-5" />
                              </div>
                            </div>
                            <div className="min-w-0 flex-1">
                              <p className="text-sm font-semibold text-gray-900 truncate">
                                {resource.name}
                              </p>
                              <p className="text-sm text-gray-500 mt-1 truncate">
                                {resource.description || '无描述'}
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
                          <p className="text-xs text-gray-500 mb-2">资源类型</p>
                          <div className="flex flex-wrap gap-1">
                            <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${
                              resource.type === 'dataset' ? 'bg-blue-100 text-blue-800' :
                              resource.type === 'app' ? 'bg-green-100 text-green-800' :
                              resource.type === 'model' ? 'bg-purple-100 text-purple-800' :
                              resource.type === 'file' ? 'bg-orange-100 text-orange-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              <IconComponent className="w-3 h-3 mr-1" />
                              {typeLabel}
                            </span>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
                          <div>
                            <span className="font-medium">所有者ID:</span>
                            <div className="mt-1">{resource.owner_id || '无'}</div>
                          </div>
                          <div>
                            <span className="font-medium">租户ID:</span>
                            <div className="mt-1">{resource.tenant_id || '无'}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>
      </div>

      {/* 创建资源弹窗 */}
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
                      <h3 className="text-3xl font-display font-extrabold text-gray-900 mb-2 tracking-tight">创建新资源</h3>
                      <p className="text-base font-medium text-gray-600">添加新的资源到系统中</p>
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
                          资源名称
                        </label>
                        <input
                          type="text"
                          value={resName}
                          onChange={(e) => setResName(e.target.value)}
                          placeholder="输入资源名称"
                          className="w-full px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 focus:bg-white transition-all duration-200 placeholder-gray-400 text-base font-medium"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-base font-bold text-gray-800 mb-3">
                          资源类型
                        </label>
                        <select
                          value={resType}
                          onChange={(e) => setResType(e.target.value)}
                          className="w-full px-4 py-4 bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 focus:bg-white transition-all duration-200 text-base font-medium"
                        >
                          <option value="dataset">数据集</option>
                          <option value="app">应用</option>
                          <option value="model">模型</option>
                          <option value="file">文件</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-base font-bold text-gray-800 mb-3">
                          资源描述 <span className="text-gray-500 font-medium">(可选)</span>
                        </label>
                        <textarea
                          value={resDescription}
                          onChange={(e) => setResDescription(e.target.value)}
                          placeholder="输入资源描述"
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
                        disabled={creating || !resName.trim()}
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
                            创建资源
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

      {/* 资源配置弹窗 */}
      {showConfigModal && configResource && (
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
                      <div className={`w-14 h-14 ${getResourceColor(configResource.type)} rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg ring-4 ring-white`}>
                        {React.createElement(resourceTypeIcons[configResource.type as keyof typeof resourceTypeIcons] || Archive, { className: "w-8 h-8" })}
                      </div>
                      <div>
                        <h3 className="text-3xl font-display font-extrabold text-gray-900 tracking-tight">{configResource.name}</h3>
                        <p className="text-base font-semibold text-gray-700">{resourceTypeLabels[configResource.type as keyof typeof resourceTypeLabels] || configResource.type}</p>
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
                        <Settings className="w-5 h-5 mr-2 text-gray-600" />
                        访问控制
                      </h4>
                      
                      <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-6">
                        <div className="text-center">
                          <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                          <h5 className="text-lg font-bold text-gray-800 mb-2">配置资源访问权限</h5>
                          <p className="text-base font-medium text-gray-600">管理谁可以访问此资源以及具体的操作权限</p>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-4">
                        <h5 className="text-base font-bold text-gray-800 mb-3">资源信息</h5>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">资源ID:</span>
                            <span className="font-medium text-gray-900">{configResource.id}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">所有者:</span>
                            <span className="font-medium text-gray-900">{configResource.owner_id || '无'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">租户:</span>
                            <span className="font-medium text-gray-900">{configResource.tenant_id || '无'}</span>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white/70 backdrop-blur-sm border border-gray-200/60 rounded-2xl p-4">
                        <h5 className="text-base font-bold text-gray-800 mb-3">权限设置</h5>
                        <div className="space-y-2">
                          <button className="w-full px-3 py-2 text-left text-base font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                            管理访问权限
                          </button>
                          <button className="w-full px-3 py-2 text-left text-base font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                            设置权限策略
                          </button>
                          <button className="w-full px-3 py-2 text-left text-base font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                            查看访问日志
                          </button>
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