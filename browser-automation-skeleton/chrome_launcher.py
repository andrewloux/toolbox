#!/usr/bin/env python3
"""
Chrome Launcher - Launch Chrome with remote debugging for browser automation.

Makes Chrome controllable via Chrome DevTools Protocol (CDP) for automation tools
like Selenium, Puppeteer, Playwright, or zendriver.
"""

import subprocess
import asyncio
import time
import os
import signal
import sys
import argparse
import shutil
import tempfile
import json

def list_chrome_profiles():
    """List all available Chrome profiles."""
    chrome_base = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    local_state_path = os.path.join(chrome_base, "Local State")
    
    if not os.path.exists(local_state_path):
        print(f"❌ Chrome Local State not found at {local_state_path}")
        return []
    
    try:
        with open(local_state_path, 'r') as f:
            local_state = json.load(f)
        
        profile_info = local_state.get('profile', {}).get('info_cache', {})
        
        print("\n📁 Available Chrome Profiles:")
        print("-" * 40)
        profiles = []
        for profile_dir, info in profile_info.items():
            name = info.get('name', 'Unknown')
            print(f"  • {profile_dir}: {name}")
            profiles.append(profile_dir)
        print("-" * 40)
        return profiles
    except Exception as e:
        print(f"❌ Error reading Chrome profiles: {e}")
        return []

def kill_existing_chrome(port=9222):
    """Kill any existing Chrome processes."""
    try:
        # Kill Chrome processes
        subprocess.run(['pkill', '-f', 'Google Chrome'], capture_output=True)
        time.sleep(1)
        
        # Also kill any process on the specified port
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"Killed process {pid} on port {port}")
                except:
                    pass
            time.sleep(1)
    except:
        pass

def reset_chrome_locks():
    """Remove all Chrome lock files from all profiles."""
    import glob
    
    chrome_base = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    
    print("🧹 Resetting Chrome state...")
    
    # Kill Chrome
    subprocess.run(['pkill', '-f', 'Google Chrome'], capture_output=True, stderr=subprocess.DEVNULL)
    time.sleep(1)
    
    # Core lock files
    LOCK_FILES = {'Singleton', 'SingletonLock', 'SingletonSocket', 'SingletonCookie', 'lockfile'}
    LOCK_PATTERNS = ['*.lock', '.org.chromium.Chromium.*', 'chrome_crashpad_handler']
    
    removed = 0
    
    # Clean Chrome base dir and all profiles
    for root, dirs, files in os.walk(chrome_base):
        # Skip deep traversal into non-profile dirs
        if root.count(os.sep) - chrome_base.count(os.sep) > 1:
            continue
            
        # Remove exact lock files
        for lock in LOCK_FILES:
            lock_path = os.path.join(root, lock)
            if os.path.exists(lock_path):
                try:
                    os.remove(lock_path)
                    removed += 1
                except:
                    pass
        
        # Remove pattern-matched files
        for pattern in LOCK_PATTERNS:
            for f in glob.glob(os.path.join(root, pattern)):
                try:
                    os.remove(f)
                    removed += 1
                except:
                    pass
    
    # Clean temp chrome dirs
    for temp_base in ['/tmp', '/var/folders']:
        pattern = os.path.join(temp_base, '**/chrome_debug_*')
        for temp_dir in glob.glob(pattern, recursive=True):
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    if removed:
        print(f"✅ Removed {removed} lock files")
    else:
        print("✅ No lock files found")
    print("Chrome state reset. You can launch Chrome normally.")

def copy_chrome_profile(profile_name):
    """Create a temporary copy of the Chrome profile."""
    chrome_base = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    source_profile = os.path.join(chrome_base, profile_name)
    
    if not os.path.exists(source_profile):
        print(f"❌ Profile '{profile_name}' not found at {source_profile}")
        sys.exit(1)
    
    # Create temporary directory for profile copy
    temp_dir = tempfile.mkdtemp(prefix="chrome_debug_")
    temp_profile = os.path.join(temp_dir, profile_name)
    
    print(f"Copying profile from {source_profile} to {temp_profile}...")
    
    # Copy the profile
    shutil.copytree(source_profile, temp_profile, dirs_exist_ok=True)
    
    # Remove Singleton files that prevent multiple instances
    singleton_files = ['Singleton', 'SingletonLock', 'SingletonSocket', 'SingletonCookie', 
                       'lockfile', '.org.chromium.Chromium.*']
    for singleton in singleton_files:
        if '*' in singleton:
            # Handle wildcards
            import glob
            for f in glob.glob(os.path.join(temp_profile, singleton)):
                os.remove(f)
                print(f"Removed {os.path.basename(f)}")
        else:
            singleton_path = os.path.join(temp_profile, singleton)
            if os.path.exists(singleton_path):
                os.remove(singleton_path)
                print(f"Removed {singleton}")
    
    # Also remove these from the Default subdirectory if it exists
    default_dir = os.path.join(temp_profile, 'Default')
    if os.path.exists(default_dir):
        for singleton in ['Singleton', 'SingletonLock', 'SingletonSocket', 'SingletonCookie']:
            singleton_path = os.path.join(default_dir, singleton)
            if os.path.exists(singleton_path):
                os.remove(singleton_path)
    
    print(f"✅ Profile copied to {temp_profile}")
    return temp_dir

def launch_chrome_with_debugging(profile_name="Profile 2", port=9222, use_copy=False, user_data_dir=None):
    """Launch Chrome with remote debugging enabled."""
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    cmd = [chrome_path]
    
    if use_copy and user_data_dir:
        # Use the copied profile
        cmd.extend([
            f'--user-data-dir={user_data_dir}',
            f'--profile-directory={profile_name}'
        ])
    else:
        # Use the original profile directly
        cmd.extend([
            f'--profile-directory={profile_name}'
        ])
    
    cmd.extend([
        f'--remote-debugging-port={port}',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-popup-blocking',
        '--disable-translate',
        '--disable-background-timer-throttling',
        '--disable-renderer-backgrounding',
        '--disable-device-discovery-notifications'
    ])
    
    print(f"Launching Chrome with debugging on port {port}...")
    print(f"Command: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for Chrome to start
    time.sleep(3)
    
    # Verify Chrome is running
    for i in range(10):
        try:
            import requests
            response = requests.get(f'http://localhost:{port}/json/version')
            if response.status_code == 200:
                version_info = response.json()
                print(f"✅ Chrome launched successfully")
                print(f"   Browser: {version_info.get('Browser', 'Unknown')}")
                return process
        except:
            time.sleep(1)
    
    print("⚠️ Chrome might not be fully ready, but continuing...")
    return process


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Launch Chrome with remote debugging for automation',
        epilog='''
Examples:
  %(prog)s --reset                                    # Fix Chrome lock issues
  %(prog)s --list-profiles                            # Show available profiles
  %(prog)s                                            # Launch with defaults (Profile 2, port 9222)
  %(prog)s --restart --copy-profile                   # Safe launch (recommended)
  %(prog)s --profile "Profile 3" --port 9223          # Custom profile and port
  %(prog)s --restart --copy-profile --profile "Work"  # Launch work profile safely
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--profile', default='Profile 2', help='Chrome profile to use (default: Profile 2)')
    parser.add_argument('--port', type=int, default=9222, help='Debug port to use (default: 9222)')
    parser.add_argument('--restart', action='store_true', help='Kill existing Chrome before starting')
    parser.add_argument('--copy-profile', action='store_true', help='Use a copy of the profile (safer)')
    parser.add_argument('--list-profiles', action='store_true', help='List available Chrome profiles')
    parser.add_argument('--reset', action='store_true', help='Reset Chrome state by removing all lock files')
    
    args = parser.parse_args()
    
    # Reset Chrome if requested
    if args.reset:
        reset_chrome_locks()
        sys.exit(0)
    
    # List profiles if requested
    if args.list_profiles:
        list_chrome_profiles()
        sys.exit(0)
    
    temp_dir = None
    chrome_process = None
    
    try:
        # Always kill existing Chrome when restarting or if something's on the specified port
        print(f"Checking for existing Chrome instances on port {args.port}...")
        kill_existing_chrome(port=args.port)
        
        # Copy profile if requested
        if args.copy_profile:
            temp_dir = copy_chrome_profile(args.profile)
            chrome_process = launch_chrome_with_debugging(
                profile_name=args.profile,
                port=args.port,
                use_copy=True,
                user_data_dir=temp_dir
            )
        else:
            chrome_process = launch_chrome_with_debugging(
                profile_name=args.profile,
                port=args.port
            )
        
        print(f"\n✅ Chrome launched with debugging enabled on port {args.port}!")
        print(f"   Profile: {args.profile}")
        print(f"   Connect with zendriver at: http://localhost:{args.port}")
        print("\nPress Ctrl+C to exit...")
        
        # Just keep Chrome running
        chrome_process.wait()
                
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if chrome_process:
            try:
                chrome_process.terminate()
                chrome_process.wait(timeout=2)
            except:
                try:
                    chrome_process.kill()
                except:
                    pass
            print("Chrome process terminated")
        
        if temp_dir and os.path.exists(temp_dir):
            try:
                print(f"Cleaning up temporary profile at {temp_dir}")
                shutil.rmtree(temp_dir, ignore_errors=True)
            except KeyboardInterrupt:
                print("Cleanup interrupted - temp files may remain")
                sys.exit(1)

if __name__ == '__main__':
    main()