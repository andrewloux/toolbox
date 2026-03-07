# Usage

This document walks through the actual workflow stored in this repo: copy a Chrome extension out of Chrome, inspect the bundled JavaScript, preview or save structural rewrites, and re-apply those rules on every fresh copy.

The current checked-in preset targets the Claude extension, but the scripts themselves are more general than that.

## What this is

This is a private, working toolbox project that acts as a generalized extension extraction and AST rewrite framework, with a Claude-oriented preset currently checked into the repo.

The current assumptions are:

- macOS Chrome profile layout
- default target extension name is currently `Claude`
- default destination is currently `~/ClaudeChromeExtension`
- AST matching is done with `ast-grep` (`sg`)
- the interactive explorer runs with `npx tsx`
- the saved rules are tuned to the current bundle shape and may need updates when upstream bundle output changes

## Repo layout

```text
claude-extension-tooling/
  Makefile
  README.md
  USAGE.md
  scripts/
    extension_transformer
    extension_ast
    extension_explorer.ts
  config/
    extension_transformer/
      hooks.sh
      rules/
        example-bypass-cache-ttl.yml
        example-log-api-calls.yml
        example-match-cache-class.yml
        stub-getCategory.yml
        stub-getUserAgent.yml
```

## Prerequisites

Install the tools the scripts expect:

```bash
brew install ast-grep
node --version
npx --version
```

You need Chrome installed with whichever target extension you want to extract present in at least one profile.

For the checked-in preset, that target is currently the Claude extension.

## Framework vs preset

The easiest way to understand this repo is to split it into two layers.

Framework layer:

- `scripts/extension_transformer`
- `scripts/extension_ast`
- `scripts/extension_explorer.ts`

Current preset layer:

- repo-local hooks in `./config/extension_transformer/hooks.sh`
- repo-local rules in `./config/extension_transformer/rules`
- default transform target of `Claude`
- default destination of `~/ClaudeChromeExtension`

So the name of the folder is historical, but the scripts are reusable.

## Repo-local command layer

This repo does not require installing anything into `~/` or `~/.config` to use the stored workflow.

The `Makefile` wires things up like this:

- `make transform` runs `scripts/extension_transformer --hooks ./config/extension_transformer/hooks.sh`
- the repo-local `hooks.sh` calls `scripts/extension_ast apply ... --rules ./config/extension_transformer/rules`
- `make explore` sets `RULES_DIR=./config/extension_transformer/rules`, so `:save <name>` writes into this repo
- rule files stay inside this repo instead of depending on `~/.config/extension_transformer/rules`

That means the repo itself is the source of truth for the current workflow.

## Standard loop

### 1. Copy a fresh extension build out of Chrome

```bash
cd /Users/andrew.louis/Documents/toolbox/claude-extension-tooling
make transform
```

What happens:

1. `extension_transformer` scans all Chrome profiles unless you force a single profile.
2. It finds installed copies of the target extension.
3. It picks the highest version it finds.
4. It copies that version into `~/ClaudeChromeExtension/runs/<unix_timestamp>/`.
5. It writes a `.source_manifest` breadcrumb into the copied run.
6. It updates `~/ClaudeChromeExtension/latest` to point at the new run.
7. Because `make transform` passes the repo hooks file, the repo-local rules are applied to the copied files after validation.

Useful variants:

```bash
make dry-run
make restore
./scripts/extension_transformer --list-profiles
./scripts/extension_transformer --profile "Default" --hooks ./config/extension_transformer/hooks.sh
./scripts/extension_transformer --extension-id <chrome-extension-id> --hooks ./config/extension_transformer/hooks.sh
```

When to use each:

- `make transform`: fresh copy and re-apply repo rules
- `make dry-run`: preview what source would be selected without copying
- `make restore`: fresh copy without transforms, useful for getting back to a clean baseline

### Retarget to another extension

The framework becomes obviously general once you override the target extension and destination.

One-off example:

```bash
./scripts/extension_transformer \
  --extension-name "Some Other Extension" \
  --destination "$HOME/SomeOtherExtension" \
  --hooks ./config/extension_transformer/hooks.sh
```

ID-based example:

```bash
./scripts/extension_transformer \
  --extension-id abcdefghijklmnopqrstuvwxyzabcdef \
  --destination "$HOME/SomeOtherExtension" \
  --hooks ./config/extension_transformer/hooks.sh
```

If you retarget like that, the rest of the workflow stays the same. The main things you change are:

- transform target
- output destination
- rule pack

## Inspect the copied extension

For the current preset, the default working extension directory is:

```bash
~/ClaudeChromeExtension/latest
```

For another target, use whatever destination you passed to `extension_transformer`.

List the JavaScript and TypeScript bundle files:

```bash
make ls
```

Or directly:

```bash
./scripts/extension_ast ls ~/ClaudeChromeExtension/latest
```

## Search with `extension_ast`

Use `extension_ast` when you want a one-shot structural search or rewrite preview.

Search for a pattern:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.cache.get($KEY)'
```

Preview a rewrite:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.CACHE_TTL_MS' -r '0'
```

Generic search examples:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.cache.get($KEY)'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'await $OBJ.someMethod($$$)'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest '$OBJ.headers.set($KEY, $VALUE)'
```

Current preset examples:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'await $OBJ.getCategory($$$)'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.getUserAgent()'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.pendingRequests.get($KEY)'
```

Important:

- `extension_ast` uses AST matching only.
- That is great for structural queries and rewrite previews.
- It also means bare identifiers can miss method names and property accesses if tree-sitter represents them as `property_identifier` instead of `identifier`.

Example of that sharp edge:

- searching for bare `getCategory` may return nothing even when the code obviously contains `obj.getCategory(...)` or `class X { getCategory() {} }`
- searching for `await $OBJ.getCategory($$$)` works because it matches the full call expression

## Preview or apply saved rules

Preview every repo-local rule:

```bash
make preview
```

Direct command:

```bash
./scripts/extension_ast preview ~/ClaudeChromeExtension/latest --rules ./config/extension_transformer/rules
```

Apply every repo-local rule:

```bash
make apply
```

Direct command:

```bash
./scripts/extension_ast apply ~/ClaudeChromeExtension/latest --rules ./config/extension_transformer/rules
```

Important behavior:

- `apply` modifies files in place
- if you already rewrote a pattern once, changing the rule and running `apply` again may do nothing because the original pattern no longer exists
- when you change a rule and want to re-test from a clean baseline, use `make transform` again instead of applying on top of an already-rewritten `latest`

## Interactive exploration with `extension_explorer.ts`

Use the explorer when you want to iterate quickly, browse matches, inspect context, preview a rewrite, or save a rule.

Launch it:

```bash
make explore
```

Direct command:

```bash
npx tsx ./scripts/extension_explorer.ts ~/ClaudeChromeExtension/latest
```

The explorer starts in search mode so you can type a pattern immediately.

### Modes

- `SEARCH`: enter an AST pattern and press Enter
- `NAV`: single-key navigation after a search completes
- `REWRITE`: enter a rewrite string and preview replacements
- `COMMAND`: save rules, apply rewrites, or change language

### NAV keys

- `n` or `j`: next match
- `p` or `k`: previous match
- `u`: show enclosing scope
- `c`: show callers / references
- `w`: widen context
- `s`: shrink context
- `/` or `i`: go to search mode
- `r`: go to rewrite mode
- `:`: go to command mode
- `?`: show help
- `q`: quit

### Command mode

- `:save <name>`: save the current pattern and rewrite as a YAML rule in `RULES_DIR`
- `:apply`: apply the current rewrite to files in place
- `:lang <lang>`: switch parser language

When launched via `make explore`, `:save <name>` writes into:

```text
./config/extension_transformer/rules
```

Explorer-specific notes:

- it resolves symlinks before searching, so `~/ClaudeChromeExtension/latest` works correctly
- it searches per file with timeouts to avoid `sg` hanging on large minified bundles
- for large files and some literal-pattern misses, it uses a grep fallback so the UI still finds text even when AST matching is a poor fit
- grep fallback is search-only; rewrites still require AST matches

## Current checked-in rule set

### `stub-getCategory.yml`

```yaml
id: stub-getCategory
language: JavaScript
rule:
  pattern: await $OBJ.getCategory($$$)
fix: '""'
```

What it does:

- replaces category lookups with an empty string
- avoids relying on matching a bare `getCategory` identifier, which misses method/property cases

### `stub-getUserAgent.yml`

```yaml
id: stub-getUserAgent
language: JavaScript
rule:
  pattern: this.getUserAgent()
fix: '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"'
```

What it does:

- replaces the embedded SDK user-agent helper call with a static browser-like user agent string

### Example rules

- `example-bypass-cache-ttl.yml`: forces the cache-expiration expression to evaluate as stale
- `example-log-api-calls.yml`: logs `fetchCategoryFromAPI` calls
- `example-match-cache-class.yml`: search-only exploration rule

These are not framework requirements. They are simply the current checked-in examples / transforms for one target extension.

## Authoring a new rule

### Path 1: quick preview first

Use `search` with `-r` before saving anything:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'await $OBJ.getCategory($$$)' -r '""'
```

If the preview looks right, create a YAML rule under:

```text
./config/extension_transformer/rules/
```

Template:

```yaml
id: my-rule-name
language: JavaScript
rule:
  pattern: some.pattern($ARG)
fix: replacement($ARG)
```

Then:

```bash
make preview
make apply
```

For a different extension, the exact same rule-authoring loop applies. Only the patterns and rewrites change.

### Path 2: interactive save from the explorer

1. Launch `make explore`
2. Search for a pattern
3. Press `r` and enter a rewrite
4. Press `:` and run `save my-rule-name`

If you launch the explorer directly without `make explore`, rule saves fall back to:

```text
~/.config/extension_transformer/rules
```

## Restore / reset workflow

If you want a clean extension copy with no transforms:

```bash
make restore
```

That uses the `.source_manifest` breadcrumb from the last copied run and re-copies the original source version without applying transforms.

If you just want to replay the current repo rules from a clean base:

```bash
make transform
```

If you are targeting another extension with a custom destination, rerun `extension_transformer` with the same target flags and hook path.

## Troubleshooting

### `sg` not found

Install it:

```bash
brew install ast-grep
```

### Explorer says `Not a TTY`

Run it directly in an interactive terminal, not through a non-interactive pipe.

### Search returns nothing for a method name that obviously exists

This is often the AST node-type mismatch mentioned above. Instead of a bare name like:

```text
getCategory
```

search for a larger structural pattern such as:

```text
await $OBJ.getCategory($$$)
```

### Large minified files are painful to search

The explorer handles this better than plain `extension_ast` because it:

- searches per file
- adds timeouts
- falls back to grep for large files or literal-pattern misses

If a pattern is rewrite-oriented, though, you still need an AST pattern that `sg` can actually match.

### I changed a rule but `apply` did not do anything

You probably already rewrote the original pattern in `latest`. Re-copy from Chrome and re-apply:

```bash
make transform
```
