const TRACKS = {
  all:      { label: "All" },
  history:  { label: "History",        dot: "#EDEDED", fg: "#cfcfcf", bg: "rgba(255,255,255,.08)" },
  plan:     { label: "Plan",           dot: "#A8E05F", fg: "#A8E05F", bg: "rgba(168,224,95,.12)" },
  decision: { label: "Open decisions", dot: "#F2C462", fg: "#F2C462", bg: "rgba(242,196,98,.12)" },
};

// ─── STATE + RENDER ─────────────────────────────────────────────────────────
const state = { track: "all", q: "", open: new Set() };
const $tl = document.getElementById("tl");
const $tbar = document.getElementById("tbar");
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const fmt = (s) => esc(s).replace(/`([^`]+)`/g, '<span class="m">$1</span>');
const monthLabel = (k) => new Date(k + "-02T00:00:00").toLocaleString("en", { month: "long", year: "numeric" });

function renderBar() {
  const counts = { all: EVENTS.length, history: 0, plan: 0, decision: 0 };
  EVENTS.forEach((e) => counts[e.track]++);
  $tbar.innerHTML = Object.entries(TRACKS).map(([k, t]) =>
    `<button class="pill${state.track === k ? " on" : ""}" data-track="${k}">${t.label}<span class="c">${counts[k]}</span></button>`
  ).join("") + `<input id="tq" placeholder="search…" value="${esc(state.q)}" aria-label="search timeline">`;
}

function renderTL() {
  const q = state.q.trim().toLowerCase();
  const filtered = EVENTS
    .filter((e) => state.track === "all" || e.track === state.track)
    .filter((e) => !q || (e.title + " " + e.summary + " " + e.detail).toLowerCase().includes(q))
    .sort((a, b) => a.date.localeCompare(b.date));
  const groups = new Map();
  for (const e of filtered) {
    const k = e.date.slice(0, 7);
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(e);
  }
  if (!filtered.length) { $tl.innerHTML = `<p class="empty">No events match.</p>`; return; }
  $tl.innerHTML = [...groups.entries()].map(([month, evs]) => `
    <div class="mon">${monthLabel(month)}</div>
    <div class="rail">${evs.map((e) => {
      const t = TRACKS[e.track], isOpen = state.open.has(e.id);
      return `<div class="ev${isOpen ? " open" : ""}" id="ev-${e.id}">
        <span class="dot" style="background:${t.dot}"></span>
        <button data-ev="${e.id}" aria-expanded="${isOpen}">
          <span class="top"><span class="chev">▸</span><span class="dt">${esc(e.dateLabel)}</span>
            <span class="bdg" style="color:${t.fg};background:${t.bg}">${t.label}</span>
            ${e.track === "decision" ? `<span class="evid">${e.id}</span>` : ""}
            ${e.status && e.status !== "open" ? `<span class="stat">${e.status}</span>` : ""}
            <span class="tt">${fmt(e.title)}</span></span>
          <span class="sm">${fmt(e.summary)}</span>
        </button>
        ${isOpen ? `<div class="exp">
          <p>${fmt(e.detail)}</p>
          <div class="si"><span class="sk">Spec impact</span><p>${fmt(e.specImpact)}</p></div>
          ${e.links.length ? `<div class="lk">${e.links.map((l) =>
            `<a href="${esc(l.url)}"${l.url.startsWith("#") ? "" : ` target="_blank" rel="noreferrer"`}>↗ ${esc(l.label)}</a>`).join("")}</div>` : ""}
        </div>` : ""}
      </div>`;
    }).join("")}</div>`).join("");
}

$tbar.addEventListener("click", (ev) => {
  const b = ev.target.closest("[data-track]");
  if (!b) return;
  state.track = b.dataset.track;
  renderBar(); renderTL();
  document.getElementById("tq").focus();
});
$tbar.addEventListener("input", (ev) => {
  if (ev.target.id !== "tq") return;
  state.q = ev.target.value;
  renderTL();
});
$tl.addEventListener("click", (ev) => {
  const b = ev.target.closest("[data-ev]");
  if (!b || ev.target.closest("a")) return;
  const id = b.dataset.ev;
  state.open.has(id) ? state.open.delete(id) : state.open.add(id);
  renderTL();
});
function openEvFromHash() {
  const m = location.hash.match(/^#ev-(.+)$/);
  if (!m) return;
  const e = EVENTS.find((x) => x.id === m[1]);
  if (!e) return;
  if (state.track !== "all" && state.track !== e.track) { state.track = "all"; renderBar(); }
  state.open.add(e.id); renderTL();
  setTimeout(() => {
    const el = document.getElementById("ev-" + e.id);
    if (el) el.scrollIntoView({ block: "center" });
  }, 50);
}
window.addEventListener("hashchange", openEvFromHash);

// ─── seam toggle ────────────────────────────────────────────────────────────
const bToday = document.getElementById("b-today"), bApi = document.getElementById("b-api");
const dToday = document.getElementById("d-today"), dApi = document.getElementById("d-api");
function seam(which) {
  const api = which === "api";
  bToday.classList.toggle("on", !api); bApi.classList.toggle("on", api);
  dToday.hidden = api; dApi.hidden = !api;
}
bToday.addEventListener("click", () => seam("today"));
bApi.addEventListener("click", () => seam("api"));

// ─── reading progress + nav scrollspy ───────────────────────────────────────
const $prog = document.getElementById("prog");
const spyTargets = [...document.querySelectorAll("nav a[href^='#']")]
  .map((a) => [a, document.querySelector(a.getAttribute("href"))])
  .filter(([, s]) => s);
function onScrollSpy() {
  const max = document.documentElement.scrollHeight - innerHeight;
  $prog.style.width = (max > 0 ? (scrollY / max) * 100 : 0) + "%";
  let cur = null;
  for (const [a, s] of spyTargets) if (s.getBoundingClientRect().top <= 130) cur = a;
  spyTargets.forEach(([a]) => a.classList.toggle("act", a === cur));
}
addEventListener("scroll", onScrollSpy, { passive: true });

renderBar(); renderTL(); onScrollSpy(); openEvFromHash();

// ─── back-trail ── labeled return after in-page jumps ───────────────────────
// Completes the browser's native history rather than competing with it: every
// in-page hash click already pushes a real entry; we stamp the *origin* entry
// with exact view state (scroll, open drills, seam tab, timeline filters) via
// replaceState, and surface history.back() as a labeled chip. Drill opens are
// deliberately NOT history entries — ✕ is panel state, back is spatial.
(() => {
  const chip = document.createElement("button");
  chip.id = "backchip"; chip.type = "button"; chip.hidden = true;
  document.body.appendChild(chip);
  chip.addEventListener("click", () => history.back());

  const secLabel = () => {
    let cur = null;
    for (const [a, s] of spyTargets) if (s.getBoundingClientRect().top <= 130) cur = a;
    if (!cur) return "the top";
    const b = cur.querySelector("b");
    return b ? `${b.textContent} · ${cur.textContent.slice(b.textContent.length)}` : cur.textContent;
  };
  const capture = () => ({
    y: scrollY,
    drills: [...document.querySelectorAll("g[data-d].sel")].map((g) => g.dataset.d),
    seam: bApi.classList.contains("on") ? "api" : "today",
    track: state.track, q: state.q, open: [...state.open],
    label: secLabel(),
  });
  const trailOf = () => (history.state && history.state.mvTrail) || [];
  const paint = () => {
    const t = trailOf();
    chip.hidden = !t.length;
    if (t.length) chip.textContent = `← back · ${t[t.length - 1]}`;
  };
  const restore = (r) => {
    seam(r.seam);
    state.track = r.track; state.q = r.q; state.open = new Set(r.open);
    renderBar(); renderTL();
    for (const id of r.drills) {
      const g = document.querySelector(`g[data-d="${id}"]`);
      if (!g || g.classList.contains("sel")) continue;
      const blk = g.closest(".vizblk");
      blk.querySelectorAll("g[data-d].sel").forEach((n) => n.classList.remove("sel"));
      g.classList.add("sel");
      renderDrill(blk.querySelector(".npanel"), id);
    }
    const go = () => scrollTo(0, r.y);
    go(); setTimeout(go, 120); // outlast openEvFromHash's centered scrollIntoView
  };

  history.replaceState({ mvTrail: trailOf() }, ""); // depth 0 on the load entry
  let pendingTrail = null;
  document.addEventListener("click", (ev) => {
    if (ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
    const a = ev.target.closest('a[href^="#"]');
    if (!a || a.getAttribute("href") === location.hash) return;
    const r = capture();
    history.replaceState({ mvBack: r, mvTrail: trailOf() }, "");
    pendingTrail = [...trailOf(), r.label];
  });
  addEventListener("hashchange", () => {
    if (pendingTrail) { history.replaceState({ mvTrail: pendingTrail }, ""); pendingTrail = null; }
    paint();
  });
  addEventListener("popstate", (ev) => {
    const s = ev.state || {};
    if (s.mvBack) restore(s.mvBack);
    paint();
  });
  paint();
})();
