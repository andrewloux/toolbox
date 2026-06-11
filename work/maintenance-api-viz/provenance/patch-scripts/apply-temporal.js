const fs = require("fs");
const FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html";
let s = fs.readFileSync(FILE, "utf8");
let ok = 0, miss = [];

// B: boundary census fifth touch — trim, point at map
const reB = /And <span class="m">site-worker<\/span>['’]s secondary connection — a <span class="m">localTemporalInstance<\/span>[^]*?not a way to request a repair\./;
const mB = s.match(reB);
if (mB) { s = s.replace(mB[0], `And <span class="m">site-worker</span>'s secondary connection registers it on Google's Temporal to execute FS-side activities for their workflows — execution plumbing inside the workflows, not a way to request a repair. Which connection is primary, which secondary, and the receipts: <a href="#temporal-map">the Temporal map below</a>.`); ok++; } else miss.push("B");

// A: decoder Temporal entry → pointer
const reA = /<span class="m">Temporal<\/span> = the durable-workflow engine both sides run\. Count three instances on this page:[^]*?the existing site-worker service or new workers/;
const mA = s.match(reA);
if (mA) { s = s.replace(mA[0], `<span class="m">Temporal</span> = the durable-workflow engine both sides run — three engines appear on this page; the full map (who connects to what, and what wasn't read) is <a href="#temporal-map">directly below</a>`); ok++; } else miss.push("A");

// C: u-fs fact → trimmed (DRILL, single-quoted attrs)
const reC = /site-worker is FS['’]s activity worker plugged into Google['’]s Temporal:[^]*?same-frontend is an inference/;
const mC = s.match(reC);
if (mC) { s = s.replace(mC[0], `site-worker is FS's activity worker plugged into Google's Temporal, executing the FS-side activities Google's workflows call: machine netboot/reset, NetBox reads, ping checks (<a href='https://github.com/fluidstackio/systems/tree/main/projects/site-worker/internal/activities' target='_blank' rel='noreferrer'>its activities tree</a>) — that's why the one FS→Google trigger's task queue, <span class='m'>google-workflows-site-worker-&lt;site&gt;</span>, carries its name. site-worker's two connections (Temporal Cloud primary, google-system secondary), the values.yaml receipt, dcim-api's unread endpoint, and the same-frontend inference are all laid out in <a href='#temporal-map'>the Temporal map</a> in 01`); ok++; } else miss.push("C");

// D: s-tenancy mutual-seam sentence → keep + pointer
const reD = /The seam is mutual: FS['’]s site-worker \(the per-site worker service in the systems repo\) points at <span class='m'>temporal-frontend\.google-system:7233<\/span> — Google['’]s Temporal frontend, their namespace, our cluster\./;
const mD = s.match(reD);
if (mD) { s = s.replace(mD[0], `The seam is mutual: FS's site-worker points at <span class='m'>temporal-frontend.google-system:7233</span> — Google's Temporal frontend, their namespace, our cluster (a secondary connection; the full map is <a href='#temporal-map'>the Temporal map</a> in 01).`); ok++; } else miss.push("D");

// E + F: redirect temporal "see the decoder" pointers
if (/is itself unestablished — see the decoder\)/.test(s)) { s = s.replace(/is itself unestablished — see the decoder\)/, "is itself unestablished — see <a href='#temporal-map'>the Temporal map</a> in 01)"); ok++; } else miss.push("E");
if (/whether that means the existing site-worker service is open, see the decoder\./.test(s)) { s = s.replace(/whether that means the existing site-worker service is open, see the decoder\./, "whether that means the existing site-worker service is open — see the Temporal map in 01."); ok++; } else miss.push("F");

fs.writeFileSync(FILE, s);
console.log("ok:", ok, "miss:", miss);
const m = s.match(/<script>([\s\S]*)<\/script>/);
try { new Function(m[1]); console.log("JS parses OK"); } catch (e) { console.log("JS ERROR:", e.message); }
