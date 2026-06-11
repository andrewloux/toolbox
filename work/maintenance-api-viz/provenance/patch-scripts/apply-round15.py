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

# ===== MEDIUM 1 (both readers): census row ① direction ambiguity =====
rep('the always-on channel, <a href="#routing">02</a>; the return half runs on polling — the webhook ingest built for it never got a route (<a href="#ev-w-dark">Mar 28</a>)</span>',
    'the always-on channel, <a href="#routing">02</a>; the Jira→dcim-tasks mirror runs on polling — the webhook ingest built for that inbound direction never got a route (<a href="#ev-w-dark">Mar 28</a>); how Google watches status flowing the other way is its own, unverified question (<a href="#todaytomorrow">01·B</a>)</span>',
    "M1-census-direction")

# ===== MEDIUM 2 (both readers): surface the May 27 commitment in state-of-play =====
rep('spec to Google ~Jul 21 → freeze ~Aug 4 · the CUJ3 sequence diagram has been owed to Google since <a href="#ev-asks">Apr 28</a></span>',
    'spec to Google ~Jul 21 → freeze ~Aug 4 · the CUJ3 sequence diagram has been owed to Google since <a href="#ev-asks">Apr 28</a> · caveat on ~Jul 21: Rob told Google on May 27 he\'d deliver the machine-management spec by Jun 1 → Jun 3 <a href="https://fluidstack.enterprise.slack.com/archives/C0B0HPZ35GV/p1779906524583829?thread_ts=1779905920.244999&amp;cid=C0B0HPZ35GV" target="_blank" rel="noreferrer">↗</a> — how that prior commitment relates to this plan is unreconciled (<a href="#ev-p4">p4</a>)</span>',
    "M2-sop-commitment")

# ===== MEDIUM 3 (Google): FISH expansion contradiction =====
rep('used as a proper name; no expansion is written down in the systems docs or #team_fish</span>',
    'used as a proper name; the systems docs and #team_fish never expand it, but the FISH RFC\'s own title does — “Fluidstack Infrastructure Services Hub” <a href="https://fluidstack.atlassian.net/wiki/spaces/Infra/pages/77660161/RFC+Fluidstack+Infrastructure+Services+Hub+FISH" target="_blank" rel="noreferrer">↗</a></span>',
    "M3-fish-row")
rep("isn't written down in anything read — like FISH and GFC)",
    "isn't written down in anything read — like GFC; FISH came off this list when its RFC title supplied the expansion, see its row below)",
    "M3-buf101-row")

# ===== LOWs =====
rep('the fallback question is open three ways (<a href="#fallback">the amber note in 01</a>)',
    'the fallback question is open on four axes — fallback system, IAH1 stand-up, window length, Jira home (<a href="#fallback">the amber note in 01</a>)',
    "L-fallback-count")
rep('<p class="slede">Three engines appear. <b>Google’s</b> runs',
    '<p class="slede">Three engines appear in the configs read. <b>Google’s</b> runs',
    "L-tmap-engines")
rep('summary: "Entity grammar (+DCN), async rejected, idempotency/batch, webhooks, correlation IDs.",',
    'summary: "Entity grammar (+DCN), async rejected, idempotency/batch, webhooks (argued — open as d-push), correlation IDs.",',
    "L-p2-webhooks-hedge")
rep("(“not quite operational” — Hannah, <a href='#ref-10'>[10]</a>)",
    "(“not quite operational” — Hannah <a href='https://fluidstack.enterprise.slack.com/archives/C0AAY9E2NF9/p1780954556831229?thread_ts=1780948308.037829&cid=C0AAY9E2NF9' target='_blank' rel='noreferrer'>↗</a>)",
    "L-hannah-permalink")
rep('built 2026-06-09, corpus stats recomputed 2026-06-10 · per-event receipts',
    'built 2026-06-09, corpus stats recomputed 2026-06-10, last revised 2026-06-11 (the link sweep + the dark-webhook research) · per-event receipts',
    "L-colophon-date")
rep('decision not yet closed; Xander returns in a day, per the Jun 9 Granola notes.',
    'decision not yet closed as of the Jun 9 Granola notes, which had Xander due back Jun 10; nothing later read.',
    "L-xander-deixis")
rep('<div class="n">1.6<i>h</i></div><div class="l">Cycle p50 (create→done)</div>',
    '<div class="n">1.6<i>h</i></div><div class="l">Cycle p50 (create→done) · sweep-deflated (pre-June: 6.0h)</div>',
    "L-hero-p50-caveat")
rep('dotted = page plank</text>\n    </svg></div>\n    <p class="scrollhint">↔ scroll the diagram sideways for the full flow',
    'dotted = page plank</text>\n    </svg></div>\n    <p class="scrollhint">↔ scroll the diagram sideways for the full flow · drawn status = decision status, not build status (whether a live foundry-gateway instance exists is <a href="#foundry">§04</a>\'s open check)',
    "L-legend-builds")
rep('The earlier crawl missed the ticket because its summary is just “Repair Cable” — and the alert title is that same two-word summary, carried verbatim, unrewritten (the incident channel\'s longer name came from incident.io\'s own template, not the ticket); the earlier either/or speculation here is retired.',
    'The earlier mining pass over summaries missed the ticket — its summary is just “Repair Cable”; the corpus crawl itself holds it, inside the 15,622 — and the alert title is that same two-word summary, carried verbatim, unrewritten (the incident channel\'s longer name is incident.io\'s template interpolating alert attributes — themselves ticket-derived — not a rewritten ticket title); the earlier either/or speculation here is retired.',
    "L-rednote-template+crawl")
rep('<span class="nk">Verified Jun 9 — via the incident.io API</span>',
    '<span class="nk">Verified Jun 9, re-checked Jun 10 — via the incident.io API</span>',
    "L-amber-title-date")
rep('carried a queue — “Compute - Cable Repair”, request type 1414 —',
    'carried a queue — “Compute - Cable Repair”, request type 1414 (a request type, strictly; incident.io\'s attribute names these “queues” and the page follows its usage) —',
    "L-queue-gloss")
rep('Name care — a third collision: that FS-side “Partner API”',
    'Name care — a third collision (after the Partner-Ops doc-title overlap in 03 and Kaiser\'s CUJ-numbering in failure mode 2): that FS-side “Partner API”',
    "L-third-collision")
rep('(<a href="#surfaces">§03</a>\'s failure mode 2 holds the name-collision story)',
    '(<a href="#surfaces">§03</a>\'s failure mode 2 holds the CUJ-numbering collision; Kaiser-the-console\'s receipt is ref <a href="#ref-6">[6]</a>)',
    "L-fm2-pointer")

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
