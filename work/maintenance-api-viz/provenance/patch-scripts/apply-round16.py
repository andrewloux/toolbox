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

# ===== MEDIUM (Google): s-pathB stale repo attribution =====
rep("a React app (<span class='m'>services/dcim-console</span> in the dcim repo) served at",
    "a React app (<span class='m'>services/dcim-console</span> — moved to the Kaiser repo, infrastructure-management, on Jun 10) served at",
    "M-spathB-repo")

# ===== FS LOWs =====
rep("caveat: dcim's repair SOPs use BMS for a third expansion — Battery Management System — so the acronym is overloaded three ways in FS repos",
    "caveat: dcim's repair SOPs use BMS for a second expansion — Battery Management System — so the acronym is overloaded even within FS repos (BMC is a different acronym again)",
    "L-bms-count")
rep("the denominator key above collapses duplicates",
    "the denominator key below (in the registry-vs-reality table) collapses duplicates",
    "L-denominator-direction")
rep("A third Sean on this page, distinct from Sean Banko (Foundry / workflow semantics).",
    "Distinct from Sean Banko (Foundry / workflow semantics) — the page's Sean census is two or three, depending on whether the review row's “Sean” is Banko (hedged there as likely but unconfirmed).",
    "L-sean-census")
rep('The Granola notes record Xander advocating mTLS externally, decision not yet closed as of the Jun 9 Granola notes, which had Xander due back Jun 10; nothing later read.',
    'The Jun 9 Granola notes record Xander advocating mTLS externally — decision not yet closed; the notes had him due back Jun 10, and nothing later was read.',
    "L-dauth-runon")
rep("A repair's life today<i>born → filed → woken</i>",
    "A repair's life today<i>born → filed → parked → woken</i>",
    "L-routemap-parked")
rep('Click any row for the mechanism, its spec impact, and receipts.</p>',
    'Click any row for the mechanism, its spec impact, and receipts. Open rows are slotted under the plan milestone they must close by — d-auth under Jun 15 (kickoff), d-vocab / d-actions / d-push under Jun 23 (the RFC), d-cancel / d-cuj5 / d-revalidate under Jul 7 (the skeleton); the month placement is the decide-by target, the label stays “open”.</p>',
    "L-decision-dates")
rep('SRE-RFC-0012</a> (FS\'s event-correlation engine, draft under review), “pending API review”</span>',
    'SRE-RFC-0012</a> (FS\'s event-correlation engine, draft under review), “pending API review” — its “Repair Pipeline API” is the internal dcim-side ingest, not this API (<a href="#anatomy">01·C</a>\'s correlation row carries the full receipt)</span>',
    "L-planks-rfc-disambig")

# ===== Google LOWs =====
rep('its production home wasn’t read either; the example config defaults to <span class="m">localhost:7233</span>.</p>',
    'its production home wasn’t read either; the example config defaults to <span class="m">localhost:7233</span> — if that engine also rides Temporal Cloud in prod, the census collapses to two.</p>',
    "L-tmap-census")
rep('differ by ~50 tickets, and the gap decomposes:',
    'differ by 54 tickets, and the gap decomposes:',
    "L-uflows-54")
rep("the bot templates' summary prefixes — SW: heads software-check failures (QA / repair / diagnosis failed), HW: heads imperative hardware actions (Reseat / Replace / Clean) — a corpus-observed convention, written down nowhere this page read",
    "the corpus' summary prefixes — SW: heads software-check failures (QA / repair / diagnosis failed), HW: heads imperative hardware actions (Reseat / Replace / Clean) — a shared convention, not bot-only (794 of 1,112 human tickets lead with HW:), written down nowhere this page read",
    "L-swhw-attribution")
rep('(<a href="#timeline">status ledger in 05</a>)',
    '(<a href="#timeline">planks table in 05</a> — receipts per plank, one shared status note)',
    "L-ledger-word")

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
