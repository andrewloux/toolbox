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

# ===== A. four missing landmark ids =====
rep('<div class="sub"><span class="sk2">01·A</span>', '<div class="sub" id="upstream"><span class="sk2">01·A</span>', "id-01A")
rep('<div class="sub"><span class="sk2">01·B</span>', '<div class="sub" id="todaytomorrow"><span class="sk2">01·B</span>', "id-01B")
rep('<div class="sub"><span class="sk2">02·A</span>', '<div class="sub" id="demux"><span class="sk2">02·A</span>', "id-02A")
rep('<div class="sub"><span class="sk2">02·B</span>', '<div class="sub" id="pathb"><span class="sk2">02·B</span>', "id-02B")

# ===== B. census table =====
rep('the always-on channel, 02</span>', 'the always-on channel, <a href="#routing">02</a></span>', "census-1")
rep('console-button-only (code receipt in 02·B)', 'console-button-only (code receipt in <a href="#pathb">02·B</a>)', "census-2")
rep('”; the Temporal map has the receipt</span>', '”; <a href="#temporal-map">the Temporal map</a> has the receipt</span>', "census-3")
rep('whether FS ever calls them today is unverified — 01·D</span>', 'whether FS ever calls them today is unverified — <a href="#vocab">01·D</a></span>', "census-4")
rep('<span>laid out in the Temporal map</span>', '<span>laid out in <a href="#temporal-map">the Temporal map</a></span>', "census-5")

# ===== C. other HTML bare pointers =====
rep('session-cited attribution — see the decoder)', 'session-cited attribution — see <a href="#decoder">the decoder</a>)', "decoder-link")
rep('8,900+ ICI occurrences, 01·D)', '8,900+ ICI occurrences, <a href="#vocab">01·D</a>)', "ici-01D")
rep('and the Temporal map carries its receipts', 'and <a href="#temporal-map">the Temporal map</a> carries its receipts', "hook-tmap")
rep('gated off in code today (01·A above)', 'gated off in code today (<a href="#upstream">01·A</a> above)', "01A-above")
rep("idempotency/dedup key in 01·C's correlation row", 'idempotency/dedup key in <a href="#anatomy">01·C</a>\'s correlation row', "01C-correlation")
rep('(full receipt in 01·C).</p></div>', '(full receipt in <a href="#anatomy">01·C</a>).</p></div>', "01C-full-receipt")
rep("the open boundary question in 01·C's anatomy row", 'the open boundary question in <a href="#anatomy">01·C</a>\'s anatomy row', "01C-anatomy-row")
rep("wider than 01·D's corpus-wide", 'wider than <a href="#vocab">01·D</a>\'s corpus-wide', "01D-corpus")
rep('(full lifecycle: 02·C)', '(full lifecycle: <a href="#sop">02·C</a>)', "02C-lifecycle")
rep('loop back into the SOP library (02·C)', 'loop back into the SOP library (<a href="#sop">02·C</a>)', "02C-library")
rep("PIN panel (02·B) scopes", 'PIN panel (<a href="#v-pipe">02·B</a>) scopes', "02B-pin")
rep('Partner Operations API (03), and not', 'Partner Operations API (<a href="#surfaces">03</a>), and not', "03-partner-ops")
rep("async terminal state (01·B / 02·B), warn-don't-reject for unknown vocabulary (01·D), and tenant-scoped vocab + authz in v0.1 (the Atlas pitch).",
    'async terminal state (<a href="#todaytomorrow">01·B</a> / <a href="#pathb">02·B</a>), warn-don\'t-reject for unknown vocabulary (<a href="#vocab">01·D</a>), and tenant-scoped vocab + authz in v0.1 (the <a href="#ev-p5">Atlas pitch</a>).', "planks-positions")
rep('on create (01·B)</span>', 'on create (<a href="#todaytomorrow">01·B</a>)</span>', "01B-routing-class")
rep('SOP·1 BORN, and 02·B)', 'SOP·1 BORN, and <a href="#pathb">02·B</a>)', "02B-ref10")

# ===== D. section-symbol refs =====
rep('note; §04’s feldspar group list', 'note; <a href="#foundry">§04</a>’s feldspar group list', "s04-feldspar")
rep("(§03's failure mode 2 holds", '(<a href="#surfaces">§03</a>\'s failure mode 2 holds', "s03-failure-mode")
rep("is §04's BlueBook-driven scan", 'is <a href="#foundry">§04</a>\'s BlueBook-driven scan', "s04-bluebook")
rep('installed-state store — §04)', 'installed-state store — <a href="#foundry">§04</a>)', "s04-crucible")
rep("open dependency of §04's migration", 'open dependency of <a href="#foundry">§04</a>\'s migration', "s04-migration")

# ===== E. DRILL bodies (single-quoted attrs) =====
rep("not yet designed (§03's CUJ4 row)", "not yet designed (<a href='#surfaces'>§03</a>'s CUJ4 row)", "s03-cuj4-drill")
rep('the same single count cited in 01·D.</p>', "the same single count cited in <a href='#vocab'>01·D</a>.</p>", "01D-drill")
rep('(the 02·C footer traces it)', "(the <a href='#sop'>02·C</a> footer traces it)", "02C-drill")

print("OK:", len(ok), ok)
print("MISS:", miss)
if miss: raise SystemExit("ABORT: misses present, file NOT written")
open(FILE, "w").write(s)

# ===== verification battery =====
m = re.search(r'<script>([\s\S]*)</script>', s)
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
    f.write("try { new Function(" + json.dumps(m.group(1)) + "); console.log('JS parses OK') } catch(e) { console.log('JS ERROR:', e.message) }")
    p = f.name
print(subprocess.run(['node', p], capture_output=True, text=True).stdout.strip())

# dead-anchor audit: every #href must resolve to an id or an EVENTS id
ids = set(re.findall(r'id="([^"]+)"', s)) | set(re.findall(r"id='([^']+)'", s))
ev = s[s.find('const EVENTS'):s.find('];', s.find('const EVENTS'))]
ev_ids = set(re.findall(r'id:\s*"([^"]+)"', ev))
dead = []
for h in set(re.findall(r'href=[\'"]#([^\'"]+)[\'"]', s)):
    if h in ids: continue
    if h.startswith('ev-') and h[3:] in ev_ids: continue
    dead.append(h)
print("dead anchors:", sorted(dead))

base = json.load(open('/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/data/inventory-v88.json'))
hrefs = set(re.findall(r'href=[\'"]([^\'"]+)[\'"]', s))
nums = set(re.findall(r'\b\d[\d,]*(?:\.\d+)?%?\b', s))
print("href removals:", sorted(set(base['hrefs']) - hrefs))
print("num removals:", sorted(set(base['nums']) - nums))
