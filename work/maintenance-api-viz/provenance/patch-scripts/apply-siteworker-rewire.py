#!/usr/bin/env python3
import re, json, subprocess, tempfile
FILE = "/Users/andrew/code/personal/toolbox/work/maintenance-api-viz/maintenance-api.html"
BASE = "/Users/andrew/code/personal/toolbox/work/maintenance-api-viz/provenance/inventory-v88.json"
s = open(FILE).read()
ok, miss = [], []
def rep(old, new, tag):
    global s
    c = s.count(old)
    if c != 1: miss.append(f"{tag} ({c})"); return
    s = s.replace(old, new); ok.append(tag)

SY = "https://github.com/fluidstackio/systems/blob/34e92787301ccdd6da52382a69bed18e3b1f2b07"
DC = "https://github.com/fluidstackio/dcim/blob/b6eea015af01044ce5c41aaa8e29bb655557a2f7"

# ===== A: census follow-up paragraph (static HTML) =====
rep("And <span class=\"m\">site-worker</span>'s secondary connection registers it on Google's Temporal to execute FS-side activities for their workflows — execution plumbing inside the workflows, not a way to request a repair. Which connection is primary, which secondary, and the receipts: <a href=\"#temporal-map\">the Temporal map below</a>. The registration and activity code are the receipts; live dispatch traffic wasn't read.",
    "And <span class=\"m\">site-worker</span> dials Google's Temporal only as a <i>client</i> — its worker, and every activity it can run, registers solely on Temporal Cloud, so a workflow on Google's engine cannot call site-worker activities at all (Temporal can't schedule activities across clusters). <b>Corrected Jun 11:</b> the earlier reading here — that it registers on Google's Temporal to execute activities for their workflows — is retired. What the dial actually is: FS's gateway <i>into</i> their instance, a bridge workflow that starts a named workflow there and polls it to completion — built, and so far caller-less. The rewired map and receipts: <a href=\"#temporal-map\">the Temporal map below</a>.",
    "A-census-follow")

# ===== B: census row 5 =====
rep('<div class="r"><span>⑤ site-worker’s activity execution</span><span>no — activity plumbing</span><span>laid out in <a href="#temporal-map">the Temporal map</a></span></div>',
    '<div class="r"><span>⑤ site-worker’s client dial into Google’s Temporal — the bridge</span><span>no — an FS→Google start path, built with zero callers</span><span>corrected Jun 11 — <a href="#temporal-map">the Temporal map</a> carries the rewire</span></div>',
    "B-census-row5")

# ===== C1: 01·MAP wiring paragraph =====
rep('holds both connections in one base config — <a href="https://github.com/fluidstackio/systems/blob/main/gitops/apps/fish-base/site-worker/values.yaml" target="_blank" rel="noreferrer">values.yaml</a> names Temporal Cloud as the primary and <span class="m">temporal-frontend.google-system:7233</span> as a <span class="m">localTemporalInstance</span> (secondary). On the secondary it executes the FS-side activities Google’s workflows call — machine netboot/reset, NetBox reads, ping checks — with the registration and the <a href="https://github.com/fluidstackio/systems/tree/main/projects/site-worker/internal/activities" target="_blank" rel="noreferrer">activities tree</a> as the receipts; live dispatch traffic wasn’t read.</p>',
    f'holds both connections in one base config — <a href="{SY}/gitops/apps/fish-base/site-worker/values.yaml#L1-L10" target="_blank" rel="noreferrer">values.yaml</a> names Temporal Cloud as the worker home and <span class="m">temporal-frontend.google-system:7233</span> as a <span class="m">localTemporalInstance</span>, dialed as a client only.</p>\n    <p class="slede"><b>Corrected Jun 11 — the direction was wrong here.</b> <span class="m">worker.New()</span> appears exactly once in site-worker, against the Temporal Cloud client (<a href="{SY}/projects/site-worker/cmd/site-worker/main.go#L87" target="_blank" rel="noreferrer">main.go:87</a>), so its activities — machine netboot/reset, NetBox reads, ping checks (<a href="https://github.com/fluidstackio/systems/tree/main/projects/site-worker/internal/activities" target="_blank" rel="noreferrer">the activities tree</a>) — register only there, and a workflow on Google’s engine cannot call them: Temporal can’t schedule activities across clusters. The earlier “on the secondary it executes the FS-side activities Google’s workflows call” reading is retired; if rack-turnup’s QA phase resets machines, it does that through Google’s own workers, not site-worker. The google-system dial serves the opposite direction: <span class="m">RunSiteLocalWorkflow</span> starts a named workflow on the local instance and polls it to completion, and its doc comment sets the direction outright — “Callers on the central Temporal instance invoke this as a child workflow, targeting the task queue of the desired site-worker, which then drives the local instance interaction” (<a href="{SY}/projects/site-worker/internal/localtemporalinstance/workflow.go#L36-L39" target="_blank" rel="noreferrer">workflow.go:36-39</a>).</p>\n    <p class="slede">So site-worker is FS’s arm <i>at the site</i> — netboot/reset/ping need device-network reachability, and only something in-cluster can reach <span class="m">temporal-frontend.google-system</span> — and FS’s gateway into Google’s Temporal, not their activity worker. Its queue <span class="m">google-workflows-site-worker-&lt;site&gt;</span> is a Temporal Cloud queue (<a href="{SY}/gitops/apps/clusters/buf101/site-worker/values.yaml#L3" target="_blank" rel="noreferrer">buf101 values:3</a>) — the prefix describes purpose, not location. Zero callers of <span class="m">RunSiteLocalWorkflow</span> (or of site-worker’s own <span class="m">ProvisionRackWorkflow</span>/<span class="m">ProvisionMachineWorkflow</span>) exist outside site-worker in either repo: the whole FS→Google start path is built but unexercised.</p>',
    "C1-tmap-rewire")

# ===== C2: turn-up trigger paragraph — TODO-bridge note (scoped to the temporal-map region) =====
tm = s.find('id="temporal-map"')
gate = s.find('TURNUP_WORKFLOW_DEPLOYED = false', tm)
pend = s.find('</p>', gate)
if tm > 0 and gate > 0 and pend > 0 and pend - tm < 8000:
    note = (' The same file’s later TODO asks whether the dial “should be a separate temporal client for the on-prem deployed control plane?” '
            f'(<a href="{DC}/services/dcim-api/internal/server/rack_workflows.go#L159" target="_blank" rel="noreferrer">rack_workflows.go:159</a>) — '
            'the bridge reads as that answer: the sanctioned FS→Google start would be a <span class="m">RunSiteLocalWorkflow</span> child on site-worker’s queue, not a direct dial. Nothing calls it yet.')
    s = s[:pend] + note + s[pend:]
    ok.append("C2-todo-bridge")
else:
    miss.append(f"C2 (tm={tm} gate={gate} pend={pend})")

# ===== C3: dcim-api prefix — staged, not live (same map region mentions it via u-fs; the inert note rides D) =====

# ===== D: u-fs facts (DRILL, single-quoted) =====
rep("Its task queue, <span class='m'>google-workflows-site-worker-&lt;site&gt;</span>, carries its name (dcim-api's prod config holds the same prefix for calls aimed at it). The FS→Google turn-up trigger targets a different queue — <span class='m'>rack-turnup-task-queue</span> — and is gated off in code pending Google deploying the workflow. Its two connections (Temporal Cloud primary, google-system secondary), the values.yaml receipt, and the retired same-frontend inference are laid out in <a href='#temporal-map'>the Temporal map</a> in 01",
    f"Its task queue, <span class='m'>google-workflows-site-worker-&lt;site&gt;</span>, is a Temporal Cloud queue — the prefix names purpose, not location (dcim-api's prod config holds the same prefix <a href='{DC}/argocd/datacenters-prod/dcim-api/values.yaml#L71' target='_blank' rel='noreferrer'>↗</a>, but staged-not-live: the Go config field is read by nothing <a href='{DC}/services/dcim-api/internal/config/temporal.go#L8' target='_blank' rel='noreferrer'>↗</a>). The FS→Google turn-up trigger targets a different queue — <span class='m'>rack-turnup-task-queue</span> — and is gated off in code pending Google deploying the workflow. Its wiring — worker home on Temporal Cloud, a client-only dial into google-system (the caller-less RunSiteLocalWorkflow bridge), the values.yaml receipt, and the retired secondary-worker inference (corrected Jun 11) — is laid out in <a href='#temporal-map'>the Temporal map</a> in 01",
    "D-ufs-facts")

# ===== D2: u-fs api fact — sharpened spec point =====
rep("<a href='#ev-d-revalidate'>d-revalidate</a> covers the closure half only\" }],",
    "<a href='#ev-d-revalidate'>d-revalidate</a> covers the closure half only. Sharpened by the Jun 11 rewire: FS-initiated flows don't pass through Google's workflow layer at all today — FS can't even start one except through a bridge nobody calls — so repairs born FS-side have no natural path into the ticket-filing machinery this API replaces; treating them as first-class API resources has to be designed in, not inherited\" }],",
    "D2-spec-point")

# ===== E: s-tenancy =====
rep("The seam is mutual: FS's site-worker points at <span class='m'>temporal-frontend.google-system:7233</span> — Google's Temporal frontend <a href='https://github.com/fluidstackio/systems/blob/main/gitops/apps/fish-base/site-worker/values.yaml' target='_blank' rel='noreferrer'>↗</a>, their namespace, our cluster. That is its secondary connection; the full map is <a href='#temporal-map'>the Temporal map</a> in 01.",
    f"The seam is mutual in presence, one-directional in code: FS's site-worker dials <span class='m'>temporal-frontend.google-system:7233</span> — Google's Temporal frontend <a href='{SY}/gitops/apps/fish-base/site-worker/values.yaml#L7-L10' target='_blank' rel='noreferrer'>↗</a>, their namespace, our cluster — but as a client only (the RunSiteLocalWorkflow bridge; its own worker registers solely on Temporal Cloud, so their workflows can't call its activities — corrected Jun 11). The full map: <a href='#temporal-map'>the Temporal map</a> in 01.",
    "E-tenancy")

print("OK:", len(ok), ok)
print("MISS:", miss)
if miss: raise SystemExit("ABORT: misses present, file NOT written")
open(FILE, "w").write(s)

# class-elimination check: any surviving secondary-connection language near site-worker
leftover = [m.start() for m in re.finditer(r'secondary', s)]
ctx = [s[max(0,i-80):i+80].replace('\n',' ') for i in leftover]
sw = [c for c in ctx if 'site-worker' in c or 'worker' in c]
print("surviving 'secondary' near worker-context:", sw if sw else "none")

m = re.search(r'<script>([\s\S]*)</script>', s)
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
    f.write("try { new Function(" + json.dumps(m.group(1)) + "); console.log('JS parses OK') } catch(e) { console.log('JS ERROR:', e.message) }")
    p = f.name
print(subprocess.run(['node', p], capture_output=True, text=True).stdout.strip())
ev = s[s.find('const EVENTS'):s.find('];', s.find('const EVENTS'))]
bad = [t[:80] for t in re.findall(r'(?:title|summary|detail|specImpact):\s*"([^"]*)"', ev) if '<' in t]
print("EVENTS html-in-string:", bad if bad else "clean")
ids = set(re.findall(r'id="([^"]+)"', s)) | set(re.findall(r"id='([^']+)'", s))
ev_ids = set(re.findall(r'id:\s*"([^"]+)"', ev))
dead = [h for h in set(re.findall(r'href=[\'"]#([^\'"]+)[\'"]', s)) if h not in ids and not (h.startswith('ev-') and h[3:] in ev_ids)]
print("dead anchors:", sorted(dead))
base = json.load(open(BASE))
hrefs = set(re.findall(r'href=[\'"]([^\'"]+)[\'"]', s))
nums = set(re.findall(r'\b\d[\d,]*(?:\.\d+)?%?\b', s))
print("href removals:", sorted(set(base['hrefs']) - hrefs))
print("num removals:", sorted(set(base['nums']) - nums))
