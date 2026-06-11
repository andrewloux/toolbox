const fs = require("fs");
const FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html";
let s = fs.readFileSync(FILE, "utf8");
let ok = 0, miss = [];

// C: u-fs fact — replace from "site-worker is FS's activity worker" through "same-frontend is an inference"
const reC = /site-worker is FS's activity worker plugged into Google's Temporal\. Its base config names[^]*?same-frontend is an inference/;
const mC = s.match(reC);
if (mC) {
  s = s.replace(mC[0], `site-worker is FS's activity worker plugged into Google's Temporal. It executes the FS-side activities Google's workflows call: machine netboot/reset, NetBox reads, ping checks (<a href='https://github.com/fluidstackio/systems/tree/main/projects/site-worker/internal/activities' target='_blank' rel='noreferrer'>its activities tree</a>). That's why the one FS→Google trigger's task queue, <span class='m'>google-workflows-site-worker-&lt;site&gt;</span>, carries its name. Its two connections (Temporal Cloud primary, google-system secondary), the values.yaml receipt, dcim-api's unread endpoint, and the same-frontend inference are laid out in <a href='#temporal-map'>the Temporal map</a> in 01`);
  ok++;
} else miss.push("C");

// D: s-tenancy mutual-seam — keep + secondary marker + map pointer
const reD = /The seam is mutual: FS's site-worker \(the per-site worker service in the systems repo\) points at <span class='m'>temporal-frontend\.google-system:7233<\/span> — Google's Temporal frontend <a href='[^']*'[^>]*>↗<\/a>, their namespace, our cluster\./;
const mD = s.match(reD);
if (mD) {
  s = s.replace(mD[0], `The seam is mutual: FS's site-worker points at <span class='m'>temporal-frontend.google-system:7233</span> — Google's Temporal frontend <a href='https://github.com/fluidstackio/systems/blob/main/gitops/apps/fish-base/site-worker/values.yaml' target='_blank' rel='noreferrer'>↗</a>, their namespace, our cluster. That is its secondary connection; the full map is <a href='#temporal-map'>the Temporal map</a> in 01.`);
  ok++;
} else miss.push("D");

// E: a-dcim pointer
if (s.includes("is itself unestablished — see the decoder.</p>")) {
  s = s.replace("is itself unestablished — see the decoder.</p>", "is itself unestablished — see <a href='#temporal-map'>the Temporal map</a> in 01.</p>");
  ok++;
} else miss.push("E");

// F: kickoff event pointer (plain text)
if (s.includes("Whether that means the existing site-worker service is open — see the decoder.")) {
  s = s.replace("Whether that means the existing site-worker service is open — see the decoder.", "Whether that means the existing site-worker service is open — see the Temporal map in 01.");
  ok++;
} else miss.push("F");

fs.writeFileSync(FILE, s);
console.log("ok:", ok, "miss:", miss);
const m = s.match(/<script>([\s\S]*)<\/script>/);
try { new Function(m[1]); console.log("JS parses OK"); } catch (e) { console.log("JS ERROR:", e.message); }
const ev = m[1].match(/const EVENTS = \[[\s\S]*?\n\];/);
console.log("raw <a in EVENTS:", /<a href/.test(ev[0].replace(/links: \[[\s\S]*?\]/g, "")) ? "BUG" : "none");
