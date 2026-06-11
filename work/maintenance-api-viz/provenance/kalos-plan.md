# Kalos synthesis plan (v88 → v89/v90) — 2026-06-10

RULE (Andrew, verbatim intent): NO CONTEXT CULLING. Every "delete/cut" proposal below is applied as
relocation: full content survives at ONE canonical home, the other sites shrink to a pointer.
Mechanical check after each patch: set-diff of unique hrefs and unique numeric tokens — no removals allowed.

Round-10 Google LOWs folded in: dhint aside (→WP7), 01·C forward ref (→WP9), census density (→WP2),
gateway-mount status unassigned (→WP6), Sean Brabson missing from who's-who (→WP10).
FS round-10 findings: fold in when it lands.

## PATCH K1 — structure (the wake-up skeleton)
1. **State-of-play box** in header after the meta line ("Where this stands"):
   DECIDED-DIRECTION — generic surface (Jun 8 scoping), gateway mount, Temporal Cloud + site workers, Auth0-M2M working assumption (Tyler #1697 vs Xander mTLS, d-auth ~Jun 15);
   PAGE PLANKS — batch · coalescing · cf_14593 key · routing-class · GET /problem-codes (status: 05);
   OPEN — the seven #ev-d-* links;
   NEXT — Wk0–1 inputs Jun 16 → RFC Jun 23 → spec ~Jul 21 → freeze ~Aug 4; CUJ3 sequence diagram owed since Apr 28;
   BURNING — the fallback question (→ amber note in 01).
   All lifted from 05/EVENTS; pure addition.
2. **Census → 5-row table** (touch | what it is | repair path? | status | receipt) + one trailing 8,737
   sentence relocated into 01·A's first diacap. Email parenthetical → pointer (canonical: §02 always-on line).
3. **Decoder ×2 → one contiguous .mt table** (term | expansion | receipt), group header rows
   Sites/Stack/Protocols/Programs/Hardware, .sub landmark, "reference — skip on a fast pass" lede.
4. **#temporal-map moves below 01·B** (after the gated-trigger prose) with its own .sub landmark;
   decoder Temporal entry pointer updated ("follows 01·B").
5. **Two-deployments table → two cards** (.scard/.kv pattern); "The gap" seg lifted to amber note
   "The fallback question — open three ways" right after the cards (BP-232 + window + which-Jira-project
   + TQ ask all preserved); Borneo card keeps 1-line pointer; dek#2 shrinks to stake + pointer.
6. **05 planks → table** (plank | who's already asking | receipt), GET /problem-codes + routing-class
   included as rows; "To extend this doc…" line moves to footer colophon. .sub landmarks for the table.

## PATCH K2 — dedup-by-relocation + prose rhythm
7. Status formula: full version ONLY at 05 lede; sites 624 / 648 / 652 / 747 / 831 → "a page plank (status: 05)".
   cf_14593 kv (747) → one-liner + pointer (content lives at 01·C row, 01·D table row, 05).
8. Turn-up gate: canonical = Temporal map. Census ③ drops embedded quote; 01·A diacap drops const name;
   01·B diacap → one sentence + pointer. Drills stay self-contained.
9. June 2: canonical = §02 red note (narrative) + lede (mapping 1669/1415). 01·B diacap → one clause + pointer.
   Red note keeps BOTH Hammad quotes (ticket + Slack — different utterances, both stay).
10. JSM email: canonical = §02 "always-on" line (full + [10]). 01·B diacap copy removed; census → pointer.
11. §02 opening: claim-first rewrite; hedges live in amber note (it already owns them); standalone 200/200
    paragraph folds its dataset caveat into the lede line.
12. Fallback: canonical = the new amber note (WP1.5). Header dek + Borneo card → pointers.
13. 01·D: staleness verdict canonical at the 705 sidebar, 753 shrinks; 1,051 definition canonical at kv,
    u-diag/s-doctor drills keep compact one-line definitions; "fired but not in proto" note cell capped
    with #ev-storm1 pointer (verify storm1 carries TROSS cross-cut first); 01·C intro arithmetic → pointer
    to u-flows; u-flows fact row = one-line sizes, reconciliation paragraphs move into panel BODY
    ("Reconciling the counts."); June 1–9 mean/median canonical at 01·D row, 955 + a-doctor → pointers.
14. §04 NetBox paragraph → 3 paragraphs; Sean Banko full quote stays at the posture slede only,
    §04 staleness line gets pointer; IES hedge compressed in place (kept).
15. Hero dhint → one line + [10] pointer ([10] verified to carry the full method block).
16. foundry-gateway cell trimmed; consolidation-plan story moves to a diacap under the stack (full content).
17. 01·B "status watch becomes contractual" run-on rewrite (prose lens text).
18. Temporal-map "an earlier draft left open / retired as wrong" revision-narration → plain fact + retirement
    notes kept but moved to sentence-final positions ([10]-class history preserved, not culled).
19. CB3: decoder entry rewrite (keeps every caveat incl. FS-authored-artifacts clause); Bloom card
    parenthetical → "(Google's name for it — decoder)".
20. BMS sentence: Bloom card → pointer "(a fourth external org, the BMS integrators — tenancy panel)";
    full content verified present in s-tenancy drill.

## PATCH K3 — ergonomics + chrome
21. Drill dhints (5 sites): "▸ solid boxes drill down — mechanism, exemplars, receipts · dashed boxes are pointers".
22. renderDrill: scrollIntoView when panel opens below the fold.
23. renderTL: suppress status chip when status === "open" (track badge already says it); keep "closing".
24. Tomorrow SVG: dashed stroke on routing-class chip + webhook edge (+coalesce annotation), 3-key legend
    (solid = settled · dashed = open d-row · dotted = page plank); apology sentence becomes legend pointer.
    Bbox-verify. Conservative: if collisions, legend-only.
25. Who's-who: add Sean Brabson line (June 2 assignee; third Sean — name-collision note).
26. 05 ledger: add the gateway-mount direction explicitly (Jun 8 scoping receipt) — closes Google-R10 LOW 4.

## Verification battery (after each patch)
JS parses · EVENTS html-in-string audit · 0 dead anchors (#/#ev-) · console clean ·
href set-diff: no removals · numeric-token set-diff: no removals · screenshot of changed regions.
Then cert rounds restart (11+12 must dual-pass).
