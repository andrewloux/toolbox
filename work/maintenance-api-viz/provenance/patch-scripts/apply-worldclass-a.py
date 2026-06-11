#!/usr/bin/env python3
import subprocess
BASE = "/Users/andrew/code/personal/toolbox/work/maintenance-api-viz"
ok, miss = [], []
def rep(path, old, new, tag):
    p = f"{BASE}/{path}"
    s = open(p).read()
    c = s.count(old)
    if c != 1: miss.append(f"{tag} ({c})"); return
    open(p, "w").write(s.replace(old, new)); ok.append(tag)

DC = "https://github.com/fluidstackio/dcim/blob/b6eea015af01044ce5c41aaa8e29bb655557a2f7"
IM = "https://github.com/fluidstackio/infrastructure-management/blob/479bc10574a80f3fd59c492bbd6057c4d2469ef8"
D = "src/70-data-drills.js"

# ===== p-done: name the close chain + 3 links (LINKS-H1 + NAMES-M4) =====
rep(D, 'Rejected%20ORDER%20BY%20created%20DESC" }] },',
    'Rejected%20ORDER%20BY%20created%20DESC" },\n'
    f'      {{ label: "handleTransition — the outbound queue consumer (sync_worker.go:476)", url: "{DC}/services/dcim-tasks/internal/jsm/sync_worker.go#L476-L580" }},\n'
    f'      {{ label: "executeTransition — POST /rest/api/3/issue/{{key}}/transitions (mutations.go:63)", url: "{DC}/pkg/jsm/mutations.go#L63-L92" }},\n'
    f'      {{ label: "the prod status→transition map (complete → \'Complete Task\' → Done)", url: "{DC}/argocd/datacenters-prod/dcim-tasks/values.yaml#L64-L80" }}] }},',
    "pdone-links")
rep(D, "is what wakes Google.</p><p>The console's",
    "is what wakes Google.</p><p>The write itself is named code: <span class='m'>handleTransition</span> drains the queue item and calls <span class='m'>TransitionIssueByTargetStatus</span>, which POSTs Jira's <span class='m'>/rest/api/3/issue/{key}/transitions</span> — walking intermediates when needed (Blocked unblocks via In Progress; Open advances through In Progress before Done).</p><p>The console's",
    "pdone-chain") if open(f"{BASE}/{D}").read().count("is what wakes Google.</p><p>The console's")==1 else miss.append("pdone-chain-anchor")

# ===== l-classify: the no-op test + handler switch links (LINKS-H2) =====
rep(D, 'p1775747152644979" }] },',
    'p1775747152644979" },\n'
    f'      {{ label: "the no-op, certified — TestHandleJiraIssueUpdated_NoRelevantChanges_Noop (priority→High, DB never touched)", url: "{DC}/services/dcim-tasks/internal/server/webhooks_jira_test.go#L378-L389" }},\n'
    f'      {{ label: "the handler\'s changelog switch — status/assignee/summary handled, the rest ignored", url: "{DC}/services/dcim-tasks/internal/server/webhooks_jira.go#L325-L347" }}] }},',
    "lclassify-links")

# ===== l-assign: 3 callers + combobox upgrade + {task_id} (LINKS-M1 + NAMES-L2) =====
rep(D, 'statusCategory%20!%3D%20Done%20ORDER%20BY%20created%20DESC" }] },',
    'statusCategory%20!%3D%20Done%20ORDER%20BY%20created%20DESC" },\n'
    f'      {{ label: "caller 1 — the REST handler, Server.AssignTask (tasks.go:400)", url: "{DC}/services/dcim-tasks/internal/server/tasks.go#L400-L484" }},\n'
    f'      {{ label: "caller 2 — the webhook\'s assignee-changelog write (webhooks_jira.go:358)", url: "{DC}/services/dcim-tasks/internal/server/webhooks_jira.go#L358-L371" }},\n'
    f'      {{ label: "caller 3 — reconcileAssignee, the 10-m drift (reconcile.go:311)", url: "{DC}/services/dcim-tasks/internal/jsm/reconcile.go#L311-L340" }},\n'
    f'      {{ label: "the endpoint, defined — PUT /v1alpha1/tasks/{{task_id}}/assign (openapi.yaml:264)", url: "{DC}/services/dcim-tasks/openapi.yaml#L264-L281" }}] }},',
    "lassign-links")
rep(D, 'console PUT /v1alpha1/tasks/{id}/assign', 'console PUT /v1alpha1/tasks/{task_id}/assign', "lassign-taskid")
rep(D, '{ label: "the console\'s Assigned To combobox (RepairsLayout.tsx)", url: "IM_SHORT/services/dcim-console/src/pages/repairs/RepairsLayout.tsx" }'.replace("IM_SHORT","https://github.com/fluidstackio/infrastructure-management/blob/479bc10"),
    f'{{ label: "the console\'s Assigned To combobox (RepairsLayout.tsx:1340)", url: "{IM}/services/dcim-console/src/pages/repairs/RepairsLayout.tsx#L1340-L1366" }}',
    "lassign-combobox")

# ===== s-ticket: prod intake map link + filer-mechanism hedge (LINKS-M2 + TYPING-M5) =====
rep(D, 'Physical%20Repair%20Task%22%20ORDER%20BY%20created%20DESC" }] },',
    'Physical%20Repair%20Task%22%20ORDER%20BY%20created%20DESC" },\n'
    f'      {{ label: "the prod intake map — serviceDesk 665 · requestTypeID 1669/1415 · the templated request fields", url: "{DC}/argocd/datacenters-prod/dcim-tasks/values.yaml#L35-L63" }}] }},',
    "sticket-link")

# ===== sop-pin: name the pinning workflow + link + non-fatal caveat (LINKS-M3 + NAMES-L1) =====
rep(D, '{ label: "schema.sql", url: "https://github.com/fluidstackio/dcim/blob/main/services/dcim-sops/internal/db/schema.sql" }] },',
    '{ label: "schema.sql", url: "https://github.com/fluidstackio/dcim/blob/main/services/dcim-sops/internal/db/schema.sql" },\n'
    f'      {{ label: "the pin, in shipped code — FetchSOPByProblemCode → RecordSOPOnTask (RepairTaskWorkflow)", url: "{DC}/services/temporal-worker/pkg/repair/workflow.go#L98-L118" }}] }},',
    "soppin-link")

# ===== p-route: checklist-task code link (LINKS-M4) =====
rep(D, '{ label: "field test thread", url: "https://fluidstack.enterprise.slack.com/archives/C0B843AL0N8/p1780495788053769" }] },',
    '{ label: "field test thread", url: "https://fluidstack.enterprise.slack.com/archives/C0B843AL0N8/p1780495788053769" },\n'
    f'      {{ label: "the handoff checklist task itself — google-qa-handoff, Milestone: Google Handoff (rackinstall/tasks.go:67)", url: "{DC}/services/dcim-api/internal/rackinstall/tasks.go#L67" }}] }},',
    "proute-link")

# ===== p-queue: deep-link receipt (LINKS-M5) =====
rep(D, '{ label: "field test thread (#ext-cb3-repair-test)", url: "https://fluidstack.enterprise.slack.com/archives/C0B843AL0N8/p1780495788053769" }] },',
    '{ label: "field test thread (#ext-cb3-repair-test)", url: "https://fluidstack.enterprise.slack.com/archives/C0B843AL0N8/p1780495788053769" },\n'
    f'      {{ label: "the deep-link, in code — AddRemoteLink(\'View in DCIM\') on issue create (sync_worker.go:459)", url: "{DC}/services/dcim-tasks/internal/jsm/sync_worker.go#L459-L467" }}] }},',
    "pqueue-link")

# ===== u-diag: proto link (LINKS-L2) =====
rep(D, '{ label: "TPU-CC diagnostics UI (teleport-gated)", url: "https://tpucc-ui-teleport-google-system-fish-buf101.fluidstack.teleport.sh" }] },',
    '{ label: "TPU-CC diagnostics UI (teleport-gated)", url: "https://tpucc-ui-teleport-google-system-fish-buf101.fluidstack.teleport.sh" },\n'
    f'      {{ label: "GetProblem · PerformHealthTest — the detection-side RPCs (vendored proto, pinned)", url: "{DC}/pkg/google/tpu_command_center/proto/tpu_command_center.proto#L29-L81" }}] }},',
    "udiag-link")

# ===== p-sync: activities→workflows fix + function names + pinned reconcile links (TYPING-M2 + NAMES-M3 + LINKS-L1) =====
rep(D, "dcim-worker's “Jira workflows” are Temporal automation activities, a different thing.",
    "dcim-worker's “Jira workflows” are Temporal <i>workflows</i> — <span class='m'>CreateJiraTicketWorkflow</span> and <span class='m'>CreateJiraTicketAndWaitWorkflow</span>, FS's own file-and-wait pattern, a small in-house mirror of Google's file-and-park — a different thing from this in-process sync.",
    "psync-jirawf")
rep(D, 'reconcile runs on independent discovery and drift tickers',
    'reconcile runs on independent discovery and drift tickers — <span class=\'m\'>reconcileDiscovery</span> every 5m, <span class=\'m\'>reconcileDrift</span> every 10m, the outbound drain every 30s (<span class=\'m\'>DrainOnce</span>/<span class=\'m\'>ReconcileOnce</span> are the admin lever\'s synchronous entries)',
    "psync-names")
rep(D, "<a href='https://github.com/fluidstackio/dcim/blob/main/services/dcim-tasks/internal/jsm/reconcile.go' target='_blank' rel='noreferrer'>reconcile.go</a> literally fetches the “problem codes field”",
    f"<a href='{DC}/services/dcim-tasks/internal/jsm/reconcile.go#L505-L517' target='_blank' rel='noreferrer'>reconcile.go</a> literally fetches the “problem codes field”",
    "psync-pin-reconcile")

# ===== p-task: resolve the trigger-wiring unknown (NAMES-H1 + TYPING-M3) =====
rep(D, "The natural starter when a mirrored task lands is the per-minute repair-watcher cron in dcim-worker's roster (the Jul 7 plan event lists it); the exact trigger wiring wasn't read.",
    f"The starter is read: dcim-worker schedules <span class='m'>RepairWatcherWorkflow</span> at startup as a Temporal cron — workflow ID <span class='m'>repair-watcher</span>, <span class='m'>CronSchedule */1 * * * *</span>, gated by <span class='m'>cfg.DCIM.Enabled</span> (<a href='{DC}/services/dcim-worker/cmd/dcim-worker/main.go#L209-L220' target='_blank' rel='noreferrer'>main.go:209 ↗</a>). Each minute it lists open repair/hospital tasks and starts a <span class='m'>RepairTaskWorkflow</span> per task keyed on its <i>first</i> problem code — code-less tasks are skipped outright, no workflow ever starts for them (<a href='{DC}/services/temporal-worker/pkg/repair/workflow.go#L460-L499' target='_blank' rel='noreferrer'>workflow.go:460 ↗</a>).",
    "ptask-trigger")

# ===== u-fs: retire the stale site-worker fact (TYPING-H1) =====
rep(D, "site-worker is FS's activity worker plugged into Google's Temporal. It executes the FS-side activities Google's workflows call: machine netboot/reset, NetBox reads, ping checks",
    "site-worker is a Temporal Cloud worker — <span class='m'>worker.New</span> appears once, against the cloud client (main.go:87) — so its activities (machine netboot/reset, NetBox reads, ping checks) register only there; Google's workflows cannot call them. Its dial into google-system is client-only: the caller-less RunSiteLocalWorkflow bridge",
    "ufs-stale-fact")

# ===== u-fs: contracts fact gains dcim-tasks' own contract (NAMES-M5) =====
rep(D, "REST: <a href='https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/openapi.yaml' target='_blank' rel='noreferrer'>services/dcim-api/openapi.yaml</a> (the api.dcim.fluidstack.io contract; console client generated from it) · protos: buf-managed — pkg/google + services/*/proto",
    f"REST: <a href='https://github.com/fluidstackio/dcim/blob/main/services/dcim-api/openapi.yaml' target='_blank' rel='noreferrer'>services/dcim-api/openapi.yaml</a> (the api.dcim.fluidstack.io contract; console client generated from it) · <a href='{DC}/services/dcim-tasks/openapi.yaml' target='_blank' rel='noreferrer'>services/dcim-tasks/openapi.yaml</a> (“DCIM Tasks API — repair ticket management with two-way JSM sync”, v1alpha1) · protos: buf-managed — pkg/google + services/*/proto",
    "ufs-contracts")

# ===== a-dcim: wrong-lines link fix + fulfill-hop grounding (STATES-L1 + NAMES-M5b) =====
rep(D, "https://github.com/fluidstackio/dcim/blob/main/services/dcim-tasks/internal/config/jira.go#L211-L247",
    f"{DC}/services/dcim-tasks/internal/config/jira.go#L250-L267",
    "adcim-3tier-fix")
rep(D, "How <span class='m'>POST /repairs</span> becomes a dcim-tasks row — the internal fulfill hop — is build-phase design, not yet specified anywhere.",
    f"How <span class='m'>POST /repairs</span> becomes a dcim-tasks row — the internal fulfill hop — is build-phase design, not yet specified anywhere. The internal surface it would map onto already exists: dcim-tasks' own v1alpha1 — <span class='m'>CreateTask (POST /racks/{{rack_id}}/tasks)</span> · UpdateTask · AssignTask · CompleteStep (<a href='{DC}/services/dcim-tasks/openapi.yaml#L133-L160' target='_blank' rel='noreferrer'>the contract ↗</a>) — so “not yet specified” means the mapping, not the absence of a surface.",
    "adcim-fulfill")

# ===== 01·MAP: engine census resolved (NAMES-H2) =====
rep("src/10-seam.html",
    'its production home wasn’t read either; the example config defaults to <span class="m">localhost:7233</span> — if that engine also rides Temporal Cloud in prod, the census collapses to two.</p>',
    f'its production home is now read: both prod dcim-worker overlays dial Temporal Cloud — <span class="m">ap-northeast-1.aws.api.temporal.io:7233</span>, namespace <span class="m">infrastructure.gdjny</span>, task queues <span class="m">dcim-worker</span> / <span class="m">dcim-worker-feldspar</span> (<a href="{DC}/argocd/datacenters-prod/dcim-worker/values.yaml#L4-L8" target="_blank" rel="noreferrer">values ↗</a>, <a href="{DC}/argocd/datacenters-prod/dcim-worker-feldspar/values.yaml#L4-L8" target="_blank" rel="noreferrer">feldspar ↗</a>). So the census resolves: <b>two Temporal deployments</b> — Google’s google-system frontend and Temporal Cloud — host the three logical engines.</p>',
    "tmap-census")
rep("src/10-seam.html",
    'Three engines appear in the configs read.',
    'Three engines appear in the configs read — hosted, it turns out, on two Temporal deployments (resolved below, Jun 11).',
    "tmap-headline")

# ===== 02·B stage-3 subline + 02·C SOP stage-2 schema names (TYPING-M4b + STATES-L2) =====
rep("src/20-routing.html",
    '<text class="sv-s" x="596" y="123">SOP version pinned at workflow start</text>',
    '<text class="sv-s" x="596" y="123">SOP pinned at RepairTaskWorkflow start</text>',
    "02b-stage3")
rep("src/20-routing.html",
    '<text class="sv-s" x="213" y="94">draft → review → approved</text>',
    '<text class="sv-s" x="213" y="94">in_progress → under_review → approved</text>',
    "02c-sop-states")

print("OK:", len(ok), ok)
print("MISS:", miss)
if miss: raise SystemExit("ABORT (file writes are per-op; review misses)")
r = subprocess.run(["make","build"], capture_output=True, text=True, cwd=BASE); print(r.stdout.strip().splitlines()[-1])
r = subprocess.run(["make","check"], capture_output=True, text=True, cwd=BASE); print(r.stdout.strip() or r.stderr.strip())
