<template>
  <section class="page-grid">
    <div class="toolbar">
      <div>
        <p class="eyebrow">Role Admin</p>
        <h3>Manage role permissions and assign roles to users.</h3>
        <p class="muted-copy">
          Current backend supports fixed roles only:
          <code>admin</code>
          and
          <code>member</code>.
        </p>
      </div>
      <div class="toolbar__badge">
        <span>Selected role</span>
        <strong>{{ selectedRole }}</strong>
      </div>
    </div>

    <p v-if="pageError" class="inline-banner inline-banner--warning">{{ pageError }}</p>
    <p v-if="pageSuccess" class="probe-result">{{ pageSuccess }}</p>
    <p v-if="permissionNotice" class="inline-banner inline-banner--warning">{{ permissionNotice }}</p>

    <div class="role-toggle" role="tablist" aria-label="Roles">
      <button
        v-for="role in roles"
        :key="role"
        :class="['role-toggle__button', role === selectedRole ? 'role-toggle__button--active' : '']"
        type="button"
        @click="switchRole(role)"
      >
        {{ role }}
      </button>
    </div>

    <div class="summary-grid">
      <article class="summary-card">
        <span class="summary-card__label">Role</span>
        <strong class="summary-card__value">{{ selectedRole }}</strong>
        <p class="summary-card__hint">The permission list below is loaded from the backend.</p>
      </article>
      <article class="summary-card">
        <span class="summary-card__label">Permissions</span>
        <strong class="summary-card__value">{{ rolePermissions.length }}</strong>
        <p class="summary-card__hint">Permissions granted to this role.</p>
      </article>
      <article class="summary-card">
        <span class="summary-card__label">Users</span>
        <strong class="summary-card__value">{{ usersWithSelectedRole.length }}</strong>
        <p class="summary-card__hint">Users currently assigned to this role.</p>
      </article>
    </div>

    <div class="management-grid">
      <article class="surface-card">
        <div class="surface-card__header">
          <div>
            <h4>Role permissions</h4>
            <p class="muted-copy">Add or remove permissions for the selected role.</p>
          </div>
          <span class="surface-card__meta">{{ rolePermissions.length }} entries</span>
        </div>

        <form class="inline-form" @submit.prevent="submitPermission">
          <label class="form-field">
            <span>Resource</span>
            <input v-model.trim="permissionForm.resource" placeholder="users" required />
          </label>
          <label class="form-field">
            <span>Action</span>
            <input v-model.trim="permissionForm.action" placeholder="read" required />
          </label>
          <button class="primary-button" :disabled="permissionLoading || !canManagePermissions" type="submit">
            {{ permissionLoading ? "Saving..." : "Add permission" }}
          </button>
        </form>

        <ul v-if="rolePermissions.length" class="permission-list permission-list--dense">
          <li v-for="item in rolePermissions" :key="`${selectedRole}-${item.resource}-${item.action}`">
            <div>
              <strong>{{ item.resource }}</strong>
              <p class="muted-copy">{{ item.action }}</p>
            </div>
            <button
              class="ghost-button"
              :disabled="permissionLoading || !canManagePermissions"
              type="button"
              @click="removePermission(item)"
            >
              Remove
            </button>
          </li>
        </ul>
        <p v-else class="empty-state">No permissions are currently assigned to this role.</p>
      </article>

      <article class="surface-card surface-card--accent">
        <div class="surface-card__header">
          <div>
            <h4>User role assignment</h4>
            <p class="muted-copy">User permissions are inherited from the assigned role.</p>
          </div>
          <span class="surface-card__meta">{{ users.length }} users loaded</span>
        </div>

        <form class="inline-form inline-form--stacked" @submit.prevent="submitUserRole">
          <label class="form-field">
            <span>User</span>
            <select v-model="userRoleForm.userId" :disabled="userLoading || !users.length">
              <option disabled value="">Select a user</option>
              <option v-for="user in users" :key="user.id" :value="String(user.id)">
                {{ user.email }} ({{ user.role }})
              </option>
            </select>
          </label>
          <label class="form-field">
            <span>Role</span>
            <select v-model="userRoleForm.role">
              <option v-for="role in roles" :key="role" :value="role">{{ role }}</option>
            </select>
          </label>
          <button class="primary-button" :disabled="userLoading || !canAssignRoles" type="submit">
            {{ userLoading ? "Saving..." : "Assign role" }}
          </button>
        </form>

        <div class="table-shell">
          <table class="data-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Current role</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>
                  <strong>{{ user.email }}</strong>
                </td>
                <td>
                  <span class="role-pill">{{ user.role }}</span>
                </td>
                <td class="data-actions">
                  <button
                    v-for="role in roles"
                    :key="`${user.id}-${role}`"
                    class="ghost-button ghost-button--small"
                    :disabled="userLoading || !canAssignRoles || user.role === role"
                    type="button"
                    @click="assignRole(user.id, role)"
                  >
                    Set {{ role }}
                  </button>
                  <button
                    v-if="user.role === 'admin'"
                    class="ghost-button ghost-button--small"
                    :disabled="userLoading || !canAssignRoles"
                    type="button"
                    @click="removeRole(user.id, user.role)"
                  >
                    Remove admin
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p v-if="!users.length" class="empty-state">No users were returned from the backend.</p>
      </article>
    </div>
  </section>
</template>

<script>
import {
  AVAILABLE_ROLES,
  assignRoleToUser,
  fetchMyPermissions,
  fetchRolePermissions,
  fetchUsers,
  grantPermissionToRole,
  removeUserRole,
  revokePermissionFromRole
} from "@/utils/api";

function readApiMessage(error, fallback) {
  return (
    (error &&
      error.response &&
      error.response.data &&
      error.response.data.message) ||
    fallback
  );
}

export default {
  name: "RoleAdminView",
  data() {
    return {
      roles: AVAILABLE_ROLES,
      selectedRole: AVAILABLE_ROLES[0],
      rolePermissions: [],
      users: [],
      currentPermissions: [],
      pageError: "",
      pageSuccess: "",
      permissionNotice: "",
      permissionLoading: false,
      userLoading: false,
      permissionForm: {
        resource: "",
        action: ""
      },
      userRoleForm: {
        userId: "",
        role: AVAILABLE_ROLES[0]
      }
    };
  },
  computed: {
    canManagePermissions() {
      return this.hasPermission("rbac", "grant_permission");
    },
    canAssignRoles() {
      return this.hasPermission("rbac", "assign_role");
    },
    usersWithSelectedRole() {
      return this.users.filter((user) => user.role === this.selectedRole);
    }
  },
  created() {
    this.bootstrap();
  },
  methods: {
    async bootstrap() {
      await Promise.all([this.loadCurrentPermissions(), this.loadUsers()]);
      await this.loadRolePermissions();
    },
    async loadCurrentPermissions() {
      try {
        const payload = await fetchMyPermissions();
        this.currentPermissions = payload.permissions || [];

        if (!this.canManagePermissions || !this.canAssignRoles) {
          this.permissionNotice =
            "Current account can view this page, but some admin actions may be blocked by backend permissions.";
        }
      } catch (error) {
        this.permissionNotice =
          "Unable to verify current RBAC capabilities. Some actions may fail until the session is refreshed.";
      }
    },
    async loadUsers() {
      try {
        const payload = await fetchUsers({ skip: 0, limit: 100 });
        this.users = payload.items || [];

        if (!this.userRoleForm.userId && this.users.length) {
          this.userRoleForm.userId = String(this.users[0].id);
        }
      } catch (error) {
        this.pageError = readApiMessage(
          error,
          "Unable to load users. Make sure the account can read the user directory."
        );
      }
    },
    async loadRolePermissions() {
      try {
        const payload = await fetchRolePermissions(this.selectedRole);
        this.rolePermissions = payload.permissions || [];
      } catch (error) {
        this.pageError = readApiMessage(
          error,
          "Unable to load the selected role permissions."
        );
      }
    },
    hasPermission(resource, action) {
      return this.currentPermissions.some((item) => {
        return item.resource === resource && item.action === action;
      });
    },
    resetMessages() {
      this.pageError = "";
      this.pageSuccess = "";
    },
    async switchRole(role) {
      this.selectedRole = role;
      this.userRoleForm.role = role;
      this.resetMessages();
      await this.loadRolePermissions();
    },
    async submitPermission() {
      this.permissionLoading = true;
      this.resetMessages();

      try {
        const payload = await grantPermissionToRole(this.selectedRole, this.permissionForm);
        this.rolePermissions = payload.permissions || [];
        this.pageSuccess = `Permission added to ${this.selectedRole}.`;
        this.permissionForm.resource = "";
        this.permissionForm.action = "";
      } catch (error) {
        this.pageError = readApiMessage(
          error,
          "Unable to add permission to the selected role."
        );
      } finally {
        this.permissionLoading = false;
      }
    },
    async removePermission(item) {
      this.permissionLoading = true;
      this.resetMessages();

      try {
        const payload = await revokePermissionFromRole(this.selectedRole, item);
        this.rolePermissions = payload.permissions || [];
        this.pageSuccess = `Permission removed from ${this.selectedRole}.`;
      } catch (error) {
        this.pageError = readApiMessage(
          error,
          "Unable to remove permission from the selected role."
        );
      } finally {
        this.permissionLoading = false;
      }
    },
    async submitUserRole() {
      if (!this.userRoleForm.userId) {
        return;
      }

      await this.assignRole(Number(this.userRoleForm.userId), this.userRoleForm.role);
    },
    async assignRole(userId, role) {
      this.userLoading = true;
      this.resetMessages();

      try {
        await assignRoleToUser(userId, role);
        await this.loadUsers();
        this.pageSuccess = `Role ${role} assigned successfully.`;
      } catch (error) {
        this.pageError = readApiMessage(
          error,
          "Unable to assign role to the selected user."
        );
      } finally {
        this.userLoading = false;
      }
    },
    async removeRole(userId, role) {
      this.userLoading = true;
      this.resetMessages();

      try {
        await removeUserRole(userId, role);
        await this.loadUsers();
        this.pageSuccess = `Role ${role} removed successfully.`;
      } catch (error) {
        this.pageError = readApiMessage(
          error,
          "Unable to remove role from the selected user."
        );
      } finally {
        this.userLoading = false;
      }
    }
  }
};
</script>
