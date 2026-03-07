EXT ?= $(HOME)/ClaudeChromeExtension/latest
HOOKS := ./config/extension_transformer/hooks.sh
RULES := ./config/extension_transformer/rules

.PHONY: transform dry-run restore ls preview apply explore

transform:
	./scripts/extension_transformer --hooks "$(HOOKS)" $(ARGS)

dry-run:
	./scripts/extension_transformer --dry-run --hooks "$(HOOKS)" $(ARGS)

restore:
	./scripts/extension_transformer --restore $(ARGS)

ls:
	./scripts/extension_ast ls "$(EXT)"

preview:
	./scripts/extension_ast preview "$(EXT)" --rules "$(RULES)"

apply:
	./scripts/extension_ast apply "$(EXT)" --rules "$(RULES)"

explore:
	RULES_DIR="$(RULES)" npx tsx ./scripts/extension_explorer.ts "$(EXT)"
