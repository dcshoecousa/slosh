<template>
  <aside class="sidebar">
    <div class="brand-panel">
      <p class="eyebrow">Slosh Console</p>
      <h1>Operations cockpit for auth, users, and access control.</h1>
    </div>
    <nav class="nav-links">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        class="nav-card"
        :to="{ name: item.name }"
      >
        <span class="nav-card__label">{{ item.label }}</span>
        <span class="nav-card__description">{{ item.description }}</span>
      </router-link>
    </nav>
    <div class="sidebar-note">
      <p>Designed for quick scanning, API-first workflows, and role-aware operations.</p>
    </div>
  </aside>
</template>

<script>
export default {
  name: "AppSidebar",
  props: {
    navItems: {
      type: Array,
      default: () => []
    }
  }
};
</script>
