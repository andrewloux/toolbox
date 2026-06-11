const fs = require("fs");
const FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html";
let s = fs.readFileSync(FILE, "utf8");
let ok = 0, miss = [];
const rep = (o, n, tag) => {
  const i = s.indexOf(o);
  if (i === -1) { miss.push(tag); return; }
  if (s.indexOf(o, i + 1) !== -1) { miss.push(tag + " (NOT UNIQUE)"); return; }
  s = s.replace(o, n); ok++;
};

const RFC = "https://fluidstack.atlassian.net/wiki/spaces/RE/pages/607617031";

// A: anatomy location field — ticket's own bullet list, verbatim-condensed; all glosses out
rep('<span class="al">【Physical Location Details】</span><span class="av">rack r0109b · mach9 ICI port 12 · patch panel r8-pp-2 (MP24-2 — the panel-module designation tickets use; by its shape, a 24-fiber MPO (multi-fiber push-on) module slot — the locator grammar is panel · module · port) port 18B · OCS 16N. <i>Page note, not ticket text:</i> the ticket speaks two location vocabularies — the entity ref\'s logical <span style="font-family:var(--mono);font-size:.9em">rack8</span> and the floor locator <span style="font-family:var(--mono);font-size:.9em">r0109b</span> name the same place; mapping between them is exactly the location-resolution job described here</span>',
  '<span class="al">【Physical Location Details】</span><span class="av">Rack: buf101-pod1-rack8 (r0109b) · Machine: mach9, ICI Port 12 · Patch Panel: r8-pp-2 (MP24-2) · MP24 Port: 18B · OCS Port: buf101-pod1-spocs3-ocs1:16N</span>',
  "A-location-field");

// B: relocated glosses land in the (location) mapping row
rep('<b>Derivable — shouldn\'t ride in the request.</b> Patch-panel/port mapping is FS inventory truth; the API resolves it from the entity ref.',
  '<b>Derivable — shouldn\'t ride in the request.</b> Patch-panel/port mapping is FS inventory truth; the API resolves it from the entity ref. The ticket does that resolution by hand — “Rack: buf101-pod1-rack8 (r0109b)” writes the logical name and the floor locator side by side. Decoder: MP24-2 names the patch panel\'s module (by shape, a 24-fiber MPO — multi-fiber push-on — slot); the locator grammar is panel · module · port.',
  "B-location-row");

// C: 01·B batch + coalescing status marker
rep('and storm-shaped load gets batch + coalescing as first-class verbs.',
  'and storm-shaped load gets batch + coalescing as first-class verbs — two of the create-path planks this page proposes; uncontested in the working plan, decided nowhere read (status gathered at <a href="#timeline">05</a>).',
  "C-batch-status");

// D: 01·C correlation/dedupe row — status + RFC receipt + upstream key-shape corroboration
rep('Plus coalescing on <span style="font-family:var(--mono);font-size:.9em">(entity, problem_code)</span>. Today “history” is otherwise a prose pointer at a prior ticket (15133).',
  'Plus coalescing on <span style="font-family:var(--mono);font-size:.9em">(entity, problem_code)</span> — the key shape FS\'s draft event-correlation engine already dedups on upstream (<span style="font-family:var(--mono);font-size:.9em">(topology_key, root_cause)</span>, 10-minute window). Today “history” is otherwise a prose pointer at a prior ticket (15133). Both are page planks, not settled contract — uncontested, hence no d-row; and the key contract has a caller waiting: <a href="' + RFC + '" target="_blank" rel="noreferrer">SRE-RFC-0012</a> plans to submit with a UUID idempotency key and lists “Does the existing Repair Pipeline API accept an external idempotency key on ingest, or does it generate its own?” as open — resolution pending API review.',
  "D-dedupe-row");

// E: 01·D cf_14593 kv — page-spec framing + RFC receipt
rep('<span class="m">cf_14593</span> is a UUID on 657 of 1,112 human tickets, mapped in dcim-tasks\' Jira schema — the API adopts it as the create-side idempotency/dedup key rather than inventing one.</p></div>',
  '<span class="m">cf_14593</span> is a UUID on 657 of 1,112 human tickets, mapped in dcim-tasks\' Jira schema — this page specs it as the create-side idempotency/dedup key rather than inventing one (uncontested; status gathered at <a href="#timeline">05</a>). An internal caller is already queued on that contract: <a href="' + RFC + '" target="_blank" rel="noreferrer">SRE-RFC-0012 ↗</a> asks whether the repair-pipeline ingest accepts an external idempotency key — “Resolution: Pending API review.”</p></div>',
  "E-cf14593-kv");

// F: §05 slede — planks are proposals; RFC claimant noted at the ledger
rep('uncontested in the working plan: no voice read disputes them, so they carry no d-row. Click any row',
  'uncontested in the working plan: no voice read disputes them, so they carry no d-row — they are this page\'s proposals, not decided contract. The idempotency plank already has an internal claimant: <a href="' + RFC + '" target="_blank" rel="noreferrer">SRE-RFC-0012</a> (FS\'s event-correlation engine, draft under review) waits on exactly that key contract, “pending API review.” Click any row',
  "F-ledger");

fs.writeFileSync(FILE, s);
console.log("ok:", ok, "miss:", miss);
const m = s.match(/<script>([\s\S]*)<\/script>/);
try { new Function(m[1]); console.log("JS parses OK"); } catch (e) { console.log("JS ERROR:", e.message); }
// EVENTS raw-anchor audit
const ev = s.match(/const EVENTS\s*=\s*\[([\s\S]*?)\n\];/);
if (ev) console.log("EVENTS raw <a tags:", (ev[1].match(/<a /g) || []).length === (ev[1].match(/links\s*:/g) ? 0 : 0) ? "audit n/a" : "check");
const evBad = ev && /(title|summary|detail)\s*:\s*"[^"]*<a /.test(ev[1]);
console.log("EVENTS html-in-string violation:", evBad ? "YES — FIX" : "none");
