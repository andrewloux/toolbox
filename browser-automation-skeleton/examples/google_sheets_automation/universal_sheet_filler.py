#!/usr/bin/env python3
"""
Universal Google Sheets filler - configurable with different answer files
"""
import asyncio
import json
import sys
import os
import zendriver as zd
import zendriver.cdp as cdp
import zendriver.cdp.input_ as input_
from zendriver.cdp.input_ import MouseButton

def load_answers_from_file(filepath):
    """Load answers from a JSON or Python file"""
    if not os.path.exists(filepath):
        print(f"❌ Error: File {filepath} does not exist")
        return None
    
    if filepath.endswith('.json'):
        with open(filepath, 'r') as f:
            return json.load(f)
    elif filepath.endswith('.py'):
        # Import the Python file and get EXPECTED_ANSWERS
        import importlib.util
        spec = importlib.util.spec_from_file_location("answers", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.EXPECTED_ANSWERS
    else:
        # Try to read as text file with format: CELL:ANSWER per line
        answers = {}
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    cell, answer = line.split(':', 1)
                    answers[cell.strip()] = answer.strip()
        return answers if answers else None

async def get_cell_content(tab, cell_address):
    """Get current content of a cell"""
    # Navigate to cell
    await tab.evaluate(f"""
        (() => {{
            const nb = document.querySelector('.waffle-name-box');
            if (nb) {{
                nb.focus();
                nb.value = '{cell_address}';
            }}
        }})()
    """)
    await asyncio.sleep(0.3)
    
    # Press Enter to navigate
    await tab.send(input_.dispatch_key_event(
        type_="keyDown",
        key="Enter",
        code="Enter",
        windows_virtual_key_code=13
    ))
    await tab.send(input_.dispatch_key_event(
        type_="keyUp",
        key="Enter",
        code="Enter",
        windows_virtual_key_code=13
    ))
    await asyncio.sleep(0.5)
    
    # Try to get cell content - handle potential tuple return
    content = await tab.evaluate("""
        (() => {
            const activeCell = document.querySelector('.cell-input');
            return activeCell ? activeCell.textContent : '';
        })()
    """)
    
    # Handle tuple or string return
    if isinstance(content, tuple):
        content = content[0] if len(content) > 0 else ""
    
    return content.strip() if content else ""

async def update_cell(tab, cell_address, content):
    """Update a cell with new content"""
    # Navigate to cell
    await tab.evaluate(f"""
        (() => {{
            const nb = document.querySelector('.waffle-name-box');
            if (nb) {{
                nb.focus();
                nb.value = '{cell_address}';
            }}
        }})()
    """)
    await asyncio.sleep(0.3)
    
    # Press Enter to navigate
    await tab.send(input_.dispatch_key_event(
        type_="keyDown",
        key="Enter",
        code="Enter",
        windows_virtual_key_code=13
    ))
    await tab.send(input_.dispatch_key_event(
        type_="keyUp",
        key="Enter",
        code="Enter",
        windows_virtual_key_code=13
    ))
    await asyncio.sleep(0.5)
    
    # First clear the cell content with Delete key (cell is already selected)
    await tab.send(input_.dispatch_key_event(
        type_="keyDown",
        key="Delete",
        code="Delete",
        windows_virtual_key_code=46
    ))
    await tab.send(input_.dispatch_key_event(
        type_="keyUp",
        key="Delete",
        code="Delete",
        windows_virtual_key_code=46
    ))
    await asyncio.sleep(0.3)
    
    # Now enter edit mode with F2 to type new content
    await tab.send(input_.dispatch_key_event(
        type_="keyDown",
        key="F2",
        code="F2",
        windows_virtual_key_code=113
    ))
    await tab.send(input_.dispatch_key_event(
        type_="keyUp",
        key="F2",
        code="F2",
        windows_virtual_key_code=113
    ))
    await asyncio.sleep(0.3)
    
    # Insert new text
    await tab.send(input_.insert_text(text=content))
    await asyncio.sleep(0.3)
    
    # Save with Tab
    await tab.send(input_.dispatch_key_event(
        type_="keyDown",
        key="Tab",
        code="Tab",
        windows_virtual_key_code=9
    ))
    await tab.send(input_.dispatch_key_event(
        type_="keyUp",
        key="Tab",
        code="Tab",
        windows_virtual_key_code=9
    ))
    await asyncio.sleep(0.5)

async def main(answers_file=None, check_only=False, force_update=False):
    """
    Main function
    Args:
        answers_file: Path to file containing answers
        check_only: If True, only check differences without updating
        force_update: If True, update all cells regardless of current content
    """
    # Get answers file from command line or use default
    if not answers_file:
        if len(sys.argv) > 1:
            answers_file = sys.argv[1]
        else:
            print("Usage: python universal_sheet_filler.py <answers_file> [--check-only] [--force]")
            print("\nExamples:")
            print("  python universal_sheet_filler.py technical_answers.json")
            print("  python universal_sheet_filler.py security_answers.txt")
            print("  python universal_sheet_filler.py answers_config.py")
            print("\nOptions:")
            print("  --check-only  Only show differences without updating")
            print("  --force       Update all cells even if content matches")
            return
    
    # Parse flags
    if '--check-only' in sys.argv:
        check_only = True
    if '--force' in sys.argv:
        force_update = True
    
    # Load answers
    expected_answers = load_answers_from_file(answers_file)
    if not expected_answers:
        print(f"❌ Could not load answers from {answers_file}")
        return
    
    print("=" * 80)
    print(f"GOOGLE SHEETS FILLER - {os.path.basename(answers_file)}")
    if check_only:
        print("MODE: CHECK ONLY (no updates will be made)")
    elif force_update:
        print("MODE: FORCE UPDATE (all cells will be updated)")
    else:
        print("MODE: SMART UPDATE (only different cells will be updated)")
    print("=" * 80)
    
    # Connect to Chrome
    browser = await zd.Browser.create(
        host="127.0.0.1",
        port=9222,
        headless=False,
        sandbox=False
    )
    
    # Find Google Sheets tab
    sheets_tab = None
    for tab in browser.tabs:
        try:
            url = await tab.evaluate("window.location.href")
            if "docs.google.com/spreadsheets" in url:
                sheets_tab = tab
                print("✅ Found Google Sheets tab")
                break
        except:
            continue
    
    if not sheets_tab:
        print("❌ No Google Sheets tab found")
        return
    
    await sheets_tab.activate()
    await asyncio.sleep(1)
    
    print(f"\n📋 Processing {len(expected_answers)} cells")
    print("-" * 80)
    
    updated_count = 0
    skipped_count = 0
    different_count = 0
    
    for cell_address, expected_content in expected_answers.items():
        print(f"\n🔍 Checking {cell_address}...")
        
        try:
            if not force_update:
                # Get current content
                current_content = await get_cell_content(sheets_tab, cell_address)
                
                # Compare (normalize whitespace for comparison)
                current_normalized = " ".join(current_content.split())
                expected_normalized = " ".join(expected_content.split())
                
                if current_normalized == expected_normalized:
                    print(f"✅ {cell_address} already has correct content - skipping")
                    skipped_count += 1
                    continue
                else:
                    different_count += 1
                    print(f"📝 {cell_address} needs update")
                    print(f"   Current: {current_content[:50]}..." if len(current_content) > 50 else f"   Current: {current_content}")
                    print(f"   Expected: {expected_content[:50]}..." if len(expected_content) > 50 else f"   Expected: {expected_content}")
                    
                    if check_only:
                        continue
            
            # Update the cell
            if not check_only:
                await update_cell(sheets_tab, cell_address, expected_content)
                print(f"✅ {cell_address} updated successfully")
                updated_count += 1
                
            await asyncio.sleep(0.3)
            
        except Exception as e:
            print(f"❌ Error processing {cell_address}: {e}")
            continue
    
    # Final summary
    print("\n" + "=" * 80)
    if check_only:
        print("📊 CHECK COMPLETE")
        print("=" * 80)
        print(f"🔍 Cells that need updates: {different_count}")
        print(f"✅ Cells already correct: {skipped_count}")
    else:
        print("📊 UPDATE COMPLETE")
        print("=" * 80)
        print(f"📝 Updated: {updated_count} cells")
        if not force_update:
            print(f"✅ Already correct: {skipped_count} cells")
        print(f"📋 Total processed: {updated_count + skipped_count}/{len(expected_answers)} cells")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())