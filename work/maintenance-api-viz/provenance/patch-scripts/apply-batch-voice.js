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

// seg3: give SRE-RFC-0012 its antecedent at first mention in the row
rep('and the key contract has a caller waiting: <a href="https://fluidstack.atlassian.net/wiki/spaces/RE/pages/607617031" target="_blank" rel="noreferrer">SRE-RFC-0012</a> plans to submit',
  'and the key contract has a caller waiting: the correlation engine\'s RFC (<a href="https://fluidstack.atlassian.net/wiki/spaces/RE/pages/607617031" target="_blank" rel="noreferrer">SRE-RFC-0012</a>) plans to submit',
  "seg3-antecedent");

// §05 ledger: batch plank's floor voice, with Slack receipt
rep('waits on exactly that key contract, “pending API review.” Click any row',
  'waits on exactly that key contract, “pending API review.” The batch plank has a floor voice asking for it — “best to batch together common repairs and give in bulk” (Thomas Barrett, FS network deployment, over eight racks of swapped management cabling <a href="https://fluidstack.enterprise.slack.com/archives/C0ARQA55XU3/p1778707120991559?thread_ts=1778704566.098799&cid=C0ARQA55XU3" target="_blank" rel="noreferrer">↗</a>). Click any row',
  "batch-voice");

fs.writeFileSync(FILE, s);
console.log("ok:", ok, "miss:", miss);
const m = s.match(/<script>([\s\S]*)<\/script>/);
try { new Function(m[1]); console.log("JS parses OK"); } catch (e) { console.log("JS ERROR:", e.message); }
