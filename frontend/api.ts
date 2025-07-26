import axios from "axios"

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
})

// Based on backend/models.py and backend/schemas.py

export interface Permission {
  id: string
  name: string
  description: string
}

export interface Role {
  id: string
  tenant_id: string
  name: string
  description: string
  permissions: string[] // Array of permission IDs
}

export interface RolePydantic {
  id: string
  tenant_id: string
  name: string
  description: string
  permission_ids: string[]
}

export interface RoleCreate {
  name: string
  description?: string
  tenant_id: string
}

export interface Account {
  // Define Account interface based on your backend model
}

export interface Group {
  // Define Group interface based on your backend model
}

// --- API Functions ---

// Role APIs
export const getRoles = async (tenantId: string): Promise<RolePydantic[]> => {
  const response = await apiClient.get(`/tenants/${tenantId}/roles`)
  return response.data
}

export const createRole = async (roleData: RoleCreate): Promise<RolePydantic> => {
  const response = await apiClient.post(`/tenants/${roleData.tenant_id}/roles`, roleData)
  return response.data
}

// TODO: Add other API functions
// - getRole(id)
// - updateRole(id, data)
// - deleteRole(id)
// - assignPermissionToRole(roleId, permissionId)
// - and similar functions for Accounts, Groups, Permissions etc.