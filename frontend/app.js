"use strict";
let currentFilter = "all";

function updateClock() {
  const ids = ["current-time", "header-clock"];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = new Date().toLocaleTimeString("en-IN", { hour12: false });
  });
}
setInterval(updateClock, 1000); updateClock();

async function fetchStats() {
  try {
    const data = await (await fetch("/api/stats")).json();
    const tEl = document.getElementById("stat-total");
    const aEl = document.getElementById("stat-animals");
    const fEl = document.getElementById("stat-fires");
    const wEl = document.getElementById("stat-weapons");
    const dEl = document.getElementById("stat-today");
    if (tEl) tEl.textContent = data.total   ?? "—";
    if (aEl) aEl.textContent = data.animals ?? "—";
    if (fEl) fEl.textContent = data.fires   ?? "—";
    if (wEl) wEl.textContent = data.weapons ?? "—";
    if (dEl) dEl.textContent = data.today   ?? "—";
  } catch(e) { console.warn("Stats error:", e); }
}
setInterval(fetchStats, 10000); fetchStats();

async function fetchEvents() {
  try {
    const p = new URLSearchParams({ limit: 50 });
    if (currentFilter !== "all") p.append("event_type", currentFilter);
    const data = await (await fetch(`/api/events?${p}`)).json();
    renderEvents(data.events);
  } catch(e) { console.warn("Events error:", e); }
}
setInterval(fetchEvents, 5000); fetchEvents();

function renderEvents(events) {
  const tbody = document.getElementById("events-body");
  if (!events || !events.length) {
    tbody.innerHTML = `<tr><td colspan="8" class="empty-row">No events detected yet.</td></tr>`;
    return;
  }
  tbody.innerHTML = events.map(e => {
    const BADGE = {
      animal: { cls: "badge-animal", label: "🐾 Animal" },
      fire:   { cls: "badge-fire",   label: "🔥 Fire"   },
      weapon: { cls: "badge-weapon", label: "🔫 Weapon" },
    };
    const bm   = BADGE[e.event_type] || { cls: "badge-animal", label: e.event_type };
    const pct  = Math.round(e.confidence * 100);
    const snap = e.snapshot_path
      ? `<img class="thumb-img" src="/api/snapshots/${e.snapshot_path}" alt="snap"
             onclick="openImageModal('/api/snapshots/${e.snapshot_path}','${e.label} Snapshot')">`
      : `<span style="color:var(--text-muted);font-size:.75rem">—</span>`;
    const vid  = e.video_path
      ? `<button class="btn-play" onclick="openVideoModal('/api/recordings/${e.video_path}','${e.label.charAt(0).toUpperCase()+e.label.slice(1)} — Event #${e.id}')">▶ Play</button>`
      : `<button class="btn-play" disabled>▶ Play</button>`;
    return `<tr>
      <td>${e.id}</td>
      <td><span class="badge ${bm.cls}">${bm.label}</span></td>
      <td><strong>${e.label.charAt(0).toUpperCase()+e.label.slice(1)}</strong></td>
      <td><div class="conf-bar-wrap"><div class="conf-bar"><div class="conf-fill" style="width:${pct}%"></div></div><span class="conf-text">${pct}%</span></div></td>
      <td>${e.camera_source}</td><td>${snap}</td><td>${vid}</td>
      <td class="time-cell">${formatTime(e.timestamp)}</td></tr>`;
  }).join("");
}

function setFilter(f) {
  currentFilter = f;
  document.querySelectorAll(".filter-btn").forEach(b => b.classList.toggle("active", b.dataset.filter === f));
  fetchEvents();
}

function openVideoModal(src, title) {
  document.getElementById("modal-title").textContent = title;
  document.getElementById("modal-video").src = src;
  document.getElementById("video-modal").classList.add("open");
}
function closeVideoModal() {
  const v = document.getElementById("modal-video");
  v.pause(); v.src = "";
  document.getElementById("video-modal").classList.remove("open");
}
function openImageModal(src, title) {
  document.getElementById("image-modal-title").textContent = title;
  document.getElementById("modal-image").src = src;
  document.getElementById("image-modal").classList.add("open");
}
function closeImageModal() { document.getElementById("image-modal").classList.remove("open"); }
function closeModal(e) { if (e.target.classList.contains("modal-overlay")) { closeVideoModal(); closeImageModal(); } }
document.addEventListener("keydown", e => { if (e.key === "Escape") { closeVideoModal(); closeImageModal(); } });

function formatTime(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-IN", { day:"2-digit", month:"short", hour:"2-digit", minute:"2-digit", second:"2-digit", hour12:false });
}
