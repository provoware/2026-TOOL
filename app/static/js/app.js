"use strict";
const App = (() => {
  const state = { bootstrap: null, help: null };
  const $ = (id) => document.getElementById(id);
  const saved = (key, fallback) => localStorage.getItem(`provoware.${key}`) ?? fallback;
  const persist = (key, value) => localStorage.setItem(`provoware.${key}`, value);

  const log = (message, kind = "info") => {
    const icon = kind === "ok" ? "🟢" : kind === "warn" ? "🟡" : kind === "error" ? "🔴" : "🔵";
    const row = document.createElement("span"); row.textContent = `${icon} ${message}`; $("log-list").prepend(row);
    if (kind !== "info") Feedback?.toast(message, kind);
  };

  function applyPreferences() {
    const theme = saved("theme", "carbon"), complexity = saved("complexity", "laie"), contrast = saved("contrast", "normal");
    const font = Math.max(90, Math.min(200, Number(saved("fontScale", "100")) || 100));
    document.documentElement.dataset.theme = theme; document.documentElement.dataset.complexity = complexity; document.documentElement.dataset.contrast = contrast;
    document.documentElement.style.setProperty("--font-scale", String(font / 100));
    $("theme-select").value = theme; $("complexity-select").value = complexity; $("contrast-select").value = contrast; $("font-scale").value = String(font); $("font-value").value = `${font}%`;
  }

  function bindPreferences() {
    $("theme-select").addEventListener("change", (event) => { document.documentElement.dataset.theme = event.target.value; persist("theme", event.target.value); log(`Theme ${event.target.options[event.target.selectedIndex].text} aktiviert.`, "ok"); });
    $("complexity-select").addEventListener("change", (event) => { document.documentElement.dataset.complexity = event.target.value; persist("complexity", event.target.value); log(`Bedienstufe ${event.target.options[event.target.selectedIndex].text} aktiviert.`, "ok"); updateNextStep(); });
    $("contrast-select").addEventListener("change", (event) => { document.documentElement.dataset.contrast = event.target.value; persist("contrast", event.target.value); log(event.target.value === "high" ? "Kontrast+ aktiviert." : "Normaler Kontrast aktiviert.", "ok"); });
    $("font-scale").addEventListener("input", (event) => { const value = Number(event.target.value); document.documentElement.style.setProperty("--font-scale", String(value / 100)); $("font-value").value = `${value}%`; persist("fontScale", String(value)); Feedback?.announce(`Schriftgröße ${value} Prozent`); });
  }

  function showWorkspace(title, content) {
    $("title-n").textContent = title; const root = $("workspace-content"); root.replaceChildren();
    if (content instanceof Node) root.appendChild(content); else { const p = document.createElement("p"); p.textContent = String(content ?? ""); root.appendChild(p); }
    root.focus({ preventScroll: true });
  }

  function genericWorkspace(label) {
    const hero = document.createElement("div"); hero.className = "hero"; const icon = document.createElement("span"); icon.className = "hero-icon"; icon.textContent = "▦";
    const body = document.createElement("div"), h = document.createElement("h3"), p = document.createElement("p"); h.textContent = label; p.textContent = "Dieses Modul ist vorbereitet. Noch nicht verfügbare Funktionen werden nicht als funktionsfähig dargestellt.";
    body.append(h, p); hero.append(icon, body); showWorkspace(label.replace(/^[^\s]+\s/, ""), hero);
  }

  function activateNav(btn) {
    document.querySelectorAll(".nav-item").forEach((item) => { const active = item === btn; item.classList.toggle("active", active); if (active) item.setAttribute("aria-current", "page"); else item.removeAttribute("aria-current"); });
  }

  function bindNavigation() {
    document.querySelectorAll(".nav-item").forEach((btn) => btn.addEventListener("click", () => { activateNav(btn); if (btn.dataset.module === "todo" && window.DataUI) window.DataUI.openTodoWorkspace(); else genericWorkspace(btn.textContent.trim()); Feedback?.announce(`Modul ${btn.textContent.trim()} geöffnet`); }));
    $("focus-workspace").addEventListener("click", () => toggleFocus(true)); $("exit-focus").addEventListener("click", () => toggleFocus(false));
    document.addEventListener("keydown", (event) => { if (event.key === "Escape" && document.body.classList.contains("focus-mode")) toggleFocus(false); });
  }
  function toggleFocus(on) { document.body.classList.toggle("focus-mode", on); $("exit-focus").classList.toggle("hidden", !on); Feedback?.announce(on ? "Hauptarbeitsbereich maximiert" : "Dashboard wiederhergestellt"); }
  function bindQuickActions() { document.querySelectorAll("[data-url]").forEach((button) => button.addEventListener("click", () => { window.open(button.dataset.url, "_blank", "noopener"); Feedback?.toast(`${button.textContent.trim()} in neuem Tab geöffnet.`, "info"); })); }

  function bindNotes() {
    const note = $("quick-note"); note.value = saved("quickNote", ""); let timer;
    note.addEventListener("input", () => { clearTimeout(timer); $("note-state").textContent = "Speichert …"; timer = setTimeout(() => { persist("quickNote", note.value); $("note-state").textContent = "Gespeichert ✓"; Feedback?.announce("Notiz automatisch gespeichert"); }, 350); });
  }

  async function refreshBootstrap() { const response = await fetch("/api/bootstrap", { cache: "no-store" }); state.bootstrap = await response.json(); renderBootstrap(); return state.bootstrap; }

  function updateNextStep() {
    const project = state.bootstrap?.project, repair = state.bootstrap?.self_repair, title = $("next-step-title"), text = $("next-step-text"), action = $("next-step-action");
    if (!title || !action) return;
    if (repair?.blocking) { title.textContent = "Sicherheitsprüfung ansehen"; text.textContent = "Ein Zustand ist blockiert. Keine Fachaktion wird empfohlen."; action.textContent = "Diagnose"; action.onclick = () => $("self-repair-button").focus(); return; }
    if (!project?.available) { title.textContent = "Projekt einrichten"; text.textContent = "Ein Projekt ist die sichere Basis für alle Daten und Aktionen."; action.textContent = "Projekt einrichten"; action.onclick = () => $("setup-project").click(); return; }
    title.textContent = "Mit einer Aufgabe beginnen"; text.textContent = "Todo und Kalender sind bereits vollständig verfügbar."; action.textContent = "Todo öffnen"; action.onclick = () => document.querySelector('[data-module="todo"]').click();
  }

  function renderBootstrap() {
    const bootstrap = state.bootstrap; if (!bootstrap) return; $("app-version").textContent = `v${bootstrap.version}`; $("profile-name").textContent = bootstrap.profile?.name || "Lokaler Nutzer";
    const project = bootstrap.project, repair = bootstrap.self_repair, badge = $("health-badge"); $("project-name").textContent = project?.configured ? (project.name || "Projekt") : "Nicht eingerichtet"; $("project-path").textContent = project?.path || "Noch kein Projektordner";
    if (repair?.blocking) { $("system-status").textContent = "Prüfung erforderlich"; badge.textContent = "🔴 Sicherer Betrieb blockiert"; badge.classList.remove("success"); Feedback?.setGlobal("error", "Sicherer Betrieb blockiert", "Diagnose K zeigt den nächsten sicheren Schritt."); }
    else if (project?.available) { $("system-status").textContent = repair?.changed ? "Automatisch repariert" : "Betriebsbereit"; badge.textContent = repair?.changed ? "🟡 Reparatur geprüft" : "🟢 Betriebsbereit"; badge.classList.toggle("success", !repair?.changed); Feedback?.setGlobal(repair?.changed ? "warn" : "ok", repair?.changed ? "Sicher repariert" : "Betriebsbereit", "Keine blockierende Prüfung offen."); }
    else { $("system-status").textContent = "Projekt einrichten"; badge.textContent = "🟡 Einrichtung"; badge.classList.remove("success"); Feedback?.setGlobal("warn", "Einrichtung erforderlich", "Bitte zuerst einen Projektordner festlegen."); }
    updateNextStep();
  }

  function bindProject() {
    const dialog = $("project-dialog"); $("setup-project").addEventListener("click", () => dialog.showModal());
    $("pick-project-base").addEventListener("click", async () => { try { const response = await fetch("/api/project/pick-base"); const data = await response.json(); if (response.ok && data.path) $("project-input-base").value = data.path; else if (data.fallback) $("project-input-base").value = data.fallback; } catch { log("Ordnerauswahl nicht verfügbar.", "warn"); } });
    $("create-project").addEventListener("click", () => Feedback.busy($("create-project"), async () => {
      const box = $("project-error"); box.classList.add("hidden"); Feedback.begin({ id: "project-create", label: "Projekt wird eingerichtet", detail: "Ordner, Marker, Datenkern und Self-Repair werden geprüft." });
      try { const response = await fetch("/api/project/create", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ base_path: $("project-input-base").value, name: $("project-input-name").value }) }); const data = await response.json(); if (!response.ok) throw new Error(data.error || "Projekt konnte nicht angelegt werden."); dialog.close(); await refreshBootstrap(); await window.DataUI?.refreshAll(); Feedback.finish("project-create", { kind: "ok", message: "Projekt sicher eingerichtet" }); log("Projekt sicher angelegt, Datenkern initialisiert und validiert.", "ok"); }
      catch (error) { box.textContent = error.message; box.classList.remove("hidden"); Feedback.finish("project-create", { kind: "error", message: "Projekt nicht eingerichtet", detail: error.message }); log(error.message, "error"); }
    }, "Prüft …"));
  }

  function bindSelfRepair() {
    const button = $("self-repair-button"), status = $("self-repair-state");
    button.addEventListener("click", () => Feedback.busy(button, async () => {
      status.textContent = "Prüft sichere Reparaturmöglichkeiten …"; Feedback.begin({ id: "self-repair", label: "Self-Repair prüft", detail: "Nur freigegebene reversible Regeln werden ausgeführt." });
      try { const response = await fetch("/api/self-repair/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }); const data = await response.json();
        if (!response.ok || data.blocking) { status.textContent = "Nicht eindeutig sicher reparierbar – keine riskante Änderung durchgeführt."; Feedback.finish("self-repair", { kind: "error", message: "Self-Repair blockiert sicher", detail: "Keine riskante Änderung durchgeführt." }); log("Self-Repair hat einen blockierenden Zustand unverändert gelassen.", "error"); }
        else if (data.changed) { status.textContent = "Sichere Reparatur abgeschlossen und protokolliert ✓"; Feedback.finish("self-repair", { kind: "warn", message: "Sichere Reparatur abgeschlossen" }); log("Self-Repair hat einen freigegebenen sicheren Zustand automatisch korrigiert.", "warn"); }
        else { status.textContent = "Keine Reparatur nötig ✓"; Feedback.finish("self-repair", { kind: "ok", message: "Keine Reparatur nötig" }); log("Self-Repair-Prüfung: kein Eingriff erforderlich.", "ok"); }
        await refreshBootstrap(); await window.DataUI?.refreshAll();
      } catch (error) { status.textContent = "Self-Repair konnte nicht ausgeführt werden."; Feedback.finish("self-repair", { kind: "error", message: "Self-Repair fehlgeschlagen", detail: error.message || "Unbekannter Fehler" }); log(error.message || "Self-Repair fehlgeschlagen.", "error"); }
    }, "Prüft …"));
  }

  function bindQuickSave() {
    const save = () => Feedback.busy($("save-button"), async () => { const title = $("save-title").value, text = $("save-text").value; if (!title.trim() || !text.trim()) { $("save-state").textContent = "Titel und Eingabe werden benötigt."; Feedback.toast("Schnellspeicher unvollständig", "warn", "Titel und Text werden benötigt."); return; } $("save-state").textContent = "Speichert …";
      try { const response = await fetch("/api/quick-save", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title, text }) }); const data = await response.json(); if (!response.ok) throw new Error(data.error || "Speichern fehlgeschlagen."); $("save-text").value = ""; $("save-state").textContent = `Gespeichert ✓ · ${data.path}`; log("Schnellspeicher-Eintrag geschrieben.", "ok"); } catch (error) { $("save-state").textContent = error.message; log(error.message, "error"); }
    }, "Speichert …");
    $("save-button").addEventListener("click", save); $("save-text").addEventListener("keydown", (event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); save(); } });
  }

  async function loadHelp() { try { const response = await fetch("/static/help.json"); state.help = await response.json(); const root = $("help-content"); root.replaceChildren(); state.help.sections.forEach((section) => { const item = document.createElement("section"), h = document.createElement("h3"), p = document.createElement("p"); h.textContent = section.title; p.textContent = section.text; item.append(h, p); root.appendChild(item); }); } catch { $("help-content").textContent = "Hilfe konnte nicht geladen werden."; } }
  function bindHelp() { const dialog = $("help-dialog"); $("help-button").addEventListener("click", () => dialog.showModal()); $("close-help").addEventListener("click", () => dialog.close()); }
  async function init() { applyPreferences(); bindPreferences(); bindNavigation(); bindQuickActions(); bindNotes(); bindProject(); bindSelfRepair(); bindQuickSave(); bindHelp(); await loadHelp(); if (window.DataUI) window.DataUI.init(); }
  return { init, refreshBootstrap, renderBootstrap, log, showWorkspace, state };
})();
window.addEventListener("DOMContentLoaded", () => App.init());
