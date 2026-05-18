const THEME_KEY = "slosh-theme";

function getSystemTheme() {
  if (
    typeof window !== "undefined" &&
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  ) {
    return "dark";
  }

  return "light";
}

export function getStoredTheme() {
  if (typeof window === "undefined") {
    return "light";
  }

  try {
    return window.localStorage.getItem(THEME_KEY) || getSystemTheme();
  } catch (error) {
    return getSystemTheme();
  }
}

export function applyTheme(theme) {
  const resolvedTheme = theme === "dark" ? "dark" : "light";

  if (typeof document !== "undefined") {
    document.documentElement.setAttribute("data-theme", resolvedTheme);
  }

  if (typeof window !== "undefined") {
    try {
      window.localStorage.setItem(THEME_KEY, resolvedTheme);
    } catch (error) {
      // Ignore storage failures and keep the theme applied for this session.
    }
  }

  return resolvedTheme;
}

export function initializeTheme() {
  return applyTheme(getStoredTheme());
}

export function getActiveTheme() {
  if (typeof document === "undefined") {
    return "light";
  }

  return document.documentElement.getAttribute("data-theme") || "light";
}

export function toggleTheme() {
  return applyTheme(getActiveTheme() === "dark" ? "light" : "dark");
}

export function setThemeCache(theme) {
  return applyTheme(theme);
}
