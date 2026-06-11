#!/usr/bin/env python3
import re, json, subprocess, tempfile
BASE = "/Users/andrew/code/personal/toolbox/work/maintenance-api-viz"
DC = "https://github.com/fluidstackio/dcim/blob/b6eea015af01044ce5c41aaa8e29bb655557a2f7"
DOC = "https://docs.google.com/document/d/1vgCxJdpeyUfDgjupARKKM8MLCV2Pk44hWt1jcjHNGew/edit"
ok, miss = [], []
def rep(path, old, new, tag):
    p = f"{BASE}/{path}"
    s = open(p).read()
    c = s.count(old)
    if c != 1: miss.append(f"{tag} ({c})"); return
    open(p, "w").write(s.replace(old, new)); ok.append(tag)

# ===== B1: 01·LOOP type upgrades =====
rep("src/10-seam.html",
    '<text class="sv-tag" x="718" y="100" text-anchor="end">SERVICE ACCOUNT</text>\n        <text class="sv-t" x="484" y="120">the filer</text>\n        <text class="sv-m" x="484" y="142">Ext-Bloom-Atlas-Workflows</text>\n        <text class="sv-s" x="484" y="160">writes 5 templated custom fields</text>\n        <text class="sv-s" x="484" y="176">93% of all 15,622 tickets</text>',
    '<text class="sv-tag" x="718" y="100" text-anchor="end">JIRA SERVICE ACCOUNT</text>\n        <text class="sv-t" x="484" y="120">the filer</text>\n        <text class="sv-m" x="484" y="142">Ext-Bloom-Atlas-Workflows</text>\n        <text class="sv-s" x="484" y="160">the identity their workflows file as —</text>\n        <text class="sv-s" x="484" y="176">5 templated fields · 93% of 15,622</text>',
    "loop-filer")
rep("src/10-seam.html",
    '<text class="sv-tag" x="308" y="518" text-anchor="end">GO SERVICE</text>',
    '<text class="sv-tag" x="308" y="518" text-anchor="end">SERVICE · REST + JSM SYNC</text>',
    "loop-dcimtasks-tag")
rep("src/10-seam.html", 'viewBox="0 0 1700 740"', 'viewBox="0 0 1700 830"', "loop-viewbox")
rep("src/10-seam.html", '<rect class="sv-zone" x="18" y="470" width="1664" height="180"/>',
    '<rect class="sv-zone" x="18" y="470" width="1664" height="270"/>', "loop-floor-zone")
rep("src/10-seam.html",
    '<text class="sv-s" x="40" y="690">grammar:',
    '''<g data-d="p-task">
        <rect class="sv-box" x="470" y="656" width="300" height="72" rx="3"/>
        <text class="sv-tag" x="758" y="672" text-anchor="end">TEMPORAL WORKFLOW &#183; FS</text>
        <text class="sv-t" x="484" y="692">RepairTaskWorkflow</text>
        <text class="sv-s" x="484" y="710">started per-minute by the repair-watcher cron;</text>
        <text class="sv-s" x="484" y="724">pins the SOP, walks auto-steps</text>
      </g>
      <path class="sv-edge" d="M180 606 V 692 H 464" marker-end="url(#ah7)"/>
      <text class="sv-s" x="196" y="660">lists open repair tasks</text>
      <path class="sv-edge" d="M770 692 H 1475 V 612" marker-end="url(#ah7)"/>
      <text class="sv-s" x="800" y="684">FetchSOPByProblemCode &#8594; RecordSOPOnTask</text>
      <text class="sv-s" x="40" y="780">grammar:''',
    "loop-rtw-box")
rep("src/10-seam.html", '<text class="sv-s" x="40" y="708">boxes and pills', '<text class="sv-s" x="40" y="798">boxes and pills', "loop-legend2")

# s-ticket drill: the file-mechanism hedge (TYPING-M5)
rep("src/70-data-drills.js",
    'priority Medium = the Jira default</text>',
    'priority Medium = the Jira default</text>', "noop-guard")  # guard: ensure file untouched pattern exists? (placeholder no-op)
ok.remove("noop-guard")
s = open(f"{BASE}/src/70-data-drills.js").read()
i = s.find('"s-ticket": {')
j = s.find('</p>', s.find('body: "', i))
if i > 0 and j > i:
    ins = " What calls Jira's create API on Google's side is Google-internal — unverified, like the status watch; FS's own outbound filer, for contrast, goes through the JSM service-desk API."
    s = s[:j] + ins + s[j:]
    open(f"{BASE}/src/70-data-drills.js","w").write(s)
    ok.append("sticket-mechanism-hedge")
else:
    miss.append("sticket-mechanism-hedge")

# ===== B2: machine-state strip in §03 =====
STRIP = '''

  <p class="slede" style="margin-top:18px"><b>The machine&#8217;s states &#8212; the actual contract content.</b> Per Partner-Ops v0.4 (read Jun 11), the repair loop&#8217;s binding signals ride this state machine, not the ticket: PARTNER_OWNED is set automatically when the ticket files, and the done-signal is FS&#8217;s PATCH to PENDING_HANDOVER. Drawn from the doc&#8217;s state table + the CUJ3 flow:</p>
  <div class="diawrap"><svg class="wide" viewBox="0 0 1700 268" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Machine asset states per Partner-Ops v0.4: Google Serving, Drained, Partner Owned, Pending Handover, Google Owned, and back to serving.">
      <defs><marker id="ah8" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#5a5a5a"/></marker></defs>
      <rect class="sv-box" x="40" y="40" width="270" height="70" rx="3"/>
      <text class="sv-t" x="54" y="66">GOOGLE_SERVING</text>
      <text class="sv-s" x="54" y="86">healthy default &#183; available to Borg</text>
      <rect class="sv-box" x="372" y="40" width="270" height="70" rx="3"/>
      <text class="sv-t" x="386" y="66">DRAINED</text>
      <text class="sv-s" x="386" y="86">Google&#8217;s, not serving &#183; nearby work ok</text>
      <rect class="sv-box" x="704" y="40" width="270" height="70" rx="3"/>
      <text class="sv-t" x="718" y="66">PARTNER_OWNED</text>
      <text class="sv-s" x="718" y="86">FS holds BMC + node &#183; repair default</text>
      <rect class="sv-box" x="1036" y="40" width="270" height="70" rx="3"/>
      <text class="sv-t" x="1050" y="66">PENDING_HANDOVER</text>
      <text class="sv-s" x="1050" y="86">FS&#8217;s signal: repair complete</text>
      <rect class="sv-box" x="1368" y="40" width="290" height="70" rx="3"/>
      <text class="sv-t" x="1382" y="66">GOOGLE_OWNED</text>
      <text class="sv-s" x="1382" y="86">re-attested &#8594; rejoins Borg, serving</text>
      <path class="sv-edge" d="M310 75 H 366" marker-end="url(#ah8)"/><text class="sv-s" x="318" y="64">&#10122;</text>
      <path class="sv-edge" d="M642 75 H 698" marker-end="url(#ah8)"/><text class="sv-s" x="650" y="64">&#10123;</text>
      <path class="sv-edge" d="M974 75 H 1030" marker-end="url(#ah8)"/><text class="sv-s" x="982" y="64">&#10124;</text>
      <path class="sv-edge" d="M1306 75 H 1362" marker-end="url(#ah8)"/><text class="sv-s" x="1314" y="64">&#10125;</text>
      <text class="sv-s" x="40" y="148">&#10122; Google drains workloads off the machine &#160;&#160; &#10123; creds rotate to pre-shared &#8212; and the state flips automatically when the repair ticket files</text>
      <text class="sv-s" x="40" y="170">&#10124; FS repairs &#183; optionally PATCHes replaced FRU serials (UpdateHardwareAsset) &#183; then PATCHes state=PENDING_HANDOVER &#8212; <tspan fill="#A8E05F">the done-signal lives here, not on the ticket</tspan></text>
      <text class="sv-s" x="40" y="192">&#10125; Google takes the BMC back, reinstalls BorneoOS, re-attests &#8212; failure routes back through CUJ3</text>
      <rect class="sv-chip" x="40" y="214" width="660" height="26" rx="4"/>
      <text class="sv-chipt" x="52" y="231">GATE &#183; before hands touch the machine: GetHardwareAsset must show PARTNER_OWNED (CUJ3 step 4)</text>
      <text class="sv-s" x="40" y="262">the v0.4 table names the partner-visible trio (Google Serving &#183; Drained &#183; Partner owned); GOOGLE_OWNED and PENDING_HANDOVER appear in its flows</text>
    </svg></div>
'''
rep("src/30-surfaces.html",
    '</div>\n\n  <p class="diacap" style="margin-top:14px"><b>Two return channels, different payloads:</b>',
    '</div>\n' + STRIP + '\n  <p class="diacap" style="margin-top:14px"><b>Two return channels, different payloads:</b>',
    "machine-states-strip")

# ===== B3: task/Jira state machine after the 02·B pipeline =====
TASKSM = '''

  <p class="slede" style="margin-top:18px"><b>The task&#8217;s states, drawn</b> &#8212; dcim-tasks&#8217; enum with its verified writers, each box carrying its Jira projection (the prod transition names). The console enforces no transition matrix &#8212; any enum value goes; the workflow and reconciler are the disciplined writers:</p>
  <div class="diawrap"><svg class="wide" viewBox="0 0 1700 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="dcim-tasks task state machine: open to in_progress to complete or rejected, with blocked and the configured-but-unused queued state.">
      <defs><marker id="ah9" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#5a5a5a"/></marker></defs>
      <path class="sv-edge" d="M540 56 V 24 H 1520 V 50" marker-end="url(#ah9)"/>
      <text class="sv-s" x="700" y="18">console human &#183; or the webhook/drift mirror of a Jira-side Reject</text>
      <rect class="sv-box" x="40" y="56" width="250" height="96" rx="3"/>
      <text class="sv-t" x="54" y="82">open</text>
      <text class="sv-s" x="54" y="102">initial &#8212; inbound only;</text>
      <text class="sv-s" x="54" y="118">Jira Open is never a dcim target</text>
      <rect class="sv-box" x="420" y="56" width="250" height="96" rx="3"/>
      <text class="sv-t" x="434" y="82">in_progress</text>
      <text class="sv-m" x="434" y="104">Jira: &#8220;Start Task&#8221;</text>
      <text class="sv-s" x="434" y="122">&#8594; In Progress</text>
      <rect class="sv-box" x="1100" y="56" width="250" height="96" rx="3"/>
      <text class="sv-t" x="1114" y="82">complete</text>
      <text class="sv-m" x="1114" y="104">Jira: &#8220;Complete Task&#8221;</text>
      <text class="sv-s" x="1114" y="122">&#8594; Done &#8212; the wake</text>
      <rect class="sv-box" x="1430" y="56" width="230" height="96" rx="3"/>
      <text class="sv-t" x="1444" y="82">rejected</text>
      <text class="sv-m" x="1444" y="104">Jira: &#8220;Reject&#8221;</text>
      <text class="sv-s" x="1444" y="122">&#8594; Rejected &#8212; also a wake</text>
      <rect class="sv-box" x="420" y="240" width="250" height="86" rx="3"/>
      <text class="sv-t" x="434" y="266">blocked</text>
      <text class="sv-m" x="434" y="288">Jira: &#8220;Blocked&#8221; + reason</text>
      <text class="sv-s" x="434" y="306">reason required in dcim too</text>
      <rect class="sv-box dash" x="40" y="240" width="250" height="86" rx="3"/>
      <text class="sv-t" x="54" y="266">queued</text>
      <text class="sv-s" x="54" y="288">in prod config (&#8220;Add to Queue&#8221;)</text>
      <text class="sv-s" x="54" y="306">&#8212; zero occurrences in the corpus</text>
      <path class="sv-edge" d="M290 104 H 414" marker-end="url(#ah9)"/>
      <text class="sv-s" x="296" y="94">RepairTaskWorkflow (auto)</text>
      <text class="sv-s" x="296" y="130">&#183; console human</text>
      <path class="sv-edge" d="M670 104 H 1094" marker-end="url(#ah9)"/>
      <text class="sv-s" x="700" y="94">workflow: all steps passed &#183; console human</text>
      <text class="sv-s" x="700" y="130">&#183; reconciler auto-close (misclassified type / deleted in Jira)</text>
      <path class="sv-edge" d="M510 152 V 234" marker-end="url(#ah9)"/>
      <text class="sv-s" x="522" y="200">workflow on step failure &#183; console</text>
      <path class="sv-edge" d="M600 240 V 158" marker-end="url(#ah9)"/>
      <text class="sv-s" x="612" y="222">console / reconciler</text>
      <text class="sv-s" x="40" y="372">unmapped Jira drift &#8212; Closed / Resolved / To Do, 55 tickets &#8212; has no dcim mapping: the mirror <tspan fill="#F2C462">silently skips</tspan> those updates</text>
      <text class="sv-s" x="40" y="390">dashed = configured but unobserved &#183; every transition is logged with reason + performed_by</text>
    </svg></div>
  <p class="diacap">Writers verified at the pinned sha: the schema&#8217;s CHECK <a href="DCURL/services/dcim-tasks/internal/db/schema.sql#L12-L15" target="_blank" rel="noreferrer">&#8599;</a> &#183; the console&#8217;s enum-only validation <a href="DCURL/services/dcim-tasks/internal/server/tasks.go#L280-L291" target="_blank" rel="noreferrer">&#8599;</a> &#183; the prod status&#8594;transition map <a href="DCURL/argocd/datacenters-prod/dcim-tasks/values.yaml#L64-L80" target="_blank" rel="noreferrer">&#8599;</a> &#183; the three-tier inbound lookup <a href="DCURL/services/dcim-tasks/internal/config/jira.go#L250-L267" target="_blank" rel="noreferrer">&#8599;</a></p>
'''
TASKSM = TASKSM.replace("DCURL", DC)
rep("src/20-routing.html",
    'sweeps re-fire whole batch',
    'sweeps re-fire whole batch', "anchor-probe")
ok.remove("anchor-probe")
r = open(f"{BASE}/src/20-routing.html").read()
k = r.find("It's a loop, not a line.")
kend = r.find('</p>', k) + 4
if k > 0:
    r = r[:kend] + TASKSM + r[kend:]
    open(f"{BASE}/src/20-routing.html","w").write(r)
    ok.append("task-state-machine")
else:
    miss.append("task-state-machine")

print("OK:", len(ok), ok)
print("MISS:", miss)
if miss: raise SystemExit("ABORT")
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
