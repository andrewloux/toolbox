# Maintenance API — working visualizer

**`maintenance-api.html`** — a single-file, self-contained HTML page explaining FluidStack's
Maintenance API program end to end: how repairs flow **today** through the Jira seam at the
Bloom/TPU deployment (buf101, serving Atlas = Anthropic), and the **API contract being specced**
to replace that seam for Google's Borneo B300 deployment at IAH1.

Built and certified 2026-06-09 → 2026-06-11. Owner: Andrew Louis (spec owner / build lead).

## Status

**Certified** at v98 (2026-06-11). Certification = two consecutive review rounds in which two
zero-context cold readers — an FS new-engineer persona and a Google Borneo-reviewer persona —
each report **zero MEDIUM and zero HIGH** findings after reading 100 % of the page (including
all click-gated drill panels and the timeline). Rounds 13 and 14 passed dual-clean on a frozen
artifact; ~30 cold-reader passes total since the grounded rebuild.

Both final readers independently re-verified: every arithmetic web reconciles (~30 cross-sums),
every internal anchor and drill target resolves, every "see X" pointer carries what it promises,
and the provenance ledger (ref [10]) matches its inline receipts item by item.

**v99 (2026-06-11)** adds the back-trail — a navigation affordance only, zero content delta
(machine-checked: href + numeric-token set-diff vs `versions/v98-pre-backtrail.html` = 0 removals,
0 href additions; 26-case headless browser matrix passes). Certification statements above refer
to the v98 content, which v99 carries unchanged.

**v100 (2026-06-11)** adds material the certification rounds did not cover (additions only;
no-loss invariant re-verified, 0 removals vs the v88 baseline):
- **Link sweep** — 32 ops converting every bare in-page pointer ("02·B", "§04", "the Temporal
  map") into a real anchor link; four landmarks (01·A/01·B/02·A/02·B) gained ids
  (`#upstream`, `#todaytomorrow`, `#demux`, `#pathb`).
- **The dark webhook** — new research (4-agent sweep over dcim@b6eea015, systems@34e92787,
  argocd, Slack, Confluence): dcim-tasks ships an HMAC-authenticated inbound Jira webhook
  (`POST /webhooks/jira/{site}`) plus two unauthenticated admin endpoints, all built in PR #1868
  (Mar 28) and unreachable in prod — `httpRoute.enabled: false` in every prod values file ever,
  no NetworkPolicy anywhere despite the code comment demanding one, the Jira-side registration
  checkbox in argocd#5090 never checked. Canonical home: the pipeline's stage-2 MIRROR panel
  (02·B); timeline row `#ev-w-dark`; d-push cross-references it as prior art.
- **Tenancy receipts** — the 01·0 triangle now links each Auth0 org to its pinned terraform
  block; the BMS-vs-BMC contrast is sourced honestly (no single doc states it; assembled from
  the terraform comment + the TPU hardware doc, both terms defined together only in the FISH RFC
  glossary; third expansion noted — dcim SOPs use BMS = Battery Management System).

**RE-CERTIFIED at v103 (2026-06-11)** after the v100 content additions: rounds 18 and 19
passed dual-clean (zero MEDIUM/HIGH from both personas) on a byte-identical frozen artifact —
the same bar as the original v97/v98 certification. The path: round 15 (v100) FAIL/FAIL →
v101 fixes; round 16 FS-PASS/Google-FAIL → v102 fixes; round 17 FS-PASS/Google-FAIL → v103
fixes; rounds 18+19 dual PASS on frozen v103 (`versions/v103-recertified.html`). Notable
research-backed corrections along the way: the boundary census gained its explicit scope rule
(signal channels, not access surfaces); git blame falsified "Xander wrote the external-org
terraform" (it's Miguel Varela Ramos's systems#1122); the FISH expansion was sourced to the
RFC's own title; Rob's May 27 spec-by-Jun-1→3 commitment was surfaced into the state-of-play
as an unreconciled caveat on ~Jul 21.

**v104 (2026-06-11)** — post-certification polish: the 20 LOW findings queued from
the two clean rounds (diagram-specific drill hints, hero "ghost"→"dashed", census row ③/④
label precision, dek hedge, d-auth status vocabulary, 03 sourcing caveat, webhook idempotency
receipt, storm denominator, feldspar org-mechanism wording, and more). Same no-loss invariant:
0 href / 0 numeric removals vs the v88 baseline, v88 → v104.

**v105 (2026-06-11)** — **material correction** (owner-supplied, code-verified): the
site-worker Temporal model was wrong in direction. `worker.New()` appears exactly once
(main.go:87) — against **Temporal Cloud** — so site-worker's activities register only there
and a workflow on Google's engine cannot call them; `temporal-frontend.google-system` is
dialed as a *client* only, via the `RunSiteLocalWorkflow` bridge (central→site direction per
its own doc comment), which has **zero callers** in either repo. The "secondary connection
executes FS-side activities for their workflows" reading is retired at all five sites that
carried it (census row ⑤ + follow-up, 01·MAP, u-fs drill, s-tenancy). Also landed:
dcim-api's `siteWorkerTaskQueuePrefix` marked staged-not-live (the Go field is read by
nothing), the rack_workflows.go:159 TODO connected to the bridge as its likely answer, and
the sharpened §03 consequence — FS-born repairs have no path into Google's ticket-filing
machinery today, so first-class API treatment must be designed in, not inherited.
The v105 correction has **not** been through cold-reader rounds yet. This copy is the
**source of truth**; the session-directory copy is a serve mirror.

**v106 (2026-06-11)** — **restores the v99 back-trail**, silently lost since v100:
the v100 push copied a session working file over this repo's v99 without diffing against it,
dropping the back-trail CSS + JS (3,354 bytes). Caught by `make check` (DRIFT) when adopting
the split-source workflow; reinstated byte-exact from the v99 chunks and verified live (chip
appears on in-page jump, returns to exact scroll, hides). Note: versions v100–v105 — including
the `v103-recertified.html` snapshot — lack the back-trail; the certification statements are
about page *content*, which was unaffected. `src/` is now re-synced to the artifact.

**v107 (2026-06-11)** — the loop diagram + assignment/classification research. New `01·LOOP`
landmark: the repair round-trip as it runs today, three swim lanes (Google's engine / the
seam / FS's floor), nine stages, every box drilling to a receipted panel. Two stages were
researched live (3-lane sweep: dcim code, the 15,622-issue corpus, live Jira changelogs +
Confluence + Slack) because the page's story was wrong: assignment is **tech self-claim**
(5/6 sampled changelogs; 79.1% of Done tickets never assigned; dcim-tasks bot has never
written a Jira assignee; the lead-routing role is dated Jun 9), and classify/ack is
**measurably nothing** (priority = Medium default with one exception ever; Severity field
never populated; JSM SLA clocks never run; paging unwired — while the contract's Sev1–4
clocks and FS's own Approved escalation matrix both sit unimplemented on paper). New drill
panels `l-classify` and `l-assign` carry the receipts; eight stale "DCO lead routes" sites
corrected page-wide.

**v108–v109 (2026-06-11, current)** — the world-class drill (4-dimension audit: code links /
API-vs-workflow typing / concrete names / entity state transitions; 24 verified findings, all
implemented). v108 redrew 01·LOOP as a component diagram (type-tagged boxes, numbered action
pills, in-SVG legend). v109: every loop stage now carries its write-path code links (the close
chain handleTransition → POST /issue/{key}/transitions was the biggest hole); two declared
unknowns resolved from the repos (the repair-watcher → RepairTaskWorkflow trigger chain; the
Temporal engine census — two deployments, dcim-worker's prod home read); the retired
site-worker claim found surviving in u-fs and fixed; dcim-worker's "Jira workflows" correctly
typed as workflows (CreateJiraTicketWorkflow — FS's own file-and-wait mirror of Google's
pattern); a wrong-lines link fixed (a-dcim's three-tier lookup); and **two new drawn state
machines**: the machine's asset states per Partner-Ops v0.4 (§03 — GOOGLE_SERVING → DRAINED →
PARTNER_OWNED → PENDING_HANDOVER → GOOGLE_OWNED, with the done-signal and pre-repair gate
marked) and the dcim-task enum with verified writers + Jira projections (02·B — including
dashed queued, zero-in-corpus, and the silently-skipped Jira drift statuses).


## What's in the page

- **Header state-of-play box** — direction / page planks / open decisions / next dates / burning
  risk; the 60-second wake-up surface. Everything links into the deep material.
- **01** — the seam: boundary census (5 touches), two-deployments cards, the fallback amber note,
  a 38-row name-decoder reference table (01·REF), upstream trigger anatomy (01·A), Today/Tomorrow
  contract diagrams with drawn epistemic status — solid = settled, dashed = open, dotted = page
  plank (01·B), the Temporal map (01·MAP), a real ticket dissected field by field (01·C,
  ATLASBUF-15573), and the problem-code registry as data (01·D).
- **02** — routing: Request Type as the page-vs-queue demux, the June 2 misroute fully receipted
  (ATLASBUF-9203 → INC-4681), the six-stage fulfillment pipeline, the SOP lifecycle.
- **03 / 04** — the two API surfaces (FS-hosted Maintenance API vs Google-hosted Partner Ops API),
  five CUJs, the Foundry/gateway mount, NetBox/feldspar reality.
- **05** — working timeline: history / plan / seven open decision rows, the plank ledger.
- ~150 live receipts: Slack permalinks, Jira tickets, GitHub file links, Confluence pages,
  incident.io objects. Footer ledger [10] tracks recovered-vs-session-only citations and retires
  earlier figures that failed reproduction.

## Provenance & grounding

- **Jira corpus**: full ATLASBUF crawl (15,622 issues, Mar 9 – Jun 9 2026), archived locally —
  see *Data* below. All headline stats recomputed from the archive 2026-06-10; non-reproducing
  earlier figures explicitly retired in [10].
- **Code**: fluidstackio/{dcim, systems, cluster-ops, foundry, infrastructure-management} at
  2026-06-10/11 HEAD (e.g. the turn-up trigger gate `TURNUP_WORKFLOW_DEPLOYED = false`, prod
  RequestTypes map, Temporal Cloud endpoint, dcim-console → Kaiser-repo move via dcim #2525).
- **Slack / Confluence / incident.io**: live pulls Jun 9–11 (SRE-RFC-0012, Platform Consolidation,
  Platform/Infra Roadmap, the June 2 alert/incident/escalation chain via the incident.io API,
  ~25 recovered permalinks — timestamps spot-verified by the cold readers).
- Everything not verifiable is explicitly marked: unestablished / unverified / session-cited /
  open decision / retired. Declared unknowns are a feature of the page, not gaps.

## Methodology (how it got this way)

1. Grounded rebuild from a corpus-mining session, then iterative zero-context cold-reader audits
   (two personas per round) with every MEDIUM/HIGH fixed via research — corpus crunches, live
   JQL, code reads, Slack/Confluence/incident.io pulls — never wordsmithing alone.
2. A five-lens editorial workflow ("kalos pass": wake-up path, narrative arc, prose rhythm,
   redundancy, visual ergonomics) restructured the page for fast command-rebuilding.
3. **Zero-information-loss invariant**: every editorial change was relocation, never deletion.
   Machine-checked after every patch: set-diff of unique hrefs and unique numeric tokens vs the
   pre-kalos baseline (`provenance/inventory-v88.json`) = **0 removals**, v88 → v98.

## Layout

| path | what |
|---|---|
| `maintenance-api.html` | the artifact (v99 = certified v98 content + back-trail) — **a build product, do not edit** |
| `src/` | the source: numbered chunks, concatenated in filename order by `make build` (pure cat, byte-stable; tag boundaries live in tiny `.html` shims so data/logic chunks are clean `.css`/`.js`) |
| `Makefile` | `build` / `run` (serves on a free port) / `check` (src↔artifact drift + no-loss invariant) |
| `versions/v98-pre-backtrail.html` | the certified v98 artifact, frozen — provenance baseline for `make check` |
| `versions/v75-pre-rebuild.html` | before the corpus-grounded rebuild |
| `versions/v88-pre-kalos.html` | post-certification-research, pre-editorial baseline |
| `versions/v91-post-kalos.html` | after the structural editorial pass |
| `provenance/kalos-plan.md` | the editorial synthesis plan (no-culling rule, work packages) |
| `provenance/inventory-v88.json` | href + numeric-token baseline for the no-loss invariant |
| `provenance/patch-scripts/` | every find-replace patch script applied across the campaign |

## Viewing

Open `maintenance-api.html` directly, or serve it (`make run` picks a free port and prints the
URL) for clean hash navigation. Deep links work cold: `#state-of-play`, `#fallback`,
`#temporal-map`, `#anatomy`, and any timeline row via `#ev-<id>` (e.g. `#ev-d-push`). 01·B has
a Today/Tomorrow tab; solid diagram boxes drill down, dashed boxes are pointers. After any
in-page jump a **back chip** (bottom-left) appears, labeled with the section it returns to —
it's the browser's own history, surfaced: exact scroll, open drills, tab and timeline-filter
state all restore; Alt+←/swipe-back work identically.

## Editing contract

- **Edit `src/`, never the artifact.** Then `make build` (regenerates the artifact) and
  `make check` (fails on src↔artifact drift and on any href/numeric-token removal vs the
  certified baseline). The migration into `src/` was proven lossless: the first rebuild was
  byte-identical to the pre-split artifact.
- Where things live: sections 01–05 are static HTML (`src/10`–`src/50`); drill-panel bodies
  live in the `DRILL` object (`src/70-data-drills.js`, raw HTML allowed); timeline rows live
  in the `EVENTS` array (`src/72-data-events.js` — title/summary/detail are escaped text,
  **no raw HTML**; backticks render mono; links go in each event's `links` array); render
  logic and the back-trail live in `src/71`/`src/73`; theme CSS in `src/02-theme.css`.
- To extend the timeline, append to `EVENTS` — the UI renders from it.
- House rules that kept this artifact honest: every claim links a receipt or is explicitly
  hedged; one canonical home per fact, pointers elsewhere; when a permalink gets recovered,
  update the [10] ledger in the same patch; never cull context — relocate it.

## Data (not committed)

The 155 MB working archive lives locally at
`~/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/data/`:
`atlasbuf-corpus/` (corpus.jsonl 79 MB + derived extracts), page backups, and the patch scripts
mirrored here. The corpus is the ground truth for every recomputed statistic on the page.

## Caveats

- Receipts require FluidStack access (Slack workspace, Atlassian, private GitHub, incident.io).
- The page is a **snapshot dated 2026-06-11**; pinned repo states are named inline where they
  matter (e.g. site-worker's workflow roster "per the Jun 10 tree").
- Sibling artifact from the same FluidStack grounding work (not stored here yet):
  `provisioning-viz.html`.
