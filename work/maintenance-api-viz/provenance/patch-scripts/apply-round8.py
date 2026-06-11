#!/usr/bin/env python3
import re, json, subprocess, tempfile
FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html"
s = open(FILE).read()
ok, miss = [], []

def rep(old, new, tag, n_expected=1):
    global s
    n = s.count(old)
    if n != n_expected:
        miss.append(f"{tag} (count={n}, expected={n_expected})"); return
    s = s.replace(old, new); ok.append(tag)

BARRETT = "https://fluidstack.enterprise.slack.com/archives/C0ARQA55XU3/p1778707120991559?thread_ts=1778704566.098799&cid=C0ARQA55XU3"
RFC = "https://fluidstack.atlassian.net/wiki/spaces/RE/pages/607617031"
IM = "https://github.com/fluidstackio/infrastructure-management"

# 1. L562 gate qualifier (G8-1 / F8-1)
rep('is the one exception: <a href="https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/internal/server/google.go" target="_blank" rel="noreferrer"><span class="m">dcim-api/…/google.go</span></a> starts <span class="m">RackTurnupWorkflow</span> by string name, and that workflow\'s QA failures are what file repair tickets.',
    'is the one near-exception: <a href="https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/internal/server/google.go" target="_blank" rel="noreferrer"><span class="m">dcim-api/…/google.go</span></a> names <span class="m">RackTurnupWorkflow</span> by string — a written start path, gated off in code today (01·A above) — and that workflow\'s QA failures are what file repair tickets.', "gate-qualifier")

# 2. Granola gloss (G8-2)
rep('Meeting notes are recovered (Granola, linked):',
    'Meeting notes are recovered (Granola, the meeting-notes tool — linked):', "granola-gloss")

# 3. §05 lede split (G8-3)
old_lede = s[s.find('<p class="slede">Three tracks: what happened'):]
old_lede = old_lede[:old_lede.find('</p>') + 4]
new_lede = '''<p class="slede">Three tracks: what happened (history), what's scheduled (plan), what's unresolved (open decisions). The d-* rows hold <b>spec-phase</b> decisions — choices the document itself must make; build-phase opens (the fulfill hop, the Path A re-wire mechanics, IAH1 stand-up) are declared where they arise and deliberately not rowed. Click any row for the mechanism, its spec impact, and receipts.</p>
  <p class="slede">One scoping fact: this page worked from a summary of the Partner Ops doc, not a full mining pass — Wk 0–1 plans that — so where a d-row says “Google preference unknown,” it means unknown to this page; the doc itself may already answer some of them.</p>
  <p class="slede">Four planks are this page's proposals — uncontested in the working plan (no voice read disputes them, so they carry no d-row), not decided contract:<br><b>batch create</b> — a floor voice already asks for it: “best to batch together common repairs and give in bulk” (Thomas Barrett, over eight racks of swapped management cabling <a href="''' + BARRETT + '''" target="_blank" rel="noreferrer">↗</a>)<br><b>coalescing on (entity, problem_code)</b> — the key shape FS's draft event-correlation engine already dedups on upstream<br><b>cf_14593 as the create-side idempotency key</b> — an internal claimant already waits on that contract: <a href="''' + RFC + '''" target="_blank" rel="noreferrer">SRE-RFC-0012</a> (FS's event-correlation engine, draft under review), “pending API review”<br><b>the routing-class field on create</b> (01·B) — the Path A re-wire keys on it<br>GET /problem-codes shares the uncontested status.</p>'''
if old_lede.startswith('<p class="slede">Three tracks') and s.count(old_lede) == 1:
    s = s.replace(old_lede, new_lede); ok.append("lede-split")
else:
    miss.append("lede-split")

# 4. task_type naming hop (F8-2)
rep("which EffectiveTaskType folds to task type <span class='m'>deployment</span>. The same values template",
    "which EffectiveTaskType folds to task type <span class='m'>deployment</span>. That type names the work; it doesn't decide queue membership — the task sits in the console queue because the sync mirrored it (whether any console view filters on task_type isn't established from anything read). The same values template", "tasktype-hop")

# 5. u-fs "must serve" voice (F8-3)
rep('{ l: "what this means for the api", v: "the same surface must serve repairs born from FS-initiated flows — actor-agnostic re-validation (open decision)" }',
    '{ l: "what this means for the api", v: "this page\'s position: the same surface should serve repairs born from FS-initiated flows too. Whether an FS-initiated event even appears as a resource on the API is not yet designed (§03\'s CUJ4 row); <a href=\'#ev-d-revalidate\'>d-revalidate</a> covers the closure half only" }', "ufs-voice")

# 6. QA-handoff SVG label (F8-4)
rep('<text class="sv-s" x="656" y="311">QA handoff button on finish (rack checklists)</text>',
    '<text class="sv-s" x="656" y="311">QA handoff: rack-checklist work only, not repair closure</text>', "qa-svg-label")

# 7. firmware 4 -> 3 (fresh-tree correction)
rep('it registers exactly four workflows (ProvisionRack, ProvisionMachine, Firmware, RunSiteLocal <a href="https://github.com/fluidstackio/systems/tree/main/projects/site-worker/internal" target="_blank" rel="noreferrer">↗</a>); the executing worker',
    'it registers exactly three workflows (ProvisionRack, ProvisionMachine, RunSiteLocal <a href="https://github.com/fluidstackio/systems/tree/main/projects/site-worker/internal" target="_blank" rel="noreferrer">↗</a> — re-checked against the Jun 10 tree; April\'s Firmware workflow is gone at HEAD); the executing worker', "firmware-three")

# 8a. SOPGuidePanel blob links (2 sites)
rep('https://github.com/fluidstackio/dcim/blob/main/services/dcim-console/src/pages/repairs/SOPGuidePanel.tsx',
    IM + '/blob/main/services/dcim-console/src/pages/repairs/SOPGuidePanel.tsx', "sopguide-links", n_expected=2)

# 8b. console tree links (2 sites)
rep('https://github.com/fluidstackio/dcim/tree/main/services/dcim-console',
    IM + '/tree/main/services/dcim-console', "console-tree-links", n_expected=2)

rep('label: "dcim-console source (dcim repo)"',
    'label: "dcim-console source — moved to the Kaiser repo Jun 10 (dcim #2525)"', "console-label")

# 8c. config-home row: console moved (live consolidation receipt)
rep('The <b>dcim repo</b> — console served at <a href="https://dcim.fluidstack.io" target="_blank" rel="noreferrer">dcim.fluidstack.io</a>, Argo-deployed (gitops — glossed in the tenancy panel) from <a href="https://github.com/fluidstackio/dcim" target="_blank" rel="noreferrer">fluidstackio/dcim</a>',
    'Console served at <a href="https://dcim.fluidstack.io" target="_blank" rel="noreferrer">dcim.fluidstack.io</a>; its source moved to the Kaiser repo on Jun 10 (<a href="' + IM + '" target="_blank" rel="noreferrer">infrastructure-management</a>, via dcim <a href="https://github.com/fluidstackio/dcim/pull/2525" target="_blank" rel="noreferrer">#2525</a>). The backing services stay in and Argo-deploy (gitops — glossed in the tenancy panel) from <a href="https://github.com/fluidstackio/dcim" target="_blank" rel="noreferrer">fluidstackio/dcim</a>', "config-home-move")

# 8d. front-door row: consolidation step 1 landed
rep('with “Partner API introduced” as its roadmap step 4 <a href="https://fluidstack.atlassian.net/wiki/spaces/Infra/pages/656965636/Platform+Consolidation+Towards+a+Unified+Console" target="_blank" rel="noreferrer">↗</a>',
    'with “Partner API introduced” as its roadmap step 4 <a href="https://fluidstack.atlassian.net/wiki/spaces/Infra/pages/656965636/Platform+Consolidation+Towards+a+Unified+Console" target="_blank" rel="noreferrer">↗</a> — and step 1 landed Jun 10: dcim-console moved into the Kaiser repo (<a href="https://github.com/fluidstackio/dcim/pull/2525" target="_blank" rel="noreferrer">#2525</a>); partner-api and partner-console already exist as services there', "frontdoor-step1")

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
print("dead dcim-console refs left:", s.count('fluidstackio/dcim/blob/main/services/dcim-console') + s.count('fluidstackio/dcim/tree/main/services/dcim-console'))
