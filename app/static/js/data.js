"use strict";
const DataUI = (() => {
  const state = { scope: "active", month: null, calendar: null, todos: [], summary: null };
  const $ = (id) => document.getElementById(id);
  function monthKey(value = new Date()) { return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}`; }
  async function api(url, options = {}) { const response = await fetch(url, { cache: "no-store", ...options }); const data = await response.json().catch(() => ({})); if (!response.ok) { const error = new Error(data.error || `HTTP ${response.status}`); error.status = response.status; throw error; } return data; }
  function projectAvailable() { return Boolean(App.state.bootstrap?.project?.available); }
  function empty(root, text) { root.replaceChildren(); const box = document.createElement("div"); box.className = "empty-state compact-empty"; const p = document.createElement("p"); p.textContent = text; box.appendChild(p); root.appendChild(box); }
  function dueLabel(todo) { if (!todo.due_date) return "Ohne Termin"; const parts = todo.due_date.split("-"); const dateText = `${parts[2]}.${parts[1]}.${parts[0]}`; return todo.due_time ? `${dateText} · ${todo.due_time}` : dateText; }
  function todoRow(todo, archived = false) {
    const row = document.createElement("article"); row.className = `todo-row priority-${todo.priority || "normal"}`; row.dataset.todoId = String(todo.id);
    const main = document.createElement("div"); main.className = "todo-main";
    const action = document.createElement("button"); action.className = archived ? "todo-check restore" : "todo-check"; action.type = "button"; action.textContent = archived ? "↶" : "○";
    action.setAttribute("aria-label", archived ? `Todo ${todo.title} wiederherstellen` : `Todo ${todo.title} abhaken`);
    action.title = archived ? "Wieder zu aktiven Aufgaben verschieben" : "Erledigt – ins Archiv verschieben";
    action.addEventListener("click", () => archived ? restoreTodo(todo.id) : archiveTodo(todo.id));
    const text = document.createElement("div"); text.className = "todo-text";
    const title = document.createElement("strong"); title.textContent = todo.title;
    const meta = document.createElement("small"); meta.textContent = archived ? `Archiviert · ${dueLabel(todo)}` : `${dueLabel(todo)} · ${todo.priority || "normal"}`;
    text.append(title, meta); main.append(action, text); row.appendChild(main); return row;
  }
  async function refreshTodos() {
    const root = $("todo-list");
    if (!projectAvailable()) { empty(root, "Nach der Projekteinrichtung können hier Aufgaben angelegt werden."); return; }
    try { const data = await api(`/api/todos?scope=${encodeURIComponent(state.scope)}`); state.todos = data.items || []; root.replaceChildren(); if (!state.todos.length) { empty(root, state.scope === "archive" ? "Das Todo-Archiv ist leer." : "Noch keine offenen Aufgaben."); return; } state.todos.forEach((todo) => root.appendChild(todoRow(todo, state.scope === "archive"))); }
    catch (error) { empty(root, `Todo-Daten konnten nicht geladen werden: ${error.message}`); App.log(error.message, "error"); }
  }
  async function refreshSummary() {
    if (!projectAvailable()) { $("metric-active").textContent = "0"; $("metric-archive").textContent = "0"; $("metric-backups").textContent = "0"; $("todo-archive-toggle").textContent = "Archiv (0)"; return; }
    try { state.summary = await api("/api/data/summary"); $("metric-active").textContent = String(state.summary.active_todos); $("metric-archive").textContent = String(state.summary.archived_todos); $("metric-backups").textContent = String(state.summary.backups); $("todo-archive-toggle").textContent = `Archiv (${state.summary.archived_todos})`; $("todo-due-today").textContent = state.summary.due_today ? `${state.summary.due_today} heute fällig` : "Heute nichts fällig"; $("todo-due-today").classList.toggle("warning-text", state.summary.due_today > 0); }
    catch (error) { App.log(`Organisationsstatus: ${error.message}`, "warn"); }
  }
  function shiftMonth(delta) { const [year, month] = state.month.split("-").map(Number); const date = new Date(year, month - 1 + delta, 1); state.month = monthKey(date); refreshCalendar(); }
  async function refreshCalendar() {
    if (!state.month) state.month = monthKey();
    if (!projectAvailable()) { renderCalendarGrid(state.month, {}); return; }
    try { state.calendar = await api(`/api/calendar?month=${encodeURIComponent(state.month)}`); renderCalendarGrid(state.calendar.month, state.calendar.days || {}); }
    catch (error) { renderCalendarGrid(state.month, {}); App.log(`Kalender: ${error.message}`, "warn"); }
  }
  function renderCalendarGrid(month, days) {
    const [year, monthNumber] = month.split("-").map(Number); const names = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]; $("calendar-label").textContent = `${names[monthNumber - 1]} ${year}`;
    const root = $("calendar"); root.replaceChildren(); ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"].forEach((name) => { const head = document.createElement("span"); head.className = "head"; head.textContent = name; root.appendChild(head); });
    const firstOffset = (new Date(year, monthNumber - 1, 1).getDay() + 6) % 7; for (let i = 0; i < firstOffset; i += 1) { const spacer = document.createElement("span"); spacer.className = "calendar-spacer"; root.appendChild(spacer); }
    const today = new Date(); const total = new Date(year, monthNumber, 0).getDate();
    for (let day = 1; day <= total; day += 1) { const iso = `${year}-${String(monthNumber).padStart(2, "0")}-${String(day).padStart(2, "0")}`; const items = days[iso] || []; const button = document.createElement("button"); button.type = "button"; button.className = "calendar-day"; button.setAttribute("aria-label", `${iso}${items.length ? `, ${items.length} Aufgabe(n)` : ""}`); if (year === today.getFullYear() && monthNumber === today.getMonth() + 1 && day === today.getDate()) button.classList.add("today"); if (items.length) button.classList.add("has-todo"); const number = document.createElement("span"); number.textContent = String(day); button.appendChild(number); if (items.length) { const count = document.createElement("b"); count.textContent = String(items.length); button.appendChild(count); } button.addEventListener("click", () => showDay(iso, items)); root.appendChild(button); }
  }
  function showDay(iso, items) { const wrap = document.createElement("div"); wrap.className = "workspace-stack"; const intro = document.createElement("div"); intro.className = "hero"; const body = document.createElement("div"); const h = document.createElement("h3"); const p = document.createElement("p"); h.textContent = `Termine am ${iso.split("-").reverse().join(".")}`; p.textContent = items.length ? `${items.length} aktive Aufgabe(n) sind für diesen Tag terminiert.` : "Für diesen Tag gibt es keine aktive terminierte Aufgabe."; body.append(h, p); intro.append(body); wrap.appendChild(intro); items.forEach((item) => wrap.appendChild(todoRow(item, false))); App.showWorkspace("Kalender", wrap); }
  async function createTodo(event) {
    event.preventDefault(); if (!projectAvailable()) { App.log("Bitte zuerst ein Projekt einrichten.", "warn"); $("setup-project").click(); return; }
    const title = $("todo-title").value; if (!title.trim()) { $("todo-state").textContent = "Bitte zuerst einen Aufgabentitel eingeben."; $("todo-title").focus(); return; }
    $("todo-state").textContent = "Speichert …";
    try { await api("/api/todos", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title, due_date: $("todo-date").value || null, due_time: $("todo-time").value || null, priority: $("todo-priority").value }) }); $("todo-title").value = ""; $("todo-date").value = ""; $("todo-time").value = ""; $("todo-state").textContent = "Gespeichert ✓"; state.scope = "active"; syncArchiveButton(); await refreshAll(); App.log("Todo gespeichert und Kalender aktualisiert.", "ok"); }
    catch (error) { $("todo-state").textContent = error.message; App.log(error.message, "error"); }
  }
  async function archiveTodo(id) { try { await api(`/api/todos/${id}/archive`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }); await refreshAll(); App.log("Todo abgehakt und sicher ins Archiv verschoben.", "ok"); } catch (error) { App.log(error.message, "error"); } }
  async function restoreTodo(id) { try { await api(`/api/todos/${id}/restore`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }); await refreshAll(); App.log("Todo aus dem Archiv wiederhergestellt.", "ok"); } catch (error) { App.log(error.message, "error"); } }
  function syncArchiveButton() { const button = $("todo-archive-toggle"); const archive = state.scope === "archive"; button.classList.toggle("active", archive); button.setAttribute("aria-pressed", String(archive)); }
  function toggleArchive() { state.scope = state.scope === "active" ? "archive" : "active"; syncArchiveButton(); refreshTodos(); }
  function openTodoWorkspace() { const wrap = document.createElement("div"); wrap.className = "workspace-stack"; const hero = document.createElement("div"); hero.className = "hero"; const icon = document.createElement("span"); icon.className = "hero-icon"; icon.textContent = "✓"; const body = document.createElement("div"); const h = document.createElement("h3"); const p = document.createElement("p"); h.textContent = "Todo & Terminierung"; p.textContent = "Bereich D ist die schnelle Aufgabenliste. Termine erscheinen automatisch im Monatskalender E. Abhaken archiviert reversibel statt zu löschen."; body.append(h, p); hero.append(icon, body); wrap.appendChild(hero); if (state.todos.length) state.todos.slice(0, 10).forEach((todo) => wrap.appendChild(todoRow(todo, state.scope === "archive"))); App.showWorkspace("Todo", wrap); }
  async function refreshAll() { await Promise.all([refreshTodos(), refreshCalendar(), refreshSummary()]); }
  function bind() { $("todo-form").addEventListener("submit", createTodo); $("todo-archive-toggle").addEventListener("click", toggleArchive); $("calendar-prev").addEventListener("click", () => shiftMonth(-1)); $("calendar-next").addEventListener("click", () => shiftMonth(1)); }
  function init() { state.month = monthKey(); bind(); syncArchiveButton(); refreshAll(); }
  return { init, refreshAll, openTodoWorkspace, state };
})();
window.DataUI = DataUI;
