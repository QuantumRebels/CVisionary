export function getInitialDarkMode() {
  const stored = localStorage.getItem("darkMode");
  return stored === null ? true : stored === "true";
}

export function setDarkModePreference(value) {
  localStorage.setItem("darkMode", value);
}