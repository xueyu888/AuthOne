import { useQuery } from "@tanstack/react-query"
import { getAccounts, getRoles, getGroups, getPermissions, getResources } from "../api"
import { Users, Shield, Settings, Archive, TrendingUp, Activity, CheckCircle, AlertCircle } from "lucide-react"
import { useTranslation } from "../contexts/TranslationContext"

const TENANT_ID = "default_tenant"

export default function Dashboard() {
  const { t } = useTranslation()

  const { data: accounts } = useQuery({
    queryKey: ["accounts", TENANT_ID],
    queryFn: () => getAccounts(TENANT_ID),
  })

  const { data: roles } = useQuery({
    queryKey: ["roles", TENANT_ID],
    queryFn: () => getRoles(TENANT_ID),
  })

  const { data: groups } = useQuery({
    queryKey: ["groups", TENANT_ID],
    queryFn: () => getGroups(TENANT_ID),
  })

  const { data: permissions } = useQuery({
    queryKey: ["permissions", TENANT_ID],
    queryFn: () => getPermissions(TENANT_ID),
  })

  const { data: resources } = useQuery({
    queryKey: ["resources", TENANT_ID],
    queryFn: () => getResources(TENANT_ID),
  })

  const stats = [
    {
      name: t('users'),
      value: accounts?.length || 0,
      icon: Users,
      color: 'bg-blue-500',
      lightBg: 'bg-blue-50 dark:bg-blue-900/20',
      textColor: 'text-blue-600 dark:text-blue-400'
    },
    {
      name: t('roles'),
      value: roles?.length || 0,
      icon: Shield,
      color: 'bg-purple-500',
      lightBg: 'bg-purple-50 dark:bg-purple-900/20',
      textColor: 'text-purple-600 dark:text-purple-400'
    },
    {
      name: t('groups'),
      value: groups?.length || 0,
      icon: Settings,
      color: 'bg-green-500',
      lightBg: 'bg-green-50 dark:bg-green-900/20',
      textColor: 'text-green-600 dark:text-green-400'
    },
    {
      name: t('permissions'),
      value: permissions?.length || 0,
      icon: Archive,
      color: 'bg-orange-500',
      lightBg: 'bg-orange-50 dark:bg-orange-900/20',
      textColor: 'text-orange-600 dark:text-orange-400'
    },
    {
      name: t('resourceManagement'),
      value: resources?.length || 0,
      icon: Archive,
      color: 'bg-indigo-500',
      lightBg: 'bg-indigo-50 dark:bg-indigo-900/20',
      textColor: 'text-indigo-600 dark:text-indigo-400'
    }
  ]

  const recentActivities = [
    { id: 1, type: 'user', message: t('userCreated'), time: '5分钟前', status: 'success' },
    { id: 2, type: 'role', message: t('roleUpdated'), time: '10分钟前', status: 'info' },
    { id: 3, type: 'permission', message: t('permissionAssigned'), time: '15分钟前', status: 'success' },
    { id: 4, type: 'resource', message: t('resourceAccessed'), time: '20分钟前', status: 'warning' },
  ]

  return (
    <div className="flex h-screen -my-8 -mx-6">
      {/* 主内容区域 */}
      <div className="flex-1 bg-slate-50 dark:bg-slate-900 flex flex-col overflow-hidden">
        <div className="p-6 flex-1 overflow-auto">
          {/* 页面标题 */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">{t('dashboardTitle')}</h1>
            <p className="text-slate-600 dark:text-slate-400">{t('dashboardSubtitle')}</p>
          </div>

          {/* 统计卡片 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
            {stats.map((stat) => {
              const Icon = stat.icon
              return (
                <div key={stat.name} className="bg-white dark:bg-slate-800 rounded-lg p-6 border border-slate-200 dark:border-slate-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-600 dark:text-slate-400">{stat.name}</p>
                      <p className="text-2xl font-bold text-slate-900 dark:text-slate-100 mt-1">{stat.value}</p>
                    </div>
                    <div className={`p-3 rounded-lg ${stat.lightBg}`}>
                      <Icon className={`w-6 h-6 ${stat.textColor}`} />
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {/* 内容区域 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 系统状态 */}
            <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
              <div className="p-6 border-b border-slate-200 dark:border-slate-700">
                <div className="flex items-center space-x-2">
                  <Activity className="w-5 h-5" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('systemStatus')}</h2>
                </div>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-slate-700 dark:text-slate-300">{t('authService')}</span>
                    </div>
                    <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                      {t('running')}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-slate-700 dark:text-slate-300">{t('database')}</span>
                    </div>
                    <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                      {t('healthy')}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <AlertCircle className="w-5 h-5 text-yellow-500" />
                      <span className="text-slate-700 dark:text-slate-300">{t('cache')}</span>
                    </div>
                    <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 text-xs rounded-full">
                      {t('warning')}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* 最近活动 */}
            <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
              <div className="p-6 border-b border-slate-200 dark:border-slate-700">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-5 h-5" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('recentActivity')}</h2>
                </div>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {recentActivities.map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${
                        activity.status === 'success' ? 'bg-green-500' :
                        activity.status === 'info' ? 'bg-blue-500' :
                        activity.status === 'warning' ? 'bg-yellow-500' : 'bg-gray-500'
                      }`}></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-900 dark:text-slate-100">{activity.message}</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}