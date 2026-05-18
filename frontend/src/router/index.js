import Vue from "vue";
import Router from "vue-router";
import AdminLayout from "@/layouts/AdminLayout.vue";
import LoginView from "@/views/auth/LoginView.vue";
import DashboardView from "@/views/dashboard/DashboardView.vue";
import UsersView from "@/views/users/UsersView.vue";
import PermissionsView from "@/views/permissions/PermissionsView.vue";
import RoleAdminView from "@/views/rbac/RoleAdminView.vue";
import { getAccessToken } from "@/utils/session";

Vue.use(Router);

const router = new Router({
  mode: "hash",
  routes: [
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: {
        guestOnly: true,
        title: "Sign In"
      }
    },
    {
      path: "/",
      component: AdminLayout,
      meta: {
        requiresAuth: true
      },
      children: [
        {
          path: "",
          redirect: "/dashboard"
        },
        {
          path: "/dashboard",
          name: "dashboard",
          component: DashboardView,
          meta: {
            title: "Dashboard"
          }
        },
        {
          path: "/users",
          name: "users",
          component: UsersView,
          meta: {
            title: "Users"
          }
        },
        {
          path: "/permissions",
          name: "permissions",
          component: PermissionsView,
          meta: {
            title: "Permissions"
          }
        },
        {
          path: "/role-admin",
          name: "role-admin",
          component: RoleAdminView,
          meta: {
            title: "Role Admin"
          }
        }
      ]
    },
    {
      path: "*",
      redirect: "/dashboard"
    }
  ],
  scrollBehavior() {
    return { x: 0, y: 0 };
  }
});

router.beforeEach((to, from, next) => {
  const token = getAccessToken();

  if (to.matched.some((record) => record.meta.requiresAuth) && !token) {
    next({
      name: "login",
      query: { redirect: to.fullPath }
    });
    return;
  }

  if (to.matched.some((record) => record.meta.guestOnly) && token) {
    next({ name: "dashboard" });
    return;
  }

  next();
});

router.afterEach((to) => {
  const title = to.meta && to.meta.title ? `${to.meta.title} | Slosh Admin` : "Slosh Admin";
  document.title = title;
});

export default router;
