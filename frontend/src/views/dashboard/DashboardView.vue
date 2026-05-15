<template>
  <section class="page-grid">
    <div class="hero-panel">
      <div>
        <p class="eyebrow">System pulse</p>
        <h3>Visibility into identity, permissions, and operator activity.</h3>
      </div>
      <p class="hero-panel__copy">
        The dashboard blends live backend data with concise operational framing so you can spot access drift quickly.
      </p>
    </div>

    <div class="stats-grid">
      <StatCard title="Current user" :value="currentUser.email || '--'" hint="Authenticated operator" chip="Session" />
      <StatCard title="Assigned roles" :value="rolesLabel" hint="Resolved from Casbin grouping rules" chip="RBAC" />
      <StatCard title="Granted permissions" :value="permissions.length" hint="Implicit permissions for this session" chip="Effective" />
      <StatCard title="Known users" :value="userTotal" hint="Fetched from /users when permitted" chip="Directory" />
    </div>

    <div class="content-grid">
      <article class="surface-card">
        <div class="surface-card__header">
          <h4>Recent permission surface</h4>
          <span class="surface-card__meta">{{ permissions.length }} entries</span>
        </div>
        <ul class="permission-list">
          <li v-for="item in permissionPreview" :key="`${item.resource}-${item.action}`">
            <strong>{{ item.resource }}</strong>
            <span>{{ item.action }}</span>
          </li>
        </ul>
      </article>

      <article class="surface-card surface-card--accent">
        <div class="surface-card__header">
          <h4>Backend connectivity</h4>
          <span class="surface-card__meta">{{ statusLabel }}</span>
        </div>
        <p class="surface-card__body">
          {{ statusMessage }}
        </p>
        <button class="ghost-button" type="button" @click="loadDashboard">
          Refresh snapshot
        </button>
      </article>
    </div>
  </section>
</template>

<script>
import StatCard from "@/components/StatCard.vue";
import { fetchCurrentUser, fetchMyPermissions, fetchUsers } from "@/utils/api";

export default {
  name: "DashboardView",
  components: {
    StatCard
  },
  data() {
    return {
      currentUser: {},
      permissions: [],
      roles: [],
      userTotal: "--",
      statusLabel: "Syncing",
      statusMessage: "Loading data from the backend services.",
      loading: false
    };
  },
  computed: {
    permissionPreview() {
      return this.permissions.slice(0, 6);
    },
    rolesLabel() {
      return this.roles.length ? this.roles.join(", ") : "--";
    }
  },
  created() {
    this.loadDashboard();
  },
  methods: {
    async loadDashboard() {
      this.loading = true;
      this.statusLabel = "Syncing";
      this.statusMessage = "Refreshing user, permission, and directory signals.";

      const [userResult, permissionResult, usersResult] = await Promise.allSettled([
        fetchCurrentUser(true),
        fetchMyPermissions(),
        fetchUsers({ skip: 0, limit: 1 })
      ]);

      if (userResult.status === "fulfilled") {
        this.currentUser = userResult.value;
      }

      if (permissionResult.status === "fulfilled") {
        this.permissions = permissionResult.value.permissions || [];
        this.roles = permissionResult.value.roles || [];
      }

      if (usersResult.status === "fulfilled") {
        this.userTotal = usersResult.value.total;
      }

      const failures = [userResult, permissionResult, usersResult].filter(
        (item) => item.status === "rejected"
      );

      if (failures.length) {
        this.statusLabel = "Partial";
        this.statusMessage =
          "Some endpoints could not be reached. The shell is still usable, but backend data is incomplete.";
      } else {
        this.statusLabel = "Healthy";
        this.statusMessage =
          "Backend responses are live. The console is currently rendering data from active API calls.";
      }

      this.loading = false;
    }
  }
};
</script>
