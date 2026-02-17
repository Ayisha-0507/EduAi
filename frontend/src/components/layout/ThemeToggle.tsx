import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("theme") === "dark";
    }
    return true;
  });

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [dark]);

  return (
    <button
      onClick={() => setDark((d) => !d)}
      className="px-2 py-1 rounded border border-border-default bg-bg-secondary hover:bg-bg-tertiary text-sm"
      aria-label="Toggle dark/light mode"
      style={{ marginLeft: 8 }}
    >
      {dark ? "🌙 Dark" : "☀️ Light"}
    </button>
  );
}
