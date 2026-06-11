#!/usr/bin/env python3
import re, json, subprocess, tempfile
FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html"
s = open(FILE).read()
ok, miss = [], []
def rep(old, new, tag):
    global s
    c = s.count(old)
    if c != 1: miss.append(f"{tag} ({c})"); return
    s = s.replace(old, new); ok.append(tag)

DHINT = '<p class="dhint">▸ <b>solid boxes drill down</b> — mechanism, real exemplars, receipts · dashed boxes are pointers</p>'
assert s.count(DHINT) == 3, f"dhint count {s.count(DHINT)}"
# occurrence 1 (after v-up, 01·A — HAS ghost pointer boxes): keep.
# occurrence 2 (d-today): no dashed/ghost boxes — drop the clause.
i1 = s.find(DHINT); i2 = s.find(DHINT, i1+1); i3 = s.find(DHINT, i2+1)
s = s[:i3] + '<p class="dhint">▸ <b>solid boxes drill down</b> — mechanism, real exemplars, receipts · dashed strokes here mark open decisions (see the legend), not pointers</p>' + s[i3+len(DHINT):]
s = s[:i2] + '<p class="dhint">▸ <b>solid boxes drill down</b> — mechanism, real exemplars, receipts</p>' + s[i2+len(DHINT):]
ok.append("dhints-positional")

rep('the three FS-namespace codes two tables up are also proto-absent',
    'the three FS-namespace codes one table up are also proto-absent', "one-table-up")
rep('Every solid box drills down (ghost boxes are pointers); nearly every claim links a receipt',
    'Every solid box drills down (dashed boxes are pointers); nearly every claim links a receipt', "hero-dashed")
rep('the month placement is the decide-by target, the label stays “open”.',
    'the month placement is the decide-by target; the six undated rows are labeled “open”, while d-auth shows its ~Jun 15 date and a closing chip.', "s05-dauth-label")
rep('<span>④ TPU-CC’s diagnostics RPCs</span><span>no — diagnostics</span>',
    '<span>④ TPU-CC’s control-and-diagnostics RPCs</span><span>no — control &amp; diagnostics, not repair requests</span>', "census4-control")
rep('Its repairs will flow through the API this page motivates and constrains; the spec itself lands ~Jul 21.',
    'Its repairs are slated to flow through the API this page motivates and constrains; the spec is planned for ~Jul 21.', "dek1-hedge")
rep('<a href="#ev-d-auth">d-auth</a> closing ~Jun 15</span>',
    'still an open decision — <a href="#ev-d-auth">d-auth</a>, closing ~Jun 15</span>', "dauth-vocab")
rep('hall 2 is ready-for-service Jun 16; the fallback question',
    'hall 2 is ready-for-service Jun 16 (a facility milestone — hardware-arrival dates aren’t tracked, per the note); the fallback question', "burning-rfs")
rep('<span class="sf">the doc demanding this API</span></div>\n  <p class="slede">Google is putting',
    '<span class="sf">the doc demanding this API</span></div>\n  <p class="slede"><b>Sourcing:</b> this page worked from a summary of the Partner Ops doc, not a full mining pass (Wk 0–1 plans that); every claim below carries its own receipt.</p>\n  <p class="slede">Google is putting', "03-sourcing")
rep("rel='noreferrer'>the handler ↗</a>). A structural loop-breaker",
    "rel='noreferrer'>the handler ↗</a>; idempotent by lookup-then-unique-key — replays no-op <a href='https://github.com/fluidstackio/dcim/blob/b6eea015af01044ce5c41aaa8e29bb655557a2f7/services/dcim-tasks/internal/server/webhooks_jira.go#L287-L295' target='_blank' rel='noreferrer'>↗</a>). A structural loop-breaker", "webhook-idem-receipt")
rep('<span>the routing-class field on create (<a href="#todaytomorrow">01·B</a>)</span><span></span><span>the Path A re-wire keys on it</span>',
    '<span>the routing-class field on create (<a href="#todaytomorrow">01·B</a>)</span><span></span><span>born of the June 2 misroute (<a href="#routing">02</a>’s red note carries the receipt); the Path A re-wire keys on it</span>', "routing-plank-receipt")
rep('“Google has yet to actually deploy this workflow”; <a href="#temporal-map">the Temporal map</a> has the receipt',
    '“Google has yet to actually deploy this workflow” — the gate scopes the FS-side Temporal-Cloud queue; rack-turnup itself runs live on Google’s own engine, filing via ①. <a href="#temporal-map">The Temporal map</a> has the receipt', "census3-scope")
rep('· IAH1 stand-up)</span>',
    '· IAH1 stand-up) · one flagged-but-unmapped requirement: Borneo two-way change/incident comms with the customer (<a href="#ev-kickoff">kickoff</a>)</span>', "open-row-comms")
rep('sweeps ride doctors · campaigns/humans file direct',
    'sweeps ride the workflows · campaigns/humans file direct', "ucamp-workflows")
rep('(the a-api drill expands it)',
    '(click the Maintenance API box in 01·B’s Tomorrow tab for the expansion)', "3p-pointer")
rep('-prefixed machine templates, 99% closed Done',
    '-prefixed machine templates — 99% of those 5,008 closed Done', "storm-denominator")
rep('keyed on the same Auth0 orgs: its',
    'keyed on the same Auth0 org mechanism (the org sets only partly overlap — google and atlas/anthropic are the shared ones): its', "feldspar-mechanism")

print("OK:", len(ok), ok)
print("MISS:", miss)
if miss: raise SystemExit("ABORT: misses present, file NOT written")
open(FILE, "w").write(s)

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
base = json.load(open('/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/data/inventory-v88.json'))
hrefs = set(re.findall(r'href=[\'"]([^\'"]+)[\'"]', s))
nums = set(re.findall(r'\b\d[\d,]*(?:\.\d+)?%?\b', s))
print("href removals:", sorted(set(base['hrefs']) - hrefs))
print("num removals:", sorted(set(base['nums']) - nums))
