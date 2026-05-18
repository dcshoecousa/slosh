import axios from "axios";
import {
  clearSession,
  getAccessToken,
  getCurrentUser,
  setAccessToken,
  setCurrentUser
} from "@/utils/session";

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8044/api/v1";

const http = axios.create({
  baseURL: apiBaseUrl,
  timeout: 12000
});

const AVAILABLE_ROLES = ["admin", "member"];

http.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      clearSession();
    }

    return Promise.reject(error);
  }
);

function unwrap(response) {
  return response.data ? response.data.data : null;
}

export async function login(email, password) {
  const payload = new URLSearchParams();
  payload.set("username", email);
  payload.set("password", password);

  const tokenResponse = await http.post("/auth/login", payload, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  });
  const tokenData = unwrap(tokenResponse);

  setAccessToken(tokenData.access_token);

  const userResponse = await http.get("/auth/me");
  const currentUser = unwrap(userResponse);
  setCurrentUser(currentUser);

  return {
    token: tokenData.access_token,
    user: currentUser
  };
}

export async function fetchCurrentUser(force = false) {
  if (!force) {
    const cachedUser = getCurrentUser();
    if (cachedUser) {
      return cachedUser;
    }
  }

  const response = await http.get("/auth/me");
  const user = unwrap(response);
  setCurrentUser(user);
  return user;
}

export async function fetchUsers(params = {}) {
  const response = await http.get("/users/", { params });
  return unwrap(response);
}

export async function fetchMyPermissions() {
  const response = await http.get("/rbac/me/permissions");
  return unwrap(response);
}

export async function checkPermission(resource, action) {
  const response = await http.get("/rbac/check", {
    params: { resource, action }
  });
  return unwrap(response);
}

export async function fetchRolePermissions(role) {
  const response = await http.get(`/rbac/roles/${role}/permissions`);
  return unwrap(response);
}

export async function fetchMySettings() {
  const response = await http.get("/settings/me");
  return unwrap(response);
}

export async function updateMySettings(payload) {
  const response = await http.patch("/settings/me", payload);
  return unwrap(response);
}

export async function assignRoleToUser(userId, role) {
  const response = await http.post(`/rbac/users/${userId}/roles`, {
    role
  });
  return unwrap(response);
}

export async function removeUserRole(userId, role) {
  const response = await http.delete(`/rbac/users/${userId}/roles/${role}`);
  return unwrap(response);
}

export async function grantPermissionToRole(role, payload) {
  const response = await http.post(`/rbac/roles/${role}/permissions`, payload);
  return unwrap(response);
}

export async function revokePermissionFromRole(role, payload) {
  const response = await http.delete(`/rbac/roles/${role}/permissions`, {
    data: payload
  });
  return unwrap(response);
}

export function logout() {
  clearSession();
}

export { AVAILABLE_ROLES, apiBaseUrl, http };
