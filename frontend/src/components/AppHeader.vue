<template>
  <header class="page-header">
    <div class="page-header__content">
      <p class="page-header__eyebrow">Slosh Admin</p>
      <h2>{{ pageTitle }}</h2>
      <p class="page-header__summary">Manage the backend with a cleaner, quieter interface.</p>
    </div>
    <div class="page-header__actions">
      <div class="user-panel">
        <div class="user-panel__avatar" aria-hidden="true">{{ userInitials }}</div>
        <div class="user-panel__content">
          <div class="user-panel__identity">
            <span class="user-panel__eyebrow">Signed in as</span>
            <strong class="user-panel__name">{{ displayName }}</strong>
            <span class="user-panel__email">{{ user ? user.email : "Not connected" }}</span>
          </div>
          <div class="user-panel__meta">
            <span v-if="user && user.role" class="user-panel__pill">{{ user.role }}</span>
            <span
              v-if="user"
              :class="['user-panel__pill', user.is_active ? 'user-panel__pill--active' : 'user-panel__pill--inactive']"
            >
              {{ user.is_active ? "Active" : "Inactive" }}
            </span>
          </div>
        </div>
        <div class="user-panel__actions">
          <button
            class="theme-switch"
            :aria-checked="String(isDark)"
            :aria-label="themeLabel"
            :title="themeLabel"
            role="switch"
            type="button"
            @click="$emit('toggle-theme')"
          >
            <span class="theme-switch__copy">
              <span class="theme-switch__title">Theme</span>
              <span class="theme-switch__state">{{ themeStateLabel }}</span>
            </span>
            <span :class="['theme-switch__track', isDark ? 'theme-switch__track--active' : '']" aria-hidden="true">
              <span class="theme-switch__thumb"></span>
            </span>
          </button>
          <button class="ghost-button ghost-button--small user-panel__logout" type="button" @click="$emit('logout')">
            Sign out
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: "AppHeader",
  props: {
    isDark: {
      type: Boolean,
      default: false
    },
    pageTitle: {
      type: String,
      default: "Workspace"
    },
    user: {
      type: Object,
      default: null
    }
  },
  computed: {
    displayName() {
      if (!this.user) {
        return "No active session";
      }

      return this.user.full_name || this.user.email;
    },
    userInitials() {
      if (!this.user) {
        return "--";
      }

      const source = this.user.full_name || this.user.email || "";
      const segments = source
        .replace(/[@._-]+/g, " ")
        .split(" ")
        .filter(Boolean)
        .slice(0, 2);

      if (!segments.length) {
        return "--";
      }

      return segments
        .map((segment) => segment.charAt(0).toUpperCase())
        .join("");
    },
    themeStateLabel() {
      return this.isDark ? "Dark" : "Light";
    },
    themeLabel() {
      return this.isDark ? "Switch to light mode" : "Switch to dark mode";
    }
  }
};
</script>
