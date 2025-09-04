# Browser Automation Skeleton

Chrome automation toolkit for web scraping and form filling. Battle-tested on Google Sheets and complex web apps.

## Core Scripts

### `real_chrome_session.py`
Launches Chrome with remote debugging for automation takeover.

```bash
# Basic launch
python real_chrome_session.py

# With specific profile
python real_chrome_session.py --profile "Profile 2"

# Kill existing & copy profile (safer)
python real_chrome_session.py --restart --copy-profile --profile "Profile 2"

# Custom port
python real_chrome_session.py --port 9223

# List available profiles
python real_chrome_session.py --list-profiles
```

### `universal_sheet_filler.py`
Universal Google Sheets automation - fills cells with complex formatting.
- Handles multi-line text with Alt+Enter
- Bullet points and formatting
- Works with any sheets structure

### CDP Scripts (Chrome DevTools Protocol)
- `cdp_insert_text.py` - First working CDP text insertion
- `fill_with_proper_breaks.py` - Advanced multi-line text filling  
- `clear_cells.py` - Clear sheets cells utility

## Setup

```bash
pip install zendriver requests
```

## Key Discoveries

### What Works
- **zendriver** library (not selenium/playwright)
- CDP's `input_.insert_text()` for text entry
- F2 to enter edit mode in sheets
- Tab to save and move cells

### What Doesn't Work
- JavaScript DOM manipulation (`element.value = "text"`)
- Regular keyboard events with characters
- nodriver library (unreliable)

## Usage Pattern

1. Launch Chrome with debugging:
```bash
python real_chrome_session.py --restart --copy-profile --profile "Profile 2"
```

2. In another terminal, run your automation:
```python
import asyncio
import zendriver as zd

async def main():
    browser = await zd.Browser.create(
        host="127.0.0.1",
        port=9222,
        headless=False,
        sandbox=False
    )
    # Your automation here

asyncio.run(main())
```

## Google Sheets Specific

```python
# Navigate to cell
await tab.evaluate(f'''
    const nb = document.querySelector('.waffle-name-box');
    if (nb) {{
        nb.focus();
        nb.value = 'C2';
    }}
''')

# Enter edit mode
await tab.send(input_.dispatch_key_event(
    type_="keyDown",
    key="F2",
    code="F2", 
    windows_virtual_key_code=113
))

# Insert text
import zendriver.cdp.input_ as input_
await tab.send(input_.insert_text(text="Your text here"))

# Save with Tab
await tab.send(input_.dispatch_key_event(
    type_="keyDown",
    key="Tab",
    code="Tab",
    windows_virtual_key_code=9
))