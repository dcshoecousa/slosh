<template>
  <section class="page-grid">
    <div class="toolbar">
      <div>
        <p class="eyebrow">Directory</p>
        <h3>Inspect the operator roster with a fast, searchable table.</h3>
      </div>
      <label class="search-input">
        <span>Search</span>
        <input v-model.trim="searchQuery" type="search" placeholder="Filter by email or role" />
      </label>
    </div>

    <p v-if="errorMessage" class="inline-banner inline-banner--warning">{{ errorMessage }}</p>

    <article class="surface-card">
      <div class="surface-card__header">
        <h4>User directory</h4>
        <span class="surface-card__meta">{{ filteredUsers.length }} shown</span>
      </div>
      <div class="table-shell">
        <table class="data-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td>
                <strong>{{ user.email }}</strong>
              </td>
              <td>
                <span class="role-pill">{{ user.role }}</span>
              </td>
              <td>
                <span :class="['status-pill', user.is_active ? 'status-pill--active' : 'status-pill--inactive']">
                  {{ user.is_active ? "Active" : "Inactive" }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>
  </section>
</template>

<script>
import { fetchUsers } from "@/utils/api";

export default {
  name: "UsersView",
  data() {
    return {
      errorMessage: "",
      searchQuery: "",
      users: []
    };
  },
  computed: {
    filteredUsers() {
      const keyword = this.searchQuery.toLowerCase();

      if (!keyword) {
        return this.users;
      }

      return this.users.filter((user) => {
        return [user.email, user.role, user.full_name || ""]
          .join(" ")
          .toLowerCase()
          .includes(keyword);
      });
    }
  },
  created() {
    this.loadUsers();
  },
  methods: {
    async loadUsers() {
      try {
        const payload = await fetchUsers({ skip: 0, limit: 50 });
        this.users = payload.items || [];
      } catch (error) {
        this.errorMessage =
          "Unable to load /users right now. Make sure the backend is running and the current account has users:read permission.";
      }
    },
    formatDate(value) {
      if (!value) {
        return "--";
      }

      return new Date(value).toLocaleString();
    }
  }
};
</script>
