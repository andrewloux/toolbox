#!/usr/bin/env python3
import re, json, subprocess, tempfile
FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html"
s = open(FILE).read()
ok, miss = [], []

def rep(old, new, tag, n=1):
    global s
    c = s.count(old)
    if c != n:
        miss.append(f"{tag} (count={c})"); return
    s = s.replace(old, new); ok.append(tag)

# ===== MEDIUM: the 33 / 1,079 / Clean+Reseat taxonomy, reconciled with the arithmetic receipt =====

# M1: 01·D who-files row
rep('humans 1,112 (1,079 file free-text; the other 33 use template shapes)',
    'humans 1,112 (1,079 in the free-text bucket — “matches none of the four bot template families,” which is where the campaign templates live; 33 match a bot family\'s shape)', "M1-whofiles")

# M2: 01·D template-families row
rep('repair-tuple 4,728 (carries the API schema) · QA sweeps 4,493 · install sweeps 2,105 · other machine 3,217 · human free-text 1,079',
    'repair-tuple 4,728 (carries the API schema) · QA sweeps 4,493 · install sweeps 2,105 · other machine 3,217 · free-text bucket 1,079 (all human; “free-text” = matches no bot family — Jun 4\'s Clean+Reseat: campaign sits here)', "M2-familyrow")

# M3: entity-grammar panel
rep('zero typed coverage across the 1,079 free-text tickets where the cleaning campaigns live',
    'zero typed coverage across the 1,079 free-text-bucket tickets where the cleaning campaigns live', "M3-grammar")

# M4a: u-flows fact — bucket label + breathing room
rep("· other machine 3,217 · human free-text 1,079. Template counting",
    "· other machine 3,217 · free-text bucket 1,079, all human (“free-text” = matches no bot family).<br>Template counting", "M4a-uflows-bucket")

# M4b: u-flows fact — the 33 redefined with the receipt, prefix myth killed
rep('The 33 “template-shaped humans” is a different, wider cut (summary shape: SW:/HW:/Clean+Reseat prefixes); only 4 of the 33 carry the full repair-tuple body, and those 4 sit inside the 21 workflow-naming human tickets.',
    '<br>The 33 “template-shaped humans” are the humans sitting inside the four template buckets — arithmetic receipt: those buckets total 14,543 = 14,510 bot + 33. Prefix alone doesn\'t make the cut: 794 humans start HW:, 26 start SW:, and Jun 4\'s 114 carry the campaign\'s own Clean+Reseat: prefix, yet only 33 match an actual bot family shape (recounted from the archive, Jun 10). Only 4 of the 33 carry the full repair-tuple body; those 4 sit inside the 21 workflow-naming human tickets.', "M4b-uflows-33")

# M5: 01·C anatomy slede — drop the unverifiable one-of-33 claim
rep('This exemplar happens to be hand-filed, one of the 33 template-shaped human tickets — and one of just 4 whose body is the full repair-tuple, the shape of the 4,728-ticket family. The template buckets count shape, not reporter; the 33 human template tickets sit inside them.',
    'This exemplar happens to be hand-filed — HW:-prefixed, like most hand filings — and one of just 4 human tickets whose body is the full repair-tuple, the shape of the 4,728-ticket family. The template buckets count shape, not reporter: 33 human tickets sit inside them (the four buckets total 14,543 = 14,510 bot + 33).', "M5-anatomy")

# M6: bulk+human drill — kill the free-text-Clean+Reseat oxymoron
rep("Campaigns arrive schema-less: the June 4 DCN cleaning campaign pushed 114 free-text <span class='m'>Clean+Reseat</span> tickets in under an hour, and 87 of them (76%) were ultimately Rejected.",
    "Campaigns arrive schema-less: the June 4 DCN cleaning campaign pushed 114 <span class='m'>Clean+Reseat:</span>-prefixed tickets in under an hour — the prefix is the campaign's own batch template, not a bot family, so they sit in the free-text bucket — and 87 of them (76%) were ultimately Rejected.", "M6-campaign-drill")

# M7: storm2 event detail (EVENTS — plain text, backticks ok)
rep('The campaign itself verifies in the archived corpus: 114 `Clean+Reseat` tickets on Jun 4, every one filed by Mohamed Ali (FS)',
    'The campaign itself verifies in the archived corpus: 114 `Clean+Reseat:`-prefixed tickets on Jun 4 — the campaign\'s own batch template, not a bot family, so they count in the free-text bucket — every one filed by Mohamed Ali (FS)', "M7-storm2")

# ===== LOWs =====

# L1: "at closure" misdirection
rep('A second, narrower cross-boundary touch exists at closure — the QA-handoff button',
    'A second, narrower cross-boundary touch exists at the close of rack-checklist work (not repair closure) — the QA-handoff button', "L1-closure")

# L2: Kaiser gloss at first use (config-home row)
rep('its source moved to the Kaiser repo on Jun 10 (<a href="https://github.com/fluidstackio/infrastructure-management" target="_blank" rel="noreferrer">infrastructure-management</a>, via dcim <a href="https://github.com/fluidstackio/dcim/pull/2525" target="_blank" rel="noreferrer">#2525</a>)',
    'its source moved on Jun 10 to the Kaiser repo — Kaiser is FS\'s business-planning console (§03\'s failure mode 2 holds the name-collision story); its repo, <a href="https://github.com/fluidstackio/infrastructure-management" target="_blank" rel="noreferrer">infrastructure-management</a>, now houses the unified-console work — via dcim <a href="https://github.com/fluidstackio/dcim/pull/2525" target="_blank" rel="noreferrer">#2525</a>', "L2-kaiser-gloss")

# L3: code-fields table preamble (two actions among the codes)
rep('This table counts ticket-level code fields.',
    'This table counts values seen in ticket-level code fields — five are problem codes; two are actions that leaked into a code field (their rows say so).', "L3-codefields")

# L4: drift-note disambiguation, simplified
rep('(Don\'t confuse this entries-vs-enum comparison <i>across</i> the two files with the within-file duplicate collapses the denominator key describes.)',
    '(Two different comparisons: this note sets entries against enums <i>across</i> the two files; the denominator key above collapses duplicates <i>within</i> the entries file.)', "L4-driftnote")

print("OK:", len(ok), ok)
print("MISS:", miss)
open(FILE, "w").write(s)
m = re.search(r'<script>([\s\S]*)</script>', s)
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
    f.write("try { new Function(" + json.dumps(m.group(1)) + "); console.log('JS parses OK') } catch(e) { console.log('JS ERROR:', e.message) }")
    p = f.name
print(subprocess.run(['node', p], capture_output=True, text=True).stdout.strip())
ev = re.search(r'const EVENTS\s*=\s*\[([\s\S]*?)\n\];', s)
print("EVENTS html-in-string violations:", len(re.findall(r'(?:title|summary|detail)\s*:\s*"[^"]*<a ', ev.group(1))))
# taxonomy consistency: no remaining "free-text Clean+Reseat" or bare "1,079 file free-text"
print("oxymoron remnants:", s.count('free-text Clean+Reseat') + s.count('1,079 file free-text') + s.count('SW:/HW:/Clean+Reseat prefixes'))
