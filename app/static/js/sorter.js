"use strict";
const SorterUI = (() => {
  const state = {
    jobId: null,
    pollTimer: null,
    task: null,
    offset: 0,
    limit: 50,
    total: 0,
    customRules: [],
    customSequence: 0,
    lastSummary: null,
  };
  const $ = (id) => document.getElementById(id);

  const CATEGORY_PRESETS = [
    ["Bilder", "Bilder", "🖼"],
    ["Video", "Videos", "🎬"],
    ["Audio", "Audio", "♫"],
    ["Dokumente", "Dokumente", "📄"],
    ["Archive", "Archive", "🗜"],
    ["Text / Code", "Text-Code", "⌨"],
  ];
  const DECISION_LABELS = {
    matched: "✓ Zugeordnet",
    conflict: "! Konflikt",
    unmatched: "○ Nicht zugeordnet",
    skipped: "↷ Übersprungen",
  };

  function el(tag, options = {}, children = []) {
    const node = document.createElement(tag);
    Object.entries(options).forEach(([key, value]) => {
      if (key === "className") node.className = value;
      else if (key === "text") node.textContent = value;
      else if (key === "htmlFor") node.htmlFor = value;
      else if (key.startsWith("data-")) node.setAttribute(key, value);
      else if (key in node) node[key] = value;
      else node.setAttribute(key, value);
    });
    (Array.isArray(children) ? children : [children]).filter(Boolean).forEach((child) => node.append(child));
    return node;
  }

  function ensureStyle() {
    if (document.querySelector('link[data-provoware-sorter="1"]')) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "/static/css/sorter.css";
    link.dataset.provowareSorter = "1";
    document.head.appendChild(link);
  }

  async function api(path, options = {}) {
    const response = await fetch(path, { cache: "no-store", ...options });
    let payload = {};
    try { payload = await response.json(); } catch { payload = {}; }
    if (!response.ok) {
      const error = new Error(payload.error || `Anfrage fehlgeschlagen (${response.status}).`);
      error.code = payload.code || "HTTP";
      error.status = response.status;
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  function jsonPost(path, body = {}) {
    return api(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }

  function formatBytes(value) {
    let bytes = Math.max(0, Number(value) || 0);
    const units = ["B", "KiB", "MiB", "GiB", "TiB"];
    let index = 0;
    while (bytes >= 1024 && index < units.length - 1) { bytes /= 1024; index += 1; }
    const digits = index === 0 ? 0 : bytes >= 100 ? 0 : bytes >= 10 ? 1 : 2;
    return `${bytes.toFixed(digits)} ${units[index]}`;
  }

  function buildStep(number, title, text) {
    const head = el("div", { className: "sorter-step-head" });
    const copy = el("div");
    copy.append(el("h3", { text: title }), el("p", { text }));
    head.append(el("span", { className: "sorter-step-no", text: String(number), "aria-hidden": "true" }), copy);
    return head;
  }

  function presetRule(category, target) {
    return {
      id: `standard-${category.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`,
      name: `${category} erkennen`,
      priority: 10,
      category,
      target_group: target,
      enabled: true,
    };
  }

  function collectRules() {
    const rules = [];
    document.querySelectorAll("[data-sorter-category]").forEach((checkbox) => {
      if (!checkbox.checked) return;
      rules.push(presetRule(checkbox.dataset.sorterCategory, checkbox.dataset.sorterTarget));
    });
    state.customRules.forEach((rule) => rules.push({ ...rule }));
    return rules;
  }

  function renderCustomRules() {
    const root = $("sorter-custom-list");
    if (!root) return;
    root.replaceChildren();
    if (!state.customRules.length) {
      root.append(el("span", { className: "sorter-empty", text: "Noch keine eigene Wortregel. Das ist optional." }));
      return;
    }
    state.customRules.forEach((rule) => {
      const chip = el("span", { className: "sorter-rule-chip" });
      chip.append(el("span", { text: `„${rule.contains_any.join(" / ")}“ → ${rule.target_group} · Vorrang ${rule.priority}` }));
      const remove = el("button", { type: "button", className: "icon-btn", text: "×", title: "Regel entfernen", ariaLabel: `Regel ${rule.name} entfernen` });
      remove.addEventListener("click", () => {
        state.customRules = state.customRules.filter((item) => item.id !== rule.id);
        renderCustomRules();
      });
      chip.append(remove);
      root.append(chip);
    });
  }

  function addCustomRule() {
    const words = $("sorter-word").value.split(",").map((item) => item.trim()).filter(Boolean);
    const target = $("sorter-word-target").value.trim();
    const priority = Number($("sorter-word-priority").value) || 100;
    if (!words.length || !target) {
      window.App?.log("Eigene Regel: Suchwort und Zielgruppe werden benötigt.", "warn");
      $("sorter-word").focus();
      return;
    }
    state.customSequence += 1;
    state.customRules.push({
      id: `wort-${state.customSequence}`,
      name: `Dateiname enthält ${words.join(" / ")}`,
      priority,
      contains_any: words,
      target_group: target,
      enabled: true,
    });
    $("sorter-word").value = "";
    $("sorter-word-target").value = "";
    renderCustomRules();
    window.App?.log(`Wortregel für ${target} hinzugefügt.`, "ok");
  }

  async function pickSource() {
    const button = $("sorter-pick-source");
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    try {
      const response = await fetch("/api/sorter/pick-source", { cache: "no-store" });
      const data = await response.json();
      if (response.ok && data.path) {
        $("sorter-source").value = data.path;
        window.App?.log("Quellordner ausgewählt. Noch wurde nichts analysiert oder verändert.", "ok");
      } else if (data.fallback) {
        $("sorter-source").value = data.fallback;
        window.App?.log("Grafische Ordnerwahl ist nicht verfügbar. Der vorgeschlagene Pfad kann geändert werden.", "warn");
      }
    } catch (error) {
      window.App?.log(error.message || "Ordnerauswahl konnte nicht geöffnet werden.", "warn");
    } finally {
      button.disabled = false;
      button.removeAttribute("aria-busy");
    }
  }

  function setControls(status) {
    const pause = $("sorter-pause"), resume = $("sorter-resume"), cancel = $("sorter-cancel");
    if (!pause || !resume || !cancel) return;
    pause.classList.toggle("sorter-hidden", status !== "running");
    resume.classList.toggle("sorter-hidden", !["paused", "interrupted"].includes(status));
    cancel.classList.toggle("sorter-hidden", !["queued", "running", "paused", "interrupted", "cancelling"].includes(status));
    cancel.disabled = status === "cancelling";
  }

  function statusText(job) {
    const map = {
      queued: "Wartet auf Start",
      running: "Analyse läuft",
      paused: "Pausiert",
      cancelling: "Abbruch wird sicher übernommen",
      cancelled: "Abgebrochen",
      completed: "Analyse abgeschlossen",
      failed: "Analyse fehlgeschlagen",
      interrupted: "Unterbrochen – Fortsetzen möglich",
    };
    return map[job?.status] || job?.status || "Bereit";
  }

  function updateJobBox(job, summary = null) {
    if (!job || !$("sorter-job-status")) return;
    $("sorter-job-status").textContent = statusText(job);
    const done = Number(job.progress_done) || 0;
    const bytes = Number(job.bytes_done) || 0;
    const detail = [`${done} Dateien erfasst`, formatBytes(bytes)].join(" · ");
    $("sorter-job-detail").textContent = `${detail} · Job ${job.id.slice(0, 8)}…`;
    setControls(job.status);
    if (summary) renderSummary(summary);
  }

  function renderSummary(summary) {
    state.lastSummary = summary;
    const root = $("sorter-summary");
    if (!root) return;
    const decisions = summary.decisions || {};
    const cards = [
      [summary.files || 0, "Dateien", "files"],
      [formatBytes(summary.bytes || 0), "Datenvolumen", "bytes"],
      [decisions.matched || 0, "Zugeordnet", "matched"],
      [decisions.conflict || 0, "Konflikte", "conflict"],
      [decisions.unmatched || 0, "Nicht zugeordnet", "unmatched"],
      [decisions.skipped || 0, "Übersprungen", "skipped"],
    ];
    root.replaceChildren();
    cards.forEach(([value, label, kind]) => {
      const card = el("article", { "data-kind": kind });
      card.append(el("strong", { text: String(value) }), el("span", { text: label }));
      root.append(card);
    });
  }

  function decisionBadge(decision) {
    return el("span", {
      className: "sorter-badge",
      "data-state": decision,
      text: DECISION_LABELS[decision] || decision,
    });
  }

  function renderPreview(page) {
    state.total = page.total || 0;
    const tbody = $("sorter-table-body");
    tbody.replaceChildren();
    if (!page.items?.length) {
      const row = el("tr");
      const cell = el("td", { colSpan: 6, className: "sorter-empty", text: "Für diesen Filter gibt es keine Einträge." });
      row.append(cell); tbody.append(row);
    } else {
      page.items.forEach((item) => {
        const row = el("tr");
        const status = el("td"); status.append(decisionBadge(item.decision));
        const file = el("td", { className: "file-cell" });
        file.append(el("strong", { text: item.name }), el("span", { className: "sorter-path", text: item.relative_path }));
        const type = el("td", { text: item.category || "Sonstige" });
        const size = el("td", { text: item.entry_kind === "file" ? formatBytes(item.size_bytes) : "–" });
        const target = el("td", { text: item.target_group || "–" });
        let reason = item.skip_reason || "";
        if (!reason && item.matches?.length) reason = item.matches.map((match) => match.name || match.id).join(", ");
        if (!reason && item.decision === "unmatched") reason = "Keine aktive Regel passt.";
        if (!reason && item.decision === "conflict") reason = "Gleich starke Regeln schlagen verschiedene Ziele vor.";
        const detail = el("td", { text: reason || "–" });
        row.append(status, file, type, size, target, detail);
        tbody.append(row);
      });
    }
    const start = state.total ? state.offset + 1 : 0;
    const end = Math.min(state.offset + state.limit, state.total);
    $("sorter-page-label").textContent = `${start}–${end} von ${state.total}`;
    $("sorter-prev").disabled = state.offset <= 0;
    $("sorter-next").disabled = state.offset + state.limit >= state.total;
  }

  async function loadPreview(reset = false) {
    if (!state.jobId) return;
    if (reset) state.offset = 0;
    const params = new URLSearchParams({ offset: String(state.offset), limit: String(state.limit) });
    const decision = $("sorter-filter-decision")?.value || "";
    const category = $("sorter-filter-category")?.value || "";
    if (decision) params.set("decision", decision);
    if (category) params.set("category", category);
    try {
      const page = await api(`/api/sorter/${state.jobId}/preview?${params.toString()}`);
      renderPreview(page);
    } catch (error) {
      window.App?.log(error.message || "Vorschau konnte nicht geladen werden.", "error");
    }
  }

  function stopPolling() {
    if (state.pollTimer) window.clearTimeout(state.pollTimer);
    state.pollTimer = null;
  }

  function finishTask(kind, message, detail) {
    if (state.task && !state.task.finished) state.task.end(kind, message, detail);
    state.task = null;
  }

  async function pollSummary() {
    if (!state.jobId) return;
    try {
      const summary = await api(`/api/sorter/${state.jobId}/summary`);
      const job = summary.job;
      updateJobBox(job, summary);
      const done = Number(job.progress_done) || 0;
      const total = Number(job.progress_total) || 0;
      const detail = `${done} Dateien · ${formatBytes(job.bytes_done || 0)} · Quelle bleibt unverändert`;
      if (state.task && !state.task.finished) state.task.update(total > 0 ? (done / total) * 100 : null, detail);

      if (job.status === "completed") {
        stopPolling();
        await loadPreview(true);
        const conflicts = Number(summary.decisions?.conflict) || 0;
        const skipped = Number(summary.decisions?.skipped) || 0;
        if (conflicts || skipped) {
          finishTask("warn", "Analyse abgeschlossen – bitte Hinweise prüfen.", `${conflicts} Konflikte · ${skipped} übersprungen · keine Datei verändert`);
        } else {
          finishTask("ok", "Analyse abgeschlossen.", `${summary.files || 0} Dateien geprüft · keine Datei verändert`);
        }
        return;
      }
      if (job.status === "paused") {
        stopPolling();
        finishTask("warn", "Analyse pausiert.", "Der gespeicherte Stand bleibt erhalten. Fortsetzen ist möglich.");
        return;
      }
      if (job.status === "interrupted") {
        stopPolling();
        finishTask("warn", "Analyse wurde unterbrochen.", "Checkpoint und bisherige Vorschau bleiben erhalten. Fortsetzen ist möglich.");
        return;
      }
      if (job.status === "cancelled") {
        stopPolling();
        finishTask("warn", "Analyse abgebrochen.", "Bereits erfasste Vorschau bleibt zur Diagnose erhalten. Keine Datei verändert.");
        await loadPreview(true);
        return;
      }
      if (job.status === "failed") {
        stopPolling();
        finishTask("error", "Analyse fehlgeschlagen.", job.error_message || "Fehlerdetails wurden protokolliert.");
        await loadPreview(true);
        return;
      }
      state.pollTimer = window.setTimeout(pollSummary, 500);
    } catch (error) {
      stopPolling();
      finishTask("error", "Scanstatus konnte nicht gelesen werden.", error.message || "Unbekannter Fehler");
    }
  }

  function beginPolling(label = "Dateien werden nur analysiert") {
    stopPolling();
    state.task = window.Feedback?.begin(label, "Die Quelldateien werden nicht verändert.") || null;
    pollSummary();
  }

  async function startScan() {
    const source = $("sorter-source").value.trim();
    if (!source) {
      window.App?.log("Bitte zuerst einen Quellordner wählen.", "warn");
      $("sorter-source").focus();
      return;
    }
    const button = $("sorter-start");
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    stopPolling();
    finishTask("warn", "Vorherige Statusbeobachtung beendet.", "Ein neuer read-only Scan wird vorbereitet.");
    try {
      const payload = await jsonPost("/api/sorter/scans", {
        source_path: source,
        recursive: $("sorter-recursive").checked,
        include_hidden: $("sorter-hidden-files").checked,
        rules: collectRules(),
      });
      state.jobId = payload.job.id;
      state.offset = 0;
      $("sorter-results").classList.remove("sorter-hidden");
      updateJobBox(payload.job);
      beginPolling("Dateien werden nur analysiert");
      window.App?.log("Read-only Analyse gestartet. Quelle wird nicht verändert.", "ok");
    } catch (error) {
      window.Feedback?.record("error", "Analyse konnte nicht gestartet werden.", error.message || "Unbekannter Fehler");
      window.App?.log(error.message || "Analyse konnte nicht gestartet werden.", "error", false);
    } finally {
      button.disabled = false;
      button.removeAttribute("aria-busy");
    }
  }

  async function control(action) {
    if (!state.jobId) return;
    const labels = { pause: "Pause wird angefordert", resume: "Analyse wird fortgesetzt", cancel: "Abbruch wird angefordert" };
    try {
      const payload = await jsonPost(`/api/sorter/${state.jobId}/${action}`, {});
      updateJobBox(payload.job, state.lastSummary);
      if (action === "resume") beginPolling("Analyse wird fortgesetzt");
      else if (!state.pollTimer) state.pollTimer = window.setTimeout(pollSummary, 100);
      window.App?.log(`${labels[action]}.`, action === "cancel" ? "warn" : "info");
    } catch (error) {
      window.App?.log(error.message || `${labels[action]} fehlgeschlagen.`, "error");
    }
  }

  function buildWorkspace() {
    const root = el("div", { className: "sorter-shell" });
    const safe = el("div", { className: "sorter-safe-banner", role: "status" });
    safe.append(el("span", { text: "🛡", "aria-hidden": "true" }), el("div", {}, [
      el("strong", { text: "Sichere Vorschau: Dieser Schritt verändert keine Datei." }),
      el("span", { text: "PROVOWARE liest nur Namen, Typ, Größe und Zeitstempel und speichert die Analyse im Projekt." }),
    ]));
    root.append(safe);

    const sourceStep = el("section", { className: "sorter-step" });
    sourceStep.append(buildStep(1, "Quellordner wählen", "Standardmäßig wird nur dieser Ordner geprüft – Unterordner erst nach ausdrücklicher Auswahl."));
    const sourceLine = el("div", { className: "sorter-source-line" });
    sourceLine.append(
      el("input", { id: "sorter-source", type: "text", placeholder: "z. B. /home/name/Downloads", ariaLabel: "Quellordner für die read-only Analyse" }),
      el("button", { id: "sorter-pick-source", type: "button", className: "btn", text: "📁 Ordner wählen" }),
    );
    sourceStep.append(sourceLine);
    const options = el("div", { className: "sorter-options" });
    const recursive = el("label", { className: "sorter-check" });
    recursive.append(el("input", { id: "sorter-recursive", type: "checkbox" }), el("span", { text: "Unterordner mit prüfen (optional)" }));
    const hidden = el("label", { className: "sorter-check profi-only" });
    hidden.append(el("input", { id: "sorter-hidden-files", type: "checkbox" }), el("span", { text: "Versteckte Inhalte mit anzeigen (Profi)" }));
    options.append(recursive, hidden);
    sourceStep.append(options, el("div", { className: "sorter-warning", text: "Symlinks sowie bekannte System-/Cachebereiche werden aus Sicherheitsgründen nicht verfolgt. Übersprungene Einträge erscheinen später mit Begründung." }));
    root.append(sourceStep);

    const rulesStep = el("section", { className: "sorter-step" });
    rulesStep.append(buildStep(2, "Sortierregeln auswählen", "Die Standardgruppen sind bereits vorbereitet. Eigene Wortregeln sind optional und haben auf Wunsch höheren Vorrang."));
    const grid = el("div", { className: "sorter-rule-grid" });
    CATEGORY_PRESETS.forEach(([category, target, icon]) => {
      const label = el("label", { className: "sorter-rule-preset" });
      const checkbox = el("input", { type: "checkbox", checked: true });
      checkbox.dataset.sorterCategory = category;
      checkbox.dataset.sorterTarget = target;
      label.append(checkbox, el("span", {}, [el("strong", { text: `${icon} ${category}` }), el("small", { text: `→ ${target}` })]));
      grid.append(label);
    });
    rulesStep.append(grid);
    const custom = el("div", { className: "sorter-custom-form" });
    custom.append(
      el("label", {}, [el("span", { text: "Wenn Dateiname enthält" }), el("input", { id: "sorter-word", type: "text", placeholder: "z. B. suno, mixdown" })]),
      el("label", {}, [el("span", { text: "Dann Zielgruppe" }), el("input", { id: "sorter-word-target", type: "text", placeholder: "z. B. Suno" })]),
      el("label", {}, [el("span", { text: "Vorrang" }), el("select", { id: "sorter-word-priority" }, [
        el("option", { value: "50", text: "Hoch" }),
        el("option", { value: "100", text: "Sehr hoch", selected: true }),
        el("option", { value: "200", text: "Höchste" }),
      ])]),
      el("button", { id: "sorter-add-rule", type: "button", className: "btn sorter-add-rule", text: "＋ Wortregel" }),
    );
    rulesStep.append(custom, el("div", { id: "sorter-custom-list", className: "sorter-custom-list" }));
    root.append(rulesStep);

    const startStep = el("section", { className: "sorter-step" });
    startStep.append(buildStep(3, "Nur analysieren und Vorschau erstellen", "Keine Datei wird verschoben, kopiert, umbenannt oder gelöscht."));
    const startRow = el("div", { className: "sorter-start-row" });
    startRow.append(el("button", { id: "sorter-start", type: "button", className: "btn primary", text: "🔎 Nur analysieren – nichts verändern" }), el("small", { className: "muted", text: "Der Scan kann pausiert oder abgebrochen werden." }));
    startStep.append(startRow);
    root.append(startStep);

    const results = el("section", { id: "sorter-results", className: "sorter-step sorter-hidden" });
    results.append(buildStep(4, "Ergebnis prüfen", "Konflikte und übersprungene Dateien bleiben sichtbar. Noch gibt es bewusst keinen Ausführen-Button."));
    const jobbar = el("div", { className: "sorter-jobbar" });
    const jobstate = el("div", { className: "sorter-jobstate" });
    jobstate.append(el("strong", { id: "sorter-job-status", text: "Bereit" }), el("small", { id: "sorter-job-detail", text: "Noch kein Scan gestartet." }));
    const controls = el("div", { className: "sorter-controls" });
    controls.append(
      el("button", { id: "sorter-pause", type: "button", className: "btn tiny sorter-hidden", text: "Ⅱ Pause" }),
      el("button", { id: "sorter-resume", type: "button", className: "btn tiny sorter-hidden", text: "▶ Weiter" }),
      el("button", { id: "sorter-cancel", type: "button", className: "btn tiny sorter-hidden", text: "■ Abbrechen" }),
    );
    jobbar.append(jobstate, controls);
    results.append(jobbar, el("div", { id: "sorter-summary", className: "sorter-summary" }));

    const filters = el("div", { className: "sorter-filters" });
    const decision = el("select", { id: "sorter-filter-decision" }, [
      el("option", { value: "", text: "Alle Ergebnisse" }),
      el("option", { value: "matched", text: "Nur zugeordnet" }),
      el("option", { value: "conflict", text: "Nur Konflikte" }),
      el("option", { value: "unmatched", text: "Nur nicht zugeordnet" }),
      el("option", { value: "skipped", text: "Nur übersprungen" }),
    ]);
    const category = el("select", { id: "sorter-filter-category" }, [el("option", { value: "", text: "Alle Dateitypen" })]);
    ["Bilder", "Video", "Audio", "Dokumente", "Archive", "Text / Code", "Sonstige"].forEach((item) => category.append(el("option", { value: item, text: item })));
    filters.append(el("label", {}, [el("span", { text: "Status filtern" }), decision]), el("label", {}, [el("span", { text: "Dateityp filtern" }), category]), el("button", { id: "sorter-refresh-preview", type: "button", className: "btn", text: "↻ Aktualisieren" }));
    results.append(filters);

    const tableWrap = el("div", { className: "sorter-table-wrap" });
    const table = el("table", { className: "sorter-table" });
    const head = el("thead");
    const headRow = el("tr");
    ["Status", "Datei", "Typ", "Größe", "Vorgeschlagenes Ziel", "Warum?"].forEach((label) => headRow.append(el("th", { text: label, scope: "col" })));
    head.append(headRow);
    table.append(head, el("tbody", { id: "sorter-table-body" }));
    tableWrap.append(table);
    results.append(tableWrap);

    const pager = el("div", { className: "sorter-pager" });
    pager.append(el("span", { id: "sorter-page-label", className: "muted", text: "0–0 von 0" }));
    const pagerActions = el("div", { className: "sorter-pager-actions" });
    pagerActions.append(el("button", { id: "sorter-prev", type: "button", className: "btn tiny", text: "‹ Zurück", disabled: true }), el("button", { id: "sorter-next", type: "button", className: "btn tiny", text: "Weiter ›", disabled: true }));
    pager.append(pagerActions);
    results.append(pager);
    root.append(results);
    return root;
  }

  function bindWorkspace() {
    $("sorter-pick-source").addEventListener("click", pickSource);
    $("sorter-add-rule").addEventListener("click", addCustomRule);
    $("sorter-word").addEventListener("keydown", (event) => { if (event.key === "Enter") { event.preventDefault(); addCustomRule(); } });
    $("sorter-start").addEventListener("click", startScan);
    $("sorter-pause").addEventListener("click", () => control("pause"));
    $("sorter-resume").addEventListener("click", () => control("resume"));
    $("sorter-cancel").addEventListener("click", () => control("cancel"));
    $("sorter-refresh-preview").addEventListener("click", () => loadPreview(true));
    $("sorter-filter-decision").addEventListener("change", () => loadPreview(true));
    $("sorter-filter-category").addEventListener("change", () => loadPreview(true));
    $("sorter-prev").addEventListener("click", () => { state.offset = Math.max(0, state.offset - state.limit); loadPreview(false); });
    $("sorter-next").addEventListener("click", () => { if (state.offset + state.limit < state.total) { state.offset += state.limit; loadPreview(false); } });
    renderCustomRules();
  }

  async function openWorkspace() {
    ensureStyle();
    const project = window.App?.state?.bootstrap?.project;
    if (!project?.available) {
      const root = el("div", { className: "sorter-shell" });
      root.append(el("div", { className: "sorter-safe-banner" }, [el("span", { text: "🟡" }), el("div", {}, [
        el("strong", { text: "Zuerst ein Projekt einrichten" }),
        el("span", { text: "Die Analyse braucht ein gültiges PROVOWARE-Projekt, damit Scanstatus und Vorschau sicher gespeichert werden können." }),
      ])]));
      const button = el("button", { type: "button", className: "btn primary", text: "Projekt einrichten" });
      button.addEventListener("click", () => $("setup-project")?.click());
      root.append(button);
      window.App?.showWorkspace("Dateien · sichere Vorschau", root);
      return;
    }
    const workspace = buildWorkspace();
    window.App?.showWorkspace("Dateien · sichere Vorschau", workspace);
    bindWorkspace();
    window.App?.log("Dateien-Modul geöffnet: read-only Analyse, keine Dateiänderung.", "info");
  }

  return { openWorkspace, formatBytes, state };
})();
window.SorterUI = SorterUI;
