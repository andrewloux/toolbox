const fs = require("fs");
const FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html";
let s = fs.readFileSync(FILE, "utf8");
let ok = 0, miss = [];
const rep = (re, n, tag) => { const m = s.match(re); if (!m) { miss.push(tag); return; } s = s.replace(m[0], n); ok++; };

// FS-M1: hero dhint bridges the denominators
rep(/987 of the 2,671 repair-task rejections carry no resolve timestamp\)/,
  "987 of the 2,671 repair-task rejections — 2,686 project-wide once 15 non-repair types are counted — carry no resolve timestamp)", "FS-M1");

// G-M1: heartbeater conclusion scoped to its premises
rep(/[Tt]he heartbeat proves the Jira→incident\.io bridge end to end either way\./,
  "The heartbeat proves Jira→incident.io connectivity generally; whether it exercises the same “Jira queues CB3” source repair tickets traverse is part of what's unread.", "G-M1");

// FS-L2: "every stage is shipped code" vs human stage 5
rep(/Six mechanisms run between “ticket lands” and “workflow wakes up”; every stage is shipped code:/,
  "Six mechanisms run between “ticket lands” and “workflow wakes up” — five are shipped code; stage 5's routing is a human act with shipped tooling around it:", "FS-L2");

// FS-L3: Dell forward-reference in Bloom row
rep(/with its own scoped Auth0 access like Google and Dell\./,
  "with its own scoped Auth0 access, like Google — and like Dell, the hardware vendor the next row introduces; one house external-org pattern covers all three.", "FS-L3");

// FS-L4: Redfish client link
rep(/FS vendors a client in the dcim repo; the GFC chip names surfaced through it/,
  "FS vendors <a href=\"https://github.com/fluidstackio/dcim/tree/main/pkg/redfishclient\" target=\"_blank\" rel=\"noreferrer\">a client in the dcim repo</a>; the GFC chip names surfaced through it", "FS-L4");

// FS-L5: BorneoOS gloss
rep(/Fluidstack QA image vs Google BorneoOS — flip a config bit on the switch/,
  "Fluidstack QA image vs Google BorneoOS — flip a config bit on the switch” (BorneoOS reads as Google's machine OS image for the program, by contrast with the FS QA image; the name appears only in this requirement", "FS-L5");

// G-L2: census touch 4 marker
rep(/④ TPU-CC’s diagnostics RPCs/,
  "④ TPU-CC’s diagnostics RPCs (whether FS ever calls them today is unverified — 01·D)", "G-L2");

// G-L3: staleness confidence aligned
rep(/The two files were copied from Google at different times — at least one is stale\./,
  "The two files were copied from Google at different times, and since they disagree, at least one no longer matches Google's current file. Which one is the unsplittable half — below.", "G-L3");

// G-L4: editorial gloss out of Mike's quotation
rep(/aka ‘Google running Vertex AI — its managed AI platform — on us’/,
  "aka ‘Google running Vertex AI on us’ (Vertex AI: Google's managed AI platform)", "G-L4");

// G-L5: Request-Type universal scoped
rep(/Every ATLASBUF ticket carries a JSM \(Jira Service Management\) <b>Request Type<\/b> field/,
  "ATLASBUF repair tickets carry a JSM (Jira Service Management) <b>Request Type</b> field — uniform on the 200/200 live pull; the universal over every issue type isn't checked", "G-L5");

fs.writeFileSync(FILE, s);
console.log("ok:", ok, "miss:", miss);
const m = s.match(/<script>([\s\S]*)<\/script>/);
try { new Function(m[1]); console.log("JS parses OK"); } catch (e) { console.log("JS ERROR:", e.message); }
