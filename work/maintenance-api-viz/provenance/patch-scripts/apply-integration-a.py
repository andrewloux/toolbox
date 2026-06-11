#!/usr/bin/env python3
import re, sys
FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html"
s = open(FILE).read()
ok, miss = [], []

def rep(old, new, tag):
    global s
    n = s.count(old)
    if n != 1:
        miss.append(f"{tag} (count={n})"); return
    s = s.replace(old, new); ok.append(tag)

def rrep(pattern, new, tag):
    global s
    ms = list(re.finditer(pattern, s))
    if len(ms) != 1:
        miss.append(f"{tag} (re count={len(ms)})"); return
    s = s[:ms[0].start()] + new + s[ms[0].end():]; ok.append(tag)

SEAN = "https://fluidstack.enterprise.slack.com/archives/C0AE7079XR8/p1779470572120259?thread_ts=1779467241.015279&cid=C0AE7079XR8"

# ---- cert LOWs ----
rep('label: "Victor&apos;s simulated-repair test ticket — ATLASBUF-5"',
    'label: "Victor\'s simulated-repair test ticket — ATLASBUF-5"', "victor-escape")

rep('987 of the 2,671 repair-task rejections — 2,686 project-wide once 15 non-repair types are counted — carry no resolve timestamp',
    '987 of the 2,671 repair-task rejections — 2,686 project-wide once 15 rejected tickets of other issue types are counted — carry no resolve timestamp', "15types-dhint")

rep('All 8,737 are repair tasks, verified, so the same count sums into the 15,622-wide decomposition in 01·A’s family panel.'.replace('’', "'"),
    "All 8,737 are repair tasks, verified — counted inside the 15,622, where they cross-cut 01·A's template buckets rather than forming a bucket of their own.", "census-8737")

rep("~30 is extractor drift between the mining session's count and this page's shape-count (4,698)",
    "~30 is drift between two tuple-extraction runs — the Jun 9 mining session counted 4,728, this page's summary-shape recount found 4,698", "4698-drift")

rep('one house external-org pattern covers all three — four, counting the BMS integrators the terraform also lists.',
    'one house external-org pattern covers all three — four, counting the BMS integrators the terraform also lists (BMS = building-management system, the facility contractors; distinct from BMC, the board controller).', "bms-gloss")

rep('<b>203 entries across 10 problem families</b> (two of them — cdu, ups — currently empty), each carrying',
    '<b>203 entries across 10 problem families</b> (the family list comes from the sibling common.proto enums — the entries file alone can’t show an empty family, and two, cdu and ups, are currently empty), each carrying', "10fam")

rep('two of the create-path planks this page proposes; uncontested in the working plan, decided nowhere read (status gathered at <a href="#timeline">05</a>).',
    'two of the create-path planks this page proposes; uncontested in the working plan, decided nowhere read (status gathered at <a href="#timeline">05</a>). The diagram above draws settled, open, and proposed in one line-weight — these captions and 05 carry each element’s status.', "svg-register")

# dek split
old_dek = '''<p class="dek">Google is landing a B300 GPU cluster — <b>Borneo</b> — at IAH1, a Stream DC colo facility where FluidStack operates the deployment. Its repairs will flow through the API this page motivates and constrains; the spec itself lands ~Jul 21. The repair machinery that exists <b>today</b> serves Google's earlier TPU deployment (<b>Bloom</b>) at buf101, run for the existing tenant (<b>Atlas</b>). There, Google's workflows decide <b>what</b> gets repaired, FluidStack does the <b>how</b>, and the repair request itself travels only as a Jira ticket. That machinery is the precedent the API generalizes. FS's working plan has Borneo never touching the Jira seam<sup class="rf"><a href="#ref-10">[10]</a></sup>; Google's acceptance of that timeline is a separate, unestablished matter, and the Jira seam is the only existing fallback if machines land before the API ships — existing at buf101; an IAH1 instance of it would be new deployment work. Atlas leaves Jira only if Rob's pitch to move its traffic onto the same API lands — a workstream pursued in parallel with the Borneo spec, not a blocker for it.</p>'''
new_dek = '''<p class="dek">Google is landing a B300 GPU cluster — <b>Borneo</b> — at IAH1, a Stream DC colo facility where FluidStack operates the deployment. Its repairs will flow through the API this page motivates and constrains; the spec itself lands ~Jul 21. The repair machinery that exists <b>today</b> serves Google's earlier TPU deployment (<b>Bloom</b>) at buf101, run for the existing tenant (<b>Atlas</b>): Google's workflows decide <b>what</b> gets repaired, FluidStack does the <b>how</b>, and the repair request itself travels only as a Jira ticket. That machinery is the precedent the API generalizes.</p>
  <p class="dek">FS's working plan has Borneo never touching the Jira seam<sup class="rf"><a href="#ref-10">[10]</a></sup>; Google's acceptance of that timeline is unestablished. If machines land before the API ships, the Jira seam is the only existing fallback — and it exists at buf101 only; an IAH1 instance would be new deployment work. Atlas leaves Jira only if Rob's pitch to move its traffic onto the same API lands — a workstream pursued in parallel, not a blocker.</p>'''
rep(old_dek, new_dek, "dek-split")

# decoder spacing slips (class fix: missing space before mid-dot-adjacent span)
n_fix = len(re.findall(r' ·<span class="m">', s))
s = s.replace(' ·<span class="m">', ' · <span class="m">')
ok.append(f"spacing-x{n_fix}")

# ---- Slack receipts ----
rep('which Jason describes as “so tired” it “REALLY wants us to replace it.”<sup class="rf"><a href="#ref-10">[10]</a></sup>',
    'which Jason Legler describes as “so tired” — “NetBox REALLY wants us to replace it” <a href="https://fluidstack.enterprise.slack.com/archives/C0AAY9E2NF9/p1778202865833239?thread_ts=1778175004.977409&cid=C0AAY9E2NF9" target="_blank" rel="noreferrer">↗</a>.', "jason-legler")

rep('the SPOCS rack-role drift between wdl101 and buf101 was exactly this class<sup class="rf"><a href="#ref-10">[10]</a></sup>.',
    'the SPOCS rack-role drift between wdl101 and buf101 was exactly this class — Sean Banko: “I assumed/expected the role name in wdl101 to be consistent with buf101, and that turned out not to be true, which is what broke me” <a href="' + SEAN + '" target="_blank" rel="noreferrer">↗</a>.', "spocs-receipt")

rep('“not prod ready” was the answer when Rob asked to swap DCIM\'s reads.<sup class="rf"><a href="#ref-10">[10]</a></sup>',
    '“not prod ready yet Rob” was Anshul Kamath’s answer when Rob came asking — the April CMDB thread <a href="https://fluidstack.enterprise.slack.com/archives/C0AE7079XR8/p1776967715264939?thread_ts=1776967539.606709&cid=C0AE7079XR8" target="_blank" rel="noreferrer">↗</a>.', "anshul-prodready")

rep('(The source says just “Sean” — likely Sean Banko, unconfirmed, the same bare-name ambiguity the who\'s-who flags.)',
    '(“Sean” is Sean Banko — the thread is recovered <a href="' + SEAN + '" target="_blank" rel="noreferrer">↗</a>; the line continues: “I assumed/expected the role name in wdl101 to be consistent with buf101, and that turned out not to be true, which is what broke me.”)', "sean-confirmed")

rep('Hannah: “not quite operational”<sup class="rf"><a href="#ref-10">[10]</a></sup>',
    'Hannah: “not quite operational” <a href="https://fluidstack.enterprise.slack.com/archives/C0AAY9E2NF9/p1780954556831229?thread_ts=1780948308.037829&cid=C0AAY9E2NF9" target="_blank" rel="noreferrer">↗</a>', "hannah-link")

rep('Rack-scan demo to Google scheduled for May 28 <a href="https://fluidstack.enterprise.slack.com/archives/C0AE7079XR8/p1779813121162009" target="_blank" rel="noreferrer">↗</a> — no post-demo recap found in Slack;',
    'Rack-scan demo to Google scheduled for May 28 <a href="https://fluidstack.enterprise.slack.com/archives/C0AE7079XR8/p1779813121162009" target="_blank" rel="noreferrer">↗</a> (Anshul, on scope: “I think just rack scan?” <a href="https://fluidstack.enterprise.slack.com/archives/C0AE7079XR8/p1779816264876489?thread_ts=1779813121.162009&cid=C0AE7079XR8" target="_blank" rel="noreferrer">↗</a>) — no post-demo recap found in Slack;', "cuj1-anshul")

rep("Andrew's build runs against the freeze — its own schedule isn't laid out on this page.\",",
    "Andrew's build runs against the freeze — its own schedule isn't laid out on this page. A dated wrinkle precedes the program: on May 27 Rob wrote in-thread that he'd already told Google he'd deliver the machine-management spec by Jun 1, slipping to Jun 3 on PTO — how that earlier commitment relates to the ~Jul 21 target isn't reconciled in anything read.\",", "wk56-detail")

rep('specImpact: "Deadline objective.",\n    links: [{ label: "Borneo Partner Operations API doc", url: "https://docs.google.com/document/d/1vgCxJdpeyUfDgjupARKKM8MLCV2Pk44hWt1jcjHNGew/edit" }]',
    'specImpact: "Deadline objective.",\n    links: [{ label: "Borneo Partner Operations API doc", url: "https://docs.google.com/document/d/1vgCxJdpeyUfDgjupARKKM8MLCV2Pk44hWt1jcjHNGew/edit" }, { label: "Rob in-thread: spec promised by Jun 1 → Jun 3 (PTO)", url: "https://fluidstack.enterprise.slack.com/archives/C0B0HPZ35GV/p1779906524583829?thread_ts=1779905920.244999&cid=C0B0HPZ35GV" }]', "wk56-link")

rep('Whether that means the existing site-worker service is open — see the Temporal map in 01.',
    'Whether that means the existing site-worker service is open — see the Temporal map in 01. Meeting notes are recovered (Granola, linked): scope “customer-facing API for submitting maintenance/repair tickets, replacing current Jira-based flow”, the ~8-week window — and a note that Anshul built a prototype: Envoy over Tailnet, a cloud-side gateway calling an on-site service.', "kickoff-granola-detail")

rep('links: [{ label: "Two-way comms note (#pgm_incident_management)", url: "https://fluidstack.enterprise.slack.com/archives/C0AC62DTVT2/p1781014939103399" }] }',
    'links: [{ label: "Two-way comms note (#pgm_incident_management)", url: "https://fluidstack.enterprise.slack.com/archives/C0AC62DTVT2/p1781014939103399" }, { label: "Granola notes — Customer Maintenance API sync (Jun 9)", url: "https://fluidstack.enterprise.slack.com/archives/C0AAY9E2NF9/p1781031650247689?thread_ts=1781031570.403159&cid=C0AAY9E2NF9" }] }', "kickoff-granola-link")

# ---- incident.io receipts ----
rrep(r'<p>June 2: a cable-repair ticket[\s\S]*?anywhere this page read\.</p>',
    '<p>June 2, 8:34 PM PDT: <a href=\'https://fluidstack.atlassian.net/browse/ATLASBUF-9203\' target=\'_blank\' rel=\'noreferrer\'>ATLASBUF-9203</a> — summary “Repair Cable”, filed by Joe Feldman, queue-bound hands work (its cf_12271: “Need to Trace mgmt uplink from mgmt-spn-1”, a mgmt-spine → leaf link) — carried Request Type <b>“Compute - Cable Repair”</b>, a queue whose own description forbids exactly this use: “Use ONLY for compute to network single cable replace. Not for network-network links.”</p><p>The route raised INC-4681, the “DC ops Alerting path” workflow escalated to Systems Esc, and Hammad Mohiuddin was paged — acked in 19 s. The incident was Declined 4 minutes later; the ticket closed Done in 16.</p><p>Recovered Jun 10 via the incident.io API (<a href=\'https://app.incident.io/fluidstack/incidents/4681\' target=\'_blank\' rel=\'noreferrer\'>INC-4681</a> · <a href=\'https://app.incident.io/fluidstack/on-call/alerts/01KT5RQ7Y998XEP3CC7F8QW22N\' target=\'_blank\' rel=\'noreferrer\'>the alert</a>). The earlier crawl missed it because the summary is just “Repair Cable” — the alert title carried it verbatim, unrewritten; the earlier either/or speculation here is retired.</p>', "june2-receipt")

rep("Whether other attributes (reporter among them) also weigh in can't be excluded while the route expressions stay unread; the full route predicate is attribute-keyed, dashboard-managed, and unread — the verified note below.",
    "The route expressions themselves are dashboard-only — the incident.io API exposes no alert-route read (re-checked Jun 10), so other attributes weighing in can't be fully excluded. Behaviorally the discriminator holds: across the June 1–3 window, “Deployment” alerts created zero incidents while all 11 incident-creating alerts carried non-Deployment queues — the verified note below.", "route-predicate")

rep('whether the mirror also synced it despite the wrong value is part of the unread config.',
    'the wrong queue (“Compute - Cable Repair”, request type 1414) has no entry in dcim-tasks’ production RequestTypes map — only Deployment (1669) and Compute or Network Device Repair (1415) are mapped <a href="https://github.com/fluidstackio/dcim/blob/main/argocd/datacenters-prod/dcim-tasks/values.yaml#L45-L63" target="_blank" rel="noreferrer">↗</a> — so the mirror had no mapping to sync it under.', "mirror-mapping")

rep('<b>interrupts page, work items queue</b> (per the receipts — the full route predicate stays unread).',
    '<b>interrupts page, work items queue</b> (per the receipts — behaviorally confirmed across the June window, though the route expressions stay dashboard-only).', "classify-line")

rep("ingests ATLASBUF broadly: machine-filed repairs arrive as alerts carrying the ticket's Request Type, reporter, and full body as attributes.</p>",
    "ingests ATLASBUF broadly: machine-filed repairs arrive as alerts carrying the ticket's Request Type, reporter, and full body as attributes — and always at priority P4; the source never sets the org's “Should Page” attribute.</p>", "p4-attrs")

rep('The route expressions themselves remain unread.',
    'The route expressions themselves remain dashboard-only — re-confirmed Jun 10 against the live API, which exposes the route’s existence (one alert route, owned by the Systems Engineering team) but not its conditions. What it does expose is two-stage behavior: a matching alert raises a triage incident carrying a Team field, then the “DC ops Alerting path” workflow fires the escalation to that team’s path (Systems Esc, 5-minute ack).', "route-twostage")

rep('Surfaced the June 2 misroute in-thread (the paged on-call · the “how did that ping you” asker — the ticket\'s filer is unestablished, like the ticket).',
    'Surfaced the June 2 misroute in-thread (the paged on-call — acked in 19 s · the “how did that ping you” asker, who is also, per the recovered alert payload, the ticket\'s reporter: <a href=\'https://fluidstack.atlassian.net/browse/ATLASBUF-9203\' target=\'_blank\' rel=\'noreferrer\'>ATLASBUF-9203</a> was Joe\'s own filing).', "whoswho-june2")

# ---- code receipts ----
rrep(r'<p class="slede">dcim-api’s <span class="m">google\.go</span> starts[\s\S]*?only the activities registration was read\.</p>',
    '<p class="slede">dcim-api’s <span class="m">google.go</span> names Google’s <span class="m">RackTurnupWorkflow</span> on queue <span class="m">rack-turnup-task-queue</span> — and the trigger is gated off in code: <span class="m">TURNUP_WORKFLOW_DEPLOYED = false</span>, “Google has yet to actually deploy this workflow” (<a href="https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/internal/server/rack_workflows.go" target="_blank" rel="noreferrer">rack_workflows.go</a>). Production config resolves the endpoint question an earlier draft left open: dcim-api dials <b>Temporal Cloud</b> — <span class="m">ap-northeast-1.aws.api.temporal.io:7233</span>, namespace <span class="m">infrastructure.gdjny</span> (<a href="https://github.com/fluidstackio/dcim/blob/main/argocd/datacenters-prod/dcim-api/values.yaml" target="_blank" rel="noreferrer">argocd values</a>) — not the google-system frontend; that same-frontend inference, drawn from a queue name, is retired as wrong. Nor does site-worker host rack-turnup: it registers exactly four workflows (ProvisionRack, ProvisionMachine, Firmware, RunSiteLocal <a href="https://github.com/fluidstackio/systems/tree/main/projects/site-worker/internal" target="_blank" rel="noreferrer">↗</a>); the executing worker would be Google-deployed on that queue, which doesn’t exist yet — the code’s own TODO wonders whether their deployment will suffix it.</p>', "temporal-map-fix")

rrep(r"That's why the one FS→Google trigger's task queue, <span class='m'>google-workflows-site-worker-&lt;site&gt;</span>, carries its name\. Its two connections \(Temporal Cloud primary, google-system secondary\), the values\.yaml receipt, dcim-api's unread endpoint, and the same-frontend inference are laid out in",
    "Its task queue, <span class='m'>google-workflows-site-worker-&lt;site&gt;</span>, carries its name (dcim-api's prod config holds the same prefix for calls aimed at it). The FS→Google turn-up trigger targets a different queue — <span class='m'>rack-turnup-task-queue</span> — and is gated off in code pending Google deploying the workflow. Its two connections (Temporal Cloud primary, google-system secondary), the values.yaml receipt, and the retired same-frontend inference are laid out in", "drill-queue-fix")

rep('② the QA-handoff button at closure (rack checklists; whether ordinary repair-task closure fires it is unestablished)',
    '② the QA-handoff button at closure (rack checklists; console-button-only — repair-task closure never fires it: the checklist endpoint’s only writers are the console UI and the rack-scan inventory step, and dcim-tasks holds zero checklist references)', "census-qa")

rep('③ google.go’s turn-up trigger ·',
    '③ google.go’s turn-up trigger (in code but gated off — “Google has yet to actually deploy this workflow”; the Temporal map has the receipt) ·', "census-turnup")

rrep(r'What the dominant observed Request Type[\s\S]*?(?=</p>)',
    "The production map is now read: argocd's datacenters-prod values give site atlasbuf exactly two entries — <span class='m'>deployment</span> ← “Deployment” (requestTypeID 1669) and <span class='m'>compute_repair</span> ← “Compute or Network Device Repair” (1415) <a href='https://github.com/fluidstackio/dcim/blob/main/argocd/datacenters-prod/dcim-tasks/values.yaml#L45-L63' target='_blank' rel='noreferrer'>↗</a> — so the dominant observed Request Type maps to repair_type <span class='m'>deployment</span>, which EffectiveTaskType folds to task type <span class='m'>deployment</span>. The same values template dcim-tasks' create-side fields: cf_11171={entity_id}, cf_12271=“[{entity_id}] {title}”, cf_14592={maintenance_action}, cf_14593={unified_problem_id}.", "requesttype-map")

rep('One hop stays undescribed: the credential path that lets the bot write into fluidstack.atlassian.net (presumably a service account) is not established by anything this page read.',
    'The credential path is now read from code: when OAuthClientID is set, dcim-tasks uses an OAuth 2.0 client-credentials service account (token exchange at auth.atlassian.com), and prod sets exactly that — env JIRA_OAUTH_CLIENT_ID_ATLASBUF, fed by an ExternalSecret from AWS Secrets Manager key dcim-tasks/jira-credentials.', "bot-credential")

rrep(r"(label: \"Victor's simulated-repair test ticket — ATLASBUF-5\", url: \"[^\"]+\" \})",
    "\\1, { label: \"sync_worker.go — the bot's OAuth service-account path\", url: \"https://github.com/fluidstackio/dcim/blob/main/services/dcim-tasks/internal/jsm/sync_worker.go\" }", "genesis-link")

rep("The consumer list is a working-session citation<sup class=\"rf\"><a href=\"#ref-10\">[10]</a></sup>; Google's enumerated FISH access doesn't cover NetBox, and how the non-FS consumers reach feldspar isn't established here.",
    "The consumer list is a working-session citation<sup class=\"rf\"><a href=\"#ref-10\">[10]</a></sup>, but the access plumbing is now read from config: dcim-api-feldspar provisions NetBox users into feldspar-editor/-operations/-viewer groups keyed by Auth0 org — google (editor), google-contractor and ies-contractors (operations), google-viewonly and anthropic (viewer) <a href=\"https://github.com/fluidstackio/dcim/blob/main/argocd/datacenters-prod/dcim-api-feldspar/values.yaml\" target=\"_blank\" rel=\"noreferrer\">↗</a>.", "feldspar-access")

# ---- ref-10 restructure ----
new_ref10 = '''<li id="ref-10"><b>Recovered to permalinks since first writing (now cited inline at their sites):</b> Jason Legler on NetBox (“so tired”); Anshul's “not prod ready” answer; Sean Banko's “dependent of that decision” (which also receipts the SPOCS rack-role drift); Hannah's “not quite operational”; the June 2 misroute's full chain (ATLASBUF-9203 / INC-4681, via the incident.io API); Rob's Jun 1 → Jun 3 spec promise; the kickoff-adjacent Granola notes.<br><b>Still session-only (Apr–Jun Slack + the Jun 9 corpus-mining session):</b> Mike's “present as our equivalent” play; the kickoff's “Temporal Cloud + site-local workers” implementation direction; the May 22 validation-sweep storm (~100 tickets/2 h) and its hand-written TROSS SOP; the hospital-rack “100% repair-loop auditability” acceptance criterion and the hospital-rack process's origin window; JSM's email-on-transition notification behavior; Hannah assigning the BP ticket owners; the DCIM-API per-machine-credentials precedent (cited in d-auth); TQ's networking / FISH-fabric role description; the Kaiser-collision clause (ref 6); the Borneo-never-Jira working plan (implicit across the kickoff-to-freeze program; no single decision document records it); the NetBox direct-consumer list (Systems, Atlas, Google, DCIM); the CB3-as-Google-side-name attribution; who's-who role/affiliation descriptions not individually receipted (Mike's B300/Borneo roadmap ownership; Victor Blake's networking affiliation); the dcim-cmms-as-CUJ4-originator designation; the Wk 0–8 program plan, the reviewer roster (Anshul / Aaron / Sean), and Rob's draft's location — kickoff outputs with no recovered permalinks; Rob's readings of CUJ3 (“them sending us repairs”) and CUJ5 (a process, not an API).<br><b>Corpus statistics</b> — recomputed 2026-06-10 directly from the archived Jun 9 corpus dump (durations = resolution date − created on tickets carrying both, Physical Repair Tasks only): peak day 5,068 (Jun 3); densest 48-min window corpus-wide 1,127 tickets (Jun 3 12:29; Jun 4's densest window held 126 — the campaign itself was 114 tickets); rejection median ≈56 h over the timestamped subset (987 of the 2,671 repair-task rejections carry no resolve timestamp; corpus-wide Rejected is 2,686 incl. 15 rejected tickets of non-repair issue types); cycle p50 1.6 h, longest 72 d, early-era (Mar–Apr) p95 18.8 d; June's sweep volume collapsed the Done median (pre-June 6.0 h → June 1.0 h); oldest unresolved open/blocked ticket at crawl: 42 d. The earlier session's headline figures (peak ~2,900/day; rejection median 44 h; cycle p50 8.9 h / p95 22 d) did not reproduce from the archive under any slice tried and are retired.</li>'''
rrep(r'<li id="ref-10">[\s\S]*?</li>', new_ref10, "ref10-rewrite")

print("OK:", len(ok), ok)
print("MISS:", miss)
open(FILE, "w").write(s)

# audits
m = re.search(r'<script>([\s\S]*)</script>', s)
import subprocess, json, tempfile
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
    f.write("new Function(" + json.dumps(m.group(1)) + "); console.log('JS parses OK')")
    p = f.name
print(subprocess.run(['node', p], capture_output=True, text=True).stdout.strip() or "JS PARSE FAILED")
ev = re.search(r'const EVENTS\s*=\s*\[([\s\S]*?)\n\];', s)
bad = re.findall(r'(?:title|summary|detail)\s*:\s*"[^"]*<a ', ev.group(1)) if ev else []
print("EVENTS html-in-string violations:", len(bad))
