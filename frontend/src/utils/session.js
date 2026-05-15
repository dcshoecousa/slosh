const TOKEN_KEY = "slosh-admin-token";
const USER_KEY = "slosh-admin-user";

export function getAccessToken() {
  return window.localStorage.getItem(TOKEN_KEY) || "";
}

export function setAccessToken(token) {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken() {
  window.localStorage.removeItem(TOKEN_KEY);
}

export function getCurrentUser() {
  const rawValue = window.localStorage.getItem(USER_KEY);

  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue);
  } catch (error) {
    window.localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function setCurrentUser(user) {
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearCurrentUser() {
  window.localStorage.removeItem(USER_KEY);
}

export function clearSession() {
  clearAccessToken();
  clearCurrentUser();
}
