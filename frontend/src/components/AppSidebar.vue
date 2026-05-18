<template>
  <aside :class="['sidebar', collapsed ? 'sidebar--collapsed' : '']">
    <div class="brand-panel">
      <div class="sidebar__header">
        <div class="sidebar__brand">
          <p class="eyebrow">Slosh</p>
          <h1>{{ collapsed ? "Admin" : "Admin Console" }}</h1>
        </div>
      </div>
      <p v-if="!collapsed" class="brand-panel__description">
        A simple workspace for users, sessions, and permissions.
      </p>
    </div>
    <nav class="nav-sections">
      <section
        v-for="section in navSections"
        :key="section.label"
        class="nav-section"
      >
        <p v-if="!collapsed" class="nav-section__label">{{ section.label }}</p>
        <div class="nav-section__items">
          <router-link
            v-for="item in section.items"
            :key="item.name"
            class="subnav-link"
            :to="{ name: item.name }"
          >
            <span class="subnav-link__label">{{ item.label }}</span>
            <span v-if="!collapsed" class="subnav-link__description">{{ item.description }}</span>
          </router-link>
        </div>
      </section>
    </nav>
    <div v-if="!collapsed" class="sidebar-note">
      <p>Keep the workflow light, readable, and focused on the data.</p>
    </div>
    <div class="sidebar__footer">
      <button
        :class="['sidebar__toggle', collapsed ? 'sidebar__toggle--collapsed' : '']"
        :aria-label="collapsed ? 'Expand navigation' : 'Collapse navigation'"
        :title="collapsed ? 'Expand navigation' : 'Collapse navigation'"
        type="button"
        @click="$emit('toggle')"
      >
        <span class="sidebar__toggle-label">{{ collapsed ? "Expand" : "Collapse" }}</span>
        <span class="sidebar__toggle-icon" aria-hidden="true">{{ collapsed ? "→" : "←" }}</span>
      </button>
    </div>
  </aside>
</template>

<script>
export default {
  name: "AppSidebar",
  props: {
    collapsed: {
      type: Boolean,
      default: false
    },
    navSections: {
      type: Array,
      default: () => []
    }
  },
  emits: ["toggle"]
};
</script>
