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

# ===== MEDIUM (Google): census scope rule =====
rep('<p class="slede"><b>The full boundary census</b> — five cross-boundary touches; only one carries repair requests:</p>',
    '<p class="slede"><b>The full boundary census</b> — five cross-boundary touches; only one carries repair requests. Scope rule: the census counts <b>signal channels</b> — paths a repair request or work signal could ride between the companies. Standing <b>access surfaces</b> are deliberately not rows: Google\'s Teleport tenancy (the tenancy drill) and its direct NetBox/feldspar editor access (<a href="#foundry">§04</a>) are how Google\'s code and people are <i>present</i> on FS systems, not channels a request crosses — the same classification the Temporal map applies to Temporal Cloud.</p>',
    "M-census-scope")

# ===== LOWs =====
rep('d-auth under Jun 15 (kickoff)',
    'd-auth under Jun 15 (the auth-RFC date the kickoff set; the Wk 0–1 inputs row lands Jun 16)',
    "L-kickoff-label")
rep('<div class="r"><span>coalescing on (entity, problem_code)</span><span></span><span>the key shape FS\'s draft event-correlation engine already dedups on upstream</span></div>',
    '<div class="r"><span>coalescing on (entity, problem_code)</span><span></span><span>the key shape FS\'s draft event-correlation engine already dedups on upstream — receipt at <a href="#anatomy">01·C</a>\'s correlation row ((topology_key, root_cause) · SRE-RFC-0012)</span></div>',
    "L-coalescing-receipt")
rep('<div class="r hd"><span>Programs &amp; Google-side</span><span></span></div>\n    <div class="r"><span><span class="m">Bloom</span></span>',
    '<div class="r hd"><span>Programs &amp; Google-side</span><span></span></div>\n    <div class="r"><span><span class="m">3P</span></span><span>third-party — Google\'s qualifier for systems it doesn\'t own; “3P Ticketing System” is the Partner-Ops doc\'s name for the FS-hosted Maintenance API (the a-api drill expands it)</span></div>\n    <div class="r"><span><span class="m">Bloom</span></span>',
    "L-3p-decoder")
rep('<text class="sv-m g" x="300" y="320">rejected = async terminal state + machine-readable reason</text>',
    '<text class="sv-m g" x="300" y="320">rejected = machine-readable async terminal state — page position (dash = d-push only)</text>',
    "L-svg-rejected-status")
rep('Dell (the hardware vendor the next row introduces —',
    'Dell (the hardware vendor — the Borneo card\'s actors row introduces it —',
    "L-dell-pointer")
rep('Auth/SSO — wrote the external-org terraform; advocates mTLS for external auth',
    'Auth/SSO — wired Google\'s Teleport app exposures into the tenancy (<a href="https://github.com/fluidstackio/systems/pull/2747" target="_blank" rel="noreferrer">#2747</a> temporal-web/tpucc-ui, <a href="https://github.com/fluidstackio/systems/pull/2740" target="_blank" rel="noreferrer">#2740</a> turnup dashboard, <a href="https://github.com/fluidstackio/systems/pull/1995" target="_blank" rel="noreferrer">#1995</a> ClickHouse port-forward); the external-org mechanism itself is Miguel Varela Ramos\'s (<a href="https://github.com/fluidstackio/systems/pull/1122" target="_blank" rel="noreferrer">#1122</a>); advocates mTLS for external auth',
    "L-xander-receipted")
rep('— seven values fired in production that our vendored <span class="m">repairs.textproto</span> doesn\'t contain.',
    '— seven values fired in production that our vendored <span class="m">repairs.textproto</span> doesn\'t contain (counting Google-side emissions only; the three FS-namespace codes two tables up are also proto-absent — by design, not skew — which would make ten).',
    "L-seven-scope")

print("OK:", len(ok), ok)
print("MISS:", miss)
if miss: raise SystemExit("ABORT: misses present, file NOT written")
open(FILE, "w").write(s)

# verification battery
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
