import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { getResources, createResource, Resource } from "../api"
import { Archive, Plus, X } from "lucide-react"
import { useTranslation } from "../contexts/TranslationContext"

const TENANT_ID = "default_tenant"

export default function Resources() {
  const { t } = useTranslation()
  const [showCreateResource, setShowCreateResource] = useState(false)
  const queryClient = useQueryClient()

  const { data: resources } = useQuery({
    queryKey: ["resources", TENANT_ID],
    queryFn: () => getResources(TENANT_ID),
  })

  const createResourceMutation = useMutation({
    mutationFn: ({ resourceType, name }: { resourceType: string; name: string }) => 
      createResource(resourceType, name, TENANT_ID),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resources", TENANT_ID] })
      setShowCreateResource(false)
    },
  })

  const handleCreateResource = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    const resourceType = formData.get("resourceType") as string
    const name = formData.get("name") as string
    createResourceMutation.mutate({ resourceType, name })
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
                  <Archive className="w-5 h-5" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('resourceManagementTitle')}</h2>
                </div>
                <button
                  onClick={() => setShowCreateResource(true)}
                  className="flex items-center space-x-2 px-5 py-2.5 bg-slate-900 dark:bg-slate-700 text-white rounded-lg hover:bg-slate-800 dark:hover:bg-slate-600 transition-colors font-medium shadow-sm"
                >
                  <Plus className="w-4 h-4" />
                  <span>{t('createResource')}</span>
                </button>
              </div>
            </div>
            <div className="border-t border-slate-200 dark:border-slate-700">
              <div className="overflow-x-auto max-h-96 overflow-y-auto">
                <table className="w-full">
                  <thead className="sticky top-0 bg-white dark:bg-slate-800 z-10">
                    <tr className="border-b border-slate-200 dark:border-slate-700">
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('resourceName')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('resourceType')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('owner')}</th>
                      <th className="text-left py-3 px-6 font-medium text-slate-700 dark:text-slate-300">{t('actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {resources?.map((resource) => (
                      <tr key={resource.id} className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-750">
                        <td className="py-3 px-6 font-medium text-slate-900 dark:text-slate-100">{resource.name}</td>
                        <td className="py-3 px-6 text-slate-600 dark:text-slate-400">
                          <span className="px-2 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 text-xs rounded-full">
                            {resource.type}
                          </span>
                        </td>
                        <td className="py-3 px-6 text-slate-600 dark:text-slate-400">{resource.owner_id || '-'}</td>
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

      {/* 创建资源弹窗 */}
      {showCreateResource && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('createNewResource')}</h3>
              <button
                onClick={() => setShowCreateResource(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateResource} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('resourceName')}</label>
                <input
                  name="name"
                  required
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{t('resourceType')}</label>
                <select
                  name="resourceType"
                  required
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">{t('selectResourceType')}</option>
                  <option value="file">{t('file')}</option>
                  <option value="database">{t('database')}</option>
                  <option value="api">API</option>
                  <option value="service">{t('service')}</option>
                </select>
              </div>
              <div className="flex justify-end space-x-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateResource(false)}
                  className="px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
                >
                  {t('cancel')}
                </button>
                <button
                  type="submit"
                  disabled={createResourceMutation.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {createResourceMutation.isPending ? t('creating') : t('create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}