const fs = require("fs");
const FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html";
let s = fs.readFileSync(FILE, "utf8");
let ok = 0, miss = [];
const rep = (o, n, tag) => { const i = s.indexOf(o); if (i === -1) { miss.push(tag); return; } s = s.replace(o, n); ok++; };

rep("only existing fallback if machines land before the API ships. Atlas leaves Jira only if",
  "only existing fallback if machines land before the API ships — existing at buf101; an IAH1 instance of it would be new deployment work. Atlas leaves Jira only if", "G-M1a");

rep("only existing fallback. BP-232 tracks facility milestones, not hardware-arrival dates, so the fallback",
  "only existing fallback — and “existing” means the buf101 instance: whether its fulfillment machinery (per-site dcim config, console queue, DCO hands, NetBox modeling) could stand at IAH1 in time is itself unestablished. BP-232 tracks facility milestones, not hardware-arrival dates, so the fallback", "G-M1b");

rep("that placement is inference, not receipt. Which ticket, and which wrong value it carrie",
  "that placement is a weak inference: the archive holds all of ATLASBUF through Jun 9 and no June 1–2 summary matches, so either incident.io's alert title rewrote the ticket's wording or the home project isn't ATLASBUF after all. Which ticket, and which wrong value it carrie", "G-L4");

fs.writeFileSync(FILE, s);
console.log("ok:", ok, "miss:", miss);
const m = s.match(/<script>([\s\S]*)<\/script>/);
try { new Function(m[1]); console.log("JS parses OK"); } catch (e) { console.log("JS ERROR:", e.message); }
