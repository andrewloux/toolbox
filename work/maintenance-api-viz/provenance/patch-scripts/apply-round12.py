#!/usr/bin/env python3
import re, json, subprocess, tempfile
FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html"
s = open(FILE).read()
ok, miss = [], []
def rep(old, new, tag, n=1):
    global s
    c = s.count(old)
    if c != n: miss.append(f"{tag} ({c})"); return
    s = s.replace(old, new); ok.append(tag)

# ===== MEDIUM: ref-10 ledger vs recovered TROSS-SOP receipt =====
rep('the May 22 validation-sweep storm (~100 tickets/2 h) and its hand-written TROSS SOP;',
    'the May 22 storm count (~100 tickets/2 h — the count is session-derived; the TROSS-SOP story itself IS receipted: Rob logs the SOP and assigns in-channel, the permalink cited at the storm1 event, SOP·1 BORN, and 02·B);', "M-ref10-tross")

# ===== L1: plank ledger non-exhaustive =====
rep("Five planks are this page's proposals — uncontested in the working plan (no voice read disputes them, so they carry no d-row), not decided contract.",
    "Five planks are this page's proposals — uncontested in the working plan (no voice read disputes them, so they carry no d-row), not decided contract. Three more page positions of the same status ride their home sections as spec consequences: Rejected as a machine-readable async terminal state (01·B / 02·B), warn-don't-reject for unknown vocabulary (01·D), and tenant-scoped vocab + authz in v0.1 (the Atlas pitch).", "L1-ledger-scope")

# ===== L2: chip split (one status per chip) + webhook consumer box dashed =====
rep('<rect class="sv-chip" x="392" y="162" width="238" height="24" rx="4"/>',
    '<rect class="sv-chip" x="392" y="162" width="104" height="24" rx="4"/>\n        <rect class="sv-chip open" x="502" y="162" width="128" height="24" rx="4"/>', "L2-chip-rects")
rep('<text class="sv-chipt" x="402" y="178">gateway mount · Auth0 M2M — d-auth</text>',
    '<text class="sv-chipt" x="402" y="178">gateway mount</text>\n        <text class="sv-chipt" x="510" y="178">Auth0 M2M — d-auth</text>', "L2-chip-texts")
rep('.sv-chip.open{stroke-dasharray:5 3}.sv-chip.plank{stroke-dasharray:2 3}.sv-edge.dash{stroke-dasharray:6 4}',
    '.sv-chip.open{stroke-dasharray:5 3}.sv-chip.plank{stroke-dasharray:2 3}.sv-edge.dash{stroke-dasharray:6 4}.sv-box.dash{stroke-dasharray:6 4}', "L2-css")
rep('<rect class="sv-box" x="38" y="260" width="212" height="80" rx="4"/>\n        <text class="sv-t" x="54" y="288">Webhook consumer</text>',
    '<rect class="sv-box dash" x="38" y="260" width="212" height="80" rx="4"/>\n        <text class="sv-t" x="54" y="288">Webhook consumer</text>', "L2-webhook-box")

# ===== L3: PIN/PINNED pointer =====
rep('the pin panel scopes how often that is',
    "the pipeline's stage-3 PIN panel (02·B) scopes how often that is", "L3-pin")

# ===== L4: code-field classifier (rows are canonical) =====
rep('This table counts values seen in ticket-level code fields — five are problem codes; two are actions that leaked into a code field (their rows say so).',
    'This table counts values seen in ticket-level code fields — seven values absent from the proto, each row classifying its own: real codes, part labels, lifecycle states, and actions leaking into a code field.', "L4-classifier")

# ===== L5: provenance slips =====
rep('The customer there was never disclosed — “they were cagey”.',
    'The customer there was never disclosed — “they were cagey” (Rob, in the Mar 17 thread; the finland event links it).', "L5-cagey")
rep('decision not yet closed; he returns in a day.',
    'decision not yet closed; Xander returns in a day, per the Jun 9 Granola notes.', "L5-xander")

# ===== L6: u-flows decomposition as bullet lines =====
i = s.find('the gap decomposes:')
if i > 0 and s.count('the gap decomposes:') == 1:
    e = s.find('not a sixth machine filer', i)
    e2 = e + len('not a sixth machine filer')
    seg = s[i:e2]
    new_seg = ('the gap decomposes:<br>· ~30 — drift between two tuple-extraction runs (the Jun 9 mining session counted 4,728; this page\'s summary-shape recount found 4,698)<br>· ~20 — tuple-shaped tickets whose run links don\'t parse to a doctor<br>· exactly 4 — hand-filed full repair-tuples; not a sixth machine filer')
    # sanity: all three figures present in original seg
    if all(x in seg for x in ['~30', '~20', '4,698', 'hand-filed']):
        s = s[:i] + new_seg + s[e2:]
        ok.append("L6-decomposition")
    else:
        miss.append("L6 (seg content)")
else:
    miss.append(f"L6 (count={s.count('the gap decomposes:')})")

# ===== L7: decoder -> table =====
def para_bounds(anchor):
    i = s.find(anchor)
    if i < 0: return None
    st = s.rfind('<p class="slede">', 0, i + 20)
    en = s.find('</p>', i) + 4
    return st, en

def to_rows(content, first_group):
    # content: inner HTML without <p> wrapper
    content = content
    groups = re.split(r'<br><b>([^<]+):</b>\s*', content)
    # groups[0] belongs to first_group
    pairs = [(first_group, groups[0])]
    for gi in range(1, len(groups), 2):
        pairs.append((groups[gi], groups[gi+1]))
    rows = []
    for gname, body in pairs:
        rows.append(f'    <div class="r hd"><span>{gname}</span><span></span></div>')
        entries = body.split('<br><span class="m">')
        for k, ent in enumerate(entries):
            ent = ent.strip()
            if not ent: continue
            if k > 0: ent = '<span class="m">' + ent
            m = re.match(r'(<span class="m">.*?</span>)\s*=\s*([\s\S]*)', ent)
            if m:
                rows.append(f'    <div class="r"><span>{m.group(1)}</span><span>{m.group(2)}</span></div>')
            else:
                rows.append(f'    <div class="r"><span></span><span>{ent}</span></div>')
    return rows

b1 = para_bounds('<b>Sites:</b>')
b2 = para_bounds('<b>Hardware:</b>')
if b1 and b2 and b1[0] < b2[0]:
    p1 = s[b1[0]:b1[1]]
    p2 = s[b2[0]:b2[1]]
    c1 = p1[len('<p class="slede"><b>Sites:</b>'):-4].strip() if p1.startswith('<p class="slede"><b>Sites:</b>') else None
    c2 = p2[len('<p class="slede"><b>Hardware:</b>'):-4].strip() if p2.startswith('<p class="slede"><b>Hardware:</b>') else None
    if c1 is not None and c2 is not None:
        rows = to_rows(c1, 'Sites') + to_rows(c2, 'Hardware')
        tbl = '<div class="mt c3w">\n' + '\n'.join(rows) + '\n  </div>'
        between = s[b1[1]:b2[0]]
        s = s[:b1[0]] + tbl + s[b2[1]:]
        if between.strip():
            miss.append("L7 (content between decoder paras dropped guard)")
            raise SystemExit("ABORT: non-empty content between decoder paragraphs: " + between[:200])
        ok.append(f"L7-decoder-table ({len(rows)} rows)")
    else:
        miss.append("L7 (paragraph prefix)")
else:
    miss.append("L7 (bounds)")

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
