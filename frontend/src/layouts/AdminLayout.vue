<template>
  <div class="admin-shell">
    <AppSidebar :nav-items="navItems" />
    <div class="admin-stage">
      <AppHeader :user="currentUser" :page-title="pageTitle" @logout="handleLogout" />
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import AppHeader from "@/components/AppHeader.vue";
import AppSidebar from "@/components/AppSidebar.vue";
import { fetchCurrentUser, logout } from "@/utils/api";

export default {
  name: "AdminLayout",
  components: {
    AppHeader,
    AppSidebar
  },
  data() {
    return {
      currentUser: null,
      navItems: [
        { name: "dashboard", label: "Overview", description: "Pulse and activity" },
        { name: "users", label: "Users", description: "Operators and accounts" },
        { name: "permissions", label: "Permissions", description: "RBAC insights" }
      ]
    };
  },
  computed: {
    pageTitle() {
      return this.$route.meta && this.$route.meta.title
        ? this.$route.meta.title
        : "Workspace";
    }
  },
  created() {
    this.loadCurrentUser();
  },
  watch: {
    $route() {
      this.loadCurrentUser();
    }
  },
  methods: {
    async loadCurrentUser() {
      try {
        this.currentUser = await fetchCurrentUser();
      } catch (error) {
        this.currentUser = null;
      }
    },
    handleLogout() {
      logout();
      this.$router.replace({ name: "login" });
    }
  }
};
</script>
