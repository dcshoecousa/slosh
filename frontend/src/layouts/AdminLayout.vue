<template>
  <div :class="['admin-shell', sidebarCollapsed ? 'admin-shell--collapsed' : '']">
    <AppSidebar
      :collapsed="sidebarCollapsed"
      :nav-sections="navSections"
      @toggle="toggleSidebar"
    />
    <div class="admin-shell__header">
      <AppHeader
        :is-dark="isDarkTheme"
        :user="currentUser"
        :page-title="pageTitle"
        @logout="handleLogout"
        @toggle-theme="handleThemeToggle"
      />
    </div>
    <div class="admin-stage">
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import AppHeader from "@/components/AppHeader.vue";
import AppSidebar from "@/components/AppSidebar.vue";
import { fetchCurrentUser, fetchMySettings, logout, updateMySettings } from "@/utils/api";
import { getActiveTheme, setThemeCache, toggleTheme } from "@/utils/theme";

const SIDEBAR_STATE_KEY = "slosh-sidebar-collapsed";

export default {
  name: "AdminLayout",
  components: {
    AppHeader,
    AppSidebar
  },
  data() {
    return {
      currentUser: null,
      isDarkTheme: false,
      sidebarCollapsed: false,
      navSections: [
        {
          label: "Workspace",
          items: [{ name: "dashboard", label: "Overview", description: "System summary" }]
        },
        {
          label: "Administration",
          items: [
            { name: "users", label: "Users", description: "Directory and status" },
            { name: "permissions", label: "Permissions", description: "Roles and access" },
            { name: "role-admin", label: "Role Admin", description: "Assign roles and permissions" }
          ]
        }
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
    this.loadCachedSidebarState();
    this.loadThemeState();
    this.bootstrapHeaderState();
  },
  watch: {
    $route() {
      this.loadCurrentUser();
    }
  },
  methods: {
    async bootstrapHeaderState() {
      await Promise.all([this.loadCurrentUser(), this.loadUserSettings()]);
    },
    async loadCurrentUser() {
      try {
        this.currentUser = await fetchCurrentUser();
      } catch (error) {
        this.currentUser = null;
      }
    },
    loadCachedSidebarState() {
      try {
        this.sidebarCollapsed = window.localStorage.getItem(SIDEBAR_STATE_KEY) === "true";
      } catch (error) {
        this.sidebarCollapsed = false;
      }
    },
    async loadUserSettings() {
      try {
        const settings = await fetchMySettings();
        this.isDarkTheme = setThemeCache(settings.theme) === "dark";
        this.sidebarCollapsed = Boolean(settings.sidebar_collapsed);
        this.persistSidebarState(this.sidebarCollapsed);
      } catch (error) {
        this.loadCachedSidebarState();
        this.loadThemeState();
      }
    },
    loadThemeState() {
      this.isDarkTheme = getActiveTheme() === "dark";
    },
    persistSidebarState(value) {
      try {
        window.localStorage.setItem(SIDEBAR_STATE_KEY, String(value));
      } catch (error) {
        // Ignore storage failures and keep the in-memory state only.
      }
    },
    async handleThemeToggle() {
      this.isDarkTheme = toggleTheme() === "dark";

      try {
        await updateMySettings({
          theme: this.isDarkTheme ? "dark" : "light"
        });
      } catch (error) {
        // Keep the local UI state even if the preference sync fails.
      }
    },
    async toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
      this.persistSidebarState(this.sidebarCollapsed);

      try {
        await updateMySettings({
          sidebar_collapsed: this.sidebarCollapsed
        });
      } catch (error) {
        // Keep the local UI state even if the preference sync fails.
      }
    },
    handleLogout() {
      logout();
      this.$router.replace({ name: "login" });
    }
  }
};
</script>
