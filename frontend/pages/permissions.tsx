import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { getPermissions, createPermission, Permission } from "../api"
import { Shield, Plus, X } from "lucide-react"
import { useTranslation } from "../contexts/TranslationContext"

const TENANT_ID = "default_tenant"

export default function Permissions() {
  const { t } = useTranslation()
  const [showCreatePermission, setShowCreatePermission] = useState(false)
  const queryClient = useQueryClient()

  const { data: permissions } = useQuery({
    queryKey: ["permissions", TENANT_ID],
    queryFn: () => getPermissions(TENANT_ID),
  })

  const createPermissionMutation = useMutation({
    mutationFn: ({ name, description }: { name: string; description: string }) => 
      createPermission(name, description),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["permissions", TENANT_ID] })
      setShowCreatePermission(false)
    },
  })

  const handleCreatePermission = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    const name = formData.get("name") as string
    const description = formData.get("description") as string
    createPermissionMutation.mutate({ name, description })
  }

  return (
    <div className="flex min-h-screen -my-8 -mx-6">
      {/* 主内容区域 */}
      <div className="flex-1 bg-slate-50 dark:bg-slate-900 flex flex-col">
        <div className="p-6 flex-1">
          <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
            <div className="p-6 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Shield className="w-5 h-5" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('permissionManagementTitle')}</h2>
                </div>
                <button
                  onClick={() => setShowCreatePermission(true)}
                  className="flex items-center space-x-2 px-5 py-2.5 bg-slate-900 dark:bg-slate-700 text-white rounded-lg hover:bg-slate-800 dark:hover:bg-slate-600 transition-colors font-medium shadow-sm"
                >
                  <Plus className="w-4 h-4" />
                  <span>{t('createPermission')}</span>
                </button>
              </div>
            </div>
            <div className="border-t border-slate-200 dark:border-slate-700">
              <div className="overflow-x-auto max-h-96 overflow-y-auto">
                <table className="w-full">
                  <thead className="sticky top-0 bg-white dark:bg-slate-800 z-10">
                    <tr className="border-b border-slate-200 dark:border-slate-700">
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('permissionName')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('description')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {permissions?.map((permission) => (
                      <tr key={permission.id} className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-750">
                        <td className="py-3 px-6 font-medium text-slate-900 dark:text-slate-100">{permission.name}</td>
                        <td className="py-3 px-6 text-slate-600 dark:text-slate-400">{permission.description}</td>
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
        </div>
      </div>

      {/* 创建权限弹窗 */}
      {showCreatePermission && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('createNewPermission')}</h3>
              <button
                onClick={() => setShowCreatePermission(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreatePermission} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('permissionName')}</label>
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
                  onClick={() => setShowCreatePermission(false)}
                  className="px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
                >
                  {t('cancel')}
                </button>
                <button
                  type="submit"
                  disabled={createPermissionMutation.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {createPermissionMutation.isPending ? t('creating') : t('create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}