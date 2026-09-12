"use strict";
const Feedback = (() => {
  const jobs = new Map();
  const $ = (id) => document.getElementById(id);
  const icons = { ok: "🟢", info: "🔵", warn: "🟡", error: "🔴", skipped: "⚪", busy: "⏳" };

  function announce(message) {
    const live = $("global-live");
    if (!live) return;
    live.textContent = "";
    requestAnimationFrame(() => { live.textContent = message; });
  }

  function setGlobal(kind, label, detail = "") {
    const root = $("global-process");
    if (!root) return;
    root.dataset.status = kind;
    $("global-process-icon").textContent = icons[kind] || icons.info;
    $("global-process-label").textContent = label;
    $("global-process-detail").textContent = detail;
    announce(`${label}. ${detail}`.trim());
  }

  function counters(values = {}) {
    for (const key of ["ok", "warn", "error", "skipped"]) {
      if (values[key] !== undefined) $(`global-count-${key}`).textContent = String(values[key]);
    }
  }

  function begin({ id, label, total = null, detail = "", counts = {} }) {
    const job = { id, label, total, done: 0, counts: { ok: 0, warn: 0, error: 0, skipped: 0, ...counts } };
    jobs.set(id, job);
    const track = $("global-progress-track");
    track.classList.remove("hidden");
    track.classList.toggle("indeterminate", !(Number.isFinite(total) && total > 0));
    $("global-progress-bar").style.width = "0%";
    $("global-progress-percent").textContent = Number.isFinite(total) && total > 0 ? "0 %" : "läuft";
    counters(job.counts);
    setGlobal("busy", label, detail || "Vorgang läuft …");
    return id;
  }

  function progress(id, { done, total, detail, counts } = {}) {
    const job = jobs.get(id);
    if (!job) return;
    if (Number.isFinite(total)) job.total = total;
    if (Number.isFinite(done)) job.done = done;
    if (counts) job.counts = { ...job.counts, ...counts };
    const determinate = Number.isFinite(job.total) && job.total > 0;
    $("global-progress-track").classList.toggle("indeterminate", !determinate);
    if (determinate) {
      const percent = Math.max(0, Math.min(100, Math.round((job.done / job.total) * 100)));
      $("global-progress-bar").style.width = `${percent}%`;
      $("global-progress-percent").textContent = `${percent} %`;
    } else {
      $("global-progress-percent").textContent = "läuft";
    }
    counters(job.counts);
    if (detail) $("global-process-detail").textContent = detail;
  }

  function finish(id, { kind = "ok", message = "Abgeschlossen", detail = "", counts } = {}) {
    const job = jobs.get(id);
    if (job && counts) job.counts = { ...job.counts, ...counts };
    if (job) counters(job.counts);
    jobs.delete(id);
    $("global-progress-track")?.classList.add("hidden");
    setGlobal(kind, message, detail);
    toast(message, kind, detail);
  }

  function toast(message, kind = "info", detail = "") {
    const root = $("toast-stack");
    if (!root) return;
    const item = document.createElement("div");
    item.className = `toast status-${kind}`;
    item.setAttribute("role", kind === "error" ? "alert" : "status");
    const icon = document.createElement("span");
    icon.textContent = icons[kind] || icons.info;
    const text = document.createElement("div");
    const strong = document.createElement("strong");
    strong.textContent = message;
    text.appendChild(strong);
    if (detail) {
      const small = document.createElement("small");
      small.textContent = detail;
      text.appendChild(small);
    }
    item.append(icon, text);
    root.prepend(item);
    while (root.children.length > 4) root.lastElementChild.remove();
    setTimeout(() => item.remove(), kind === "error" ? 9000 : 4500);
  }

  async function busy(button, work, label = "Bitte warten …") {
    if (!button) return work();
    const previous = button.textContent;
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    button.textContent = label;
    try { return await work(); }
    finally {
      button.disabled = false;
      button.removeAttribute("aria-busy");
      button.textContent = previous;
    }
  }

  function skipped(reason, current = null) {
    const value = current ?? Number($("global-count-skipped")?.textContent || 0);
    counters({ skipped: value + 1 });
    toast("Übersprungen", "skipped", reason || "Kein Grund angegeben.");
  }

  return { announce, setGlobal, counters, begin, progress, finish, toast, busy, skipped };
})();
window.Feedback = Feedback;
