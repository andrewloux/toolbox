
const escq = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
function renderDrill(host, id) {
  const d = DRILL[id];
  host.innerHTML = `<div class="np">
    <div class="np-h"><span class="np-k">${d.k}</span><button class="np-x" aria-label="close">✕</button></div>
    <div class="np-t">${d.t}</div>
    <div class="np-b">${d.body}</div>
    ${d.facts ? `<div class="np-f">${d.facts.map(f => `<div class="fr"><span class="fl">${f.l}</span><span class="fv">${f.v}</span></div>`).join("")}</div>` : ""}
    ${d.links ? `<div class="np-l">${d.links.map(l => `<a href="${escq(l.url)}"${l.url.startsWith("#") ? "" : ` target="_blank" rel="noreferrer"`}>↗ ${escq(l.label)}</a>`).join("")}</div>` : ""}
  </div>`;
  host.classList.add("on");
  if (host.getBoundingClientRect().top > innerHeight - 160) host.scrollIntoView({ block: "nearest", behavior: "smooth" });
}
document.addEventListener("click", (ev) => {
  const x = ev.target.closest(".np-x");
  if (x) {
    const p = x.closest(".npanel"); p.classList.remove("on"); p.innerHTML = "";
    p.closest(".vizblk").querySelectorAll("g[data-d].sel").forEach((n) => n.classList.remove("sel"));
    return;
  }
  const g = ev.target.closest("g[data-d]");
  if (!g) return;
  const blk = g.closest(".vizblk");
  const host = blk.querySelector(".npanel");
  const already = g.classList.contains("sel");
  blk.querySelectorAll("g[data-d].sel").forEach((n) => n.classList.remove("sel"));
  if (already) { host.classList.remove("on"); host.innerHTML = ""; return; }
  g.classList.add("sel");
  renderDrill(host, g.dataset.d);
});

