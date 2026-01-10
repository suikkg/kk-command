const state = {
  commands: [],
  keyword: "",
  category: "all",
  favorites: new Set(),
  favOnly: false
};

const els = {};
const STORAGE_KEYS = {
  favorites: "cmd-cheatsheet-favorites",
  history: "cmd-cheatsheet-history",
  theme: "cmd-cheatsheet-theme",
  lastSearch: "cmd-cheatsheet-last-search"
};

document.addEventListener("DOMContentLoaded", () => {
  cacheElements();
  bindEvents();
  hydrateTheme();
  loadFavorites();
  loadHistory();
  restoreLastSearch();
  fetchData();
});

function cacheElements() {
  els.list = document.getElementById("commandList");
  els.empty = document.getElementById("emptyState");
  els.search = document.getElementById("searchInput");
  els.clear = document.getElementById("clearSearch");
  els.categoryRow = document.getElementById("categoryRow");
  els.history = document.getElementById("historyChips");
  els.themeToggle = document.getElementById("themeToggle");
  els.favOnly = document.getElementById("favOnly");
  els.modal = document.getElementById("modal");
  els.modalClose = document.getElementById("modalClose");
  els.modalCategory = document.getElementById("modalCategory");
  els.modalScene = document.getElementById("modalScene");
  els.modalCommand = document.getElementById("modalCommand");
  els.modalParams = document.getElementById("modalParams");
  els.modalNotes = document.getElementById("modalNotes");
  els.modalCopy = document.getElementById("modalCopy");
}

async function fetchData() {
  try {
    const res = await fetch("data.json");
    state.commands = await res.json();
    renderList();
  } catch (err) {
    console.error("加载数据失败:", err);
    els.empty.classList.remove("hidden");
    els.empty.textContent = "数据加载失败，请检查 data.json 是否可访问。";
  }
}

function bindEvents() {
  els.search.addEventListener("input", (e) => {
    state.keyword = e.target.value.trim();
    saveLastSearch();
    renderList();
  });

  els.search.addEventListener("keydown", (e) => {
    if (e.key === "Enter") addHistory(state.keyword);
  });

  els.clear.addEventListener("click", () => {
    state.keyword = "";
    els.search.value = "";
    saveLastSearch();
    renderList();
  });

  els.categoryRow.addEventListener("click", (e) => {
    if (e.target.matches(".cat-btn")) {
      document.querySelectorAll(".cat-btn").forEach((btn) => btn.classList.remove("active"));
      e.target.classList.add("active");
      state.category = e.target.dataset.category;
      renderList();
    }
  });

  els.history.addEventListener("click", (e) => {
    if (e.target.matches(".chip")) {
      state.keyword = e.target.dataset.term;
      els.search.value = state.keyword;
      renderList();
    }
  });

  els.themeToggle.addEventListener("click", toggleTheme);
  els.favOnly.addEventListener("change", (e) => {
    state.favOnly = e.target.checked;
    renderList();
  });

  els.modalClose.addEventListener("click", closeModal);
  els.modal.addEventListener("click", (e) => {
    if (e.target === els.modal) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });

  els.modalCopy.addEventListener("click", () => {
    const text = els.modalCommand.dataset.raw || "";
    copyToClipboard(text);
  });
}

function renderList() {
  const keyword = state.keyword.toLowerCase();
  const category = state.category;
  const filtered = state.commands.filter((cmd) => {
    const matchCategory = category === "all" || cmd.category === category;
    const matchKeyword =
      !keyword ||
      cmd.scene.toLowerCase().includes(keyword) ||
      cmd.command.toLowerCase().includes(keyword) ||
      cmd.category.toLowerCase().includes(keyword);
    const matchFavorite = !state.favOnly || state.favorites.has(cmd.id);
    return matchCategory && matchKeyword && matchFavorite;
  });

  els.list.innerHTML = "";
  if (!filtered.length) {
    els.empty.classList.remove("hidden");
    return;
  }
  els.empty.classList.add("hidden");

  filtered.forEach((cmd) => {
    const card = document.createElement("article");
    card.className = "card cmd-card";
    card.innerHTML = `
      <div class="cmd-title">
        <div>
          <div class="badge">${cmd.category}</div>
          <div class="scene">${cmd.scene}</div>
        </div>
        <button class="favorite-btn ${state.favorites.has(cmd.id) ? "active" : ""}" data-id="${cmd.id}" aria-label="收藏">★</button>
      </div>
      <div class="command">${highlightCommand(cmd.command)}</div>
      <div class="actions">
        <button class="primary small" data-action="copy" data-id="${cmd.id}">复制</button>
        <button class="ghost small" data-action="detail" data-id="${cmd.id}">详情</button>
      </div>
    `;
    els.list.appendChild(card);
  });

  els.list.querySelectorAll(".favorite-btn").forEach((btn) => {
    btn.addEventListener("click", () => toggleFavorite(btn.dataset.id));
  });

  els.list.querySelectorAll("[data-action='copy']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const cmd = state.commands.find((c) => c.id === btn.dataset.id);
      copyToClipboard(cmd.command);
    });
  });

  els.list.querySelectorAll("[data-action='detail']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const cmd = state.commands.find((c) => c.id === btn.dataset.id);
      openModal(cmd);
    });
  });
}

function highlightCommand(cmd) {
  const escaped = escapeHtml(cmd);
  return escaped.replace(/(^|\\s)(-[-\\w.=/:]+)/g, (_m, space, flag) => {
    return `${space}<span class="param">${flag}</span>`;
  });
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function openModal(cmd) {
  els.modalCategory.textContent = cmd.category;
  els.modalScene.textContent = cmd.scene;
  els.modalCommand.innerHTML = highlightCommand(cmd.command);
  els.modalCommand.dataset.raw = cmd.command;
  els.modalParams.textContent = cmd.params || "—";
  els.modalNotes.textContent = cmd.notes || "—";
  els.modal.classList.remove("hidden");
}

function closeModal() {
  els.modal.classList.add("hidden");
}

async function copyToClipboard(text) {
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    toast("已复制");
  } catch (err) {
    console.error("复制失败", err);
    toast("复制失败，可手动选中复制");
  }
}

function toast(msg) {
  const tip = document.createElement("div");
  tip.textContent = msg;
  tip.style.position = "fixed";
  tip.style.bottom = "18px";
  tip.style.left = "50%";
  tip.style.transform = "translateX(-50%)";
  tip.style.padding = "10px 14px";
  tip.style.background = "rgba(0,0,0,0.75)";
  tip.style.color = "#fff";
  tip.style.borderRadius = "10px";
  tip.style.fontSize = "13px";
  tip.style.zIndex = "20";
  document.body.appendChild(tip);
  setTimeout(() => tip.remove(), 1200);
}

function toggleFavorite(id) {
  if (state.favorites.has(id)) {
    state.favorites.delete(id);
  } else {
    state.favorites.add(id);
  }
  persistFavorites();
  renderList();
}

function loadFavorites() {
  const raw = localStorage.getItem(STORAGE_KEYS.favorites);
  if (raw) {
    try {
      const ids = JSON.parse(raw);
      state.favorites = new Set(ids);
    } catch (_) {
      state.favorites = new Set();
    }
  }
}

function persistFavorites() {
  localStorage.setItem(STORAGE_KEYS.favorites, JSON.stringify([...state.favorites]));
}

function addHistory(term) {
  if (!term) return;
  const list = getHistory();
  const newList = [term, ...list.filter((t) => t !== term)].slice(0, 6);
  localStorage.setItem(STORAGE_KEYS.history, JSON.stringify(newList));
  renderHistory(newList);
}

function loadHistory() {
  renderHistory(getHistory());
}

function getHistory() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.history)) || [];
  } catch (_) {
    return [];
  }
}

function renderHistory(list) {
  els.history.innerHTML = "";
  if (!list.length) {
    els.history.innerHTML = '<span class="chip" aria-disabled="true">暂无</span>';
    return;
  }
  list.forEach((term) => {
    const chip = document.createElement("button");
    chip.className = "chip";
    chip.dataset.term = term;
    chip.textContent = term;
    els.history.appendChild(chip);
  });
}

function toggleTheme() {
  const isDark = document.body.classList.toggle("dark");
  if (isDark) document.body.classList.remove("light");
  else document.body.classList.add("light");
  localStorage.setItem(STORAGE_KEYS.theme, isDark ? "dark" : "light");
}

function hydrateTheme() {
  const saved = localStorage.getItem(STORAGE_KEYS.theme);
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  if (saved === "dark" || (!saved && prefersDark)) {
    document.body.classList.add("dark");
    document.body.classList.remove("light");
  } else {
    document.body.classList.add("light");
    document.body.classList.remove("dark");
  }
}

function saveLastSearch() {
  localStorage.setItem(STORAGE_KEYS.lastSearch, state.keyword);
}

function restoreLastSearch() {
  const last = localStorage.getItem(STORAGE_KEYS.lastSearch);
  if (last) {
    state.keyword = last;
    els.search.value = last;
  }
}
