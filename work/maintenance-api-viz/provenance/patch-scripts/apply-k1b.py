#!/usr/bin/env python3
import re, json, subprocess, tempfile
FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html"
s = open(FILE).read()
ok = []

def rep1(old, new, tag):
    global s
    assert s.count(old) == 1, f"{tag}: count={s.count(old)}"
    s = s.replace(old, new); ok.append(tag)

# ---------- 1. cut the temporal-map block out of the decoder run ----------
i = s.find('<div id="temporal-map">')
assert i > 0
e = s.find('</div>', i)
assert 0 < e - i < 5000 and s.count('<div', i, e) == 1, "map block bounds"
map_block = s[i:e+6]
s = s[:i] + s[e+6:]
ok.append("map-cut")

# ---------- 2. decoder: landmark + one-entry-per-line; hardware merged ----------
di = s.find('<p class="slede">Name decoder, since both vocabularies appear.')
de = s.find('</p>', di) + 4
dec = s[di:de]
dec = dec.replace('<p class="slede">Name decoder, since both vocabularies appear. <b>Sites:</b>',
                  '<p class="slede"><b>Sites:</b>')
dec = dec.replace(' · <span class="m">', '<br><span class="m">')
landmark = '<div class="sub" id="decoder"><span class="sk2">01·REF</span><h3>Name decoder — reference; skip on a fast pass</h3></div>\n  '
s = s[:di] + landmark + dec + s[de:]
ok.append("decoder-lines")

hi = s.find('<p class="slede">Hardware layer, same treatment:')
he = s.find('</p>', hi) + 4
hw = s[hi:he]
hw = hw.replace('<p class="slede">Hardware layer, same treatment: ', '<p class="slede"><b>Hardware:</b> ')
hw = hw.replace(' · <span class="m">', '<br><span class="m">')
s = s[:hi] + hw + s[he:]
ok.append("hardware-lines")

# decoder's Temporal pointer: now points below 01·B
n = s.count('the Temporal map in 01')
s = s.replace('the Temporal map in 01', 'the Temporal map (01·MAP, after 01·B)')
ok.append(f"map-pointers-x{n}")

# ---------- 3. re-insert the map after 01·B with its landmark ----------
LEAD = '<p class="slede"><b>The Temporal map — every engine on this page, in one place.</b> '
assert map_block.count(LEAD) == 1
map_block = map_block.replace(LEAD, '<p class="slede">')
MAPSUB = '<div class="sub" id="tmap"><span class="sk2">01·MAP</span><h3>The Temporal map — every engine on this page, in one place</h3></div>\n  '
rep1('<!-- 01·C anatomy -->', MAPSUB + map_block + '\n\n  <!-- 01·C anatomy -->', "map-insert")

# ---------- 4. two-deployments landmark ----------
rep1('<p class="slede" style="margin-top:26px"><b>Two deployments, one page.</b> Every “today” receipt on this page comes from the first; the API is being built for the second:</p>',
     '<div class="sub" id="twodep"><span class="sk2">01·0</span><h3>Two deployments, one page</h3></div>\n  <p class="slede">Every “today” receipt on this page comes from the first; the API is being built for the second:</p>', "twodep-landmark")

# ---------- 5. 05 planks -> table; direction-class sentence; extend-line to colophon ----------
pi = s.find('<p class="slede">Four planks are this page\'s proposals')
pe = s.find('</p>', pi) + 4
planks = s[pi:pe]
items = planks.split('<br>')
assert len(items) == 6, f"plank items={len(items)}"
lead = items[0][len('<p class="slede">'):].rstrip(':') + '.'
def split_item(it):
    it = it.replace('</p>', '')
    m = re.match(r'<b>([\s\S]*?)</b>\s*(?:\(01·B\)\s*)?—?\s*([\s\S]*)', it)
    if m: return m.group(1), m.group(2)
    return None, it
tbl_rows = []
b1, d1 = split_item(items[1]); tbl_rows.append(('batch create', d1))
b2, d2 = split_item(items[2]); tbl_rows.append(('coalescing on (entity, problem_code)', d2))
b3, d3 = split_item(items[3]); tbl_rows.append(('cf_14593 as the create-side idempotency key', d3))
b4, d4 = split_item(items[4]); tbl_rows.append(('the routing-class field on create (01·B)', d4))
getline = items[5].replace('</p>', '')
tbl_rows.append(('GET /problem-codes', getline.replace('GET /problem-codes shares the uncontested status.', 'shares the uncontested status; what registry backs it is the open half (<a href="#ev-d-vocab">d-vocab</a>).')))
tbl = '<p class="slede">' + lead + '</p>\n  <div class="mt c3w">\n    <div class="r hd"><span>plank</span><span></span><span>who is already asking, and the receipts</span></div>\n'
for name, desc in tbl_rows:
    tbl += f'    <div class="r"><span>{name}</span><span></span><span>{desc.strip()}</span></div>\n'
tbl += '  </div>'
s = s[:pi] + tbl + s[pe:]
ok.append("planks-table")

rep1('are declared where they arise and deliberately not rowed.',
     'are declared where they arise and deliberately not rowed. Direction-class items — the generic surface, the gateway mount, Temporal Cloud + site-local workers — are settled direction, not d-rows; the header’s state-of-play box gathers them.', "direction-class")

rep1('  <p class="slede">To extend this doc, append to the <span class="m">EVENTS</span> array in source — the UI renders from it.</p>\n', '', "extend-cut")
rep1('jira/slack pulls verified live in-session</p>',
     'jira/slack pulls verified live in-session · to extend this doc, append to the EVENTS array in source — the UI renders from it</p>', "extend-colophon")

print("OK:", ok)
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
