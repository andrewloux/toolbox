#!/usr/bin/env python3
import re, json, subprocess, tempfile
FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html"
s = open(FILE).read()
ok, miss = [], []

def rep(old, new, tag, n_expected=1):
    global s
    n = s.count(old)
    if n != n_expected:
        miss.append(f"{tag} (count={n})"); return
    s = s.replace(old, new); ok.append(tag)

GGO = '<a href="https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/internal/server/google.go" target="_blank" rel="noreferrer"><span class="m">google.go</span></a>'
RWF = "https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/internal/server/rack_workflows.go"

# --- HIGH: turnup origin reconciled at every site ---
rep('<text class="sv-m" x="36" y="318">turnup repairs descend from our call</text>',
    '<text class="sv-m" x="36" y="318">turnup runs: Google-started; our hook gated</text>', "svg-label")

rep('One of the three trigger classes is ours — ' + GGO + ' starting <span class="m">RackTurnupWorkflow</span> is the only FS→Google workflow pointer, and turnup-phase repair tickets descend from that call.</p>',
    'The third trigger class is written to be ours — ' + GGO + ' naming <span class="m">RackTurnupWorkflow</span> is the only FS→Google workflow pointer — but it is gated off in code (<span class="m">TURNUP_WORKFLOW_DEPLOYED = false</span>), so the runs filing today\'s tickets are not FS-started: rack-turnup, like the doctors, starts on Google\'s side, and FS holds no live trigger for any family member in anything read. The gated hook marks intent — the start path the API era expects — and the Temporal map carries its receipts.</p>', "diacap-trigger")

rep("<p><a href='https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/internal/server/google.go' target='_blank' rel='noreferrer'><span class='m'>dcim-api/internal/server/google.go</span></a> starts <span class='m'>RackTurnupWorkflow</span> by string name + task queue. When that workflow's QA phase fails, <b>it</b> files the repair ticket — so turnup-phase repairs descend from a FluidStack call even though the filing code is Google's.</p>",
    "<p><a href='https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/internal/server/google.go' target='_blank' rel='noreferrer'><span class='m'>dcim-api/internal/server/google.go</span></a> names <span class='m'>RackTurnupWorkflow</span> by string + task queue — a written FS start path, gated off in code: <span class='m'>TURNUP_WORKFLOW_DEPLOYED = false</span>, “Google has yet to actually deploy this workflow” (<a href='" + RWF + "' target='_blank' rel='noreferrer'>rack_workflows.go</a>). The console's Start-Rack-Workflow endpoint routes here and would error today. So the runs filing tickets are not FS-started: when the workflow's QA phase fails, <b>it</b> files the repair ticket — from Google's side of the glass.</p>", "ufs-body")

rep("but its QA failures are what file most repair tickets, and it's the family's one FS-startable member.",
    "but its QA failures are what file most repair tickets, and it's the one member with a written FS start path — gated off today (the panel text above has the gate).", "ufs-fact")

rep("`dcim-api/internal/server/google.go` starts `RackTurnupWorkflow` by string name + task queue. `rack-turnup` is the family's one FS-startable member; the repair doctors themselves (`machine-doctor`, `link-repair`) have no FS-side trigger — for them, Jira is the entire interface.",
    "`dcim-api/internal/server/google.go` names `RackTurnupWorkflow` by string + task queue — a written FS start path, gated off in code (`TURNUP_WORKFLOW_DEPLOYED = false`); the repair doctors (`machine-doctor`, `link-repair`) have no FS-side pointer at all. For every family member today, Jira is the entire interface.", "genesis-detail")

# --- MEDIUM: QA-handoff drill reconciled with census ---
rep("— built for Google-side re-validation; what it actually fires over there is one of the three unknowns below.</p><p>Three things aren't established from our side: whether ordinary repair-task closure fires the button or only rack-checklist work; what it fires on Google's side; and the sequencing — whether the button precedes or gates the Done write, and how its re-validation relates to the resumed workflow's own QA re-run.</p>",
    "— built for Google-side re-validation; what it actually fires over there is one of the two unknowns below.</p><p>One question is closed from code: only rack-checklist work fires the button — ordinary repair-task closure never does (the checklist endpoint's writers are the console UI and the rack-scan inventory step; dcim-tasks holds zero checklist references). Two things still aren't established from our side: what the button fires on Google's side; and the sequencing — whether it precedes or gates the Done write, and how its re-validation relates to the resumed workflow's own QA re-run.</p>", "proute-drill")

# census ② shortened, points at the drill receipt
rep('② the QA-handoff button at closure (rack checklists; console-button-only — repair-task closure never fires it: the checklist endpoint’s only writers are the console UI and the rack-scan inventory step, and dcim-tasks holds zero checklist references)',
    '② the QA-handoff button at closure (rack checklists; console-button-only — repair-task closure never fires it; 02·B carries the code receipt)', "census-qa-short")

# --- MEDIUM: stale mirror hedge in 01·B ---
rep('Whether the mirror also synced it despite the wrong Request Type is hidden with the rest of the unread config.',
    'The mirror had no mapping to sync it under — its wrong queue has no entry in dcim-tasks’ production RequestTypes map (02 carries the receipt).', "mirror-hedge-01B")

# --- MEDIUM: a-api drill auth attribution ---
rep("<p>Auth is Auth0 M2M, firming up when Xander's RFC closes (~Jun 15).</p>",
    "<p>Auth is Auth0 M2M as the working assumption. The live draft is Tyler van Hensbergen's foundry PR #1697 — Auth0 as sole token issuer, M2M as the v1 flow — with Xander advocating mTLS externally; decision open (<a href='#ev-d-auth'>d-auth</a>).</p>", "aapi-auth")

rep('confirm Auth0 machine-to-machine pattern post-Xander.',
    'confirm the Auth0 machine-to-machine pattern once d-auth closes (Tyler\'s Auth0-M2M draft vs Xander\'s mTLS advocacy).', "wk01-auth")

# --- LOW: Path A page-shaped class, post-receipt ---
rep("Who closes the Jira ticket for a genuinely page-shaped item isn't established; the class is near-empty — no page-shaped Request Type value appears anywhere this page read",
    "Who closes the Jira ticket for a genuinely page-shaped item isn't established. The class is thin but real — page-shaped values exist (Urgent Compute Request, Urgent Network Request, Network: observed in alert attributes via the incident.io API, mostly Rob's tests), and June 2's misrouted “Compute - Cable Repair” actually paged; repairs themselves ride “Deployment”, which never pages", "pathA-class")

# --- LOW: harmonize the two same-day API-check descriptions ---
rep('The route expressions themselves are dashboard-only — the incident.io API exposes no alert-route read (re-checked Jun 10), so other attributes weighing in can’t be fully excluded.',
    'The route expressions themselves are dashboard-only — the incident.io API shows the route exists but exposes no read of its conditions (re-checked Jun 10), so other attributes weighing in can’t be fully excluded.', "api-check-harmonize")

# --- LOW: 11-alert figure provenance in the verified note ---
rep('then the “DC ops Alerting path” workflow fires the escalation to that team’s path (Systems Esc, 5-minute ack).',
    'then the “DC ops Alerting path” workflow fires the escalation to that team’s path (Systems Esc, 5-minute ack). The June 1–3 behavioral receipt, observed through the same API: 11 alerts created incidents, every one carrying a non-Deployment queue (urgent-request tests, plus June 2’s misroute); “Deployment” alerts in the window created none.', "note-11-provenance")

# --- LOW: Hammad's two utterances disambiguated ---
rep('<p>Hammad: <span class="q">“I\'m getting paged for this, we probably need to change the Request Type so that this doesn\'t page the systems on-call”</span>',
    '<p>Hammad, in the Slack thread — he\'d said the same on the ticket three minutes earlier (that comment is quoted above): <span class="q">“I\'m getting paged for this, we probably need to change the Request Type so that this doesn\'t page the systems on-call”</span>', "hammad-two-quotes")

# --- LOW: routing-class plank in the 05 ledger ---
rep('over eight racks of swapped management cabling <a href="https://fluidstack.enterprise.slack.com/archives/C0ARQA55XU3/p1778707120991559?thread_ts=1778704566.098799&cid=C0ARQA55XU3" target="_blank" rel="noreferrer">↗</a>). Click any row',
    'over eight racks of swapped management cabling <a href="https://fluidstack.enterprise.slack.com/archives/C0ARQA55XU3/p1778707120991559?thread_ts=1778704566.098799&cid=C0ARQA55XU3" target="_blank" rel="noreferrer">↗</a>). A fourth page plank rides the contract sketch in 01·B — the routing-class field on create: same status, uncontested and undecided; the Path A re-wire keys on it. Click any row', "ledger-routing-class")

# --- LOW: glosses ---
rep('Envoy over Tailnet, a cloud-side gateway calling an on-site service.',
    'Envoy over Tailnet (Tailscale\'s private mesh network), a cloud-side gateway calling an on-site service.', "tailnet-gloss")

rep('google (editor), google-contractor and ies-contractors (operations), google-viewonly and anthropic (viewer)',
    'google (editor), google-contractor and ies-contractors (operations; “IES” is an external-contractor Auth0 org — its expansion isn\'t written in anything read), google-viewonly and anthropic (viewer)', "ies-gloss")

# --- LOW: density rewrites ---
rep('one house external-org pattern covers all three — four, counting the BMS integrators the terraform also lists (BMS = building-management system, the facility contractors; distinct from BMC, the board controller).',
    'one house external-org pattern covers all three. The terraform lists a fourth external org besides — “External contractors who configure Ignition BMS when we bring up new sites” (BMS: building-management system, the facility discipline — not BMC, the board controller).', "triangle-rewrite")

rep('the gap decomposes: ~30 is drift between two tuple-extraction runs — the Jun 9 mining session counted 4,728, this page\'s summary-shape recount found 4,698, ~20 are tuple-shaped tickets whose run links don\'t parse to a doctor, and exactly 4 are hand-filed full repair-tuples',
    'the gap decomposes: ~30 is drift between two tuple-extraction runs (the Jun 9 mining session counted 4,728; this page\'s summary-shape recount found 4,698); ~20 are tuple-shaped tickets whose run links don\'t parse to a doctor; and exactly 4 are hand-filed full repair-tuples', "uflows-parens")

print("OK:", len(ok), ok)
print("MISS:", miss)
open(FILE, "w").write(s)
m = re.search(r'<script>([\s\S]*)</script>', s)
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
    f.write("try { new Function(" + json.dumps(m.group(1)) + "); console.log('JS parses OK') } catch(e) { console.log('JS ERROR:', e.message) }")
    p = f.name
print(subprocess.run(['node', p], capture_output=True, text=True).stdout.strip())
ev = re.search(r'const EVENTS\s*=\s*\[([\s\S]*?)\n\];', s)
print("EVENTS html-in-string violations:", len(re.findall(r'(?:title|summary|detail)\s*:\s*"[^"]*<a ', ev.group(1))))
print("stray backref:", s.count('\\1'))
