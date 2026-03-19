# Claude Extension Tooling

This directory is the checked-in source of truth for the Claude extension extraction and AST rewrite workflow.

It does three jobs:

- copies the newest installed Claude extension build out of Chrome
- keeps timestamped extracted runs plus a `latest` symlink
- reapplies a repo-owned AST rule pack on every fresh copy

The scripting layer is generic, but the current defaults and rules are tuned for the Claude extension.

## Quick start

```bash
cd /Users/andrew.louis/Documents/toolbox/claude-extension-tooling
make doctor
make transform
make preview
make explore
```

If you want the repo to become your global command layer too:

```bash
make install-global
```

That symlinks `~/extension_transformer`, `~/extension_ast`, `~/extension_explorer.ts`, and `~/.config/extension_transformer` back to this repo so the repo stays the source of truth.

## Command layer

```bash
make help
```

Most useful commands:

- `make doctor`: check prerequisites, current extracted run, and Chrome source detection
- `make transform`: copy the newest installed Claude extension and apply repo rules
- `make dry-run`: see which installed extension build would be selected
- `make restore`: re-copy the selected extension without transforms
- `make status`: show the current extracted run, source manifest, and git hash
- `make preview`: preview the saved AST rules against `~/ClaudeChromeExtension/latest`
- `make apply`: apply the saved AST rules directly to `~/ClaudeChromeExtension/latest`
- `make explore`: launch the interactive AST explorer
- `make text-search PATTERN='foo'`: raw `rg` over the extracted extension for stable strings
- `make install-global`: point the global `~/extension_*` commands and `~/.config/extension_transformer` at this repo

## What lives here

- `scripts/extension_transformer`: copies an installed Chrome extension and runs lifecycle hooks
- `scripts/extension_ast`: AST search / preview / apply wrapper around `ast-grep`
- `scripts/extension_explorer.ts`: interactive explorer for finding and saving rewrite rules
- `config/extension_transformer/hooks.sh`: repo-local hook that applies the repo-local rule pack
- `config/extension_transformer/rules/*.yml`: Claude-oriented rule pack

## Current assumptions

- macOS Chrome profile layout
- default target extension name is `Claude`
- default destination is `~/ClaudeChromeExtension`
- `sg` from `ast-grep` is installed
- `node` and `npx` are available for the explorer

## When upstream updates break the rules

Start here:

- [`USAGE.md`](./USAGE.md) for the full workflow
- [`PATTERN_RECOVERY.md`](./PATTERN_RECOVERY.md) for concrete pattern-finding guidance

The short version:

- use `make transform` to pull a clean new run
- use `make text-search` to find stable strings like endpoint paths, headers, storage keys, or UI labels
- use `make explore` and `./scripts/extension_ast search ...` to turn those anchors into structural patterns
- prefer full expressions like `await $OBJ.getCategory($$$)` over bare identifiers like `getCategory`

## Retargeting the framework

The scripting layer is not Claude-only. You can point it at another extension with `--extension-name` or `--extension-id` and a different destination.

Example:

```bash
./scripts/extension_transformer \
  --extension-name "Some Other Extension" \
  --destination "$HOME/SomeOtherExtension" \
  --hooks ./config/extension_transformer/hooks.sh
```
