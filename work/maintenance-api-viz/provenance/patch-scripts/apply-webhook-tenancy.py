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

DC = "https://github.com/fluidstackio/dcim/blob/b6eea015af01044ce5c41aaa8e29bb655557a2f7"
SY = "https://github.com/fluidstackio/systems/blob/34e92787301ccdd6da52382a69bed18e3b1f2b07"
RFC = "https://fluidstack.atlassian.net/wiki/spaces/Infra/pages/77660161/RFC+Fluidstack+Infrastructure+Services+Hub+FISH"

# ===== 1. p-sync body: the webhook story (4 paragraphs after the polls paragraph) =====
P1 = ("<p><b>And there is a webhook — built, dark.</b> The same service mounts <span class='m'>POST /webhooks/jira/{site}</span> outside JWT auth "
      f"(<a href='{DC}/services/dcim-tasks/cmd/dcim-tasks/main.go#L111-L115' target='_blank' rel='noreferrer'>main.go:111-115 ↗</a> — the comment delegates protection to the network layer): "
      "an HMAC-SHA256-signed ingest (<span class='m'>X-Hub-Signature</span>, per-site secret <span class='m'>JIRA_WEBHOOK_SECRET_&lt;SITE&gt;</span>) that mirrors four Jira event types straight into Postgres — issue created/updated, comment created/deleted "
      f"(<a href='{DC}/services/dcim-tasks/internal/server/webhooks_jira.go#L130-L224' target='_blank' rel='noreferrer'>the handler ↗</a>). "
      "A structural loop-breaker keeps inbound from ever re-triggering outbound sync: the handler's DB interface simply has no enqueue method "
      f"(<a href='{DC}/services/dcim-tasks/internal/server/webhooks_jira.go#L25-L37' target='_blank' rel='noreferrer'>webhookQuerier ↗</a>).</p>")
P2 = ("<p>Dark because nothing routes to it. The chart's only ingress object exposes exactly the <span class='m'>/webhooks/jira</span> prefix "
      f"(<a href='{DC}/services/dcim-tasks/helm/dcim-tasks/templates/httproute.yaml#L24-L29' target='_blank' rel='noreferrer'>template ↗</a>) and is switched off in both prod overlays from day one "
      f"(<a href='{DC}/argocd/datacenters-prod/dcim-tasks/values.yaml#L91-L92' target='_blank' rel='noreferrer'>httpRoute.enabled: false ↗</a>, "
      "<a href='https://github.com/fluidstackio/dcim/pull/2024' target='_blank' rel='noreferrer'>#2024</a>); the service is ClusterIP-only, and the public host (dcim-api) proxies only the JWT'd /v1alpha1 task paths — no /webhooks. "
      "Atlassian Cloud needs a public URL, so not one delivery can arrive; the deploy PR's manual prerequisite — “Webhook secret configured in JSM (ATLASBUF project webhook settings)” — sits unchecked "
      "(<a href='https://github.com/fluidstackio/argocd/pull/5090' target='_blank' rel='noreferrer'>argocd#5090</a>), though the secret itself was minted "
      "(<a href='https://github.com/fluidstackio/dcim/pull/2042' target='_blank' rel='noreferrer'>#2042</a>, AWS SM <span class='m'>dcim-tasks/jira-credentials</span>). "
      "Rob's Apr 29 architecture brief to security names the reconciler, not webhooks, as the inbound path <a href='https://fluidstack.enterprise.slack.com/archives/C0AAY9E2NF9/p1777496342367569?thread_ts=1777489512.893739&cid=C0AAY9E2NF9' target='_blank' rel='noreferrer'>↗</a> — whether dark-by-design or never-finished is written down nowhere read.</p>")
P3 = ("<p>The unauthenticated admin pair rides the same posture: <span class='m'>GET /admin/jsm-queue-stats</span> (outbound-queue snapshot — pending / in-flight / exhausted / oldest-age "
      f"<a href='{DC}/services/dcim-tasks/internal/server/admin_jsm.go#L37-L73' target='_blank' rel='noreferrer'>↗</a>) and <span class='m'>POST /admin/jsm-reconcile</span> "
      f"(synchronous drain-then-reconcile, 2-minute timeout — the manual “sync now” lever <a href='{DC}/services/dcim-tasks/internal/server/admin_jsm.go#L19-L35' target='_blank' rel='noreferrer'>↗</a>). "
      "The route template never exposes /admin even when enabled, so both are in-cluster/port-forward only; the NetworkPolicy the code comment asks for exists in no repo read — the only “NetworkPolicy” match in dcim is the comment itself — and a reviewer's question about the unauthenticated endpoint on "
      "<a href='https://github.com/fluidstackio/dcim/pull/1868' target='_blank' rel='noreferrer'>#1868</a> has no recorded reply.</p>")
P4 = ("<p>Cadence, for the record: 30s outbound drain, 5m discovery, 10m drift "
      f"(<a href='{DC}/services/dcim-tasks/internal/jsm/sync_worker.go#L28-L35' target='_blank' rel='noreferrer'>sync_worker.go ↗</a>) — and before "
      "<a href='https://github.com/fluidstackio/dcim/pull/2045' target='_blank' rel='noreferrer'>#2045</a> (Apr 13) prod's <span class='m'>jira.sites</span> was literally <span class='m'>{}</span>: nothing synced at all. "
      "For <a href='#ev-d-push'>d-push</a> this is evidence: the inbound-webhook pattern — HMAC, idempotency, loop-breaker — is already built once, and went dark on wiring (an ingress flag and a Jira admin step), not capability.</p>")
rep(", and the schema prep for both — backoff, DLQ, and cursor columns (<a href='https://github.com/fluidstackio/dcim/pull/2191' target='_blank' rel='noreferrer'>#2191</a>).</p>",
    ", and the schema prep for both — backoff, DLQ, and cursor columns (<a href='https://github.com/fluidstackio/dcim/pull/2191' target='_blank' rel='noreferrer'>#2191</a>).</p>" + P1 + P2 + P3 + P4,
    "psync-body")

# ===== 2. p-sync facts rows =====
rep("<a href='https://github.com/fluidstackio/dcim/pull/2191' target='_blank' rel='noreferrer'>#2191</a> schema prep\" }],",
    "<a href='https://github.com/fluidstackio/dcim/pull/2191' target='_blank' rel='noreferrer'>#2191</a> schema prep\" },\n"
    "      { l: \"the dark webhook\", v: \"<span class='m'>POST /webhooks/jira/{site}</span> · HMAC-SHA256 (X-Hub-Signature) · site slugs atlasbuf→buf101, atlaswdl→wdl101 (no deployed slug is literally 'wdl' or 'buf') · secret via ExternalSecret from AWS SM <span class='m'>dcim-tasks/jira-credentials</span> · zero deliveries possible: no route exists\" },\n"
    "      { l: \"admin pair (no auth, by design)\", v: \"jsm-queue-stats · jsm-reconcile — in-cluster only; naming drift: the doc comment says repair_jira_sync_queue, the table is task_jira_sync_queue (leftover from the repairs→tasks rename, #1868)\" }],",
    "psync-facts")

# ===== 3. p-sync links =====
rep('{ label: "PR #2159 — collapse network_repair for Jira sync", url: "https://github.com/fluidstackio/dcim/pull/2159" }] },',
    '{ label: "PR #2159 — collapse network_repair for Jira sync", url: "https://github.com/fluidstackio/dcim/pull/2159" },\n'
    f'      {{ label: "the three unauthed routes (main.go:111-115, pinned Jun 10)", url: "{DC}/services/dcim-tasks/cmd/dcim-tasks/main.go#L111-L115" }},\n'
    '      { label: "PR #1868 — dcim-tasks born: webhooks + reconciler", url: "https://github.com/fluidstackio/dcim/pull/1868" },\n'
    '      { label: "Rob, Apr 29 — the e2e-review thread (“bane of my existence”)", url: "https://fluidstack.enterprise.slack.com/archives/C0AAY9E2NF9/p1777489512893739" },\n'
    '      { label: "Repair Workflows (Confluence) — design intent: “webhooks into dcim-tasks”", url: "https://fluidstack.atlassian.net/wiki/spaces/RE/pages/593494034/Repair+Workflows" }] },',
    "psync-links")

# ===== 4. new timeline event w-dark (renderer sorts by date) =====
WD = '''{ id: "w-dark", date: "2026-03-28", dateLabel: "Mar 28", track: "history",
    title: "dcim-tasks born — with a webhook ingest prod never routed",
    summary: "PR #1868 ships the Jira seam both ways: a polling reconciler, plus an HMAC webhook handler that has no route to it to this day.",
    detail: "Rob's `very-obvious-jsm-integration` branch lands the microservice four days after the Slack origin note. Inbound design: webhooks for near-real-time (`POST /webhooks/jira/{site}`, HMAC-SHA256 via `X-Hub-Signature`, per-site secret), the reconciler as the safety net, and a structural loop-breaker — the webhook's DB interface has no enqueue method, so inbound events can never re-trigger outbound sync. But the deploy PR's manual prerequisite — “Webhook secret configured in JSM (ATLASBUF project webhook settings)” — sits unchecked, and `httpRoute.enabled` is false in every prod values file in history: the service is cluster-internal, so Atlassian has nothing to deliver to. The HMAC secret was minted (AWS SM, Apr 13); the route never was. Prod inbound rides the poller — 5-minute discovery, 10-minute drift — and before Apr 13, prod `jira.sites` was `{}` and nothing synced at all. Whether dark-by-design or never-finished is written down nowhere read; a reviewer's question on #1868 about the unauthenticated admin pair has no recorded reply.",
    specImpact: "d-push prior art: the inbound-webhook pattern (HMAC, idempotency, loop-breaker) is already built — it went dark on wiring (an ingress flag and a Jira admin step), not capability. The API's push channel faces the same last mile: an exposed route, and a registration step someone owns.",
    links: [
      { label: "PR #1868 — dcim-tasks: webhooks + reconciler", url: "https://github.com/fluidstackio/dcim/pull/1868" },
      { label: "argocd#5090 — deploy PR; the unchecked JSM-webhook step", url: "https://github.com/fluidstackio/argocd/pull/5090" },
      { label: "main.go:111-115 — three routes outside JWT, “protect at the network layer”", url: "''' + DC + '''/services/dcim-tasks/cmd/dcim-tasks/main.go#L111-L115" },
      { label: "httpRoute.enabled: false (prod values, from day one)", url: "''' + DC + '''/argocd/datacenters-prod/dcim-tasks/values.yaml#L91-L92" },
      { label: "the loop-breaker (webhookQuerier — no enqueue method)", url: "''' + DC + '''/services/dcim-tasks/internal/server/webhooks_jira.go#L25-L37" },
      { label: "Slack origin, Mar 24 — “very obvious… seamless”", url: "https://fluidstack.enterprise.slack.com/archives/C090UBT9DLN/p1774374859495619?thread_ts=1774374759.728369&cid=C090UBT9DLN" },
      { label: "security brief, Apr 29 — names the reconciler, not webhooks", url: "https://fluidstack.enterprise.slack.com/archives/C0AAY9E2NF9/p1777496342367569?thread_ts=1777489512.893739&cid=C0AAY9E2NF9" },
      { label: "Repair Workflows (Confluence) — design intent says “webhooks into dcim-tasks”", url: "https://fluidstack.atlassian.net/wiki/spaces/RE/pages/593494034/Repair+Workflows" }] },
  '''
rep('{ id: "seed", date: "2026-04-22"', WD + '{ id: "seed", date: "2026-04-22"', "event-w-dark")

# ===== 5. d-push: prior-art cross-reference =====
rep('detail: "Today their workflow watches Jira status. Push moves the watch into a contract. The choice itself is what\'s open; if push wins, the mechanics ride with it — where Google\'s consumer runs, how FS authenticates to it, delivery/retry semantics.",',
    'detail: "Today their workflow watches Jira status. Push moves the watch into a contract. The choice itself is what\'s open; if push wins, the mechanics ride with it — where Google\'s consumer runs, how FS authenticates to it, delivery/retry semantics. New (Jun 11, from code): the inbound mirror of this pattern already exists — dcim-tasks ships an HMAC-signed Jira webhook ingest that prod never routed (the Mar 28 history row) — so the open question is wiring and ownership, not capability.",',
    "d-push-detail")
rep('links: [{ label: "The park, in a live ticket footer", url: "https://fluidstack.atlassian.net/browse/ATLASBUF-16958" }] },',
    'links: [\n      { label: "The park, in a live ticket footer", url: "https://fluidstack.atlassian.net/browse/ATLASBUF-16958" },\n'
    '      { label: "the dark webhook — Mar 28 history row", url: "#ev-w-dark" },\n'
    f'      {{ label: "main.go:111-115 — the unrouted webhook mount", url: "{DC}/services/dcim-tasks/cmd/dcim-tasks/main.go#L111-L115" }}] }},',
    "d-push-links")

# ===== 6. the three sync claims =====
rep('the always-on channel, <a href="#routing">02</a></span>',
    'the always-on channel, <a href="#routing">02</a>; the return half runs on polling — the webhook ingest built for it never got a route (<a href="#ev-w-dark">Mar 28</a>)</span>',
    "census-row1")
rep("<b>dcim-tasks' own sync mirrors them into the queue</b> — this path's",
    "<b>dcim-tasks' own sync mirrors them into the queue</b> (polling — 5-minute discovery / 10-minute drift; the webhook ingest built for this seam is dark, <a href=\"#ev-w-dark\">Mar 28</a>) — this path's",
    "02A-intake")
rep('dcim-tasks\' sync polls to mirror) — webhooks are the argued-for shape, with webhook-vs-poll open as <a href="#ev-d-push">d-push</a>.<sup class="rf"><a href="#ref-9">[9]</a></sup></p>',
    'dcim-tasks\' sync polls to mirror) — webhooks are the argued-for shape, with webhook-vs-poll open as <a href="#ev-d-push">d-push</a>.<sup class="rf"><a href="#ref-9">[9]</a></sup> And the inbound mirror of the pattern already exists in code: dcim-tasks ships an HMAC-signed Jira webhook ingest that prod never routed (built <a href="#ev-w-dark">Mar 28</a>, dark since; receipts at the pipeline\'s stage-2 MIRROR panel, <a href="#v-pipe">02·B</a>) — capability isn\'t the open question; wiring and ownership are.</p>',
    "polls-to-mirror")

# ===== 7. triangle rewrite (links in; zero facts out) =====
OLD_TRI = ('<b>FluidStack</b> operates the building and the floor · <b>Google (Bloom)</b> supplies and operates the TPU system and its repair automation (the operating split per FS — the tenancy drill hedges it) · <b>Atlas</b> — FS\'s codename for the customer, Anthropic (written down: <a href="https://github.com/fluidstackio/atlas-issue-tracker/blob/main/CLAUDE.md" target="_blank" rel="noreferrer">“between Fluidstack (FS) and Anthropic (Atlas)”</a>) — consumes the capacity. '
           'Atlas, Google, and Dell (the hardware vendor the next row introduces) each hold scoped Auth0 access; one house external-org pattern covers all three, four orgs counting the BMS integrators (the tenancy panel carries the terraform’s verbatim comment and the BMS-vs-BMC note; <a href="#foundry">§04</a>’s feldspar group list is a different, wider census — NetBox provisioning, not Teleport — keyed on the same Auth0 orgs: its “anthropic” is the terraform’s “atlas”, one org, two config labels).')
NEW_TRI = ('<b>FluidStack</b> operates the building and the floor · <b>Google (Bloom)</b> supplies and operates the TPU system and its repair automation (the operating split per FS — the tenancy drill hedges it, and no repo doc read states it) · <b>Atlas</b> — FS\'s codename for the customer, Anthropic (written down: <a href="https://github.com/fluidstackio/atlas-issue-tracker/blob/main/CLAUDE.md" target="_blank" rel="noreferrer">“between Fluidstack (FS) and Anthropic (Atlas)”</a>) — consumes the capacity. '
           f'Atlas (<a href="{SY}/terraform/fish/envs/prod/main.tf#L54-L59" target="_blank" rel="noreferrer">org_17EFoZ7YaZi1mqh1</a>), Google (<a href="{SY}/terraform/fish/envs/prod/main.tf#L36-L53" target="_blank" rel="noreferrer">org_siG1C0abE90FUnWo</a>), and Dell (the hardware vendor the next row introduces — <a href="{SY}/terraform/fish/envs/prod/main.tf#L69-L74" target="_blank" rel="noreferrer">org_j7mjrToZkciBXK1h</a>, bastion-enabled) each hold scoped Auth0 access; one house external-org pattern covers all three, four orgs counting the <a href="{SY}/terraform/fish/envs/prod/main.tf#L60-L68" target="_blank" rel="noreferrer">BMS integrators</a> (org_fXULDu3zQbqpamgA — the tenancy panel carries the terraform’s verbatim comment). '
           f'BMS there is Ignition’s building-management system, not the board-controller BMC — a contrast no single doc states: this page assembles it from the terraform comment and <a href="{SY}/docs/hardware/tpu.md" target="_blank" rel="noreferrer">the TPU hardware doc</a>, and only <a href="{RFC}" target="_blank" rel="noreferrer">the FISH RFC glossary</a> defines both terms in one table. '
           f'<a href="#foundry">§04</a>’s feldspar group list is a different, wider census — NetBox provisioning, not Teleport — keyed on the same Auth0 orgs: its <a href="{DC}/argocd/datacenters-prod/dcim-api-feldspar/values.yaml#L23-L47" target="_blank" rel="noreferrer">“anthropic”</a> is the terraform’s “atlas”, one org, two config labels.')
rep(OLD_TRI, NEW_TRI, "triangle")

# ===== 8. s-tenancy drill: pinned link + third-expansion caveat =====
rep('{ label: "SSO terraform (external_orgs)", url: "https://github.com/fluidstackio/systems/blob/main/terraform/fish/envs/prod/main.tf" }',
    f'{{ label: "SSO terraform (external_orgs, main.tf:26-74, pinned Jun 11)", url: "{SY}/terraform/fish/envs/prod/main.tf#L26-L74" }}',
    "tenancy-link-pin")
rep("Google's access is an instance of the house external-org mechanism\" }],",
    "Google's access is an instance of the house external-org mechanism · caveat: dcim's repair SOPs use BMS for a third expansion — Battery Management System — so the acronym is overloaded three ways in FS repos\" }],",
    "tenancy-caveat")

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

# EVENTS raw-HTML audit (title/summary/detail/specImpact must hold no tags)
ev = s[s.find('const EVENTS'):s.find('];', s.find('const EVENTS'))]
bad = [t[:80] for t in re.findall(r'(?:title|summary|detail|specImpact):\s*"([^"]*)"', ev) if '<' in t]
print("EVENTS html-in-string:", bad if bad else "clean")

ids = set(re.findall(r'id="([^"]+)"', s)) | set(re.findall(r"id='([^']+)'", s))
ev_ids = set(re.findall(r'id:\s*"([^"]+)"', ev))
dead = [h for h in set(re.findall(r'href=[\'"]#([^\'"]+)[\'"]', s))
        if h not in ids and not (h.startswith('ev-') and h[3:] in ev_ids)]
print("dead anchors:", sorted(dead))

base = json.load(open('/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/data/inventory-v88.json'))
hrefs = set(re.findall(r'href=[\'"]([^\'"]+)[\'"]', s))
nums = set(re.findall(r'\b\d[\d,]*(?:\.\d+)?%?\b', s))
print("href removals:", sorted(set(base['hrefs']) - hrefs))
print("num removals:", sorted(set(base['nums']) - nums))
