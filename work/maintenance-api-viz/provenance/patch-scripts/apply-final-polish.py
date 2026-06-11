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

# R13-1: a-hook box back to solid (dashed return edge already carries d-push's status)
rep('<rect class="sv-box dash" x="38" y="260" width="212" height="80" rx="4"/>',
    '<rect class="sv-box" x="38" y="260" width="212" height="80" rx="4"/>', "box-solid")

# R13-2 / R14: Teleport gets its own decoder row (+ the missing space dies with it)
rep('is <a href="#temporal-map">at 01·MAP, after 01·B</a>· <span class="m">Teleport</span> = FS\'s access proxy: SSO-brokered, audited access to cluster services (the “teleport-gated” links)</span></div>',
    'is <a href="#temporal-map">at 01·MAP, after 01·B</a></span></div>\n    <div class="r"><span><span class="m">Teleport</span></span><span>FS\'s access proxy: SSO-brokered, audited access to cluster services (the “teleport-gated” links)</span></div>', "teleport-row")

# R13-3: TPU-CC code comments marked as page glosses
rep('proto" target="_blank" rel="noreferrer">↗ source</a></div>\n      <pre>service <span class="cv">TpuCommandCenter</span> {',
    'proto" target="_blank" rel="noreferrer">↗ source</a></div>\n      <pre><span class="cc">// signatures from the vendored proto; the // notes are this page\'s glosses</span>\nservice <span class="cv">TpuCommandCenter</span> {', "tpucc-gloss-marker")

# R13-4 + R14-FS-2: 200/200 appositive + "universal" hedge rewrite
rep('uniform on the 200/200 live pull — a live in-session Jira pull, a different dataset from the archived corpus crawl, whose field set lacked request type; the universal over every issue type isn\'t checked',
    'uniform on the 200/200 live pull (an in-session Jira pull; the archived corpus crawl is a different dataset, and the crawl\'s field set lacked request type). Whether the field is uniform across every issue type wasn\'t checked', "200-rewrite")

# R13-5: gloss the RFC quote's "Repair Pipeline API"
rep('as open — resolution pending API review.</span></span></div>',
    'as open — resolution pending API review. (The RFC\'s “Repair Pipeline API” is the internal dcim-side ingest the worker would submit to — not this Maintenance API.)</span></span></div>', "rfc-referent")

# R14-G-2: red-note antecedent
rep('The earlier crawl missed it because the summary is just “Repair Cable” — the alert title carried it verbatim, unrewritten; the earlier either/or speculation here is retired.',
    'The earlier crawl missed the ticket because its summary is just “Repair Cable” — and the alert title is that same two-word summary, carried verbatim, unrewritten (the incident channel\'s longer name came from incident.io\'s own template, not the ticket); the earlier either/or speculation here is retired.', "antecedent")

# R14-G-4: fallback echo varied
rep('<span class="nk">The fallback question — open, and burning</span>\n    <p>No repair traffic yet; the API is specified for it, deliberately generic so Atlas can later migrate onto it as a second tenant.</p>',
    '<span class="nk">The fallback question — open, and burning</span>\n    <p>Borneo has no repair traffic yet, and the API being specified for it is deliberately generic so Atlas can later migrate onto it as a second tenant.</p>', "echo-varied")

# R14-G-5: planks row label loses the settled-green
rep('<span class="lb grn">page planks</span>', '<span class="lb">page planks</span>', "planks-label")

# R14-FS-3: 8,737 appositive chain
rep('8,737 of the corpus’ 15,529 repair tasks reference its runs — all 8,737 repair tasks, verified, counted inside the 15,622, cross-cutting the template buckets rather than forming a bucket of their own (the u-flows panel reconciles).',
    '8,737 of the corpus’ 15,529 repair tasks reference its runs. All 8,737 are repair tasks (verified); they sit inside the 15,622 and cross-cut the template buckets rather than forming one of their own — the u-flows panel reconciles.', "8737-rewrite")

# R14-G-3: Auth0-org census reconciled across 01·0 and §04
rep('one house external-org pattern covers all three, four orgs counting the BMS integrators (the tenancy panel carries the terraform’s verbatim comment and the BMS-vs-BMC note).',
    'one house external-org pattern covers all three, four orgs counting the BMS integrators (the tenancy panel carries the terraform’s verbatim comment and the BMS-vs-BMC note; §04’s feldspar group list is a different, wider census — NetBox provisioning, not Teleport — keyed on the same Auth0 orgs: its “anthropic” is the terraform’s “atlas”, one org, two config labels).', "org-census")

print("OK:", ok)
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
