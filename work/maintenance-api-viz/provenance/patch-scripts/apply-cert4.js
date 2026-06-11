const fs = require("fs");
const FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html";
let s = fs.readFileSync(FILE, "utf8");
let ok = 0, miss = [];
const rep = (o, n, tag) => { const i = s.indexOf(o); if (i === -1) { miss.push(tag); return; } s = s.replace(o, n); ok++; };

// FS-M1: reseat-doc classification unified to the born path
const r1 = s.match(/Field-test receipts:[^]*?render-layer gaps, not data gaps\./);
if (r1) { s = s.replace(r1[0], "Field-test receipts: the absent location-verification scan step is a render-layer gap. The missing reseat-the-cable doc was an authoring gap — the procedure didn't exist yet, so it took the born path (the 02·C footer traces it)."); ok++; } else miss.push("FS-M1a");

const r2 = s.match(/a repair whose SOP isn['’]t approved is a repair the floor can['’]t execute[^]*?missing reseat-the-cable doc is the live case\./);
if (r2) { s = s.replace(r2[0], "a repair whose SOP isn't approved is a repair the floor can't execute — and one whose SOP doesn't exist at all takes the born path first. June 3's missing reseat-the-cable doc was the latter."); ok++; } else miss.push("FS-M1b");

// G-M1: week arithmetic
rep("Wk 5–6 · Google loop; freeze lands by ~Aug 4", "Wk 5–6 · Google loop → spec ~Jul 21; Wk 7–8 → freeze ~Aug 4", "G-M1a");
rep("Wk 0–6 program plan", "Wk 0–8 program plan", "G-M1b");

// FS-L3: 42-day stat sourced
rep("aged 42 days at crawl time.", "aged 42 days at crawl time (a recomputed archive stat, enumerated in [10]).", "FS-L3a");
rep("June's sweep volume collapsed the Done median (pre-June 6.0 h → June 1.0 h).", "June's sweep volume collapsed the Done median (pre-June 6.0 h → June 1.0 h); oldest unresolved open/blocked ticket at crawl: 42 d.", "FS-L3b");

// FS-L4: Dell terraform attach-point
rep("holds bastion-only support access (<a href=\"https://github.com/fluidstackio/systems/blob/main/terraform/fish/envs/prod/main.tf\" target=\"_blank\" rel=\"noreferrer\">scoped in the sso terraform</a>)", "holds bastion-only support access (<a href=\"https://github.com/fluidstackio/systems/blob/main/terraform/fish/envs/prod/main.tf\" target=\"_blank\" rel=\"noreferrer\">scoped in the sso terraform</a> — the buf101-era FISH env; the pattern is org-level Auth0, and its IAH1 instantiation is unestablished like the rest of the stand-up)", "FS-L4");

// G-L2: registry disambiguation in decoder
rep("the registry's site entry", "the site registry's entry", "G-L2a");
rep("the registry's <span class=\"m\">type_of_rma", "the problem-code registry's <span class=\"m\">type_of_rma", "G-L2b");
rep("registry's rectifier entries", "problem-code registry's rectifier entries", "G-L2c");

// G-L3: JSM email first-occurrence [10]
rep("Always-on, both paths:", "Always-on, both paths (the email behavior is session-cited<sup class=\"rf\"><a href=\"#ref-10\">[10]</a></sup>):", "G-L3");

// G-L4: all three vs four tenants
rep("one house external-org pattern covers all three.", "one house external-org pattern covers all three — four, counting the BMS integrators the terraform also lists.", "G-L4");

fs.writeFileSync(FILE, s);
console.log("ok:", ok, "miss:", miss);
const m = s.match(/<script>([\s\S]*)<\/script>/);
try { new Function(m[1]); console.log("JS parses OK"); } catch (e) { console.log("JS ERROR:", e.message); }
