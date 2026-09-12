"use strict";
const App = (() => {
  const state = { bootstrap: null, help: null };
  const $ = (id) => document.getElementById(id);
  const saved = (key, fallback) => localStorage.getItem(`provoware.${key}`) ?? fallback;
  const persist = (key, value) => localStorage.setItem(`provoware.${key}`, value);
  let sorterLoader = null;

  const log = (message, kind = "info", announce = true) => {
    const icon = kind === "ok" ? "🟢" : kind === "warn" ? "🟡" : kind === "error" ? "🔴" : "🔵";
    const row = document.createElement("span");
    row.textContent = `${icon} ${message}`;
    $("log-list").prepend(row);
    if (announce && window.Feedback) window.Feedback.record(kind, message);
  };

  function clampZoom(value) { return Math.max(100, Math.min(200, Number(value) || 100)); }
  function setZoom(value, announce = false) {
    const zoom = clampZoom(value);
    document.documentElement.style.setProperty("--font-scale", String(zoom / 100));
    $("font-scale").value = String(zoom);
    $("font-value").value = `${zoom}%`;
    persist("fontScale", String(zoom));
    if (announce) log(`Zoom auf ${zoom} Prozent eingestellt.`, "ok");
  }

  function applyPreferences() {
    const theme = saved("theme", "carbon");
    const complexity = saved("complexity", "laie");
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.complexity = complexity;
    $("theme-select").value = theme;
    $("complexity-select").value = complexity;
    setZoom(saved("fontScale", "100"));
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
    $("font-scale").addEventListener("input", (event) => setZoom(event.target.value));
  }

  function bindZoomShortcuts() {
    document.addEventListener("keydown", (event) => {
      if (!event.ctrlKey) return;
      if (["+", "="].includes(event.key)) { event.preventDefault(); setZoom(Number($("font-scale").value) + 5, true); }
      else if (event.key === "-") { event.preventDefault(); setZoom(Number($("font-scale").value) - 5, true); }
      else if (event.key === "0") { event.preventDefault(); setZoom(100, true); }
    });
    document.addEventListener("wheel", (event) => {
      if (!event.ctrlKey) return;
      event.preventDefault();
      setZoom(Number($("font-scale").value) + (event.deltaY < 0 ? 5 : -5));
    }, { passive: false });
  }

  function showWorkspace(title, content) {
    $("title-n").textContent = title;
    const root = $("workspace-content"); root.replaceChildren();
    if (content instanceof Node) root.appendChild(content);
    else { const p = document.createElement("p"); p.textContent = String(content ?? ""); root.appendChild(p); }
  }

  function genericWorkspace(label) {
    const hero = document.createElement("div"); hero.className = "hero";
    const icon = document.createElement("span"); icon.className = "hero-icon"; icon.textContent = "▦";
    const body = document.createElement("div"), h = document.createElement("h3"), p = document.createElement("p");
    h.textContent = label; p.textContent = "Dieses Modul ist registriert. Fachfunktionen werden hinter derselben stabilen Modulgrenze ergänzt.";
    body.append(h, p); hero.append(icon, body); showWorkspace(label.replace(/^[^\s]+\s/, ""), hero);
  }

  async function openSorterWorkspace() {
    if (!window.SorterUI) {
      if (!sorterLoader) {
        sorterLoader = new Promise((resolve, reject) => {
          const script = document.createElement("script");
          script.src = "/static/js/sorter.js";
          script.async = true;
          script.dataset.provowareSorter = "1";
          script.addEventListener("load", resolve, { once: true });
          script.addEventListener("error", () => reject(new Error("Dateien-Modul konnte nicht geladen werden.")), { once: true });
          document.head.appendChild(script);
        });
      }
      await sorterLoader;
    }
    if (!window.SorterUI) throw new Error("Dateien-Modul wurde nicht korrekt initialisiert.");
    await window.SorterUI.openWorkspace();
  }

  function bindNavigation() {
    document.querySelectorAll(".nav-item").forEach((btn) => btn.addEventListener("click", async () => {
      document.querySelectorAll(".nav-item").forEach((item) => item.classList.toggle("active", item === btn));
      try {
        if (btn.dataset.module === "todo" && window.DataUI) window.DataUI.openTodoWorkspace();
        else if (btn.dataset.module === "dateien") await openSorterWorkspace();
        else genericWorkspace(btn.textContent.trim());
        log(`Modul ${btn.textContent.trim()} geöffnet.`, "info");
      } catch (error) {
        genericWorkspace(btn.textContent.trim());
        log(error.message || "Modul konnte nicht geladen werden.", "error");
      }
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
    const project = bootstrap.project, repair = bootstrap.self_repair;
    $("project-name").textContent = project?.configured ? (project.name || "Projekt") : "Nicht eingerichtet";
    $("project-path").textContent = project?.path || "Noch kein Projektordner";
    const badge = $("health-badge");
    if (repair?.blocking) {
      $("system-status").textContent = "Prüfung erforderlich"; badge.textContent = "🔴 Sicherer Betrieb blockiert"; badge.classList.remove("success");
    } else if (project?.available) {
      $("system-status").textContent = repair?.changed ? "Automatisch repariert" : "Betriebsbereit";
      badge.textContent = repair?.changed ? "🟡 Reparatur geprüft" : "🟢 Betriebsbereit"; badge.classList.toggle("success", !repair?.changed);
    } else {
      $("system-status").textContent = "Projekt einrichten"; badge.textContent = "🟡 Einrichtung"; badge.classList.remove("success");
    }
  }

  function bindProject() {
    const dialog = $("project-dialog");
    $("setup-project").addEventListener("click", () => dialog.showModal());
    $("pick-project-base").addEventListener("click", async () => {
      try { const response = await fetch("/api/project/pick-base"); const data = await response.json(); if (response.ok && data.path) $("project-input-base").value = data.path; else if (data.fallback) $("project-input-base").value = data.fallback; }
      catch { log("Ordnerauswahl nicht verfügbar. Der Pfad kann weiterhin von Hand eingetragen werden.", "warn"); }
    });
    $("create-project").addEventListener("click", async () => {
      const button = $("create-project"), box = $("project-error"), task = window.Feedback?.begin("Projekt wird eingerichtet", "Ordner und Datenkern werden vorvalidiert.");
      button.disabled = true; button.setAttribute("aria-busy", "true"); box.classList.add("hidden");
      try {
        task?.update(25, "Projektpfad und Eingaben werden geprüft …");
        const response = await fetch("/api/project/create", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ base_path: $("project-input-base").value, name: $("project-input-name").value }) });
        const data = await response.json(); if (!response.ok) throw new Error(data.error || "Projekt konnte nicht angelegt werden.");
        task?.update(75, "Projekt wurde angelegt; Oberfläche wird aktualisiert …");
        dialog.close(); await refreshBootstrap(); await window.DataUI?.refreshAll();
        task?.end("ok", "Projekt ist sicher eingerichtet.", "Projektstruktur und Datenkern wurden validiert.");
        log("Projekt sicher angelegt, Datenkern initialisiert und validiert.", "ok", false);
      } catch (error) {
        box.textContent = `${error.message} Es wurden keine unsicheren Folgeaktionen ausgeführt.`; box.classList.remove("hidden");
        task?.end("error", "Projekt konnte nicht sicher eingerichtet werden.", error.message); log(error.message, "error", false);
      } finally { button.disabled = false; button.removeAttribute("aria-busy"); }
    });
  }

  function bindSelfRepair() {
    const button = $("self-repair-button"), status = $("self-repair-state");
    button.addEventListener("click", async () => {
      const task = window.Feedback?.begin("Sichere Reparaturprüfung", "Nur freigegebene reversible Reparaturen werden betrachtet.");
      button.disabled = true; button.setAttribute("aria-busy", "true"); status.textContent = "Prüft sichere Reparaturmöglichkeiten …";
      try {
        const response = await fetch("/api/self-repair/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }); const data = await response.json();
        if (!response.ok || data.blocking) {
          status.textContent = "Nicht eindeutig sicher reparierbar – keine riskante Änderung durchgeführt.";
          task?.end("error", "Self-Repair hat sicher gestoppt.", "Der Zustand war nicht eindeutig reparierbar; keine riskante Änderung wurde durchgeführt.");
          log("Self-Repair hat einen blockierenden Zustand unverändert gelassen.", "error", false);
        } else if (data.changed) {
          status.textContent = "Sichere Reparatur abgeschlossen und protokolliert ✓";
          task?.end("warn", "Self-Repair hat sicher korrigiert.", "Die Reparatur wurde protokolliert und nachvalidiert.");
          log("Self-Repair hat einen freigegebenen sicheren Zustand automatisch korrigiert.", "warn", false);
        } else {
          status.textContent = "Keine Reparatur nötig ✓";
          task?.end("ok", "Self-Repair: alles in Ordnung.", "Kein Eingriff war erforderlich.");
          log("Self-Repair-Prüfung: kein Eingriff erforderlich.", "ok", false);
        }
        await refreshBootstrap(); await window.DataUI?.refreshAll();
      } catch (error) {
        status.textContent = "Self-Repair konnte nicht ausgeführt werden.";
        task?.end("error", "Self-Repair konnte nicht abgeschlossen werden.", error.message || "Unbekannter Fehler"); log(error.message || "Self-Repair fehlgeschlagen.", "error", false);
      } finally { button.disabled = false; button.removeAttribute("aria-busy"); }
    });
  }

  function bindQuickSave() {
    const save = async () => {
      const title = $("save-title").value, text = $("save-text").value, button = $("save-button");
      if (!title.trim() || !text.trim()) { $("save-state").textContent = "Titel und Eingabe werden benötigt."; log("Schnellspeicher: Titel und Text fehlen.", "warn"); return; }
      const task = window.Feedback?.begin("Schnellspeicher schreibt", "Der vorhandene Dateiinhalt wird nicht überschrieben.");
      button.disabled = true; button.setAttribute("aria-busy", "true"); $("save-state").textContent = "Speichert …";
      try {
        const response = await fetch("/api/quick-save", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title, text }) });
        const data = await response.json(); if (!response.ok) throw new Error(data.error || "Speichern fehlgeschlagen.");
        $("save-text").value = ""; $("save-state").textContent = `Gespeichert ✓ · ${data.path}`;
        task?.end("ok", "Schnellspeicher abgeschlossen.", "Der Text wurde mit Zeitstempel angehängt."); log("Schnellspeicher-Eintrag geschrieben.", "ok", false);
      } catch (error) {
        $("save-state").textContent = error.message; task?.end("error", "Schnellspeicher fehlgeschlagen.", error.message); log(error.message, "error", false);
      } finally { button.disabled = false; button.removeAttribute("aria-busy"); }
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
  async function init() { applyPreferences(); bindPreferences(); bindZoomShortcuts(); bindNavigation(); bindQuickActions(); bindNotes(); bindProject(); bindSelfRepair(); bindQuickSave(); bindHelp(); await loadHelp(); if (window.DataUI) window.DataUI.init(); }
  return { init, refreshBootstrap, renderBootstrap, log, showWorkspace, setZoom, state };
})();
window.addEventListener("DOMContentLoaded", () => App.init());
