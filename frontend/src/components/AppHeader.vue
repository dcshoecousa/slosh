<template>
  <header class="page-header">
    <div>
      <p class="page-header__eyebrow">Admin workspace</p>
      <h2>{{ pageTitle }}</h2>
    </div>
    <div class="page-header__actions">
      <div class="identity-card">
        <span class="identity-card__label">Signed in</span>
        <strong>{{ user ? user.email : "Not connected" }}</strong>
      </div>
      <button class="ghost-button" type="button" @click="$emit('logout')">
        Sign out
      </button>
    </div>
  </header>
</template>

<script>
export default {
  name: "AppHeader",
  props: {
    pageTitle: {
      type: String,
      default: "Workspace"
    },
    user: {
      type: Object,
      default: null
    }
  }
};
</script>
