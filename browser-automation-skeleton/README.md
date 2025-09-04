# Browser Automation Skeleton

Launch Chrome with debugging enabled for browser automation (Selenium, Puppeteer, zendriver, etc).

## Quick Start

```bash
make setup        # First time only
make chrome       # Launch Chrome with debugging
```

## Common Tasks

```bash
make chrome                                  # Launch Chrome (default: Profile 2, port 9222)
make chrome PROFILE="Work"                  # Different profile
make chrome PORT=9223                        # Different port
make chrome-reset                            # Fix when Chrome won't open
make test                                    # Check if Chrome debugging is running
```

## When Chrome is Broken

**"The application Google Chrome.app is not open anymore"** or Chrome won't launch:

```bash
make chrome-reset  # or ./reset_chrome.sh
```

Then try opening Chrome from Applications. If it works, run `make chrome` again.

Still broken? → `make clean && make setup`

## Manual Usage (without Make)

```bash
# Setup
uv venv
uv pip install -r requirements.txt
source .venv/bin/activate

# Launch Chrome
python chrome_launcher.py --restart --copy-profile --profile "Profile 2"

# See all options
python chrome_launcher.py --help
```

## How It Works

1. **chrome_launcher.py** - Launches Chrome with `--remote-debugging-port` flag
2. Chrome becomes controllable via Chrome DevTools Protocol (CDP) on port 9222
3. Your automation tool connects to `http://localhost:9222` to control Chrome

## Files

- `chrome_launcher.py` - Main Chrome launcher script
- `reset_chrome.sh` - Fixes Chrome lock/zombie issues  
- `Makefile` - Simple commands for common tasks
- `examples/google_sheets_automation/` - Example automation for Google Sheets

## Examples

See [examples/google_sheets_automation/](examples/google_sheets_automation/) for a complete Google Sheets automation example using zendriver.