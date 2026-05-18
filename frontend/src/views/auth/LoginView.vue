<template>
  <section class="auth-shell">
    <div class="auth-shell__toolbar">
      <button
        :class="['theme-toggle-button', 'theme-toggle-button--icon', isDarkTheme ? 'theme-toggle-button--sun' : 'theme-toggle-button--moon']"
        :aria-label="isDarkTheme ? 'Switch to light mode' : 'Switch to dark mode'"
        :title="isDarkTheme ? 'Switch to light mode' : 'Switch to dark mode'"
        type="button"
        @click="handleThemeToggle"
      >
        <span aria-hidden="true">{{ isDarkTheme ? "☀" : "☾" }}</span>
      </button>
    </div>
    <div class="auth-card">
      <div class="auth-copy">
        <p class="eyebrow">Slosh Admin</p>
        <h1>Sign in to manage users and permissions.</h1>
        <p>
          This frontend connects to
          <code>{{ apiBaseUrl }}</code>
          and is already wired to the current auth and RBAC endpoints.
        </p>
      </div>

      <form class="auth-form" @submit.prevent="submitLogin">
        <label>
          <span>Email</span>
          <input v-model.trim="form.email" type="email" placeholder="admin@example.com" required />
        </label>
        <label>
          <span>Password</span>
          <input
            v-model="form.password"
            type="password"
            placeholder="password123"
            required
          />
        </label>

        <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>

        <button class="primary-button" :disabled="loading" type="submit">
          {{ loading ? "Signing in..." : "Sign in" }}
        </button>

        <div class="auth-helper">
          <span>Note</span>
          <p>Use an existing backend account. The first registered user is admin by default.</p>
        </div>
      </form>
    </div>
  </section>
</template>

<script>
import { apiBaseUrl, login } from "@/utils/api";
import { getActiveTheme, toggleTheme } from "@/utils/theme";

export default {
  name: "LoginView",
  data() {
    return {
      apiBaseUrl,
      errorMessage: "",
      isDarkTheme: false,
      loading: false,
      form: {
        email: "",
        password: ""
      }
    };
  },
  created() {
    this.isDarkTheme = getActiveTheme() === "dark";
  },
  methods: {
    handleThemeToggle() {
      this.isDarkTheme = toggleTheme() === "dark";
    },
    async submitLogin() {
      this.loading = true;
      this.errorMessage = "";

      try {
        await login(this.form.email, this.form.password);
        this.$router.replace(this.$route.query.redirect || "/dashboard");
      } catch (error) {
        const backendMessage =
          error &&
          error.response &&
          error.response.data &&
          error.response.data.message;

        this.errorMessage =
          backendMessage ||
          "Unable to sign in. Confirm the backend is running and the credentials are correct.";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
