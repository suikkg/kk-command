document.addEventListener("DOMContentLoaded", () => {
  const cards = Array.from(document.querySelectorAll(".cmd-card"));
  const searchInput = document.getElementById("searchInput");
  const clearBtn = document.getElementById("clearSearch");
  const toast = document.getElementById("toast");
  const empty = document.getElementById("emptyState");
  const themeToggle = document.getElementById("themeToggle");

  const STORAGE_THEME = "cmd-cheatsheet-theme";

  const showToast = (text) => {
    if (!toast) return;
    toast.textContent = text;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 1500);
  };

  const copyCommand = async (command) => {
    if (!command) return;
    try {
      await navigator.clipboard.writeText(command);
      showToast("已复制到剪贴板");
    } catch (_) {
      const textarea = document.createElement("textarea");
      textarea.value = command;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
      showToast("已复制到剪贴板");
    }
  };

  const filterCards = () => {
    const q = (searchInput?.value || "").trim().toLowerCase();
    let visibleCount = 0;
    const sectionVisibility = new Map();

    cards.forEach((card) => {
      const cmd = card.dataset.cmd || "";
      const keywords = card.dataset.keywords || "";
      const desc = card.querySelector(".scene")?.textContent || "";
      const text = `${cmd} ${keywords} ${desc}`.toLowerCase();
      const match = !q || text.includes(q);
      card.style.display = match ? "" : "none";
      if (match) visibleCount += 1;

      const section = card.closest(".git-section");
      if (section) {
        const prev = sectionVisibility.get(section) || false;
        sectionVisibility.set(section, prev || match);
      }
    });

    sectionVisibility.forEach((visible, section) => {
      section.style.display = visible ? "" : "none";
    });

    if (empty) empty.classList.toggle("hidden", visibleCount > 0);
  };

  cards.forEach((card) => {
    const btn = card.querySelector(".copy-btn");
    const cmd = btn?.dataset.command || card.dataset.cmd;
    btn?.addEventListener("click", () => copyCommand(cmd));
    card.querySelector(".command")?.addEventListener("click", () => copyCommand(cmd));
  });

  searchInput?.addEventListener("input", filterCards);
  clearBtn?.addEventListener("click", () => {
    searchInput.value = "";
    filterCards();
    searchInput.focus();
  });

  const hydrateTheme = () => {
    const saved = localStorage.getItem(STORAGE_THEME);
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const useDark = saved ? saved === "dark" : prefersDark;
    document.body.classList.toggle("dark", useDark);
    document.body.classList.toggle("light", !useDark);
  };

  themeToggle?.addEventListener("click", () => {
    const willDark = !document.body.classList.contains("dark");
    document.body.classList.toggle("dark", willDark);
    document.body.classList.toggle("light", !willDark);
    localStorage.setItem(STORAGE_THEME, willDark ? "dark" : "light");
  });

  hydrateTheme();
  filterCards();
});
