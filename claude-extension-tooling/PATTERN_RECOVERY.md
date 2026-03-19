# Pattern Recovery

Use this when an upstream Claude extension update changes the bundle enough that the saved AST rules stop matching.

## The recovery loop

1. Start from a clean extracted build.

```bash
cd /Users/andrew.louis/Documents/toolbox/claude-extension-tooling
make transform
```

2. Confirm what changed.

```bash
make status
make dry-run
```

Look at:

- `.source_manifest` for the selected Chrome source version
- `git-hash.txt` for the upstream build fingerprint
- renamed `assets/*.js` bundle files between the previous run and the new run

3. Find stable text anchors first.

Use raw text search before AST search when you do not yet know the new structure:

```bash
make text-search PATTERN='domain_info'
make text-search PATTERN='User-Agent'
make text-search PATTERN='category_org_blocked'
make text-search PATTERN='pendingRequests'
```

4. Turn those anchors into structural patterns.

Once you know the file and surrounding code, switch to AST search:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'await $OBJ.getCategory($$$)'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.getUserAgent()'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'Date.now() - $CACHE.timestamp > this.CACHE_TTL_MS'
```

5. Iterate in the explorer.

```bash
make explore
```

Useful explorer keys:

- `/`: search
- `r`: preview a rewrite
- `u`: show enclosing scope
- `c`: show callers / references
- `:save <name>`: save a rule into the repo rule pack
- `:apply`: apply the current rewrite to the extracted extension

6. Validate before saving the rule as canonical.

```bash
make preview
```

If the match count is zero or wildly too large, the pattern is not specific enough yet.

7. Re-test from a clean baseline.

Do not trust a rule that only works on a bundle you already mutated. Re-run `make transform` and preview again.

## Pattern selection rules

These rules will save time when the bundle moves around:

- Prefer stable literals over local variable names. Endpoint paths, header names, storage keys, and user-facing strings survive minification better than local identifiers.
- Prefer full expressions over bare identifiers. `await $OBJ.getCategory($$$)` is much more reliable than `getCategory`.
- Match the behavior, not the filename. Asset filenames are content-hashed and will change on almost every upstream update.
- Keep one rule per behavior. Small rules are easier to recover and safer to preview.
- Use raw text search first when AST search returns nothing. AST misses are often a pattern-shape issue, not proof that the behavior vanished.
- Re-run from a clean extracted copy after each rule change. Once a rewrite has been applied, the original pattern may no longer exist.

## Concrete recovery recipes

### `stub-getCategory.yml`

Goal:

- bypass category checks by stubbing `await $OBJ.getCategory($$$)` to `""`

Stable anchors to grep:

- `domain_info`
- `category_org_blocked`
- `pendingRequests`
- `getEffectiveCategory`
- `blocked.html`

AST patterns to try:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'await $OBJ.getCategory($$$)'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest '$OBJ.getCategory($$$)'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.pendingRequests.get($KEY)'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'new URL("/api/web/domain_info/browser_extension", $BASE)'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'return "category_org_blocked"'
```

Why these work:

- even if the method name moves or gets inlined, the domain classification flow usually still touches the endpoint path, the cache maps, or the category literals

### `stub-getUserAgent.yml`

Goal:

- replace `this.getUserAgent()` with a fixed browser UA string

Stable anchors to grep:

- `User-Agent`
- `X-Stainless-Runtime`
- `anthropic-dangerous-direct-browser-access`
- `defaultHeaders`

AST patterns to try:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.getUserAgent()'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'getUserAgent() { $$$ }'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest '{ "User-Agent": $VALUE, $$$ }'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest '$OBJ.headers.set("User-Agent", $VALUE)'
```

Why these work:

- the user-agent override often sits near the Anthropic client default headers, which tend to keep stable header keys even when variable names churn

### `example-bypass-cache-ttl.yml`

Goal:

- force cached category entries to look stale so the code re-fetches

Stable anchors to grep:

- `CACHE_TTL_MS`
- `timestamp`
- `pendingRequests`
- `Date.now()`

AST patterns to try:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'Date.now() - $CACHE.timestamp > this.CACHE_TTL_MS'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.CACHE_TTL_MS'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.cache.get($KEY)'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.cache.set($KEY, $VALUE)'
```

Why these work:

- the cache flow usually preserves the TTL constant or at least the `timestamp` comparison shape

## When AST search seems wrong

Common failure modes:

- the pattern is too small and tree-sitter tokenizes it differently than you expect
- the file is large and the explorer or `sg` fallback is behaving differently
- the bundle got refactored so the method is now inlined or split across helpers

Practical fixes:

- widen the pattern to include the call shape or surrounding control flow
- fall back to `make text-search` on stable strings and then search structurally within the candidate file
- use the explorer on the candidate file and inspect `u` and `c` output to see the actual AST neighborhood

## Diffing the old and new runs

If you already have a known-good older run, diff it against the fresh run to see what moved:

```bash
diff -rq ~/ClaudeChromeExtension/runs/<old-run> ~/ClaudeChromeExtension/latest
```

What to look for:

- new hashed asset filenames
- new bundle splits or merged bundles
- unchanged string literals inside renamed files
- the same endpoint path or category literals in a different scope

The filenames will change. The stable strings and behaviors are what matter.
