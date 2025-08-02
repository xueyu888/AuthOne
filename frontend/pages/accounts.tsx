import { useState, useEffect, useRef } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { getAccounts, createAccount, updateAccountRolesAndGroups, getRoles, getGroups, createRole, createGroup, getPermissions, Account, Role, Group, Permission } from "../api"
import { User, UserPlus, Settings, Badge, X, Users, Edit, Trash2 } from "lucide-react"
import { useTranslation } from "../contexts/TranslationContext"

interface TruncatedTextProps {
  text: string
  maxLength: number
  className?: string
}

function TruncatedText({ text, maxLength, className = "" }: TruncatedTextProps) {
  const needsTruncation = text.length > maxLength
  const triggerRef = useRef<HTMLDivElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    const updateTooltipPosition = () => {
      if (triggerRef.current && tooltipRef.current) {
        const rect = triggerRef.current.getBoundingClientRect()
        const tooltipRect = tooltipRef.current.getBoundingClientRect()
        
        tooltipRef.current.style.left = `${rect.left + rect.width / 2 - tooltipRect.width / 2}px`
        tooltipRef.current.style.top = `${rect.top - tooltipRect.height - 8}px`
      }
    }
    
    const trigger = triggerRef.current
    if (trigger) {
      trigger.addEventListener('mouseenter', updateTooltipPosition)
      trigger.addEventListener('mouseleave', updateTooltipPosition)
      
      return () => {
        trigger.removeEventListener('mouseenter', updateTooltipPosition)
        trigger.removeEventListener('mouseleave', updateTooltipPosition)
      }
    }
  }, [])
  
  if (!needsTruncation) {
    return <span className={className}>{text}</span>
  }
  
  return (
    <div ref={triggerRef} className="relative group inline-block w-full">
      <span 
        className={`${className} truncate block`} 
        style={{ maxWidth: `${maxLength * 0.55}em` }}
      >
        {text}
      </span>
      {/* Tooltip - 使用 fixed 定位避免被容器截断 */}
      <div ref={tooltipRef} className="fixed opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-[9999] px-3 py-2 bg-gray-900 dark:bg-gray-700 text-white text-sm rounded-lg shadow-lg">
        {text}
        {/* Arrow */}
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
      </div>
    </div>
  )
}


const TENANT_ID = "default_tenant"

export default function Accounts() {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<'users' | 'roles' | 'groups'>('users')
  const [showCreateUser, setShowCreateUser] = useState(false)
  const [showCreateRole, setShowCreateRole] = useState(false)
  const [showCreateGroup, setShowCreateGroup] = useState(false)
  const [showEditUser, setShowEditUser] = useState(false)
  const [editingUser, setEditingUser] = useState<Account | null>(null)
  const [selectedRoles, setSelectedRoles] = useState<string[]>([])
  const [selectedGroups, setSelectedGroups] = useState<string[]>([])
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([])
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

  const { data: permissions } = useQuery({
    queryKey: ["permissions", TENANT_ID],
    queryFn: () => getPermissions(TENANT_ID),
  })

  const createAccountMutation = useMutation({
    mutationFn: ({ username, email }: { username: string; email: string }) => 
      createAccount(username, email, TENANT_ID),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts", TENANT_ID] })
      setShowCreateUser(false)
      setSelectedRoles([])
      setSelectedGroups([])
    },
  })

  const createRoleMutation = useMutation({
    mutationFn: ({ name, description }: { name: string; description: string }) => 
      createRole(name, TENANT_ID, description),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles", TENANT_ID] })
      setShowCreateRole(false)
      setSelectedPermissions([])
    },
  })

  const createGroupMutation = useMutation({
    mutationFn: ({ name, description }: { name: string; description: string }) => 
      createGroup(name, TENANT_ID, description),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["groups", TENANT_ID] })
      setShowCreateGroup(false)
      setSelectedPermissions([])
    },
  })

  const updateAccountMutation = useMutation({
    mutationFn: ({ accountId, roles, groups, currentRoles, currentGroups }: { accountId: string; roles: string[]; groups: string[]; currentRoles: string[]; currentGroups: string[] }) => 
      updateAccountRolesAndGroups(accountId, roles, groups, currentRoles, currentGroups),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts", TENANT_ID] })
      setShowEditUser(false)
      setEditingUser(null)
      setSelectedRoles([])
      setSelectedGroups([])
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

  const handleEditUser = (user: Account) => {
    setEditingUser(user)
    setSelectedRoles(user.roles)
    setSelectedGroups(user.groups)
    setShowEditUser(true)
  }

  const handleUpdateUser = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!editingUser) return
    
    updateAccountMutation.mutate({
      accountId: editingUser.id,
      roles: selectedRoles,
      groups: selectedGroups,
      currentRoles: editingUser.roles,
      currentGroups: editingUser.groups
    })
  }

  const sidebarItems = [
    { id: 'users' as const, label: t('users'), icon: User, count: accounts?.length || 0 },
    { id: 'roles' as const, label: t('roles'), icon: Badge, count: roles?.length || 0 },
    { id: 'groups' as const, label: t('groups'), icon: Users, count: groups?.length || 0 },
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
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-lg text-left transition-colors duration-150 ${
                    activeTab === item.id
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200 border border-transparent'
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
            <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 h-full flex flex-col">
            <div className="p-6 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <User className="w-5 h-5" />
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
            <div className="border-t border-slate-200 dark:border-slate-700 flex-1 flex flex-col min-h-0">
              <div className="overflow-x-auto overflow-y-auto flex-1">
                <table className="w-full">
                  <thead className="sticky top-0 bg-white dark:bg-slate-800 z-10">
                    <tr className="border-b border-slate-200 dark:border-slate-700">
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-1/5">{t('username')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-1/4">{t('email')}</th>
                      <th className="text-center py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-1/5">{t('roles')}</th>
                      <th className="text-center py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-1/5">{t('groups')}</th>
                      <th className="text-center py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-1/8">{t('actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                  {accounts?.map((account) => (
                    <tr key={account.id} className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50">
                      <td className="py-3 px-6 font-medium text-slate-900 dark:text-slate-100 text-left">
                        <TruncatedText text={account.username} maxLength={15} />
                      </td>
                      <td className="py-3 px-6 text-slate-600 dark:text-slate-400 text-left">
                        <TruncatedText text={account.email} maxLength={25} />
                      </td>
                      <td className="py-3 px-6 text-center">
                        <div className="flex flex-wrap gap-1 justify-center">
                          {account.roles.map((roleId) => {
                            const role = roles?.find(r => r.id === roleId)
                            return role ? (
                              <div key={roleId} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                                {role.name}
                              </div>
                            ) : null
                          })}
                          {account.roles.length === 0 && (
                            <div className="text-slate-500 dark:text-slate-400 text-xs">
                              {t('unassigned')}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-6 text-center">
                        <div className="flex flex-wrap gap-1 justify-center">
                          {account.groups.map((groupId) => {
                            const group = groups?.find(g => g.id === groupId)
                            return group ? (
                              <div key={groupId} className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                                {group.name}
                              </div>
                            ) : null
                          })}
                          {account.groups.length === 0 && (
                            <div className="text-slate-500 dark:text-slate-400 text-xs">
                              {t('unassigned')}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-6 text-center">
                        <div className="flex gap-2 justify-center">
                          <button 
                            onClick={() => handleEditUser(account)}
                            className="p-1 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button className="p-1 text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded">
                            <Trash2 className="w-4 h-4" />
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

          {activeTab === 'roles' && (
            <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 h-full flex flex-col">
            <div className="p-6 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Badge className="w-5 h-5" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('roleManagementTitle')}</h2>
                </div>
                <button
                  onClick={() => setShowCreateRole(true)}
                  className="flex items-center space-x-2 px-5 py-2.5 bg-slate-900 dark:bg-slate-700 text-white rounded-lg hover:bg-slate-800 dark:hover:bg-slate-600 transition-colors font-medium shadow-sm"
                >
                  <Badge className="w-4 h-4" />
                  <span>{t('createRole')}</span>
                </button>
              </div>
            </div>
            <div className="border-t border-slate-200 dark:border-slate-700 flex-1 flex flex-col min-h-0">
              <div className="overflow-x-auto overflow-y-auto flex-1">
                <table className="w-full">
                  <thead className="sticky top-0 bg-white dark:bg-slate-800 z-10">
                    <tr className="border-b border-slate-200 dark:border-slate-700">
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-1/4">{t('roleName')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-2/5">{t('description')}</th>
                      <th className="text-center py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-1/5">{t('permissionCount')}</th>
                      <th className="text-center py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-1/6">{t('actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                  {roles?.map((role) => (
                    <tr key={role.id} className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50">
                      <td className="py-3 px-6 font-medium text-slate-900 dark:text-slate-100 text-left">
                        <TruncatedText text={role.name} maxLength={20} />
                      </td>
                      <td className="py-3 px-6 text-slate-600 dark:text-slate-400 text-left">
                        <TruncatedText text={role.description || ''} maxLength={30} />
                      </td>
                      <td className="py-3 px-6 text-center">
                        <div className="relative group">
                          <span className="inline-block px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 text-xs rounded-full cursor-pointer hover:bg-orange-200 dark:hover:bg-orange-900/50 transition-colors">
                            {role.permissions.length}{t('permissions')}
                          </span>
                          {/* Expandable permission list */}
                          {role.permissions.length > 0 && (
                            <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none group-hover:pointer-events-auto z-10 min-w-48 max-w-64">
                              <div className="p-3">
                                <div className="text-xs font-medium text-slate-700 dark:text-slate-300 mb-2">{t('permissionList')}</div>
                                <div className="max-h-32 overflow-y-auto space-y-1">
                                  {role.permissions.map(permissionId => {
                                    const permission = permissions?.find(p => p.id === permissionId)
                                    return permission ? (
                                      <div key={permissionId} className="text-xs text-slate-600 dark:text-slate-400 p-1 bg-slate-50 dark:bg-slate-700 rounded">
                                        <div className="font-medium">{permission.name}</div>
                                        {permission.description && (
                                          <div className="text-slate-500 dark:text-slate-500 mt-0.5">{permission.description}</div>
                                        )}
                                      </div>
                                    ) : null
                                  })}
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-6 text-center">
                        <div className="flex gap-2 justify-center">
                          <button className="p-1 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded">
                            <Edit className="w-4 h-4" />
                          </button>
                          <button className="p-1 text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded">
                            <Trash2 className="w-4 h-4" />
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
            <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 h-full flex flex-col">
            <div className="p-6 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('groupManagementTitle')}</h2>
                </div>
                <button
                  onClick={() => setShowCreateGroup(true)}
                  className="flex items-center space-x-2 px-5 py-2.5 bg-slate-900 dark:bg-slate-700 text-white rounded-lg hover:bg-slate-800 dark:hover:bg-slate-600 transition-colors font-medium shadow-sm"
                >
                  <Users className="w-4 h-4" />
                  <span>{t('createGroup')}</span>
                </button>
              </div>
            </div>
            <div className="border-t border-slate-200 dark:border-slate-700 flex-1 flex flex-col min-h-0">
              <div className="overflow-x-auto overflow-y-auto flex-1">
                <table className="w-full">
                  <thead className="sticky top-0 bg-white dark:bg-slate-800 z-10">
                    <tr className="border-b border-slate-200 dark:border-slate-700">
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-1/4">{t('groupName')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-2/5">{t('description')}</th>
                      <th className="text-center py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-1/5">{t('userCount')}</th>
                      <th className="text-center py-3 px-6 font-medium text-slate-700 dark:text-slate-300 w-1/6">{t('actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                  {groups?.map((group) => {
                    // Calculate user count based on accounts that have this group
                    const userCount = accounts?.filter(account => account.groups.includes(group.id)).length || 0
                    return (
                      <tr key={group.id} className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50">
                        <td className="py-3 px-6 font-medium text-slate-900 dark:text-slate-100 text-left">
                          <TruncatedText text={group.name} maxLength={20} />
                        </td>
                        <td className="py-3 px-6 text-slate-600 dark:text-slate-400 text-left">
                          <TruncatedText text={group.description || ''} maxLength={30} />
                        </td>
                        <td className="py-3 px-6 text-center">
                          <div className="relative group">
                            <span className="inline-block px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs rounded-full cursor-pointer hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors">
                              {userCount}{t('usersCount')}
                            </span>
                            {/* Expandable user list */}
                            {userCount > 0 && (
                              <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none group-hover:pointer-events-auto z-10 min-w-48 max-w-64">
                                <div className="p-3">
                                  <div className="text-xs font-medium text-slate-700 dark:text-slate-300 mb-2">{t('userList')}</div>
                                  <div className="max-h-32 overflow-y-auto space-y-1">
                                    {accounts?.filter(account => account.groups.includes(group.id)).map(account => (
                                      <div key={account.id} className="text-xs text-slate-600 dark:text-slate-400 p-1 bg-slate-50 dark:bg-slate-700 rounded">
                                        <div className="font-medium">{account.username}</div>
                                        <div className="text-slate-500 dark:text-slate-500 mt-0.5">{account.email}</div>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-6 text-center">
                          <div className="flex gap-2 justify-center">
                            <button className="p-1 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded">
                              <Edit className="w-4 h-4" />
                            </button>
                            <button className="p-1 text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
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
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('roles')}</label>
                <select 
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => {
                    const roleId = e.target.value
                    if (roleId && !selectedRoles.includes(roleId)) {
                      setSelectedRoles([...selectedRoles, roleId])
                    }
                    e.target.value = ''
                  }}
                >
                  <option value="">{t('selectRole')}</option>
                  {roles?.filter(role => !selectedRoles.includes(role.id)).map(role => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                  ))}
                </select>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedRoles.map(roleId => {
                    const role = roles?.find(r => r.id === roleId)
                    return role ? (
                      <span key={roleId} className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                        {role.name}
                        <button
                          type="button"
                          onClick={() => setSelectedRoles(selectedRoles.filter(id => id !== roleId))}
                          className="hover:text-blue-900 dark:hover:text-blue-100"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ) : null
                  })}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('groups')}</label>
                <select 
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => {
                    const groupId = e.target.value
                    if (groupId && !selectedGroups.includes(groupId)) {
                      setSelectedGroups([...selectedGroups, groupId])
                    }
                    e.target.value = ''
                  }}
                >
                  <option value="">{t('selectGroup')}</option>
                  {groups?.filter(group => !selectedGroups.includes(group.id)).map(group => (
                    <option key={group.id} value={group.id}>{group.name}</option>
                  ))}
                </select>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedGroups.map(groupId => {
                    const group = groups?.find(g => g.id === groupId)
                    return group ? (
                      <span key={groupId} className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                        {group.name}
                        <button
                          type="button"
                          onClick={() => setSelectedGroups(selectedGroups.filter(id => id !== groupId))}
                          className="hover:text-green-900 dark:hover:text-green-100"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ) : null
                  })}
                </div>
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
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('permissions')}</label>
                <select 
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => {
                    const permissionId = e.target.value
                    if (permissionId && !selectedPermissions.includes(permissionId)) {
                      setSelectedPermissions([...selectedPermissions, permissionId])
                    }
                    e.target.value = ''
                  }}
                >
                  <option value="">{t('selectPermission')}</option>
                  {permissions?.filter(permission => !selectedPermissions.includes(permission.id)).map(permission => (
                    <option key={permission.id} value={permission.id}>{permission.name}</option>
                  ))}
                </select>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedPermissions.map(permissionId => {
                    const permission = permissions?.find(p => p.id === permissionId)
                    return permission ? (
                      <span key={permissionId} className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 text-xs rounded-full">
                        {permission.name}
                        <button
                          type="button"
                          onClick={() => setSelectedPermissions(selectedPermissions.filter(id => id !== permissionId))}
                          className="hover:text-orange-900 dark:hover:text-orange-100"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ) : null
                  })}
                </div>
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
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('permissions')}</label>
                <select 
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => {
                    const permissionId = e.target.value
                    if (permissionId && !selectedPermissions.includes(permissionId)) {
                      setSelectedPermissions([...selectedPermissions, permissionId])
                    }
                    e.target.value = ''
                  }}
                >
                  <option value="">{t('selectPermission')}</option>
                  {permissions?.filter(permission => !selectedPermissions.includes(permission.id)).map(permission => (
                    <option key={permission.id} value={permission.id}>{permission.name}</option>
                  ))}
                </select>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedPermissions.map(permissionId => {
                    const permission = permissions?.find(p => p.id === permissionId)
                    return permission ? (
                      <span key={permissionId} className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 text-xs rounded-full">
                        {permission.name}
                        <button
                          type="button"
                          onClick={() => setSelectedPermissions(selectedPermissions.filter(id => id !== permissionId))}
                          className="hover:text-orange-900 dark:hover:text-orange-100"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ) : null
                  })}
                </div>
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
      
      {/* 编辑用户弹窗 */}
      {showEditUser && editingUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('editUser')}</h3>
              <button
                onClick={() => {
                  setShowEditUser(false)
                  setEditingUser(null)
                  setSelectedRoles([])
                  setSelectedGroups([])
                }}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleUpdateUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('username')}</label>
                <input
                  name="username"
                  defaultValue={editingUser.username}
                  readOnly
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-slate-100 dark:bg-slate-600 text-slate-900 dark:text-slate-100 cursor-not-allowed"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('email')}</label>
                <input
                  name="email"
                  type="email"
                  defaultValue={editingUser.email}
                  readOnly
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-slate-100 dark:bg-slate-600 text-slate-900 dark:text-slate-100 cursor-not-allowed"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('roles')}</label>
                <select 
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => {
                    const roleId = e.target.value
                    if (roleId && !selectedRoles.includes(roleId)) {
                      setSelectedRoles([...selectedRoles, roleId])
                    }
                    e.target.value = ''
                  }}
                >
                  <option value="">{t('selectRole')}</option>
                  {roles?.filter(role => !selectedRoles.includes(role.id)).map(role => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                  ))}
                </select>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedRoles.map(roleId => {
                    const role = roles?.find(r => r.id === roleId)
                    return role ? (
                      <span key={roleId} className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                        {role.name}
                        <button
                          type="button"
                          onClick={() => setSelectedRoles(selectedRoles.filter(id => id !== roleId))}
                          className="hover:text-blue-900 dark:hover:text-blue-100"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ) : null
                  })}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('groups')}</label>
                <select 
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => {
                    const groupId = e.target.value
                    if (groupId && !selectedGroups.includes(groupId)) {
                      setSelectedGroups([...selectedGroups, groupId])
                    }
                    e.target.value = ''
                  }}
                >
                  <option value="">{t('selectGroup')}</option>
                  {groups?.filter(group => !selectedGroups.includes(group.id)).map(group => (
                    <option key={group.id} value={group.id}>{group.name}</option>
                  ))}
                </select>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedGroups.map(groupId => {
                    const group = groups?.find(g => g.id === groupId)
                    return group ? (
                      <span key={groupId} className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                        {group.name}
                        <button
                          type="button"
                          onClick={() => setSelectedGroups(selectedGroups.filter(id => id !== groupId))}
                          className="hover:text-green-900 dark:hover:text-green-100"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ) : null
                  })}
                </div>
              </div>
              <div className="flex justify-end space-x-2 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditUser(false)
                    setEditingUser(null)
                    setSelectedRoles([])
                    setSelectedGroups([])
                  }}
                  className="px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
                >
                  {t('cancel')}
                </button>
                <button
                  type="submit"
                  disabled={updateAccountMutation.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {updateAccountMutation.isPending ? t('updating') : t('update')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}