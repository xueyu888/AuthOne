"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { createRole, getRoles, RolePydantic } from "@/lib/api"
import { PlusCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

// A mock tenant ID. In a real app, this would come from user session or context.
const TENANT_ID = "default_tenant"

export default function RolesPage() {
  const queryClient = useQueryClient()
  const [isCreateDialogOpen, setCreateDialogOpen] = useState(false)

  const { data: roles, isLoading, error } = useQuery({
    queryKey: ["roles", TENANT_ID],
    queryFn: () => getRoles(TENANT_ID),
  })

  const createRoleMutation = useMutation({
    mutationFn: createRole,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles", TENANT_ID] })
      setCreateDialogOpen(false)
    },
    // TODO: Add onError handling to show a toast/notification
  })

  const handleCreateRole = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    const name = formData.get("name") as string
    const description = formData.get("description") as string
    createRoleMutation.mutate({ name, description, tenant_id: TENANT_ID })
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Roles</CardTitle>
            <CardDescription>Manage roles and their permissions.</CardDescription>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="gap-1">
                <PlusCircle className="h-3.5 w-3.5" />
                <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">Create Role</span>
              </Button>
            </DialogTrigger>
            <DialogContent>
              <form onSubmit={handleCreateRole}>
                <DialogHeader>
                  <DialogTitle>Create a new role</DialogTitle>
                  <DialogDescription>
                    Fill in the details below to create a new role.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="name" className="text-right">Name</Label>
                    <Input id="name" name="name" className="col-span-3" required />
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="description" className="text-right">Description</Label>
                    <Input id="description" name="description" className="col-span-3" />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit" disabled={createRoleMutation.isPending}>
                    {createRoleMutation.isPending ? "Creating..." : "Create Role"}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Permissions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && <TableRow><TableCell colSpan={3}>Loading roles...</TableCell></TableRow>}
            {error && <TableRow><TableCell colSpan={3} className="text-destructive">Failed to load roles.</TableCell></TableRow>}
            {roles?.map((role) => (
              <TableRow key={role.id}>
                <TableCell className="font-medium">{role.name}</TableCell>
                <TableCell>{role.description}</TableCell>
                <TableCell>{role.permission_ids.length} assigned</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}