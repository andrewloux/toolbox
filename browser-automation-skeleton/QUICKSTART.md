# Quick Start

## First Time
```bash
make setup
make chrome
```

## Daily Use
```bash
make chrome  # Launch Chrome with debugging
make test    # Check if it's running
```

## When Chrome is Fucked

If you see "The application Google Chrome.app is not open anymore":

```bash
make chrome-reset     # or ./fix_chrome.sh
```

Then try opening Chrome normally from Applications. If it works, run `make chrome` again.

## Still Broken?
```bash
make clean   # Nuclear option - wipes everything
make setup   # Start fresh
make chrome  # Try again
```

## The Actual Workflow

1. **Morning**: `make chrome` - Launch Chrome for debugging
2. **Chrome crashes/hangs**: `make fix` - Reset everything  
3. **Run automation**: Do your actual work
4. **Chrome fucks up again**: `make fix`
5. **Repeat**

## Common Issues

**"No such file or directory: .venv/bin/python"**
→ Run `make setup` first

**"Chrome not detected on port 9222"**  
→ Chrome didn't launch properly. Run `make fix` then `make chrome`

**"Permission denied"**
→ Run `chmod +x fix_chrome.sh`

**Everything is fucked**
→ `make clean && make setup`