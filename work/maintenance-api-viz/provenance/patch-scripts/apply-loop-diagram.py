#!/usr/bin/env python3
import re, json, subprocess, tempfile
BASE_DIR = "/Users/andrew/code/personal/toolbox/work/maintenance-api-viz"
ok, miss = [], []
def rep_file(path, old, new, tag, n=1):
    p = f"{BASE_DIR}/{path}"
    s = open(p).read()
    c = s.count(old)
    if c != n: miss.append(f"{tag} ({c})"); return
    open(p, "w").write(s.replace(old, new)); ok.append(tag)

DC = "https://github.com/fluidstackio/dcim/blob/b6eea015af01044ce5c41aaa8e29bb655557a2f7"
IM = "https://github.com/fluidstackio/infrastructure-management/blob/479bc10"
MATRIX = "https://fluidstack.atlassian.net/wiki/spaces/HWOps/pages/622919690/Data+Center+Repair+Escalation+Matrix"
HWAAS = "https://docs.google.com/document/d/1oFGmVgo6_0zQdJR2h554vN5GPMRetA0gcN88Z9PxtuU/edit"

# ============ 1. THE 01·LOOP BLOCK ============
LOOP = '''

  <div class="sub" id="loop"><span class="sk2">01·LOOP</span><h3>The repair loop, end to end — as it runs today</h3></div>
  <p class="slede">The unit of the seam isn’t a ticket — it’s a <b>round trip</b>: broken machine out of Google’s pool, fixed machine back, no human on Google’s side. Every box below is shipped code or measured corpus behavior; the two stages history never built — classify/acknowledge and assignment — are drawn as they actually are (researched live, Jun 11). Click any box for mechanism and receipts.</p>
  <div class="diawrap"><svg class="wide" viewBox="0 0 1480 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The repair loop today: Google's doctors detect and file; the workflow parks; FluidStack mirrors the ticket, techs self-claim, execute the SOP, and the Done transition wakes the workflow; failures refile.">
      <defs>
        <marker id="ah7" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#5a5a5a"/></marker>
        <marker id="ahg7" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#A8E05F"/></marker>
      </defs>
      <rect class="sv-zone" x="18" y="40" width="1444" height="132"/>
      <text class="sv-zl g" x="32" y="60">GOOGLE’S ENGINE · TEMPORAL IN GOOGLE-SYSTEM — THEIR CODE, OUR CLUSTER</text>
      <rect class="sv-zone" x="18" y="204" width="1444" height="124"/>
      <text class="sv-zl" x="32" y="224">THE SEAM · ATLASBUF — JIRA SERVICE MANAGEMENT</text>
      <rect class="sv-zone" x="18" y="360" width="1444" height="146"/>
      <text class="sv-zl" x="32" y="380">FLUIDSTACK’S FLOOR · DCIM-TASKS → CONSOLE → HANDS</text>

      <g data-d="u-diag">
        <rect class="sv-box" x="40" y="72" width="212" height="86" rx="4"/>
        <text class="sv-t" x="54" y="96">① DETECT &amp; DECIDE</text>
        <text class="sv-m" x="54" y="118">machine-doctor · ocs-link ·</text>
        <text class="sv-m" x="54" y="134">link-repair · rack-turnup QA</text>
        <text class="sv-s" x="54" y="150">emits (entity · code · action)</text>
      </g>
      <g data-d="s-ticket">
        <rect class="sv-box" x="306" y="72" width="212" height="86" rx="4"/>
        <text class="sv-t" x="320" y="96">② FILE</text>
        <text class="sv-m" x="320" y="118">Ext-Bloom-Atlas-Workflows</text>
        <text class="sv-m" x="320" y="134">5 templated fields · RT 1669</text>
        <text class="sv-s" x="320" y="150">storms: 1,127 in 48 min</text>
      </g>
      <g data-d="s-paused">
        <rect class="sv-box" x="572" y="72" width="212" height="86" rx="4"/>
        <text class="sv-t" x="586" y="96">③ PARK</text>
        <text class="sv-m" x="586" y="118">watches the status field</text>
        <text class="sv-s" x="586" y="134">“Close this ticket … to</text>
        <text class="sv-s" x="586" y="150">resume the workflow”</text>
      </g>
      <g data-d="u-flows">
        <rect class="sv-box" x="1230" y="72" width="212" height="86" rx="4"/>
        <text class="sv-t" x="1244" y="96">⑨ WAKE &amp; VERIFY</text>
        <text class="sv-m" x="1244" y="118">Done resumes · re-runs QA</text>
        <text class="sv-s" x="1244" y="134">refile on fail — Attempt++</text>
        <text class="sv-s" x="1244" y="150">their workers, not ours</text>
      </g>

      <g data-d="s-pathA">
        <rect class="sv-box" x="40" y="236" width="212" height="78" rx="4"/>
        <text class="sv-t" x="54" y="260">LISTENER A · INCIDENT.IO</text>
        <text class="sv-m" x="54" y="282">repairs land as P4 alerts</text>
        <text class="sv-s" x="54" y="298">no paging route matches</text>
      </g>
      <g data-d="p-tkt">
        <rect class="sv-box" x="306" y="236" width="212" height="78" rx="4"/>
        <text class="sv-t" x="320" y="260">THE TICKET</text>
        <text class="sv-m" x="320" y="282">Physical Repair Task</text>
        <text class="sv-s" x="320" y="298">priority Medium = Jira default</text>
      </g>
      <rect class="sv-chip" x="1000" y="252" width="240" height="24" rx="4"/>
      <text class="sv-chipt" x="1010" y="268">the status transition — the only return signal</text>

      <g data-d="p-sync">
        <rect class="sv-box" x="40" y="396" width="212" height="92" rx="4"/>
        <text class="sv-t" x="54" y="420">④ MIRROR</text>
        <text class="sv-m" x="54" y="442">dcim-tasks polls 5m / 10m</text>
        <text class="sv-s" x="54" y="458">webhook built · dark (Mar 28)</text>
      </g>
      <g data-d="l-classify">
        <rect class="sv-box" x="306" y="396" width="212" height="92" rx="4"/>
        <text class="sv-t" x="320" y="420">⑤ CLASSIFY / ACK — NONE</text>
        <text class="sv-m" x="320" y="442">Severity field: never used</text>
        <text class="sv-m" x="320" y="458">SLA clocks: never run</text>
        <text class="sv-s" x="320" y="474">contract Sev1–4 unmapped</text>
      </g>
      <g data-d="l-assign">
        <rect class="sv-box" x="572" y="396" width="212" height="92" rx="4"/>
        <text class="sv-t" x="586" y="420">⑥ ASSIGN — SELF-CLAIM</text>
        <text class="sv-m" x="586" y="442">techs take tickets themselves</text>
        <text class="sv-m" x="586" y="458">81% never assigned in Jira</text>
        <text class="sv-s" x="586" y="474">lead-routing role: 2 days old</text>
      </g>
      <g data-d="p-task">
        <rect class="sv-box" x="838" y="396" width="212" height="92" rx="4"/>
        <text class="sv-t" x="852" y="420">⑦ EXECUTE</text>
        <text class="sv-m" x="852" y="442">pinned, versioned SOP</text>
        <text class="sv-s" x="852" y="458">guide panels on the task</text>
      </g>
      <g data-d="p-done">
        <rect class="sv-box" x="1104" y="396" width="212" height="92" rx="4"/>
        <text class="sv-t" x="1118" y="420">⑧ CLOSE</text>
        <text class="sv-m" x="1118" y="442">outbound sync writes Done</text>
        <text class="sv-s" x="1118" y="458">≤30s after console completion</text>
      </g>

      <path class="sv-edge g" d="M252 115 H 300" marker-end="url(#ahg7)"/>
      <path class="sv-edge g" d="M518 115 H 566" marker-end="url(#ahg7)"/>
      <path class="sv-edge g" d="M412 158 V 230" marker-end="url(#ahg7)"/>
      <text class="sv-s" x="424" y="196">files</text>
      <path class="sv-edge" d="M306 275 H 258" marker-end="url(#ah7)"/>
      <path class="sv-edge" d="M340 314 V 352 H 146 V 390" marker-end="url(#ah7)"/>
      <text class="sv-s" x="170" y="345">listener B — the mirror</text>
      <path class="sv-edge" d="M252 442 H 300" marker-end="url(#ah7)"/>
      <path class="sv-edge" d="M518 442 H 566" marker-end="url(#ah7)"/>
      <path class="sv-edge" d="M784 442 H 832" marker-end="url(#ah7)"/>
      <path class="sv-edge" d="M1050 442 H 1098" marker-end="url(#ah7)"/>
      <path class="sv-edge" d="M1210 396 V 276 H 1240" marker-end="url(#ah7)"/>
      <path class="sv-edge g" d="M1240 264 H 1336 V 164" marker-end="url(#ahg7)"/>
      <path class="sv-edge g" d="M784 115 H 1224" marker-end="url(#ahg7)"/>
      <text class="sv-s" x="940" y="106">wakes on Done</text>
      <path class="sv-edge g" d="M1336 72 V 28 H 412 V 66" marker-end="url(#ahg7)"/>
      <text class="sv-s" x="700" y="20">refile on failed re-QA — the Attempt counters in the corpus</text>
    </svg></div>
    <p class="scrollhint">↔ scroll the diagram sideways for the full loop · stages ⑤ and ⑥ are the two the floor never built — both researched live Jun 11 (their boxes carry the receipts)</p>
  <p class="dhint">▸ <b>solid boxes drill down</b> — mechanism, real exemplars, receipts</p>
'''
rep_file("src/10-seam.html",
    'The rewired map and receipts: <a href="#temporal-map">the Temporal map below</a>.</p>',
    'The rewired map and receipts: <a href="#temporal-map">the Temporal map below</a>.</p>' + LOOP,
    "loop-block")

# ============ 2. NEW DRILLS ============
DRILLS = '''"l-classify": { k: "TODAY · LOOP ⑤", t: "Classify & acknowledge — nothing happens, measurably",
    body: "<p>When a machine-filed ticket lands, no classification or acknowledgment fires — and that's measured, not assumed (researched live, Jun 11). Priority: every machine-filed Physical Repair Task carries <span class='m'>Medium</span>, Jira's default — exactly one PRT in the project's history has any other priority, and a human set it (<a href='https://fluidstack.atlassian.net/browse/ATLASBUF-4063' target='_blank' rel='noreferrer'>ATLASBUF-4063</a>, “Highest”).</p><p>A <span class='m'>Severity</span> field exists in the ATLASBUF schema (cf_10071) and has never been populated on any PRT (JQL: zero results). JSM SLA fields exist too — “Time to first response” (cf_10083), “Time to resolution” (cf_10082) — but <span class='m'>everBreached()</span> and its negation both return zero across the whole project: no SLA clock has ever run. ATLASBUF is a service_desk project, so the clocks are configurable; they're just not configured.</p><p>Nothing pages, either: dcim-tasks has no paging integration (grep for priority/severity/sla in production code: zero), a unit test certifies that a Jira priority change is an explicit no-op in the webhook handler, and the “P4” the Path A story mentions is incident.io's <i>alert</i> priority, not a Jira field. At project birth this was deferred on purpose — the Mar 24–27 setup-era test tickets literally say “Add sev later”.</p><p><b>The taxonomy already exists on paper, twice.</b> The signed Google contract (Attachment E §5, Table 2) binds FS to per-ticket severity with clocks — Sev1: 15-min response, work within 30 min, 4-hr resolution, credits attached <a href='" + HWAAS_URL + "' target='_blank' rel='noreferrer'>↗</a>. And FS's own <a href='" + MATRIX_URL + "' target='_blank' rel='noreferrer'>Data Center Repair Escalation Matrix</a> (DC Operations, Approved, Apr 30) designs P4–P0 “auto-assigned at ticket intake based on classification” — with its “auto-paging integration” prerequisite still unchecked in the page's own checklist.</p><p><b>Spec consequence:</b> severity is where the contract meets the routing-class plank — the API has to carry or derive it, because today's floor runs entirely on the absence, and the contract's clocks have nothing to start against.</p>",
    facts: [
      { l: "the four empty surfaces", v: "priority = Medium default (1 exception ever, human) · Severity cf_10071 = never populated · SLA clocks cf_10082/10083 = never run (everBreached() and negation both 0) · paging on PRT creation = none" },
      { l: "designed, not wired", v: "Escalation Matrix P4–P0 “auto-assigned at ticket intake” — Approved Apr 30, auto-paging checkbox unchecked · contract Sev1–4 with clocks — signed, unmapped to any field" }],
    links: [
      { label: "Data Center Repair Escalation Matrix (Confluence)", url: "MATRIX_URL" },
      { label: "HWaaS contract [SIGNED] — Attachment E (SLA)", url: "HWAAS_URL" },
      { label: "the one non-Medium PRT ever (ATLASBUF-4063)", url: "https://fluidstack.atlassian.net/browse/ATLASBUF-4063" },
      { label: "Talal, Apr 9 — SEV vs Priority vocabulary; SLAs “we will define together”", url: "https://fluidstack.enterprise.slack.com/archives/C0AC62DTVT2/p1775747152644979" }] },
  "l-assign": { k: "TODAY · LOOP ⑥", t: "Assignment — self-claim, when it happens at all",
    body: "<p>The mechanism, from code: exactly one write path — the <span class='m'>AssignTask</span> SQL (<span class='m'>UPDATE tasks SET assigned_to</span>) with three callers in the whole dcim repo: the console's REST endpoint, the Jira webhook's assignee-changelog path, and the 10-minute drift reconciler <a href='" + DC_URL + "/services/dcim-tasks/internal/db/query.sql#L60-L70' target='_blank' rel='noreferrer'>↗</a>. No round-robin, no auto-assign, no claim button: FluidStack runs round-robin on other projects (MNT, IAT) — never on ATLASBUF.</p><p>The behavior, from live changelogs (Jun 10–11 sample): <b>techs assign themselves</b> — 5 of 6 recent assigned PRTs were self-claims, 50 seconds to 44 minutes after creation; the sixth was routed by the ticket's human <i>creator</i>, not a dispatcher. The dcim-tasks bot has never changed a Jira assignee (JQL CHANGED BY: zero), so the console's assign path — a searchable “Assigned To” combobox fed by Jira's project-assignable users, permission-gated (anthropic, view-only and contractor orgs can't), with a ≤30s outbound sync built — has effectively never fired in anger. Assignment lives in Jira.</p><p>The numbers, from the corpus: only <b>19.35%</b> of issues ever carry an assignee; <b>79.1% of Done tickets finished never-assigned</b>. The skew is the story — HW: summaries 63.3% assigned vs SW: 10.4%; human-filed 71.3% vs bot-filed 15.4% — and the two assignee populations barely overlap (bot-filed work lands on Robi Buranyi / Marco Li / James Chacon; human-filed on Jake Rettig / jsmorton / cameron b judd).</p><p>The “DCO lead routes” model this page used to assert is a role, not yet a mechanism: as of Apr 14 the queues “all go to Unassigned” with ownership an open question (Victor Blake); on <b>Jun 9</b> Johntaan Gonzalez-Najera — “Hardware lead for BUF site” — was granted JSM admin explicitly “to assign and check tickets for DCTs”. Two days later, 100+ open PRTs created Jun 8–11 sat unassigned.</p><p><b>Spec consequence:</b> there is no assignment surface for the API to inherit — “who works it” is FS-internal and currently informal. That's fine for the contract boundary (Google never asked), but the contract's response clocks (l-classify) have to start against <i>something</i>, and today nothing marks “a human has this”.</p>",
    facts: [
      { l: "write path", v: "one SQL (AssignTask) · three callers: console PUT /v1alpha1/tasks/{id}/assign · webhook changelog · 10-m drift — zero automation for ATLASBUF" },
      { l: "observed", v: "self-claim 5/6 (50s–44m) · creator-routed 1/6 · dcim-tasks bot: 0 Jira assignee writes ever · 19.35% ever assigned · 79.1% of Done never assigned" }],
    links: [
      { label: "a self-claim exemplar (ATLASBUF-17206 — James Kim, 29m42s in)", url: "https://fluidstack.atlassian.net/browse/ATLASBUF-17206" },
      { label: "AssignTask — the only assignee write (query.sql)", url: "DC_URL/services/dcim-tasks/internal/db/query.sql#L60-L70" },
      { label: "the console's Assigned To combobox (RepairsLayout.tsx)", url: "IM_URL/services/dcim-console/src/pages/repairs/RepairsLayout.tsx" },
      { label: "Jun 9 — the lead-assignment role gets its permissions", url: "https://fluidstack.enterprise.slack.com/archives/C09TLSKHD27/p1781017323769809" },
      { label: "Apr 14 — “all go to Unassigned”, ownership an open question", url: "https://fluidstack.enterprise.slack.com/archives/C0AHL7USP4P/p1776189277334409" },
      { label: "open + unassigned PRTs right now (JQL)", url: "https://fluidstack.atlassian.net/issues/?jql=project%20%3D%20ATLASBUF%20AND%20issuetype%20%3D%20%22Physical%20Repair%20Task%22%20AND%20assignee%20is%20EMPTY%20AND%20statusCategory%20!%3D%20Done%20ORDER%20BY%20created%20DESC" }] },
  '''
DRILLS = DRILLS.replace('" + HWAAS_URL + "', HWAAS).replace('" + MATRIX_URL + "', MATRIX).replace('" + DC_URL + "', DC)
DRILLS = DRILLS.replace('"MATRIX_URL"', f'"{MATRIX}"').replace('"HWAAS_URL"', f'"{HWAAS}"')
DRILLS = DRILLS.replace('"DC_URL/services', f'"{DC}/services').replace('"IM_URL/services', f'"{IM}/services')
rep_file("src/70-data-drills.js", '"s-tenancy": {', DRILLS + '"s-tenancy": {', "new-drills")

# ============ 3. DCO-LEAD CORRECTIONS ============
rep_file("src/10-seam.html",
    'DCO (DC-ops) lead routes → hands repair',
    'hands self-claim (a lead can route) → repair',
    "dco-1-btoday-svg")
rep_file("src/20-routing.html",
    'Lands unassigned; a <b>DCO (Data-Center Operations) lead routes it</b> (Slack @-mention or JSM assignment',
    'Lands unassigned — and 79% of Done tickets stay that way; the observed norm is <b>tech self-claim</b> (assignment researched live Jun 11: <a href="#loop">01·LOOP</a> ⑥). A DCO (Data-Center Operations) lead <i>can</i> route (Slack @-mention or JSM assignment',
    "dco-2-assignment-row")
rep_file("src/20-routing.html",
    'Data-Center Operations — the humans at the site. Leads triage and route the queue; technicians (“hands”) walk the floor and do the repair.',
    'Data-Center Operations — the humans at the site. Technicians (“hands”) walk the floor, do the repair, and mostly route themselves (self-claim); a dedicated lead-assignment role was formalized Jun 9 (<a href="#loop">01·LOOP</a> ⑥).',
    "dco-3-decoder-row")
rep_file("src/20-routing.html",
    "a ticket becomes a task; a DCO lead assigns it; the tech opens it in the console",
    'a ticket becomes a task; the tech claims it (self-assign is the observed norm — <a href="#loop">01·LOOP</a> ⑥; a lead can route); the tech opens it in the console',
    "dco-4-loop-sentence")
rep_file("src/20-routing.html",
    'the console queues it, a DCO lead routes hands, and the status transition',
    'the console queues it, hands claim work, and the status transition',
    "dco-5-aria")
rep_file("src/20-routing.html",
    '>DCO lead routes → hands repair</text>',
    '>hands self-claim (or lead routes) → repair</text>',
    "dco-6-pipeline-svg")
rep_file("src/70-data-drills.js",
    'a DCO lead routes it; hands execute; the status transition flows back.',
    "hands claim and execute it (assignment is mostly self-claim — <a href='#loop'>01·LOOP</a> ⑥); the status transition flows back.",
    "dco-7-spathB")
rep_file("src/70-data-drills.js",
    '"p-route": { k: "PIPELINE 5 · ROUTE + EXECUTE", t: "A DCO lead routes; hands repair",\n    body: "<p>Assignment is human: Slack @-mention or JSM assignment by a DC-ops lead.',
    '"p-route": { k: "PIPELINE 5 · ROUTE + EXECUTE", t: "Hands claim; hands repair (leads can route)",\n    body: "<p>Assignment is human and mostly self-service: the tech sets the Jira assignee to themselves — 5 of 6 sampled June changelogs, 50s–44m after creation; leads can route (the May 22 TROSS assignment), and a dedicated lead role got its permissions Jun 9. The numbers and the write-path live on <a href=\'#loop\'>01·LOOP</a>\'s assignment box.',
    "dco-8-proute")

print("OK:", len(ok), ok)
print("MISS:", miss)
if miss: raise SystemExit("ABORT")

# ============ build + battery ============
print(subprocess.run(["make", "build"], capture_output=True, text=True, cwd=BASE_DIR).stdout.strip())
print(subprocess.run(["make", "check"], capture_output=True, text=True, cwd=BASE_DIR).stdout.strip() or "check FAILED")
s = open(f"{BASE_DIR}/maintenance-api.html").read()
m = re.search(r'<script>([\s\S]*)</script>', s)
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
    f.write("try { new Function(" + json.dumps(m.group(1)) + "); console.log('JS parses OK') } catch(e) { console.log('JS ERROR:', e.message) }")
    p = f.name
print(subprocess.run(['node', p], capture_output=True, text=True).stdout.strip())
ev = s[s.find('const EVENTS'):s.find('];', s.find('const EVENTS'))]
bad = [t[:60] for t in re.findall(r'(?:title|summary|detail|specImpact):\s*"([^"]*)"', ev) if '<' in t]
print("EVENTS html-in-string:", bad if bad else "clean")
ids = set(re.findall(r'id="([^"]+)"', s)) | set(re.findall(r"id='([^']+)'", s))
ev_ids = set(re.findall(r'id:\s*"([^"]+)"', ev))
dead = [h for h in set(re.findall(r'href=[\'"]#([^\'"]+)[\'"]', s)) if h not in ids and not (h.startswith('ev-') and h[3:] in ev_ids)]
print("dead anchors:", sorted(dead))
# drill key wiring: every data-d has a DRILL key
dr = s[s.find('const DRILL'):s.find('const EVENTS')]
keys = set(re.findall(r'"([a-z0-9-]+)":\s*\{\s*k:', dr))
hooks = set(re.findall(r'data-d="([a-z0-9-]+)"', s))
print("data-d without DRILL key:", sorted(hooks - keys))
