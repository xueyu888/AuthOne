import { useState, useEffect } from 'react';
import { Shield, Users, Key, UserCheck, Archive, TrendingUp, Activity } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://182.150.118.137:8000';

interface Stats {
  accounts: number;
  roles: number;
  permissions: number;
  groups: number;
  resources: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    accounts: 0,
    roles: 0,
    permissions: 0,
    groups: 0,
    resources: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [accounts, roles, permissions, groups, resources] = await Promise.all([
          axios.get(`${API_BASE}/accounts`),
          axios.get(`${API_BASE}/roles`),
          axios.get(`${API_BASE}/permissions`),
          axios.get(`${API_BASE}/groups`),
          axios.get(`${API_BASE}/resources`),
        ]);

        setStats({
          accounts: accounts.data.length,
          roles: roles.data.length,
          permissions: permissions.data.length,
          groups: groups.data.length,
          resources: resources.data.length,
        });
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statCards = [
    {
      title: '账户总数',
      value: stats.accounts,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: '角色数量',
      value: stats.roles,
      icon: UserCheck,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: '权限数量',
      value: stats.permissions,
      icon: Key,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: '用户组',
      value: stats.groups,
      icon: Users,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      title: '资源数量',
      value: stats.resources,
      icon: Archive,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
    },
  ];

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
          <h1 className="text-2xl font-bold text-gray-900">仪表盘</h1>
          <p className="text-gray-600 mt-1">管理您的权限系统</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Activity className="w-4 h-4" />
          <span>实时数据</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.title} className="card">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${card.bgColor}`}>
                  <Icon className={`w-6 h-6 ${card.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{card.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">快速操作</h3>
            <TrendingUp className="w-5 h-5 text-gray-400" />
          </div>
          <div className="space-y-3">
            <a href="/accounts" className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
              <Users className="w-5 h-5 text-blue-600 mr-3" />
              <div>
                <p className="font-medium text-gray-900">管理账户</p>
                <p className="text-sm text-gray-600">创建和管理用户账户</p>
              </div>
            </a>
            <a href="/roles" className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
              <UserCheck className="w-5 h-5 text-green-600 mr-3" />
              <div>
                <p className="font-medium text-gray-900">管理角色</p>
                <p className="text-sm text-gray-600">配置角色和权限</p>
              </div>
            </a>
            <a href="/permissions" className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
              <Key className="w-5 h-5 text-purple-600 mr-3" />
              <div>
                <p className="font-medium text-gray-900">管理权限</p>
                <p className="text-sm text-gray-600">定义系统权限</p>
              </div>
            </a>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">系统状态</h3>
            <Shield className="w-5 h-5 text-gray-400" />
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm font-medium text-green-900">API 服务</span>
              </div>
              <span className="text-sm text-green-600">正常运行</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm font-medium text-green-900">数据库</span>
              </div>
              <span className="text-sm text-green-600">连接正常</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                <span className="text-sm font-medium text-blue-900">权限引擎</span>
              </div>
              <span className="text-sm text-blue-600">活跃</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}