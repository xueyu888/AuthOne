import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { getAccounts, createAccount, getRoles, getGroups, createRole, createGroup, Account, Role, Group } from "../api"
import { Users, UserPlus, Settings, Shield, X } from "lucide-react"
import { useTranslation } from "../contexts/TranslationContext"

const TENANT_ID = "default_tenant"

export default function Accounts() {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<'users' | 'roles' | 'groups'>('users')
  const [showCreateUser, setShowCreateUser] = useState(false)
  const [showCreateRole, setShowCreateRole] = useState(false)
  const [showCreateGroup, setShowCreateGroup] = useState(false)
  const queryClient = useQueryClient()

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

  const createAccountMutation = useMutation({
    mutationFn: ({ username, email }: { username: string; email: string }) => 
      createAccount(username, email, TENANT_ID),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts", TENANT_ID] })
      setShowCreateUser(false)
    },
  })

  const createRoleMutation = useMutation({
    mutationFn: ({ name, description }: { name: string; description: string }) => 
      createRole(name, TENANT_ID, description),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles", TENANT_ID] })
      setShowCreateRole(false)
    },
  })

  const createGroupMutation = useMutation({
    mutationFn: ({ name, description }: { name: string; description: string }) => 
      createGroup(name, TENANT_ID, description),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["groups", TENANT_ID] })
      setShowCreateGroup(false)
    },
  })

  const handleCreateUser = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    const username = formData.get("username") as string
    const email = formData.get("email") as string
    createAccountMutation.mutate({ username, email })
  }

  const handleCreateRole = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    const name = formData.get("name") as string
    const description = formData.get("description") as string
    createRoleMutation.mutate({ name, description })
  }

  const handleCreateGroup = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    const name = formData.get("name") as string
    const description = formData.get("description") as string
    createGroupMutation.mutate({ name, description })
  }

  const sidebarItems = [
    { id: 'users' as const, label: t('users'), icon: Users, count: accounts?.length || 0 },
    { id: 'roles' as const, label: t('roles'), icon: Shield, count: roles?.length || 0 },
    { id: 'groups' as const, label: t('groups'), icon: Settings, count: groups?.length || 0 },
  ]

  return (
    <div className="flex min-h-screen -my-8 -mx-6">
      {/* 侧边栏 */}
      <div className="w-80 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col">
        <div className="p-6 flex-1">
          <div className="space-y-2">
            {sidebarItems.map((item) => {
              const Icon = item.icon
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-lg text-left transition-all duration-200 ${
                    activeTab === item.id
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </div>
                  <span className="px-2 py-1 bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs rounded-full">
                    {item.count}
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="flex-1 bg-slate-50 dark:bg-slate-900 flex flex-col">
        <div className="p-6 flex-1">
          {activeTab === 'users' && (
            <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
            <div className="p-6 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('userManagementTitle')}</h2>
                </div>
                <button
                  onClick={() => setShowCreateUser(true)}
                  className="flex items-center space-x-2 px-5 py-2.5 bg-slate-900 dark:bg-slate-700 text-white rounded-lg hover:bg-slate-800 dark:hover:bg-slate-600 transition-colors font-medium shadow-sm"
                >
                  <UserPlus className="w-4 h-4" />
                  <span>{t('createUser')}</span>
                </button>
              </div>
            </div>
            <div className="border-t border-slate-200 dark:border-slate-700">
              <div className="overflow-x-auto max-h-96 overflow-y-auto">
                <table className="w-full">
                  <thead className="sticky top-0 bg-white dark:bg-slate-800 z-10">
                    <tr className="border-b border-slate-200 dark:border-slate-700">
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('username')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('email')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('roles')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('groups')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                  {accounts?.map((account) => (
                    <tr key={account.id} className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-750">
                      <td className="py-3 px-6 font-medium text-slate-900 dark:text-slate-100">{account.username}</td>
                      <td className="py-3 px-6 text-slate-600 dark:text-slate-400">{account.email}</td>
                      <td className="py-3 px-6">
                        <div className="flex flex-wrap gap-1">
                          {account.roles.map((roleId) => {
                            const role = roles?.find(r => r.id === roleId)
                            return role ? (
                              <span key={roleId} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                                {role.name}
                              </span>
                            ) : null
                          })}
                        </div>
                      </td>
                      <td className="py-3 px-6">
                        <div className="flex flex-wrap gap-1">
                          {account.groups.map((groupId) => {
                            const group = groups?.find(g => g.id === groupId)
                            return group ? (
                              <span key={groupId} className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                                {group.name}
                              </span>
                            ) : null
                          })}
                        </div>
                      </td>
                      <td className="py-3 px-6">
                        <button className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
                          {t('edit')}
                        </button>
                      </td>
                    </tr>
                  ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

          {activeTab === 'roles' && (
            <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
            <div className="p-6 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Shield className="w-5 h-5" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('roleManagementTitle')}</h2>
                </div>
                <button
                  onClick={() => setShowCreateRole(true)}
                  className="flex items-center space-x-2 px-5 py-2.5 bg-slate-900 dark:bg-slate-700 text-white rounded-lg hover:bg-slate-800 dark:hover:bg-slate-600 transition-colors font-medium shadow-sm"
                >
                  <Shield className="w-4 h-4" />
                  <span>{t('createRole')}</span>
                </button>
              </div>
            </div>
            <div className="border-t border-slate-200 dark:border-slate-700">
              <div className="overflow-x-auto max-h-96 overflow-y-auto">
                <table className="w-full">
                  <thead className="sticky top-0 bg-white dark:bg-slate-800 z-10">
                    <tr className="border-b border-slate-200 dark:border-slate-700">
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('roleName')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('description')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('permissionCount')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                  {roles?.map((role) => (
                    <tr key={role.id} className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-750">
                      <td className="py-3 px-6 font-medium text-slate-900 dark:text-slate-100">{role.name}</td>
                      <td className="py-3 px-6 text-slate-600 dark:text-slate-400">{role.description}</td>
                      <td className="py-3 px-6">
                        <span className="px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 text-xs rounded-full">
                          {role.permissions.length}{t('permissions')}
                        </span>
                      </td>
                      <td className="py-3 px-6">
                        <div className="flex space-x-2">
                          <button className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
                            {t('edit')}
                          </button>
                          <button className="text-sm text-green-600 dark:text-green-400 hover:text-green-700 dark:hover:text-green-300">
                            {t('assignPermissions')}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

          {activeTab === 'groups' && (
            <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
            <div className="p-6 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Settings className="w-5 h-5" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('groupManagementTitle')}</h2>
                </div>
                <button
                  onClick={() => setShowCreateGroup(true)}
                  className="flex items-center space-x-2 px-5 py-2.5 bg-slate-900 dark:bg-slate-700 text-white rounded-lg hover:bg-slate-800 dark:hover:bg-slate-600 transition-colors font-medium shadow-sm"
                >
                  <Settings className="w-4 h-4" />
                  <span>{t('createGroup')}</span>
                </button>
              </div>
            </div>
            <div className="border-t border-slate-200 dark:border-slate-700">
              <div className="overflow-x-auto max-h-96 overflow-y-auto">
                <table className="w-full">
                  <thead className="sticky top-0 bg-white dark:bg-slate-800 z-10">
                    <tr className="border-b border-slate-200 dark:border-slate-700">
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('groupName')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('roleCount')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                  {groups?.map((group) => (
                    <tr key={group.id} className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-750">
                      <td className="py-3 px-6 font-medium text-slate-900 dark:text-slate-100">{group.name}</td>
                      <td className="py-3 px-6">
                        <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs rounded-full">
                          {group.roles.length}{t('rolesCount')}
                        </span>
                      </td>
                      <td className="py-3 px-6">
                        <div className="flex space-x-2">
                          <button className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300">
                            {t('edit')}
                          </button>
                          <button className="text-sm text-green-600 dark:text-green-400 hover:text-green-700 dark:hover:text-green-300">
                            {t('assignRoles')}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          )}
        </div>
      </div>

      {/* 创建用户弹窗 */}
      {showCreateUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('createNewUser')}</h3>
              <button
                onClick={() => setShowCreateUser(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('username')}</label>
                <input
                  name="username"
                  required
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('email')}</label>
                <input
                  name="email"
                  type="email"
                  required
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateUser(false)}
                  className="px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
                >
                  {t('cancel')}
                </button>
                <button
                  type="submit"
                  disabled={createAccountMutation.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {createAccountMutation.isPending ? t('creating') : t('create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 创建角色弹窗 */}
      {showCreateRole && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('createNewRole')}</h3>
              <button
                onClick={() => setShowCreateRole(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateRole} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('roleName')}</label>
                <input
                  name="name"
                  required
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('description')}</label>
                <input
                  name="description"
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateRole(false)}
                  className="px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
                >
                  {t('cancel')}
                </button>
                <button
                  type="submit"
                  disabled={createRoleMutation.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {createRoleMutation.isPending ? t('creating') : t('create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 创建用户组弹窗 */}
      {showCreateGroup && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('createNewGroup')}</h3>
              <button
                onClick={() => setShowCreateGroup(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateGroup} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('groupName')}</label>
                <input
                  name="name"
                  required
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('description')}</label>
                <input
                  name="description"
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateGroup(false)}
                  className="px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
                >
                  {t('cancel')}
                </button>
                <button
                  type="submit"
                  disabled={createGroupMutation.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {createGroupMutation.isPending ? t('creating') : t('create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}