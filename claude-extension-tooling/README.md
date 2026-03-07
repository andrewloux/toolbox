# Claude Extension Tooling

Despite the folder name, this is really a generalized Chrome extension extraction and rewrite framework with a checked-in Claude-oriented preset.

The reusable part is:

- copy an installed extension out of Chrome
- keep timestamped runs plus a `latest` symlink
- inspect bundled code with `ast-grep`
- preview and apply structural rewrite rules
- wire those rewrites into the copy pipeline through hooks

The Claude-specific part is mostly in the current defaults, output path, and sample rule pack.

It is intentionally honest about what it is: a working private toolbox project, not a polished package. The scripts here are copied from the current live versions in `~` with only a small amount of repo-local glue added so you can run them from this checkout.

## What is here

- `scripts/extension_transformer`: generic extension copier and hook runner
- `scripts/extension_ast`: generic AST search / preview / apply wrapper around `ast-grep`
- `scripts/extension_explorer.ts`: generic interactive explorer for AST matches and rewrites
- `config/extension_transformer/hooks.sh`: repo-local hook that applies the rule pack in this repo
- `config/extension_transformer/rules/*.yml`: the current checked-in rule pack, which is presently Claude-oriented

## Honest caveats

- This is built around macOS Chrome profile paths.
- The current default target extension name is `Claude`, but `extension_transformer` can be retargeted with `--extension-name` or `--extension-id`.
- The current default destination is `~/ClaudeChromeExtension`, but it can be overridden with `--destination`.
- `extension_ast` depends on `sg` from `ast-grep`.
- `extension_explorer.ts` depends on `npx tsx`.
- The saved rules are bundle-pattern dependent; they may stop matching when the upstream extension bundle changes.
- The repo stores the current workflow, but it does not automatically install these scripts into `~/` or `~/.config`.

## Quick start

```bash
cd /Users/andrew.louis/Documents/toolbox/claude-extension-tooling

# Copy a fresh extension build out of Chrome and apply the repo's rules
make transform

# Inspect what got copied
make ls

# Preview all saved rules
make preview

# Launch the interactive explorer
make explore
```

Detailed walkthrough: [`USAGE.md`](./USAGE.md)

## Framework shape

Think of this repo as two layers:

- Framework: `extension_transformer`, `extension_ast`, `extension_explorer.ts`
- Current preset: repo-local hooks, repo-local rules, and defaults that happen to target the Claude extension

That means you can use the exact same scripts for another Chrome extension by changing the transform target and swapping the rule pack.

Example:

```bash
./scripts/extension_transformer \
  --extension-name "Some Other Extension" \
  --destination "$HOME/SomeOtherExtension" \
  --hooks ./config/extension_transformer/hooks.sh
```

## Typical flow

```bash
# 1. Pull a fresh copy and apply the current repo-local preset
make transform

# 2. Search for a structural pattern
./scripts/extension_ast search ~/ClaudeChromeExtension/latest 'await $OBJ.getCategory($$$)'

# 3. Preview the repo-local rules
./scripts/extension_ast preview ~/ClaudeChromeExtension/latest --rules ./config/extension_transformer/rules

# 4. Apply the repo-local rules directly
./scripts/extension_ast apply ~/ClaudeChromeExtension/latest --rules ./config/extension_transformer/rules

# 5. Explore interactively
npx tsx ./scripts/extension_explorer.ts ~/ClaudeChromeExtension/latest
```

To retarget this flow to another extension, the main knobs are:

- `--extension-name` or `--extension-id`
- `--destination`
- the rule files under `./config/extension_transformer/rules`

## Current checked-in rules

- `stub-getCategory.yml`: rewrites `await $OBJ.getCategory($$$)` to `""`
- `stub-getUserAgent.yml`: rewrites `this.getUserAgent()` to the current browser user agent string
- `example-*.yml`: example rules used for exploration / experimentation

## Notes

- `make transform` passes `--hooks ./config/extension_transformer/hooks.sh`, so this repo can be used without relying on `~/.config/extension_transformer/hooks.sh`.
- If you want the repo rules to become your global defaults, copy or symlink `config/extension_transformer` into `~/.config/extension_transformer`.
