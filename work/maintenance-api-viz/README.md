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

The v100 additions have **not** been through cold-reader certification rounds; the v98
statements above do not extend to them.

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
