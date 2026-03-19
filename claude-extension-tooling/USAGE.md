# Usage

This document covers the repo-owned workflow for extracting the Claude Chrome extension, exploring its bundled code, and reapplying repo-local AST rewrites on each fresh copy.

The current preset targets the Claude extension, but the scripts themselves are more general than the folder name suggests.

## What this repo contains

Framework layer:

- `scripts/extension_transformer`
- `scripts/extension_ast`
- `scripts/extension_explorer.ts`

Current Claude preset:

- `config/extension_transformer/hooks.sh`
- `config/extension_transformer/rules/*.yml`
- default target extension name `Claude`
- default output root `~/ClaudeChromeExtension`

## Prerequisites

Install the expected tools:

```bash
brew install ast-grep
node --version
npx --version
```

You also need Chrome installed with the target extension present in at least one profile.

## First-time setup

Start with a health check:

```bash
cd /Users/andrew.louis/Documents/toolbox/claude-extension-tooling
make doctor
```

If you want the repo to become the global source of truth for the old home-directory command layer too:

```bash
make install-global
```

That symlinks:

- `~/extension_transformer`
- `~/extension_ast`
- `~/extension_explorer.ts`
- `~/.config/extension_transformer`

The install step is conservative: it backs up conflicting paths into `~/.toolbox-backups/claude-extension-tooling/...`.

## Command layer

Show the command summary:

```bash
make help
```

Most useful targets:

- `make doctor`
- `make transform`
- `make dry-run`
- `make restore`
- `make status`
- `make preview`
- `make apply`
- `make explore`
- `make text-search PATTERN='foo'`

## Standard loop

### 1. Pull a fresh extension build out of Chrome

```bash
make transform
```

What happens:

1. `extension_transformer` scans all Chrome profiles unless you force a single profile.
2. It finds installed copies of the target extension.
3. It picks the highest version it finds.
4. It copies that version into `~/ClaudeChromeExtension/runs/<unix_timestamp>/`.
5. It writes a `.source_manifest` breadcrumb into the copied run.
6. It updates `~/ClaudeChromeExtension/latest` to point at the new run.
7. Because `make transform` passes the repo hooks file, the repo-local rule pack gets applied after validation.

Useful variants:

```bash
make dry-run
make restore
make status
./scripts/extension_transformer --list-profiles
./scripts/extension_transformer --profile "Default" --hooks ./config/extension_transformer/hooks.sh
./scripts/extension_transformer --extension-id fcoeoabgfenejglbffodgkkbkcdhcgfn --hooks ./config/extension_transformer/hooks.sh
```

When to use each:

- `make doctor`: confirm prerequisites and current state before you begin
- `make transform`: fresh copy plus repo-local rewrites
- `make dry-run`: preview which installed extension build would be selected
- `make restore`: clean copy with no rewrites
- `make status`: inspect the current extracted run, source manifest, and git hash

### 2. Inspect the extracted extension

By default, the working directory is:

```bash
~/ClaudeChromeExtension/latest
```

List bundle files:

```bash
make ls
```

Show the current extracted source metadata:

```bash
make status
```

### 3. Search for stable strings first

When you are reacquiring a pattern after an upstream update, raw text search is often the fastest first move:

```bash
make text-search PATTERN='domain_info'
make text-search PATTERN='User-Agent'
make text-search PATTERN='category_org_blocked'
```

This is especially useful when hashed asset filenames changed and you need to relocate the right bundle.

### 4. Move from raw text to AST patterns

Use `extension_ast` when you want a structural search or rewrite preview.

Examples:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.cache.get($KEY)'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'await $OBJ.getCategory($$$)'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'this.getUserAgent()'
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'Date.now() - $CACHE.timestamp > this.CACHE_TTL_MS'
```

Preview a rewrite:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'await $OBJ.getCategory($$$)' -r '""'
```

Important AST rule:

- prefer full expressions over bare identifiers

Example:

- `getCategory` may miss method/property cases
- `await $OBJ.getCategory($$$)` is much more reliable

### 5. Preview or apply the saved rule pack

Preview all repo-local rules:

```bash
make preview
```

Apply all repo-local rules:

```bash
make apply
```

Important behavior:

- `apply` modifies files in place
- once a rewrite has already been applied, the original pattern may no longer exist
- if you change a rule, re-test from a fresh `make transform` instead of trusting an already-mutated `latest`

### 6. Use the interactive explorer when search gets fuzzy

Launch it:

```bash
make explore
```

Direct command:

```bash
npx tsx ./scripts/extension_explorer.ts ~/ClaudeChromeExtension/latest
```

Fastest useful explorer loop:

1. `/` search for a candidate pattern
2. `u` inspect the enclosing scope
3. `c` inspect nearby references
4. `r` preview a rewrite
5. `:save <name>` save the rule into the repo
6. `make preview` validate it against a fresh extracted run

Explorer notes:

- it resolves symlinks, so `~/ClaudeChromeExtension/latest` works correctly
- it searches per file with timeouts
- for large files and some literal misses, it falls back to grep for search-only exploration
- rewrites still require AST matches

Useful keys:

- `n` / `p`: next / previous match
- `u`: enclosing scope
- `c`: callers / references
- `w` / `s`: widen / shrink context
- `/`: search mode
- `r`: rewrite mode
- `:save <name>`: save a rule into `./config/extension_transformer/rules`
- `:apply`: apply the current rewrite

## Current checked-in rules

- `stub-getCategory.yml`: rewrites `await $OBJ.getCategory($$$)` to `""`
- `stub-getUserAgent.yml`: rewrites `this.getUserAgent()` to a fixed browser-like user agent string
- `example-bypass-cache-ttl.yml`: forces the TTL expression to evaluate stale
- `example-log-api-calls.yml`: logs `fetchCategoryFromAPI` calls
- `example-match-cache-class.yml`: search-only exploration rule

## Retargeting the framework

The scripting layer can target another extension by changing the extension selector and destination.

Example:

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

The main knobs are:

- `--extension-name` or `--extension-id`
- `--destination`
- the rule files under `./config/extension_transformer/rules`

## Troubleshooting

### `sg` not found

Install it:

```bash
brew install ast-grep
```

### Explorer search finds nothing for an obvious method name

This usually means the pattern is too small. Use a larger structural pattern:

```bash
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'await $OBJ.getCategory($$$)'
```

instead of:

```text
getCategory
```

### I changed a rule but `apply` did nothing

You probably already mutated `latest`. Re-copy from Chrome and test again:

```bash
make transform
make preview
```

### Upstream updates broke the current rules

Use the dedicated recovery guide:

- [`PATTERN_RECOVERY.md`](./PATTERN_RECOVERY.md)
