<template>
  <section class="page-grid">
    <div class="toolbar">
      <div>
        <p class="eyebrow">RBAC explorer</p>
        <h3>Review effective permissions and test access decisions in real time.</h3>
      </div>
      <div class="toolbar__badge">
        <span>Roles</span>
        <strong>{{ roles.join(", ") || "--" }}</strong>
      </div>
    </div>

    <div class="content-grid">
      <article class="surface-card">
        <div class="surface-card__header">
          <h4>Effective permissions</h4>
          <span class="surface-card__meta">{{ permissions.length }} grants</span>
        </div>
        <ul class="permission-list permission-list--dense">
          <li v-for="item in permissions" :key="`${item.resource}-${item.action}`">
            <strong>{{ item.resource }}</strong>
            <span>{{ item.action }}</span>
          </li>
        </ul>
      </article>

      <article class="surface-card surface-card--accent">
        <div class="surface-card__header">
          <h4>Permission probe</h4>
          <span class="surface-card__meta">/rbac/check</span>
        </div>
        <form class="probe-form" @submit.prevent="runCheck">
          <label>
            <span>Resource</span>
            <input v-model.trim="probe.resource" placeholder="users" required />
          </label>
          <label>
            <span>Action</span>
            <input v-model.trim="probe.action" placeholder="read" required />
          </label>
          <button class="primary-button" :disabled="checking" type="submit">
            {{ checking ? "Checking..." : "Check permission" }}
          </button>
        </form>
        <p v-if="probeResult" class="probe-result">
          Decision:
          <strong>{{ probeResult.allowed ? "ALLOW" : "DENY" }}</strong>
          for
          <code>{{ probeResult.resource }}:{{ probeResult.action }}</code>
        </p>
        <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
      </article>
    </div>
  </section>
</template>

<script>
import { checkPermission, fetchMyPermissions } from "@/utils/api";

export default {
  name: "PermissionsView",
  data() {
    return {
      checking: false,
      errorMessage: "",
      permissions: [],
      probe: {
        resource: "users",
        action: "read"
      },
      probeResult: null,
      roles: []
    };
  },
  created() {
    this.loadPermissions();
  },
  methods: {
    async loadPermissions() {
      try {
        const payload = await fetchMyPermissions();
        this.permissions = payload.permissions || [];
        this.roles = payload.roles || [];
      } catch (error) {
        this.errorMessage =
          "Unable to fetch current RBAC permissions. Confirm the backend session is active.";
      }
    },
    async runCheck() {
      this.checking = true;
      this.errorMessage = "";

      try {
        this.probeResult = await checkPermission(this.probe.resource, this.probe.action);
      } catch (error) {
        this.errorMessage =
          "Permission probe failed. The endpoint may be unavailable or the session may lack rbac:check.";
      } finally {
        this.checking = false;
      }
    }
  }
};
</script>
