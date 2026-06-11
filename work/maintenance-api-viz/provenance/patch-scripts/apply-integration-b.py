#!/usr/bin/env python3
import re, json, subprocess, tempfile
FILE = "/Users/andrew/Documents/Codex/2026-06-08/yo-i-m-in-the-production-2/code/accelerator-provisioning-app/maintenance-api.html"
s = open(FILE).read()
ok, miss = [], []

def rep(old, new, tag):
    global s
    n = s.count(old)
    if n != 1:
        miss.append(f"{tag} (count={n})"); return
    s = s.replace(old, new); ok.append(tag)

CONSOL = "https://fluidstack.atlassian.net/wiki/spaces/Infra/pages/656965636/Platform+Consolidation+Towards+a+Unified+Console"
ROADMAP = "https://fluidstack.atlassian.net/wiki/spaces/Infra/pages/245628984/Platform+Infra+Roadmap+Q1+-+Q2+26"
PR1697 = "https://github.com/fluidstackio/foundry/pull/1697"

# 1. bot-side cf_14593 coverage: measured (dedupe row, 01·C)
rep("Caveat: bot-side coverage is unmeasured; the custom-field pass ran on human tickets only.",
    "Bot-side coverage, measured Jun 10 by a 500-ticket random sample over the 14,510 bot filings (live JQL): <b>~2%</b> (95% CI 0.8–3.2%, ≈290 tickets) — and 7 of the 10 hits were created Jun 7 or later, so the bot has only just started stamping it.",
    "cf14593-sample-row")

# 2. 01·D facts table cell
rep("<span>UUID · wired through dcim-tasks · human tickets only — bot-side coverage unmeasured</span>",
    "<span>UUID · wired through dcim-tasks · bot-side coverage sampled Jun 10: ~2% of 14,510 (95% CI 0.8–3.2%), concentrated in Jun-7+ tickets</span>",
    "cf14593-facts-cell")

# 3. June 2 drill enrichment: in-ticket receipts
rep("The route raised INC-4681, the “DC ops Alerting path” workflow escalated to Systems Esc, and Hammad Mohiuddin was paged — acked in 19 s. The incident was Declined 4 minutes later; the ticket closed Done in 16.</p>",
    "The route raised INC-4681, the “DC ops Alerting path” workflow escalated to Systems Esc, and Hammad Mohiuddin was paged — acked in 19 s. He said so on the ticket itself, three minutes in: “I'm getting paged on this via incident.io systems-oncall. We should probably change the request type or hook it up so that systems does not get paged for requests like these.” The incident was Declined 4 minutes later; the ticket closed Done in 16, assignee Sean Brabson, resolution: a white BMC cable was attached where the mgmt cable should have been.</p>",
    "june2-enrich")

# 4. kickoff event: auth sentence corrected
rep("Auth/authz resolves when Xander's RFC closes (~Jun 15).",
    "Auth/authz was expected to close with Xander's RFC (~Jun 15) — what actually landed by Jun 10 is Tyler van Hensbergen's Auth0-M2M draft (foundry PR #1697: “Auth0 is the sole token issuer for the REST surface… M2M client credentials is the v1 flow”), with Xander advocating mTLS externally and the decision not yet closed (per the Granola notes).",
    "kickoff-auth-fix")

# 5. d-auth event: summary + detail + link
rep('summary: "Auth0 M2M assumed; closes with Xander\'s RFC.",',
    'summary: "Auth0 M2M assumed; the live draft is Tyler\'s RFC (foundry #1697), Xander the mTLS counter-voice.",', "dauth-summary")

rep("Xander's RFC isn't circulated yet (expected ~Jun 15) — no document to link until it lands.\",",
    "The kickoff expected Xander's RFC ~Jun 15. What's circulated as of Jun 10 is Tyler van Hensbergen's draft instead — foundry PR #1697, “docs(root): add Auth0 REST authentication RFC”: Auth0 as sole token issuer for the REST surface, M2M client credentials as the v1 flow. The Granola notes record Xander advocating mTLS externally, decision not yet closed; he returns in a day.\",", "dauth-detail")

rep('links: [{ label: "Xander on the auth story (May 28, flavor)", url: "https://fluidstack.enterprise.slack.com/archives/C0ABALH2R9C/p1780007749949769?thread_ts=1780007749.949769&cid=C0ABALH2R9C" }] },',
    'links: [{ label: "Tyler\'s Auth0-M2M RFC — foundry PR #1697 (draft, Jun 10)", url: "' + PR1697 + '" }, { label: "Xander on the auth story (May 28, flavor)", url: "https://fluidstack.enterprise.slack.com/archives/C0ABALH2R9C/p1780007749949769?thread_ts=1780007749.949769&cid=C0ABALH2R9C" }] },', "dauth-link")

# 6. who's-who Xander row
rep('Auth/SSO — wrote the external-org terraform; auth RFC closes ~Jun 15',
    'Auth/SSO — wrote the external-org terraform; advocates mTLS for external auth (the live Auth0-M2M RFC draft is Tyler\'s, foundry #1697 — decision open)', "whoswho-xander")

# 7. auditability provenance corrected (DRILL body — raw HTML ok)
rep("That replay property is the auditability precedent the API inherits — 100% repair-loop auditability already appears in hospital-rack acceptance criteria (a working-session citation — <a href='#ref-10'>[10]</a>).",
    "That replay property is the auditability precedent the API inherits — “Repair loop auditability: current 0%, target 100% — all repairs tracked end-to-end” is a success metric on the Platform/Infra Q1–Q2 roadmap <a href='" + ROADMAP + "' target='_blank' rel='noreferrer'>↗</a> (an earlier draft here placed it in hospital-rack acceptance criteria; the roadmap is where it's actually written).",
    "auditability-fix")

# 8. front-door row: Platform Consolidation receipt
rep("Deployment status unestablished: the foundry repo holds no deploy receipts beyond the RFC. Whether a live instance exists is a Wk-2 shape-check question for Jason + Tyler",
    "Deployment status unestablished: the foundry repo holds no deploy receipts beyond the RFC. Whether a live instance exists is a Wk-2 shape-check question for Jason + Tyler. The consolidation plan one level up is written though: Anshul's Platform Consolidation page sketches a stateless API Proxy Layer (Kaiser API, Partner API, DCIM API) with “Partner API introduced” as its roadmap step 4 <a href=\"" + CONSOL + "\" target=\"_blank\" rel=\"noreferrer\">↗</a>",
    "frontdoor-consol")

# 9. Kaiser collision receipted (ref-6)
rep("(the Kaiser-collision clause remains session-cited — also named in [10])",
    "(the collision target is receipted: Kaiser is FS's business/planning console — “capacity planning, finance, site selection, delivery, and commercial operations” — with an API of its own, per Anshul's Platform Consolidation page <a href=\"" + CONSOL + "\" target=\"_blank\" rel=\"noreferrer\">↗</a>; an adjacent collision to know about: “Foundry” also names the partner portal)",
    "kaiser-receipt")

# 10. ref-10: move auditability + Kaiser out of still-session-only
rep("the hospital-rack “100% repair-loop auditability” acceptance criterion and the hospital-rack process's origin window;",
    "the hospital-rack process's origin window;", "ref10-audit-out")
rep("the DCIM-API per-machine-credentials precedent (cited in d-auth); TQ's networking / FISH-fabric role description; the Kaiser-collision clause (ref 6);",
    "the DCIM-API per-machine-credentials precedent (cited in d-auth); TQ's networking / FISH-fabric role description;", "ref10-kaiser-out")
rep("Rob's Jun 1 → Jun 3 spec promise; the kickoff-adjacent Granola notes.",
    "Rob's Jun 1 → Jun 3 spec promise; the kickoff-adjacent Granola notes; the repair-loop-auditability target (a roadmap success metric, not hospital-rack AC as earlier drafted); the Kaiser collision (Platform Consolidation page); bot-side cf_14593 coverage (now a measured sample, ~2%).",
    "ref10-recovered-add")

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
