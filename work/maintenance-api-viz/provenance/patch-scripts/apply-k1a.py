#!/usr/bin/env python3
import re, json, subprocess, tempfile
FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html"
s = open(FILE).read()
ok = []

def rep1(old, new, tag):
    global s
    assert s.count(old) == 1, f"{tag}: count={s.count(old)}"
    s = s.replace(old, new); ok.append(tag)

# ---------- CSS for the state-of-play box ----------
rep1('.meta{', '.sop{border:1px solid #2e2e2e;background:var(--panel2);padding:14px 18px;margin:18px 0 4px;font-size:13px;line-height:1.6}.sop .r2{display:flex;gap:12px;margin:3px 0}.sop .lb{font-family:var(--mono);font-size:9.5px;letter-spacing:1.2px;text-transform:uppercase;color:var(--amb);min-width:96px;padding-top:3px;flex-shrink:0}.sop .lb.grn{color:var(--grn)}.meta{', "css-sop")

# ---------- 1. state-of-play box after the meta line ----------
META = '<p class="meta">Owner &amp; build <b>Andrew Louis</b> · Sponsor <b>Rob Colantuoni</b> · Spec to Google <b>~Jul 21, frozen by ~Aug 4</b> · Build starts <b>after the freeze</b></p>'
SOP = META + '''
  <div class="sop" id="state-of-play">
    <div class="r2"><span class="lb grn">direction</span><span>A generic customer-facing surface, not a Borneo one-off (<a href="#ev-scoping">Jun 8 scoping</a>) · mounts behind foundry-gateway (<a href="#surfaces">03</a>/<a href="#foundry">04</a>) · Temporal Cloud + site-local workers (<a href="#ev-kickoff">kickoff</a>) · Auth0 M2M as the working assumption — Tyler's <a href="https://github.com/fluidstackio/foundry/pull/1697" target="_blank" rel="noreferrer">#1697</a> vs Xander's mTLS, <a href="#ev-d-auth">d-auth</a> closing ~Jun 15</span></div>
    <div class="r2"><span class="lb grn">page planks</span><span>batch create · coalescing on (entity, problem_code) · cf_14593 as idempotency key · routing-class field · GET /problem-codes — uncontested, not yet decided (<a href="#timeline">status ledger in 05</a>)</span></div>
    <div class="r2"><span class="lb">open</span><span><a href="#ev-d-vocab">d-vocab</a> · <a href="#ev-d-actions">d-actions</a> · <a href="#ev-d-push">d-push</a> · <a href="#ev-d-cancel">d-cancel</a> · <a href="#ev-d-cuj5">d-cuj5</a> · <a href="#ev-d-revalidate">d-revalidate</a> — plus the declared build-phase opens (fulfill hop · Path A re-wire · IAH1 stand-up)</span></div>
    <div class="r2"><span class="lb">next</span><span>Wk 0–1 inputs by Jun 16 → RFC Jun 23 → OpenAPI skeleton Jul 7 → spec to Google ~Jul 21 → freeze ~Aug 4 · the CUJ3 sequence diagram has been owed to Google since <a href="#ev-asks">Apr 28</a></span></div>
    <div class="r2"><span class="lb">burning</span><span>Machines may land before the API ships — hall 2 is ready-for-service Jun 16; the fallback question is open three ways (<a href="#fallback">the amber note in 01</a>)</span></div>
  </div>'''
rep1(META, SOP, "state-of-play")

# ---------- 2. census paragraph -> table; 8,737 relocates to the 01-A diacap ----------
CENSUS_OLD = s[s.find('<p class="slede">The full boundary census'):]
CENSUS_OLD = CENSUS_OLD[:CENSUS_OLD.find('</p>') + 4]
assert 'forming a bucket of their own' in CENSUS_OLD
GGO = '<a href="https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/internal/server/google.go" target="_blank" rel="noreferrer"><span class="m">google.go</span></a>'
CENSUS_NEW = '''<p class="slede"><b>The full boundary census</b> — five cross-boundary touches; only one carries repair requests:</p>
  <div class="mt c3w">
    <div class="r hd"><span>touch</span><span>repair path?</span><span>status &amp; receipt</span></div>
    <div class="r"><span>① the Jira ticket</span><span>yes — the only one</span><span>JSM (Jira Service Management) transition emails ride it, counted here, not separately — the always-on channel, 02</span></div>
    <div class="r"><span>② the QA-handoff button — a control on the console’s per-rack turn-up step lists (the OCS/TPU rack checklists) that hands fire on finish</span><span>no — rack-checklist closure only; repair-task closure never fires it</span><span>console-button-only (code receipt in 02·B) · its Google side is unverified</span></div>
    <div class="r"><span>③ ''' + GGO + '''’s turn-up trigger</span><span>no — deployment turn-up</span><span>in code but gated off — “Google has yet to actually deploy this workflow”; the Temporal map has the receipt</span></div>
    <div class="r"><span>④ TPU-CC’s diagnostics RPCs</span><span>no — diagnostics</span><span>whether FS ever calls them today is unverified — 01·D</span></div>
    <div class="r"><span>⑤ site-worker’s activity execution</span><span>no — activity plumbing</span><span>laid out in the Temporal map</span></div>
  </div>'''
rep1(CENSUS_OLD, CENSUS_NEW, "census-table")

# the QA-handoff intro sentence (now fully absorbed by census row 2) -> removed, paragraph ends at transport
rep1(' A second, narrower cross-boundary touch exists at the close of rack-checklist work (not repair closure) — the QA-handoff button, a control on the console’s per-rack turn-up step lists (the OCS/TPU rack checklists) that hands fire on finish (detailed in 02·B) — and its Google side is unverified.</p>',
     '</p>', "qa-intro-absorbed")

# 8,737 fact relocates into the 01-A trigger diacap (corrected "names" wording)
rep1('The gated hook marks intent — the start path the API era expects — and the Temporal map carries its receipts.</p>',
     'The gated hook marks intent — the start path the API era expects — and the Temporal map carries its receipts. Rack-turnup is deployment turn-up, not repair, but its QA failures are what <i>file</i> most repair tickets: 8,737 of the corpus’ 15,529 repair tasks reference its runs — all 8,737 repair tasks, verified, counted inside the 15,622, cross-cutting the template buckets rather than forming a bucket of their own (the u-flows panel reconciles).</p>', "8737-relocate")

# ---------- 3. dek #2 shrink (full content lands in the fallback amber note) ----------
rep1("FS's working plan has Borneo never touching the Jira seam<sup class=\"rf\"><a href=\"#ref-10\">[10]</a></sup>; Google's acceptance of that timeline is unestablished. If machines land before the API ships, the Jira seam is the only existing fallback — and it exists at buf101 only; an IAH1 instance would be new deployment work. Atlas leaves Jira only if Rob's pitch to move its traffic onto the same API lands — a workstream pursued in parallel, not a blocker.",
     "FS's working plan has Borneo never touching the Jira seam<sup class=\"rf\"><a href=\"#ref-10\">[10]</a></sup>; Google's acceptance of that timeline is unestablished. If machines land before the API ships, the fallback is undecided — the Jira seam exists at buf101 only, and <a href=\"#fallback\">the fallback note in 01</a> carries the question whole. Atlas leaves Jira only if Rob's pitch to move its traffic onto the same API lands — a workstream pursued in parallel, not a blocker.", "dek2-shrink")

# ---------- 4. two-deployments rows -> cards + fallback amber note ----------
i = s.find('<div class="r"><span>Bloom')
tbl_open = s.rfind('<div class="mt c3w">', 0, i)
hdr_end = s.find('</div>', s.find('<div class="r hd">', tbl_open)) + 6
borneo_i = s.find('<div class="r"><span>Borneo')
tbl_close = s.find('\n  </div>', borneo_i) + len('\n  </div>')
bloom_row = s[i:borneo_i]
borneo_row = s[borneo_i:tbl_close - len('\n  </div>')]

def row_parse(row):
    m = re.match(r'<div class="r"><span>([^<]+)</span><span>([^<]*)</span><span>([\s\S]*)</span></div>\s*$', row.strip())
    assert m, "row parse failed"
    return m.group(1), m.group(2), m.group(3)

def segs_to_kv(inner):
    parts = re.findall(r'<span class="seg">([\s\S]*?)</span>(?=<span class="seg">|$)', inner)
    if not parts:
        parts = [inner]
    out = []
    for p in parts:
        mm = re.match(r'\s*<b>([^<]+?)\.?</b>\s*([\s\S]*)', p)
        if mm:
            out.append((mm.group(1), mm.group(2)))
        else:
            out.append((None, p))
    return out

bname, bwhere, binner = row_parse(bloom_row)
gname, gwhere, ginner = row_parse(borneo_row)
bkv = segs_to_kv(binner)
gkv = segs_to_kv(ginner)

# pull "The gap" out of the Borneo card
gap_body = None
gkv2 = []
for label, body in gkv:
    if label == 'The gap':
        gap_body = body
    else:
        gkv2.append((label, body))
assert gap_body and 'fallback' in gap_body

def card(name, where, kvs, extra=''):
    h = f'<div class="scard">\n      <h3>{name} — {where}</h3>\n'
    for label, body in kvs:
        if label:
            h += f'      <div class="kv"><span class="kk">{label}</span><p>{body}</p></div>\n'
        else:
            h += f'      <p>{body}</p>\n'
    return h + extra + '    </div>'

gap_pointer = '      <div class="kv"><span class="kk">The gap</span><p>No repair traffic yet; the API is specified for it. The rest of the gap — the fallback question — is <a href="#fallback">the amber note below</a>.</p></div>\n'
cards = ('<div class="surfaces">\n    ' + card(bname.strip(), bwhere.strip(), bkv) + '\n    '
         + card(gname.strip(), gwhere.strip(), gkv2, gap_pointer) + '\n  </div>')

# fallback amber note: the gap seg's full content, re-paragraphed (nothing dropped)
gp = gap_body
note = ('\n  <div class="note amber" id="fallback">\n    <span class="nk">The fallback question — open, and burning</span>\n    <p>'
        + gp.replace(' What Borneo uses if machines land', '</p>\n    <p>What Borneo uses if machines land')
            .replace(' BP-232 tracks facility milestones', '</p>\n    <p>BP-232 tracks facility milestones')
            .replace(' So is which Jira project', '</p>\n    <p>So is which Jira project')
        + '</p>\n  </div>')

s = s[:tbl_open] + cards + note + s[tbl_close:]
ok.append("cards+fallback-note")

print("OK:", ok)
open(FILE, "w").write(s)

# ---------- verification ----------
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
