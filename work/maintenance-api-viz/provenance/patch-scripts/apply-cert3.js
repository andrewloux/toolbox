const fs = require("fs");
const FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html";
let s = fs.readFileSync(FILE, "utf8");
let ok = 0, miss = [];
const rep = (re, n, tag) => { const m = s.match(re); if (!m) { miss.push(tag); return; } s = s.replace(m[0], n); ok++; };

// FS-M1: "so Google re-validates" → intent, not established effect
rep(/On rack-checklist work, finishing fires the Google QA handoff button \(PR #2163\) so Google re-validates\./,
  "On rack-checklist work, finishing fires the Google QA handoff button (PR #2163) — built for Google-side re-validation; what it actually fires over there is one of the three unknowns below.", "FS-M1");

// FS-L2: repair the garbled staleness sequence
rep(/Which one is the unsplittable half — below\. Which one is answerable: bloom-diagnostics was readable at vendoring time, the embed PR pins <span class="m">@68ae89d<\/span>[^]*?staleness is a process gap, not an access gap, which is the d-vocab argument\./,
  "Which one is behind can't be split from the artifacts read for this page — though a fresh pull of bloom-diagnostics would answer it: the file was readable at vendoring time, the embed PR pins <span class=\"m\">@68ae89d</span>, and Wk 0–1 plans the re-pull. Nothing re-pulls it automatically. Staleness is a process gap, not an access gap — which is the d-vocab argument.", "FS-L2");

// FS-L3: TPU decoder gloss — append at the ICI decoder entry start
rep(/<span class="m">ICI<\/span> = inter-chip interconnect, the optical TPU↔TPU fabric/,
  "<span class=\"m\">TPU</span> = tensor processing unit, Google's AI accelerator · <span class=\"m\">ICI</span> = inter-chip interconnect, the optical TPU↔TPU fabric", "FS-L3");

// G-M1a: hero fallback "existing" scoped
rep(/though the Jira seam is the only existing fallback if machines land before the API ships/,
  "though the Jira seam is the only existing fallback if machines land before the API ships — existing at buf101; an IAH1 instance of it would be new deployment work", "G-M1a");

// G-M1b: Borneo-row gap seg — third fallback problem
rep(/the Jira seam is the only existing fallback — and BP-232 tracks facility milestones/,
  "the Jira seam is the only existing fallback — and “existing” means the buf101 instance: whether its fulfillment machinery (per-site dcim config, console queue, DCO hands, NetBox modeling) could stand at IAH1 in time is itself unestablished. BP-232 tracks facility milestones", "G-M1b");

// G-M2: QA button tomorrow-state at the transport diacap
rep(/for API-borne traffic their only successor is whatever <a href="#ev-d-push">d-push<\/a> decides\./,
  "for API-borne traffic their only successor is whatever <a href=\"#ev-d-push\">d-push</a> decides. The QA-handoff button — boundary touch ② — likewise has no declared tomorrow-state: whether <a href=\"#ev-d-revalidate\">d-revalidate</a>'s actor-agnostic re-validation subsumes it or it persists outside the contract isn't designed anywhere read.", "G-M2");

// G-M3: d-row epistemic scope at the §05 decisions intro
rep(/are declared where they arise and deliberately not rowed\./,
  "are declared where they arise and deliberately not rowed. One scoping fact: this page worked from a summary of the Partner Ops doc, not a full mining pass — Wk 0–1 plans that — so where a d-row says “Google preference unknown,” it means unknown to this page; the doc itself may already answer some of them.", "G-M3");

// G-L4: misroute inference vs complete archive — name the disjunction
rep(/but since the ticket itself isn['’]t recoverable, that placement is inference, not receipt\.\)/,
  "but the archive holds all of ATLASBUF through Jun 9 and no June 1–2 summary matches — so either incident.io's alert title rewrote the ticket's wording, or the home project isn't ATLASBUF after all. The placement is a weak inference, flagged as such.)", "G-L4");

fs.writeFileSync(FILE, s);
console.log("ok:", ok, "miss:", miss);
const m = s.match(/<script>([\s\S]*)<\/script>/);
try { new Function(m[1]); console.log("JS parses OK"); } catch (e) { console.log("JS ERROR:", e.message); }
