TARGET_ROOT ?= $(HOME)/ClaudeChromeExtension
EXT ?= $(TARGET_ROOT)/latest
HOOKS := ./config/extension_transformer/hooks.sh
RULES := ./config/extension_transformer/rules

.DEFAULT_GOAL := help

.PHONY: help doctor install-global transform dry-run restore status ls preview apply explore text-search

help:
	@printf '%s\n' \
		'Claude extension tooling' \
		'' \
		'Common targets:' \
		'  make doctor                         Check local prerequisites and current extension status' \
		'  make transform                      Copy the newest installed Claude extension and apply repo rules' \
		'  make dry-run                        Show which installed extension build would be selected' \
		'  make restore                        Re-copy the selected extension without applying transforms' \
		'  make status                         Show the current extracted run and source manifest' \
		'  make preview                        Preview all saved AST rules against $(EXT)' \
		'  make apply                          Apply all saved AST rules to $(EXT)' \
		'  make explore                        Launch the interactive AST explorer against $(EXT)' \
		"  make text-search PATTERN='foo'      Raw ripgrep over the extracted extension for stable strings" \
		'  make install-global                 Symlink ~/extension_* and ~/.config/extension_transformer to this repo' \
		'' \
		'Useful overrides:' \
		'  make transform ARGS="--profile Default"' \
		'  make transform ARGS="--extension-id fcoeoabgfenejglbffodgkkbkcdhcgfn"' \
		'  make preview EXT=$(HOME)/ClaudeChromeExtension/latest'

doctor:
	./scripts/doctor.sh

install-global:
	./scripts/install_global.sh

transform:
	./scripts/extension_transformer --hooks "$(HOOKS)" $(ARGS)

dry-run:
	./scripts/extension_transformer --dry-run --hooks "$(HOOKS)" $(ARGS)

restore:
	./scripts/extension_transformer --restore $(ARGS)

status:
	@printf 'Target root: %s\n' "$(TARGET_ROOT)"
	@if [ -L "$(EXT)" ]; then printf 'latest -> %s\n' "$$(readlink "$(EXT)")"; else printf 'latest symlink missing: %s\n' "$(EXT)"; fi
	@if [ -f "$(EXT)/.source_manifest" ]; then printf '\n'; sed -n '1,20p' "$(EXT)/.source_manifest"; else printf '\nNo .source_manifest at %s\n' "$(EXT)"; fi
	@if [ -f "$(EXT)/git-hash.txt" ]; then printf '\ngit-hash: '; sed -n '1p' "$(EXT)/git-hash.txt"; fi

ls:
	./scripts/extension_ast ls "$(EXT)"

preview:
	./scripts/extension_ast preview "$(EXT)" --rules "$(RULES)"

apply:
	./scripts/extension_ast apply "$(EXT)" --rules "$(RULES)"

explore:
	RULES_DIR="$(RULES)" npx tsx ./scripts/extension_explorer.ts "$(EXT)"

text-search:
	@if [ -z "$(PATTERN)" ]; then printf "Usage: make text-search PATTERN='domain_info'\n" >&2; exit 1; fi
	rg -n --hidden --max-count 20 --max-columns 240 --max-columns-preview --glob '!*.map' --glob '!_metadata/*' "$(PATTERN)" "$(EXT)"
