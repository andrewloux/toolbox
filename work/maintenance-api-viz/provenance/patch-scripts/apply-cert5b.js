const fs = require("fs");
const FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html";
let s = fs.readFileSync(FILE, "utf8");
let ok = 0, miss = [];
const rep = (o, n, tag) => { const i = s.indexOf(o); if (i === -1) { miss.push(tag); return; } s = s.replace(o, n); ok++; };

rep("differ by ~50 tickets: hand-filed repair-tuples (the 33 human template tickets sit here) plus extractor drift — not a sixth machine filer.",
  "differ by ~50 tickets, and the gap decomposes: ~30 is extractor drift between the mining session's count and this page's shape-count (4,698), ~20 are tuple-shaped tickets whose run links don't parse to a doctor, and exactly 4 are hand-filed full repair-tuples — not a sixth machine filer. The 33 “template-shaped humans” is a different, wider cut (summary shape: SW:/HW:/Clean+Reseat prefixes); only 4 of the 33 carry the full repair-tuple body, and those 4 sit inside the 21 workflow-naming human tickets.", "G-M1");

rep("one of the 33 template-shaped human tickets; but its structure is the bot's repair-tuple template, the shape of the 4,728-ticket repair-tuple family.",
  "one of the 33 template-shaped human tickets — and one of just 4 whose body is the full repair-tuple, the shape of the 4,728-ticket family.", "exemplar");

rep("99% closed Done, <b>unassigned</b>, median 34 minutes: automation wrote those transitions, not hands.",
  "99% closed Done; of those Dones, 99% were unassigned (median 34 minutes) — automation wrote the transitions, not hands.", "ratio");

rep('dcim-api (home of the qualification enum)", url: "https://github.com/fluidstackio/dcim/tree/main/services/dcim-api" }] },',
  'QualificationType enum — dcim-api openapi.yaml", url: "https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/openapi.yaml#L6810-L6812" }] },', "FS-L3");

fs.writeFileSync(FILE, s);
console.log("ok:", ok, "miss:", miss);
const m = s.match(/<script>([\s\S]*)<\/script>/);
try { new Function(m[1]); console.log("JS parses OK"); } catch (e) { console.log("JS ERROR:", e.message); }
