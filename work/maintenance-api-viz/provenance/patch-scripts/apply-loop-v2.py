#!/usr/bin/env python3
import re, json, subprocess, tempfile
BASE = "/Users/andrew/code/personal/toolbox/work/maintenance-api-viz"
ok, miss = [], []

# ---- 1. CSS for the type grammar ----
css = open(f"{BASE}/src/02-theme.css").read()
NEW_CSS = """
.sv-pill{fill:rgba(168,224,95,.08);stroke:#7fa758;stroke-width:1.1}
.sv-pt{font-family:var(--mono);font-size:11.5px;font-weight:600;fill:#cfe8a8;letter-spacing:.3px}
.sv-tag{font-family:var(--mono);font-size:9px;letter-spacing:1px;fill:var(--dim)}
"""
if '.sv-pill' not in css:
    open(f"{BASE}/src/02-theme.css","w").write(css.rstrip() + "\n" + NEW_CSS)
    ok.append("css")

# ---- 2. replace the loop SVG with the component-grammar version ----
s = open(f"{BASE}/src/10-seam.html").read()
i = s.find('<div class="diawrap"><svg class="wide" viewBox="0 0 1480 600"')
j = s.find('</svg></div>', i) + len('</svg></div>')
assert i > 0 and j > i

NEW_SVG = '''<div class="diawrap"><svg class="wide" viewBox="0 0 1700 740" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Component view of the repair loop today: Google workflows file a Jira ticket; FluidStack services mirror it; techs self-claim and execute; the Done transition wakes the parked run; failures refile.">
      <defs>
        <marker id="ah7" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#5a5a5a"/></marker>
        <marker id="ahg7" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#A8E05F"/></marker>
      </defs>

      <rect class="sv-zone" x="18" y="44" width="1664" height="166"/>
      <text class="sv-zl g" x="32" y="64">GOOGLE&#8217;S ENGINE &#183; TEMPORAL IN GOOGLE-SYSTEM &#8212; THEIR CODE, OUR CLUSTER</text>
      <rect class="sv-zone" x="18" y="260" width="1664" height="146"/>
      <text class="sv-zl" x="32" y="280">THE SEAM &#183; ATLASBUF &#8212; JIRA SERVICE MANAGEMENT</text>
      <rect class="sv-zone" x="18" y="470" width="1664" height="180"/>
      <text class="sv-zl" x="32" y="490">FLUIDSTACK&#8217;S FLOOR &#183; DCIM-TASKS &#8594; CONSOLE &#8594; HANDS</text>

      <!-- refile arc (drawn first, under everything) -->
      <path class="sv-edge g" d="M1475 84 V 26 H 600 V 78" marker-end="url(#ahg7)"/>
      <text class="sv-s" x="700" y="20">refile on failed re-QA &#8212; the Attempt counters in the corpus</text>

      <!-- ===== GOOGLE LANE: components ===== -->
      <g data-d="u-diag">
        <rect class="sv-box" x="40" y="84" width="260" height="104" rx="3"/>
        <text class="sv-tag" x="288" y="100" text-anchor="end">TEMPORAL WORKFLOWS</text>
        <text class="sv-t" x="54" y="120">the doctor family</text>
        <text class="sv-m" x="54" y="142">machine-doctor &#183; ocs-link &#183;</text>
        <text class="sv-m" x="54" y="158">link-repair &#183; rack-turnup QA</text>
        <text class="sv-s" x="54" y="176">rack-turnup&#8217;s QA failures file most tickets</text>
      </g>
      <g data-d="s-ticket">
        <rect class="sv-box" x="470" y="84" width="260" height="104" rx="3"/>
        <text class="sv-tag" x="718" y="100" text-anchor="end">SERVICE ACCOUNT</text>
        <text class="sv-t" x="484" y="120">the filer</text>
        <text class="sv-m" x="484" y="142">Ext-Bloom-Atlas-Workflows</text>
        <text class="sv-s" x="484" y="160">writes 5 templated custom fields</text>
        <text class="sv-s" x="484" y="176">93% of all 15,622 tickets</text>
      </g>
      <g data-d="s-paused">
        <rect class="sv-box" x="900" y="84" width="260" height="104" rx="3"/>
        <text class="sv-tag" x="1148" y="100" text-anchor="end">WORKFLOW RUN</text>
        <text class="sv-t" x="914" y="120">the parked run</text>
        <text class="sv-m" x="914" y="142">sits on the status field</text>
        <text class="sv-s" x="914" y="160">ticket footer: &#8220;Close this ticket &#8230;</text>
        <text class="sv-s" x="914" y="176">to resume the workflow&#8221;</text>
      </g>
      <g data-d="u-flows">
        <rect class="sv-box" x="1330" y="84" width="290" height="104" rx="3"/>
        <text class="sv-tag" x="1608" y="100" text-anchor="end">WORKFLOW RUN</text>
        <text class="sv-t" x="1344" y="120">the woken run</text>
        <text class="sv-m" x="1344" y="142">re-runs QA &#8212; their workers</text>
        <text class="sv-s" x="1344" y="160">pass &#8594; machine back in the pool</text>
        <text class="sv-s" x="1344" y="176">fail &#8594; refile, Attempt++</text>
      </g>

      <!-- ===== SEAM LANE ===== -->
      <g data-d="s-pathA">
        <rect class="sv-box" x="40" y="292" width="260" height="92" rx="3"/>
        <text class="sv-tag" x="288" y="308" text-anchor="end">SAAS LISTENER</text>
        <text class="sv-t" x="54" y="328">incident.io</text>
        <text class="sv-m" x="54" y="350">ingests repairs as P4 alerts</text>
        <text class="sv-s" x="54" y="368">no paging route matches &#8212; by design</text>
      </g>
      <g data-d="p-tkt">
        <rect class="sv-box" x="470" y="292" width="260" height="92" rx="3"/>
        <text class="sv-tag" x="718" y="308" text-anchor="end">JIRA ARTIFACT</text>
        <text class="sv-t" x="484" y="328">the ticket</text>
        <text class="sv-m" x="484" y="350">Physical Repair Task</text>
        <text class="sv-s" x="484" y="368">priority Medium = the Jira default</text>
      </g>
      <rect class="sv-chip" x="1170" y="312" width="300" height="26" rx="4"/>
      <text class="sv-chipt" x="1182" y="329">SIGNAL &#183; the status field &#8212; the only return channel</text>

      <!-- ===== FLOOR LANE: components ===== -->
      <g data-d="p-sync">
        <rect class="sv-box" x="40" y="502" width="280" height="104" rx="3"/>
        <text class="sv-tag" x="308" y="518" text-anchor="end">GO SERVICE</text>
        <text class="sv-t" x="54" y="538">dcim-tasks &#183; JSM sync</text>
        <text class="sv-m" x="54" y="560">inbound mirror + outbound writer</text>
        <text class="sv-s" x="54" y="578">polls 5m discovery / 10m drift &#183; 30s drain</text>
        <text class="sv-s" x="54" y="594">its webhook ingest: built, dark (Mar 28)</text>
      </g>
      <g data-d="p-queue">
        <rect class="sv-box" x="470" y="502" width="260" height="104" rx="3"/>
        <text class="sv-tag" x="718" y="518" text-anchor="end">WEB UI</text>
        <text class="sv-t" x="484" y="538">the console queue</text>
        <text class="sv-m" x="484" y="560">dcim.fluidstack.io &#183; repairs</text>
        <text class="sv-s" x="484" y="578">task lands unassigned,</text>
        <text class="sv-s" x="484" y="594">pinned SOP rendered as panels</text>
      </g>
      <g data-d="p-route">
        <rect class="sv-box" x="900" y="502" width="260" height="104" rx="3"/>
        <text class="sv-tag" x="1148" y="518" text-anchor="end">HUMANS</text>
        <text class="sv-t" x="914" y="538">DC techs &#8212; &#8220;hands&#8221;</text>
        <text class="sv-m" x="914" y="560">claim, walk the floor, repair</text>
        <text class="sv-s" x="914" y="578">a lead-routing role exists &#8212;</text>
        <text class="sv-s" x="914" y="594">permissions granted Jun 9</text>
      </g>
      <g data-d="sop-pin">
        <rect class="sv-box" x="1330" y="502" width="290" height="104" rx="3"/>
        <text class="sv-tag" x="1608" y="518" text-anchor="end">VERSIONED PROCEDURE</text>
        <text class="sv-t" x="1344" y="538">the pinned SOP</text>
        <text class="sv-m" x="1344" y="560">resolved from the problem code</text>
        <text class="sv-s" x="1344" y="578">version pinned at workflow start;</text>
        <text class="sv-s" x="1344" y="594">guide panels + evidence capture</text>
      </g>

      <!-- ===== EDGES + ACTION PILLS (numbered, time order) ===== -->
      <path class="sv-edge g" d="M300 136 H 464" marker-end="url(#ahg7)"/>
      <g data-d="u-diag"><rect class="sv-pill" x="312" y="110" width="142" height="24" rx="12"/><text class="sv-pt" x="324" y="126">&#9312; DETECT</text></g>
      <text class="sv-s" x="306" y="156">emits (entity &#183; problem_code &#183; action)</text>

      <path class="sv-edge g" d="M600 188 V 286" marker-end="url(#ahg7)"/>
      <g data-d="s-ticket"><rect class="sv-pill" x="520" y="214" width="118" height="24" rx="12"/><text class="sv-pt" x="532" y="230">&#9313; FILE</text></g>
      <text class="sv-s" x="650" y="230">RT &#8220;Deployment&#8221; 1669 &#183; storms: 1,127 in 48 min</text>

      <path class="sv-edge g" d="M730 136 H 894" marker-end="url(#ahg7)"/>
      <g data-d="s-paused"><rect class="sv-pill" x="745" y="110" width="124" height="24" rx="12"/><text class="sv-pt" x="757" y="126">&#9314; PARK</text></g>

      <path class="sv-edge" d="M470 338 H 306" marker-end="url(#ah7)"/>
      <text class="sv-s" x="330" y="330">listener A</text>

      <path class="sv-edge" d="M520 384 V 446 H 180 V 496" marker-end="url(#ah7)"/>
      <g data-d="p-sync"><rect class="sv-pill" x="210" y="424" width="142" height="24" rx="12"/><text class="sv-pt" x="222" y="440">&#9315; MIRROR</text></g>
      <text class="sv-s" x="210" y="464">listener B &#8212; poll, not push</text>

      <g data-d="l-classify"><rect class="sv-pill" x="790" y="300" width="330" height="24" rx="12"/><text class="sv-pt" x="802" y="316">&#9316; CLASSIFY / ACK &#8212; NOTHING FIRES</text></g>
      <text class="sv-s" x="790" y="344">Severity field: never set &#183; SLA clocks: never run</text>
      <text class="sv-s" x="790" y="360">no paging &#183; contract Sev1&#8211;4 + FS&#8217;s own escalation</text>
      <text class="sv-s" x="790" y="376">matrix: both on paper only &#8212; click the pill</text>

      <path class="sv-edge" d="M1030 502 V 338 H 736" marker-end="url(#ah7)"/>
      <g data-d="l-assign"><rect class="sv-pill" x="905" y="424" width="250" height="24" rx="12"/><text class="sv-pt" x="917" y="440">&#9317; ASSIGN &#8212; SELF-CLAIM</text></g>
      <text class="sv-s" x="905" y="464">tech sets assignee = self &#183; 50s&#8211;44m &#183; 79% of Done: never assigned</text>

      <path class="sv-edge" d="M730 554 H 894" marker-end="url(#ah7)"/>
      <text class="sv-s" x="752" y="546">opens the task</text>
      <path class="sv-edge" d="M1160 554 H 1324" marker-end="url(#ah7)"/>
      <g data-d="p-task"><rect class="sv-pill" x="1170" y="528" width="150" height="24" rx="12"/><text class="sv-pt" x="1182" y="544">&#9318; EXECUTE</text></g>

      <path class="sv-edge" d="M1475 502 V 342 H 1322" marker-end="url(#ah7)"/>
      <g data-d="p-done"><rect class="sv-pill" x="1487" y="424" width="190" height="24" rx="12"/><text class="sv-pt" x="1499" y="440">&#9319; CLOSE &#8212; &#8804;30s</text></g>
      <text class="sv-s" x="1487" y="464">dcim-tasks&#8217; outbound queue</text>
      <text class="sv-s" x="1487" y="478">writes Done to the ticket</text>

      <path class="sv-edge g" d="M1300 312 V 192" marker-end="url(#ahg7)"/>
      <text class="sv-s" x="1190" y="248">the run sits on this field</text>
      <path class="sv-edge g" d="M1160 136 H 1324" marker-end="url(#ahg7)"/>
      <g data-d="u-flows"><rect class="sv-pill" x="1162" y="96" width="160" height="24" rx="12"/><text class="sv-pt" x="1174" y="112">&#9320; WAKE</text></g>
      <text class="sv-s" x="1168" y="158">Done resumes the run</text>

      <!-- legend -->
      <text class="sv-s" x="40" y="690">grammar: sharp boxes = components &amp; actors (type-tagged top-right) &#183; green pills = the nine actions, numbered in time order &#183; chips = signals</text>
      <text class="sv-s" x="40" y="708">boxes and pills both drill down &#183; lanes = who runs the machinery &#183; green strokes = Google-side motion, grey = FS-side</text>
    </svg></div>'''

s = s[:i] + NEW_SVG + s[j:]
# update the intro slede + scrollhint to describe the grammar
s = s.replace(
  'The unit of the seam isn’t a ticket — it’s a <b>round trip</b>: broken machine out of Google’s pool, fixed machine back, no human on Google’s side. Every box below is shipped code or measured corpus behavior; the two stages history never built — classify/acknowledge and assignment — are drawn as they actually are (researched live, Jun 11). Click any box for mechanism and receipts.',
  'The unit of the seam isn’t a ticket — it’s a <b>round trip</b>: broken machine out of Google’s pool, fixed machine back, no human on Google’s side. The diagram separates <b>kinds</b>: sharp boxes are the components and actors (type-tagged), the numbered green pills are the nine actions in time order, chips are signals. Every box and pill below is shipped code or measured corpus behavior — including the two actions history never built, classify/ack (③… nothing fires) and assignment (self-claim), both researched live Jun 11. Click anything for mechanism and receipts.')
s = s.replace(
  '<p class="scrollhint">↔ scroll the diagram sideways for the full loop · stages ⑤ and ⑥ are the two the floor never built — both researched live Jun 11 (their boxes carry the receipts)</p>',
  '<p class="scrollhint">↔ scroll the diagram sideways for the full loop · actions ⑤ and ⑥ are the two the floor never built — their pills carry the receipts</p>')
open(f"{BASE}/src/10-seam.html","w").write(s)
ok.append("svg-v2")

print("OK:", ok)
r = subprocess.run(["make","build"], capture_output=True, text=True, cwd=BASE); print(r.stdout.strip().splitlines()[-1])
r = subprocess.run(["make","check"], capture_output=True, text=True, cwd=BASE); print(r.stdout.strip() or r.stderr.strip())
art = open(f"{BASE}/maintenance-api.html").read()
m = re.search(r'<script>([\s\S]*)</script>', art)
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
    f.write("try { new Function(" + json.dumps(m.group(1)) + "); console.log('JS parses OK') } catch(e) { console.log('JS ERROR:', e.message) }")
    p = f.name
print(subprocess.run(['node', p], capture_output=True, text=True).stdout.strip())
dr = art[art.find('const DRILL'):art.find('const EVENTS')]
keys = set(re.findall(r'"([a-z0-9-]+)":\s*\{\s*k:', dr))
hooks = set(re.findall(r'data-d="([a-z0-9-]+)"', art))
print("data-d without DRILL key:", sorted(hooks - keys))
ids = set(re.findall(r'id="([^"]+)"', art)) | set(re.findall(r"id='([^']+)'", art))
ev = art[art.find('const EVENTS'):art.find('];', art.find('const EVENTS'))]
ev_ids = set(re.findall(r'id:\s*"([^"]+)"', ev))
dead = [h for h in set(re.findall(r'href=[\'"]#([^\'"]+)[\'"]', art)) if h not in ids and not (h.startswith('ev-') and h[3:] in ev_ids)]
print("dead anchors:", sorted(dead))
