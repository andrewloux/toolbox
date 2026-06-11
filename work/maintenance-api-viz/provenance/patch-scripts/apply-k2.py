#!/usr/bin/env python3
import re, json, subprocess, tempfile
FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html"
s = open(FILE).read()
ok, miss = [], []

def rep(old, new, tag):
    global s
    c = s.count(old)
    if c != 1: miss.append(f"{tag} (count={c})"); return False
    s = s.replace(old, new); ok.append(tag); return True

# 7a. d-push sentence + plank tag (01·B)
rep('The status watch becomes contractual — this page argues webhooks; webhook-vs-poll is open decision <a href="#ev-d-push">d-push</a> — and storm-shaped load gets batch + coalescing as first-class verbs — two of the create-path planks this page proposes; uncontested in the working plan, decided nowhere read (status gathered at <a href="#timeline">05</a>).',
    'The status watch becomes contractual — webhooks argued, webhook-vs-poll open as <a href="#ev-d-push">d-push</a>. Storm-shaped load gets batch + coalescing as first-class verbs — two page planks (status: <a href="#timeline">05</a>).', "7a-dpush")

# 7b. problem_code row tag
rep('The endpoint is uncontested in the working plan; no voice read disputes it. What registry backs it is the open half',
    'The endpoint is a page plank (status: <a href="#timeline">05</a>); what registry backs it is the open half', "7b-getrow")

# 7c. dedupe seg3 tag (claimant receipt stays here, canonical)
rep('Both are page planks, not settled contract — uncontested, hence no d-row; and the key contract has a caller waiting:',
    'Both are page planks (status: <a href="#timeline">05</a>) — and the key contract has a caller waiting:', "7c-dedupe")

# 7d. cf_14593 kv -> pointer (full facts live in the table above + 01·C + 05)
rep('<span class="m">cf_14593</span> is a UUID on 657 of 1,112 human tickets, mapped in dcim-tasks\' Jira schema — this page specs it as the create-side idempotency/dedup key rather than inventing one (uncontested; status gathered at <a href="#timeline">05</a>). An internal caller is already queued on that contract: <a href="https://fluidstack.atlassian.net/wiki/spaces/RE/pages/607617031" target="_blank" rel="noreferrer">SRE-RFC-0012 ↗</a> asks whether the repair-pipeline ingest accepts an external idempotency key — “Resolution: Pending API review.”',
    '<span class="m">cf_14593</span>, a UUID mapped in dcim-tasks\' Jira schema (counts in the table above), is specced as the create-side idempotency/dedup key in 01·C\'s correlation row — a page plank (status: <a href="#timeline">05</a>) with an internal claimant already queued: <a href="https://fluidstack.atlassian.net/wiki/spaces/RE/pages/607617031" target="_blank" rel="noreferrer">SRE-RFC-0012 ↗</a> (full receipt in 01·C).', "7d-cf-kv")

# 7e. a-api GET line tag
rep('The endpoint is the uncontested part (no decision row because no voice read disputes it)',
    'The endpoint is a page plank (status: 05)', "7e-aapi")

# 8. 01·A diacap: drop const (map canonical)
rep('but it is gated off in code (<span class="m">TURNUP_WORKFLOW_DEPLOYED = false</span>), so the runs',
    'but it is gated off in code, so the runs', "8-diacap-const")

# 9a. 01·B June 2 -> one clause
rep('June 2\'s mis-typed ticket paged the on-call while being queue-class work by nature — a cable repair for hands (02). The mirror had no mapping to sync it under — its wrong queue has no entry in dcim-tasks’ production RequestTypes map (02 carries the receipt).',
    'June 2\'s mis-typed ticket paged the on-call for queue-class work — the full failure mode, mirror mapping included, is 02\'s red note.', "9a-june2-01B")

# 9b. §02 lede merge (third-watcher up front; mapping stays canonical here)
rep('The two intake watchers are independent listeners, not a fork. June 2’s mis-typed ticket paged the on-call while being, by nature, queue-class floor work — a cable repair; the wrong queue (“Compute - Cable Repair”, request type 1414) has no entry in dcim-tasks’ production RequestTypes map',
    'The two intake watchers are independent listeners, not a fork; a third watcher — Google’s parked workflow — sits on the status field, not intake. June 2’s mis-typed ticket (the red note below) carried a queue — “Compute - Cable Repair”, request type 1414 — with no entry in dcim-tasks’ production RequestTypes map', "9b-02lede")
rep(' — so the mirror had no mapping to sync it under. A third watcher — Google’s parked workflow — sits on the status field, not intake.</p>',
    ' — so the mirror had no mapping to sync it under.</p>', "9c-02lede-tail")

# 10. JSM email: remove 01·B duplicate (canonical: §02 always-on line + census row)
rep('    <p class="diacap">Always-on, both paths (the email behavior is session-cited<sup class="rf"><a href="#ref-10">[10]</a></sup>): JSM (Jira Service Management) emails the reporter + request participants on every transition — for machine-filed tickets, that reporter is the bot.</p>\n', '', "10-jsm-dup")

# 11. §02 opening claim-first
old11 = 'ATLASBUF repair tickets carry a JSM (Jira Service Management) <b>Request Type</b> field — uniform on the 200/200 live pull; the universal over every issue type isn\'t checked, and that field is what the receipts show deciding whether a ticket becomes a page or a queue entry. The route expressions themselves are dashboard-only — the incident.io API shows the route exists but exposes no read of its conditions (re-checked Jun 10), so other attributes weighing in can\'t be fully excluded. Behaviorally the discriminator holds: across the June 1–3 window, “Deployment” alerts created zero incidents while all 11 incident-creating alerts carried non-Deployment queues — the verified note below.'
new11 = 'One form field decides whether a repair becomes a page or a queue entry: the JSM (Jira Service Management) <b>Request Type</b> — uniform on the 200/200 live pull (the universal over every issue type isn\'t checked). Behaviorally the discriminator holds: June 1–3, “Deployment” alerts created zero incidents; all 11 incident-creating alerts carried non-Deployment queues. The route expressions themselves are dashboard-only — the verified note below carries the Jun 10 re-check, its limits (other attributes can\'t be fully excluded), and the receipts.'
rep(old11, new11, "11-02-claimfirst")

# 11b. standalone 200/200 paragraph: fold unique caveats into lede, then remove
i = s.find('Every one of the 200 most-recent repair tickets carries Request Type:')
if i > 0:
    pstart = s.rfind('<p', 0, i); pend = s.find('</p>', i) + 4
    para = s[pstart:pend]
    extra = ''
    m = re.search(r'\(([^)]*in-session[^)]*)\)', para)
    if m: extra = ' (' + m.group(1) + ')'
    if 'uniform on the 200/200 live pull' in s and extra:
        s = s.replace('uniform on the 200/200 live pull (the universal', 'uniform on the 200/200 live pull' + extra + ' (the universal', 1)
    # only remove if its content is now redundant: check key claims exist elsewhere
    if ('nothing paged' in para and 'nothing paged' not in s.replace(para, '')):
        s = s.replace(para, '<p class="slede">Every one of those 200 carries “Deployment”; nothing paged.</p>')
        ok.append("11b-fold-keepline")
    else:
        s = s.replace(para, '')
        ok.append("11b-fold-removed")
else:
    miss.append("11b (not found)")

# 13a. 01·D staleness: shrink the second teller (the sidebar at ~705 keeps fresh-pull/Wk0-1)
if s.count('fresh pull of bloom-diagnostics') == 2:
    rep('Either our copy is behind Google\'s canonical file, or their emitters lead their registry; the artifacts read for this page can\'t split the two, though a fresh pull of bloom-diagnostics would — Wk 0–1 plans exactly that. The consumer lesson is the same either way: warn, don\'t reject.',
        'Either our copy is behind Google\'s canonical file, or their emitters lead their registry — the same can\'t-split staleness as the drift note above (a fresh bloom-diagnostics pull settles it; Wk 0–1 plans that). The consumer lesson either way: warn, don\'t reject.', "13a-staleness")
else:
    miss.append(f"13a (fresh-pull count={s.count('fresh pull of bloom-diagnostics')})")

# 13b. u-flows fact row -> body relocation of the reconciliation
fi = s.find("l: \"template families")
if fi < 0: fi = s.find("template families (full corpus)")
ti = s.find('<br>Template counting', fi if fi > 0 else 0)
if ti > 0:
    vend = s.find('" }', ti)
    recon = s[ti:vend]
    s = s[:ti] + s[vend:]
    body_recon = recon.replace('<br>', '</p><p>')[len('</p><p>'):]
    body_recon = '<p><b>Reconciling the counts.</b> ' + body_recon + '</p>'
    # insert at end of u-flows body (before its closing quote + facts)
    ub = s.find('"u-flows"')
    bend = s.find('",\n    facts:', ub)
    if ub > 0 and bend > 0:
        s = s[:bend] + body_recon.replace('"', '\\"').replace('\\"', "'").replace("'", "'") + s[bend:]
        ok.append("13b-uflows-recon")
    else:
        miss.append("13b (u-flows body anchor)")
else:
    miss.append("13b (recon anchor)")

# 13c. 01·C forward-ref soften
rep('one of just 4 human tickets whose body is the full repair-tuple, the shape of the 4,728-ticket family. The template buckets count shape, not reporter: 33 human tickets sit inside them (the four buckets total 14,543 = 14,510 bot + 33).',
    'one of just 4 human tickets whose body is the full repair-tuple — the shape of the 4,728-ticket family defined in <a href="#vocab">01·D</a>\'s template table. The buckets count shape, not reporter: 33 human tickets sit inside them (14,543 = 14,510 bot + 33; the u-flows panel reconciles).', "13c-anatomy-ref")

# 14. §04 NetBox paragraph split (Sean quote canonical at the posture slede below)
i = s.find("FluidStack's infrastructure truth lives in <b>NetBox</b>")
if i > 0:
    pstart = s.rfind('<p class="slede">', 0, i); pend = s.find('</p>', i) + 4
    para = s[pstart:pend]
    p2 = para
    p2 = p2.replace(' The consumer list is a working-session citation', '</p>\n  <p class="slede">The consumer list is a working-session citation')
    p2 = p2.replace(' Multiple stores synced expensively produce staleness bugs', '</p>\n  <p class="slede">Multiple stores synced expensively produce staleness bugs')
    qm = re.search(r' — Sean Banko: “[^”]+” (<a href="[^"]+" target="_blank" rel="noreferrer">↗</a>)\.', p2)
    if qm:
        p2 = p2.replace(qm.group(0), ' — Sean Banko\'s receipt, quoted in full below ' + qm.group(1) + '.')
    if p2 != para:
        s = s.replace(para, p2); ok.append("14-netbox-split")
    else:
        miss.append("14 (no change)")
else:
    miss.append("14 (anchor)")

# 15. hero dhint tighten (figures kept inline)
rep('(durations = resolution date − created, on tickets carrying both; 987 of the 2,671 repair-task rejections — 2,686 project-wide once 15 rejected tickets of other issue types are counted — carry no resolve timestamp)',
    '— durations = resolution − created where both timestamps exist; 987 of the 2,671 rejections carry no resolve timestamp (the 2,686-project-wide reconciliation, incl. the 15 non-repair rejected tickets, is in [10])', "15-dhint")

# 16. foundry-gateway cell trim + consolidation/partner-api diacap under the stack
gi = s.find('The consolidation plan one level up is written though:')
if gi > 0:
    gend = s.find('</span></div>', gi)
    consol = s[gi:gend]
    s = s[:gi].rstrip().rstrip('.') + '.' + s[gend:]
    lay_end = s.find('</div>', s.find('<div class="lay gw">')) + 6
    diacap = ('\n    <p class="diacap">' + consol.strip() +
              '. Name care — a third collision: that FS-side “Partner API” is a Go proxy between the partner console and Kaiser (<a href="https://github.com/fluidstackio/infrastructure-management/tree/main/services/partner-api" target="_blank" rel="noreferrer">its own docs say exactly that</a>) — not Google\'s Partner Operations API (03), and not this Maintenance API; whether foundry-gateway and that proxy layer converge isn\'t designed anywhere read.</p>')
    s = s[:lay_end] + diacap + s[lay_end:]
    ok.append("16-gateway+partner-api")
else:
    miss.append("16 (anchor)")

# 18. Temporal map: plain-fact order, history notes kept but parenthesized
rep('Production config resolves the endpoint question an earlier draft left open: dcim-api dials <b>Temporal Cloud</b>',
    'Production config answers the endpoint question: dcim-api dials <b>Temporal Cloud</b>', "18a-map-fact")
rep('— not the google-system frontend; that same-frontend inference, drawn from a queue name, is retired as wrong. Nor does site-worker host rack-turnup: it registers exactly three workflows (ProvisionRack, ProvisionMachine, RunSiteLocal <a href="https://github.com/fluidstackio/systems/tree/main/projects/site-worker/internal" target="_blank" rel="noreferrer">↗</a> — re-checked against the Jun 10 tree; April’s Firmware workflow is gone at HEAD); the executing worker',
    '— not the google-system frontend. (An earlier draft inferred a same-frontend link from a queue name; retired as wrong.) Nor does site-worker host rack-turnup: it registers exactly three workflows — ProvisionRack, ProvisionMachine, RunSiteLocal <a href="https://github.com/fluidstackio/systems/tree/main/projects/site-worker/internal" target="_blank" rel="noreferrer">↗</a> (the Jun 10 tree; an April read showed a fourth, Firmware, since removed); the executing worker', "18b-map-history")

# 20. BMS: card -> pointer IF the tenancy drill carries the content; else move it there
card_bms = 'one house external-org pattern covers all three. The terraform lists a fourth external org besides — “External contractors who configure Ignition BMS when we bring up new sites” (BMS: building-management system, the facility discipline — not BMC, the board controller).'
drill_has = ('Ignition' in s.split(card_bms)[0] + s.split(card_bms)[1]) if s.count(card_bms) == 1 else False
ten_i = s.find('"s-tenancy"')
ten_block = s[ten_i:ten_i+3000] if ten_i > 0 else ''
if s.count(card_bms) == 1 and 'BMS' in ten_block:
    rep(card_bms,
        'one house external-org pattern covers all three — four orgs counting the Ignition-BMS integrators (the tenancy panel carries the terraform’s wording and the BMS-vs-BMC note).', "20-bms-pointer")
    if 'Ignition BMS' not in s[ten_i:ten_i+3000]:
        bi = s.find('",\n    facts:', ten_i)
        s = s[:bi] + "<p>The terraform’s fourth external org, verbatim: “External contractors who configure Ignition BMS when we bring up new sites” — BMS the building-management system, the facility discipline; not BMC, the board controller.</p>" + s[bi:]
        ok.append("20b-bms-into-drill")
else:
    miss.append(f"20 (card count={s.count(card_bms)}, tenancy BMS={'BMS' in ten_block})")

# 25. who's-who: Sean Brabson row
hr = "Surfaced the June 2 misroute in-thread (the paged on-call — acked in 19 s"
i = s.find(hr)
if i > 0:
    row_end = s.find('</div>', s.find('</span></div>', i)) if False else s.find('</span></div>', i) + len('</span></div>')
    brab = '\n    <div class="r"><span>Sean Brabson</span><span></span><span>June 2’s assignee — the resolution comment records the on-site finding (a white BMC cable where the mgmt cable belonged). A third Sean on this page, distinct from Sean Banko (Foundry / workflow semantics).</span></div>'
    s = s[:row_end] + brab + s[row_end:]
    ok.append("25-brabson")
else:
    miss.append("25 (anchor)")

print("OK:", len(ok), ok)
print("MISS:", miss)
open(FILE, "w").write(s)
m = re.search(r'<script>([\s\S]*)</script>', s)
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
    f.write("try { new Function(" + json.dumps(m.group(1)) + "); console.log('JS parses OK') } catch(e) { console.log('JS ERROR:', e.message) }")
    p = f.name
print(subprocess.run(['node', p], capture_output=True, text=True).stdout.strip())
base = json.load(open('/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/data/inventory-v88.json'))
hrefs = set(re.findall(r'href=[\'"]([^\'"]+)[\'"]', s))
nums = set(re.findall(r'\b\d[\d,]*(?:\.\d+)?%?\b', s))
print("href removals:", sorted(set(base['hrefs']) - hrefs))
print("num removals:", sorted(set(base['nums']) - nums))
ev = re.search(r'const EVENTS\s*=\s*\[([\s\S]*?)\n\];', s)
print("EVENTS violations:", len(re.findall(r'(?:title|summary|detail)\s*:\s*"[^"]*<a ', ev.group(1))))
