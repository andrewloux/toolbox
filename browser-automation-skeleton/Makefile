# Browser Automation - Developer Workflow
.PHONY: help setup chrome chrome-reset test clean

help:
	@echo "make setup         - First time setup"
	@echo "make chrome        - Launch Chrome with debugging"
	@echo "make chrome-reset  - Fix when Chrome is fucked"
	@echo "make test          - Test if Chrome is running"
	@echo "make clean         - Clean everything"

# First time setup
setup:
	@echo "Setting up environment..."
	@command -v uv >/dev/null 2>&1 || (echo "Installing uv..." && curl -LsSf https://astral.sh/uv/install.sh | sh)
	@uv venv
	@uv pip install -r requirements.txt
	@echo "✅ Setup complete"
	@echo ""
	@echo "To use the environment:"
	@echo "  • make chrome (uses .venv automatically)"
	@echo "  • OR activate manually: source .venv/bin/activate"

# Launch Chrome (what you run 90% of the time)
# Usage: make chrome
#        make chrome PROFILE="Profile 3"
#        make chrome PROFILE="Profile 3" PORT=9223
#        make chrome ARGS="--list-profiles"
chrome: .venv
	@if [ ! -z "$(ARGS)" ]; then \
		.venv/bin/python chrome_launcher.py $(ARGS); \
	else \
		.venv/bin/python chrome_launcher.py --restart --copy-profile --profile "$(or $(PROFILE),Profile 2)" --port $(or $(PORT),9222); \
	fi

# Fix Chrome when it's broken (no dependencies on anything)
chrome-reset:
	@bash reset_chrome.sh

# Test if debugging is working
test:
	@curl -s http://localhost:9222/json/version >/dev/null 2>&1 && \
		echo "✅ Chrome debugging is running on port 9222" || \
		echo "❌ Chrome debugging not detected. Run 'make chrome'"

# Clean everything and start fresh
clean: chrome-reset
	@rm -rf .venv
	@rm -rf __pycache__
	@echo "✅ Clean slate. Run 'make setup' to start fresh"

# Check that venv exists
.venv:
	@echo "❌ No virtual environment found. Run 'make setup' first"
	@exit 1