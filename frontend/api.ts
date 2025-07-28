import axios from "axios"

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://199.199.199.8:8000",
  headers: {
    "Content-Type": "application/json",
  },
})

export interface Permission {
  id: string
  name: string
  description: string
}

export interface Role {
  id: string
  tenant_id: string
  name: string
  description?: string
  permissions: string[]
}

export interface Account {
  id: string
  username: string
  email: string
  tenant_id: string
  roles: string[]
  groups: string[]
}

export interface Group {
  id: string
  name: string
  tenant_id: string
  roles: string[]
}

export interface Resource {
  id: string
  name: string
  type: string
  tenant_id: string
  owner_id?: string
}

export interface AccessCheckRequest {
  account_id: string
  resource: string
  action: string
  tenant_id?: string
}

export interface AccessCheckResponse {
  allowed: boolean
  reason?: string
}

// Permission APIs
export const getPermissions = async (tenantId?: string): Promise<Permission[]> => {
  const params = tenantId ? { tenant_id: tenantId } : {}
  const response = await apiClient.get("/permissions", { params })
  return response.data
}

export const createPermission = async (name: string, description?: string): Promise<Permission> => {
  const response = await apiClient.post("/permissions", null, {
    params: { name, description: description || "" }
  })
  return response.data
}

// Role APIs
export const getRoles = async (tenantId?: string): Promise<Role[]> => {
  const params = tenantId ? { tenant_id: tenantId } : {}
  const response = await apiClient.get("/roles", { params })
  return response.data
}

export const createRole = async (name: string, tenantId?: string, description?: string): Promise<Role> => {
  const response = await apiClient.post("/roles", null, {
    params: { name, tenant_id: tenantId, description: description || "" }
  })
  return response.data
}

// Account APIs
export const getAccounts = async (tenantId?: string): Promise<Account[]> => {
  const params = tenantId ? { tenant_id: tenantId } : {}
  const response = await apiClient.get("/accounts", { params })
  return response.data
}

export const createAccount = async (username: string, email: string, tenantId?: string): Promise<Account> => {
  const response = await apiClient.post("/accounts", null, {
    params: { username, email, tenant_id: tenantId }
  })
  return response.data
}

// Group APIs
export const getGroups = async (tenantId?: string): Promise<Group[]> => {
  const params = tenantId ? { tenant_id: tenantId } : {}
  const response = await apiClient.get("/groups", { params })
  return response.data
}

export const createGroup = async (name: string, tenantId?: string, description?: string): Promise<Group> => {
  const response = await apiClient.post("/groups", null, {
    params: { name, tenant_id: tenantId, description: description || "" }
  })
  return response.data
}

// Resource APIs
export const getResources = async (tenantId?: string): Promise<Resource[]> => {
  const params = tenantId ? { tenant_id: tenantId } : {}
  const response = await apiClient.get("/resources", { params })
  return response.data
}

export const createResource = async (
  resourceType: string, 
  name: string, 
  tenantId?: string, 
  ownerId?: string
): Promise<Resource> => {
  const response = await apiClient.post("/resources", null, {
    params: { resource_type: resourceType, name, tenant_id: tenantId, owner_id: ownerId }
  })
  return response.data
}

// Assignment APIs
export const assignPermissionToRole = async (roleId: string, permissionId: string): Promise<void> => {
  await apiClient.post(`/roles/${roleId}/permissions/${permissionId}`)
}

export const assignRoleToAccount = async (accountId: string, roleId: string): Promise<void> => {
  await apiClient.post(`/accounts/${accountId}/roles/${roleId}`)
}

export const assignRoleToGroup = async (groupId: string, roleId: string): Promise<void> => {
  await apiClient.post(`/groups/${groupId}/roles/${roleId}`)
}

export const assignGroupToAccount = async (accountId: string, groupId: string): Promise<void> => {
  await apiClient.post(`/accounts/${accountId}/groups/${groupId}`)
}

// Access Check API
export const checkAccess = async (request: AccessCheckRequest): Promise<AccessCheckResponse> => {
  const response = await apiClient.post("/access/check", request)
  return response.data
}