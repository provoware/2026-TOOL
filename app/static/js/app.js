"use strict";
const App = (() => {
  const state = { bootstrap: null, help: null };
  const $ = (id) => document.getElementById(id);
  const saved = (key, fallback) => localStorage.getItem(`provoware.${key}`) ?? fallback;
  const persist = (key, value) => localStorage.setItem(`provoware.${key}`, value);

  const log = (message, kind = "info") => {
    const icon = kind === "ok" ? "🟢" : kind === "warn" ? "🟡" : kind === "error" ? "🔴" : "🔵";
    const row = document.createElement("span");
    row.textContent = `${icon} ${message}`;
    $("log-list").prepend(row);
  };

  function applyPreferences() {
    const theme = saved("theme", "carbon");
    const complexity = saved("complexity", "laie");
    const font = saved("fontScale", "100");
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.complexity = complexity;
    document.documentElement.style.setProperty("--font-scale", String(Number(font) / 100));
    $("theme-select").value = theme;
    $("complexity-select").value = complexity;
    $("font-scale").value = font;
    $("font-value").value = `${font}%`;
  }

  function bindPreferences() {
    $("theme-select").addEventListener("change", (event) => {
      document.documentElement.dataset.theme = event.target.value;
      persist("theme", event.target.value);
      log(`Theme ${event.target.options[event.target.selectedIndex].text} aktiviert.`, "ok");
    });
    $("complexity-select").addEventListener("change", (event) => {
      document.documentElement.dataset.complexity = event.target.value;
      persist("complexity", event.target.value);
      log(`Bedienstufe ${event.target.options[event.target.selectedIndex].text} aktiviert.`, "ok");
    });
    $("font-scale").addEventListener("input", (event) => {
      const value = event.target.value;
      document.documentElement.style.setProperty("--font-scale", String(Number(value) / 100));
      $("font-value").value = `${value}%`;
      persist("fontScale", value);
    });
  }

  function showWorkspace(title, content) {
    $("title-n").textContent = title;
    const root = $("workspace-content");
    root.replaceChildren();
    if (content instanceof Node) root.appendChild(content);
    else {
      const p = document.createElement("p");
      p.textContent = String(content ?? "");
      root.appendChild(p);
    }
  }

  function genericWorkspace(label) {
    const hero = document.createElement("div"); hero.className = "hero";
    const icon = document.createElement("span"); icon.className = "hero-icon"; icon.textContent = "▦";
    const body = document.createElement("div");
    const h = document.createElement("h3"); h.textContent = label;
    const p = document.createElement("p"); p.textContent = "Dieses Modul ist registriert. Fachfunktionen werden hinter derselben stabilen Modulgrenze ergänzt.";
    body.append(h, p); hero.append(icon, body); showWorkspace(label.replace(/^[^\s]+\s/, ""), hero);
  }

  function bindNavigation() {
    document.querySelectorAll(".nav-item").forEach((btn) => btn.addEventListener("click", () => {
      document.querySelectorAll(".nav-item").forEach((item) => item.classList.toggle("active", item === btn));
      if (btn.dataset.module === "todo" && window.DataUI) window.DataUI.openTodoWorkspace();
      else genericWorkspace(btn.textContent.trim());
      log(`Modul ${btn.textContent.trim()} geöffnet.`);
    }));
    $("focus-workspace").addEventListener("click", () => toggleFocus(true));
    $("exit-focus").addEventListener("click", () => toggleFocus(false));
    document.addEventListener("keydown", (event) => { if (event.key === "Escape" && document.body.classList.contains("focus-mode")) toggleFocus(false); });
  }

  function toggleFocus(on) { document.body.classList.toggle("focus-mode", on); $("exit-focus").classList.toggle("hidden", !on); }
  function bindQuickActions() { document.querySelectorAll("[data-url]").forEach((button) => button.addEventListener("click", () => window.open(button.dataset.url, "_blank", "noopener"))); }

  function bindNotes() {
    const note = $("quick-note"); note.value = saved("quickNote", ""); let timer;
    note.addEventListener("input", () => {
      clearTimeout(timer); $("note-state").textContent = "Speichert …";
      timer = setTimeout(() => { persist("quickNote", note.value); $("note-state").textContent = "Gespeichert ✓"; }, 350);
    });
  }

  async function refreshBootstrap() {
    const response = await fetch("/api/bootstrap", { cache: "no-store" });
    state.bootstrap = await response.json(); renderBootstrap(); return state.bootstrap;
  }

  function renderBootstrap() {
    const bootstrap = state.bootstrap; if (!bootstrap) return;
    $("app-version").textContent = `v${bootstrap.version}`;
    $("profile-name").textContent = bootstrap.profile?.name || "Lokaler Nutzer";
    const project = bootstrap.project;
    $("project-name").textContent = project?.configured ? (project.name || "Projekt") : "Nicht eingerichtet";
    $("project-path").textContent = project?.path || "Noch kein Projektordner";
    const badge = $("health-badge");
    if (project?.available) { $("system-status").textContent = "Betriebsbereit"; badge.textContent = "🟢 Betriebsbereit"; badge.classList.add("success"); }
    else { $("system-status").textContent = "Projekt einrichten"; badge.textContent = "🟡 Einrichtung"; badge.classList.remove("success"); }
  }

  function bindProject() {
    const dialog = $("project-dialog");
    $("setup-project").addEventListener("click", () => dialog.showModal());
    $("pick-project-base").addEventListener("click", async () => {
      try { const response = await fetch("/api/project/pick-base"); const data = await response.json(); if (response.ok && data.path) $("project-input-base").value = data.path; else if (data.fallback) $("project-input-base").value = data.fallback; }
      catch { log("Ordnerauswahl nicht verfügbar.", "warn"); }
    });
    $("create-project").addEventListener("click", async () => {
      const box = $("project-error"); box.classList.add("hidden");
      try {
        const response = await fetch("/api/project/create", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ base_path: $("project-input-base").value, name: $("project-input-name").value }) });
        const data = await response.json(); if (!response.ok) throw new Error(data.error || "Projekt konnte nicht angelegt werden.");
        dialog.close(); await refreshBootstrap(); await window.DataUI?.refreshAll(); log("Projekt sicher angelegt, Datenkern initialisiert und validiert.", "ok");
      } catch (error) { box.textContent = error.message; box.classList.remove("hidden"); log(error.message, "error"); }
    });
  }

  function bindQuickSave() {
    const save = async () => {
      const title = $("save-title").value, text = $("save-text").value;
      if (!title.trim() || !text.trim()) { $("save-state").textContent = "Titel und Eingabe werden benötigt."; return; }
      $("save-state").textContent = "Speichert …";
      try {
        const response = await fetch("/api/quick-save", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title, text }) });
        const data = await response.json(); if (!response.ok) throw new Error(data.error || "Speichern fehlgeschlagen.");
        $("save-text").value = ""; $("save-state").textContent = `Gespeichert ✓ · ${data.path}`; log("Schnellspeicher-Eintrag geschrieben.", "ok");
      } catch (error) { $("save-state").textContent = error.message; log(error.message, "error"); }
    };
    $("save-button").addEventListener("click", save);
    $("save-text").addEventListener("keydown", (event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); save(); } });
  }

  async function loadHelp() {
    try {
      const response = await fetch("/static/help.json"); state.help = await response.json(); const root = $("help-content"); root.replaceChildren();
      state.help.sections.forEach((section) => { const item = document.createElement("section"), h = document.createElement("h3"), p = document.createElement("p"); h.textContent = section.title; p.textContent = section.text; item.append(h, p); root.appendChild(item); });
    } catch { $("help-content").textContent = "Hilfe konnte nicht geladen werden."; }
  }

  function bindHelp() { const dialog = $("help-dialog"); $("help-button").addEventListener("click", () => dialog.showModal()); $("close-help").addEventListener("click", () => dialog.close()); }
  async function init() { applyPreferences(); bindPreferences(); bindNavigation(); bindQuickActions(); bindNotes(); bindProject(); bindQuickSave(); bindHelp(); await loadHelp(); if (window.DataUI) window.DataUI.init(); }
  return { init, refreshBootstrap, renderBootstrap, log, showWorkspace, state };
})();
window.addEventListener("DOMContentLoaded", () => App.init());
