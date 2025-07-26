import { useEffect, useState } from 'react';
import { Plus, Archive, Database, FileText, Smartphone, Cpu, Edit, Trash2 } from 'lucide-react';
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

export default function ResourcesPage() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [resName, setResName] = useState('');
  const [resType, setResType] = useState('dataset');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

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
      await fetchResources();
    } catch (error) {
      console.error('Failed to create resource:', error);
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
          <h1 className="text-2xl font-bold text-gray-900">资源管理</h1>
          <p className="text-gray-600 mt-1">管理系统资源和访问控制</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">已有资源</h2>
              <span className="text-sm text-gray-500">{resources.length} 个资源</span>
            </div>
            
            {resources.length === 0 ? (
              <div className="text-center py-8">
                <Archive className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">暂无资源</p>
              </div>
            ) : (
              <div className="space-y-3">
                {resources.map((resource) => {
                  const IconComponent = resourceTypeIcons[resource.type as keyof typeof resourceTypeIcons] || Archive;
                  const typeLabel = resourceTypeLabels[resource.type as keyof typeof resourceTypeLabels] || resource.type;
                  
                  return (
                    <div key={resource.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center">
                            <IconComponent className="w-5 h-5 text-orange-600 mr-2" />
                            <h3 className="font-medium text-gray-900">{resource.name}</h3>
                          </div>
                          <div className="flex items-center mt-1">
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-orange-100 text-orange-700">
                              {typeLabel}
                            </span>
                          </div>
                          <div className="flex items-center mt-2 text-xs text-gray-500">
                            <span>ID: {resource.id}</span>
                            {resource.tenant_id && <span className="ml-4">租户: {resource.tenant_id}</span>}
                            {resource.owner_id && <span className="ml-4">所有者: {resource.owner_id}</span>}
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
                  );
                })}
              </div>
            )}
          </div>
        </div>

        <div>
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">创建新资源</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  资源名称
                </label>
                <input
                  type="text"
                  value={resName}
                  onChange={(e) => setResName(e.target.value)}
                  placeholder="输入资源名称"
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  资源类型
                </label>
                <select
                  value={resType}
                  onChange={(e) => setResType(e.target.value)}
                  className="input-field"
                >
                  <option value="dataset">数据集</option>
                  <option value="app">应用</option>
                  <option value="model">模型</option>
                  <option value="file">文件</option>
                </select>
              </div>
              <button 
                type="submit" 
                disabled={creating || !resName.trim()}
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
                    创建资源
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