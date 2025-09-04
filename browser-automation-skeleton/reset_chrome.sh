#!/bin/bash
# Chrome Reset - Fixes all Chrome issues

echo "🔧 Resetting Chrome..."

# Step 1: Kill all Chrome processes
echo "→ Killing Chrome processes..."
pkill -f "Google Chrome" 2>/dev/null
pkill -f "chrome" 2>/dev/null
killall "Google Chrome" 2>/dev/null
sleep 1

# Step 2: Check for zombie processes
ZOMBIES=$(ps aux | grep "Google Chrome" | grep -E "\s+UE\s+" | awk '{print $2}')
if [ ! -z "$ZOMBIES" ]; then
    echo "⚠️  Found stuck Chrome processes (zombies): $ZOMBIES"
    echo "   These require a reboot to clear, but we'll work around them..."
    for pid in $ZOMBIES; do
        sudo kill -9 $pid 2>/dev/null || true
    done
fi

# Step 3: Free debug ports
echo "→ Freeing debug ports..."
for port in 9222 9223 9224 9225; do
    lsof -ti:$port 2>/dev/null | xargs kill -9 2>/dev/null || true
done

# Step 4: Remove ALL lock files
echo "→ Removing lock files..."
CHROME_DIR=~/Library/Application\ Support/Google/Chrome

# Main directory locks
find "$CHROME_DIR" -maxdepth 1 \( -name "Singleton*" -o -name "lockfile" -o -name ".org.chromium*" \) -delete 2>/dev/null

# Profile locks (all profiles)
find "$CHROME_DIR" -mindepth 2 \( -name "Singleton*" -o -name "lockfile" \) -delete 2>/dev/null

# Step 5: Clean temp directories
echo "→ Cleaning temp files..."
rm -rf /tmp/chrome_debug_* 2>/dev/null
rm -rf /tmp/.org.chromium* 2>/dev/null
rm -rf /var/folders/*/*/*/*chrome* 2>/dev/null

# Step 6: If .venv exists, use Python reset too
if [ -f ".venv/bin/python" ]; then
    echo "→ Running Python reset..."
    .venv/bin/python chrome_launcher.py --reset 2>/dev/null || true
fi

# Final check
echo ""
REMAINING=$(ps aux | grep "Google Chrome" | grep -v grep | wc -l)
if [ $REMAINING -gt 0 ]; then
    echo "⚠️  Warning: $REMAINING Chrome process(es) still running"
    echo "   If Chrome still won't open:"
    echo "   1. Try: sudo killall -9 'Google Chrome'"
    echo "   2. Or reboot your Mac"
else
    echo "✅ Chrome reset complete"
fi

echo ""
echo "Next steps:"
echo "  1. Open Chrome normally from Applications"
echo "  2. If it works, run: make chrome"
echo "  3. If not, reboot your Mac (kernel issue)"