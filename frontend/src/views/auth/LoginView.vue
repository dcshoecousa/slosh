<template>
  <section class="auth-shell">
    <div class="auth-card">
      <div class="auth-copy">
        <p class="eyebrow">Vue 2 Admin</p>
        <h1>Sign in to orchestrate users and access with the Slosh backend.</h1>
        <p>
          This frontend talks to
          <code>{{ apiBaseUrl }}</code>
          and is already wired for the current FastAPI auth and RBAC endpoints.
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
          {{ loading ? "Signing in..." : "Enter workspace" }}
        </button>

        <div class="auth-helper">
          <span>Tip</span>
          <p>The first registered backend user becomes admin by default.</p>
        </div>
      </form>
    </div>
  </section>
</template>

<script>
import { apiBaseUrl, login } from "@/utils/api";

export default {
  name: "LoginView",
  data() {
    return {
      apiBaseUrl,
      errorMessage: "",
      loading: false,
      form: {
        email: "",
        password: ""
      }
    };
  },
  methods: {
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
          "Unable to sign in. Confirm the backend is running and the credentials are valid.";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
