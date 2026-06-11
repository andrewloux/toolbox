const fs = require("fs");
const FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html";
let s = fs.readFileSync(FILE, "utf8");
let ok = 0, miss = [];
const rep = (o, n, tag) => { const i = s.indexOf(o); if (i === -1) { miss.push(tag); return; } s = s.replace(o, n); ok++; };
const repRe = (re, n, tag) => { const m = s.match(re); if (!m) { miss.push(tag); return; } s = s.replace(m[0], n); ok++; };

// FS-M1: create-path planks marked uncontested at the §05 criterion
rep("so where a d-row says “Google preference unknown,” it means unknown to this page; the doc itself may already answer some of them.",
  "so where a d-row says “Google preference unknown,” it means unknown to this page; the doc itself may already answer some of them. Three create-path planks — batch create, coalescing on (entity, problem_code), and adopting cf_14593 as the idempotency key — are, like GET /problem-codes, uncontested in the working plan: no voice read disputes them, so they carry no d-row.", "FS-M1");

// G-M1: the 33/21/~50 reconciliation, computed
repRe(/repair-tuple 4,728 vs the three repair doctors['’] 4,674 differ by ~50 tickets — hand-filed repair-tuples \(the 33 human template tickets sit here\) plus extractor drift; not a sixth machine filer\./,
  "repair-tuple 4,728 vs the three repair doctors' 4,674 differ by ~50 tickets, and the gap decomposes: ~30 is extractor drift between the mining session's count and this page's shape-count (4,698), ~20 are tuple-shaped tickets whose run links don't parse to a doctor, and exactly 4 are hand-filed full repair-tuples. The 33 “template-shaped humans” is a different, wider cut — summary shape (SW:/HW:/Clean+Reseat prefixes); only 4 of the 33 carry the full repair-tuple body, and those 4 sit inside the 21 workflow-naming human tickets.", "G-M1");

// 01·C exemplar precision
rep("one of the 33 template-shaped human tickets — but its structure is the bot's repair-tuple template",
  "one of the 33 template-shaped human tickets, and one of just 4 whose body is the full repair-tuple — the bot's own template", "exemplar");

// FS-L2/G-L2: u-camp ratio chained
repRe(/99% closed Done, unassigned, median 34 minutes: automation wrote those transitions, not hands/,
  "99% closed Done; of those Dones, 99% were unassigned (median 34 minutes) — automation wrote those transitions, not hands", "ratio");

// FS-L3: qualification enum file-precise link
rep("<a href='https://github.com/fluidstackio/dcim/tree/main/services/dcim-api' target='_blank' rel='noreferrer'>dcim-api (home of the qualification enum)</a>",
  "<a href='https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/openapi.yaml#L6810-L6812' target='_blank' rel='noreferrer'>QualificationType in dcim-api's openapi.yaml</a>", "FS-L3");

// FS-L4: dcim-api vs gateway estate
rep("The unified external surface — <b>where the Maintenance API mounts</b>",
  "The unified external surface — <b>where the Maintenance API mounts</b> (whether today's separate door, api.dcim.fluidstack.io, eventually mounts behind it or stays outside isn't designed anywhere read)", "FS-L4");

// FS-L5: boot-time hash open
rep("renderBar(); renderTL(); onScrollSpy();", "renderBar(); renderTL(); onScrollSpy(); openEvFromHash();", "FS-L5");

// G-L3a: Vertex gloss outside Mike's quotation
repRe(/aka ‘Google running Vertex AI on us’ \(Vertex AI: Google's managed AI platform\); starting with 5k B300 in Stream Houston”/,
  "aka ‘Google running Vertex AI on us’; starting with 5k B300 in Stream Houston” (Vertex AI: Google's managed AI platform)", "G-L3a");

// G-L3b: anatomy page-note marked as page commentary
rep("port 18B · OCS 16N. Note the ticket speaks two location vocabularies",
  "port 18B · OCS 16N. <i>Page note, not ticket text:</i> the ticket speaks two location vocabularies", "G-L3b");

// G-L4: Argo-deployed gloss at §02
rep("Argo-deployed from", "Argo-deployed (gitops — glossed in the tenancy panel) from", "G-L4");

fs.writeFileSync(FILE, s);
console.log("ok:", ok, "miss:", miss);
const m = s.match(/<script>([\s\S]*)<\/script>/);
try { new Function(m[1]); console.log("JS parses OK"); } catch (e) { console.log("JS ERROR:", e.message); }
