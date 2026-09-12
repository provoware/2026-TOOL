"use strict";
const Feedback = (() => {
  const state = { active: 0, warnings: 0, errors: 0, sequence: 0 };
  const $ = (id) => document.getElementById(id);

  function stamp() {
    return new Intl.DateTimeFormat("de-DE", { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(new Date());
  }

  function setCounters() {
    const warning = $("warning-count");
    const error = $("error-count");
    if (warning) warning.textContent = `🟡 ${state.warnings}`;
    if (error) error.textContent = `🔴 ${state.errors}`;
  }

  function setProcess(kind, label, detail = "", percent = null) {
    const center = $("process-center");
    if (!center) return;
    center.dataset.status = kind;
    const icon = $("process-icon");
    const title = $("process-label");
    const info = $("process-detail");
    const progress = $("process-progress");
    const icons = { ready: "●", busy: "↻", ok: "✓", warn: "!", error: "×" };
    icon.textContent = icons[kind] || "●";
    title.textContent = label;
    info.textContent = detail;
    if (percent === null) {
      progress.removeAttribute("value");
      progress.setAttribute("aria-label", `${label}: läuft`);
    } else {
      const value = Math.max(0, Math.min(100, Number(percent) || 0));
      progress.value = value;
      progress.setAttribute("aria-label", `${label}: ${Math.round(value)} Prozent`);
    }
  }

  function toast(kind, message) {
    const region = $("toast-region");
    if (!region || !message) return;
    const item = document.createElement("div");
    item.className = `toast toast-${kind}`;
    item.setAttribute("role", kind === "error" ? "alert" : "status");
    const icon = document.createElement("span");
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = kind === "ok" ? "✓" : kind === "warn" ? "!" : "×";
    const text = document.createElement("span");
    text.textContent = message;
    item.append(icon, text);
    region.appendChild(item);
    while (region.children.length > 3) region.firstElementChild.remove();
    window.setTimeout(() => item.remove(), 5500);
  }

  function record(kind, message, detail = "") {
    if (kind === "warn") state.warnings += 1;
    if (kind === "error") state.errors += 1;
    setCounters();
    const normalized = kind === "info" ? "ready" : kind;
    setProcess(normalized, message, detail || `Letzte Rückmeldung · ${stamp()}`, 100);
    if (["ok", "warn", "error"].includes(kind)) toast(kind, message);
  }

  function begin(label, detail = "") {
    const id = ++state.sequence;
    state.active += 1;
    setProcess("busy", label, detail || "Vorgang läuft …", null);
    let finished = false;
    return {
      id,
      get finished() { return finished; },
      update(percent, nextDetail = detail) {
        if (!finished) setProcess("busy", label, nextDetail || "Vorgang läuft …", percent);
      },
      end(kind = "ok", message = label, nextDetail = "") {
        if (finished) return;
        finished = true;
        state.active = Math.max(0, state.active - 1);
        record(kind, message, nextDetail);
      },
    };
  }

  async function run(button, label, operation) {
    const task = begin(label);
    if (button) {
      button.disabled = true;
      button.setAttribute("aria-busy", "true");
    }
    try {
      const result = await operation(task);
      task.end("ok", `${label} abgeschlossen.`);
      return result;
    } catch (error) {
      task.end("error", error?.message || `${label} ist fehlgeschlagen.`);
      throw error;
    } finally {
      if (button) {
        button.disabled = false;
        button.removeAttribute("aria-busy");
      }
    }
  }

  function ready(message = "Bereit") {
    setProcess("ready", message, "Keine Aktion läuft.", 100);
    setCounters();
  }

  return { begin, run, record, ready, state };
})();
window.Feedback = Feedback;
window.addEventListener("DOMContentLoaded", () => Feedback.ready());
