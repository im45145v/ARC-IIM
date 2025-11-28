#!/usr/bin/env python3
"""
Interactive script to watch the PDF download process step by step.
The browser will be visible and pause at each step so you can see what's happening.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright


async def watch_pdf_download():
    """Watch the PDF download process interactively."""
    
    test_profile = os.getenv("TEST_LINKEDIN_PROFILE", "https://www.linkedin.com/in/williamhgates/")
    cookies_file = "cookies/linkedin_cookies_1.json"
    
    print("=" * 70)
    print("INTERACTIVE PDF DOWNLOAD WATCHER")
    print("=" * 70)
    print()
    print("This script will:")
    print("  • Open a visible browser window")
    print("  • Navigate to the LinkedIn profile")
    print("  • Pause at each step so you can observe")
    print("  • Show you exactly what the automation is doing")
    print()
    print(f"Profile: {test_profile}")
    print()
    
    if not os.path.exists(cookies_file):
        print(f"❌ Cookies file not found: {cookies_file}")
        return False
    
    input("Press ENTER to start...")
    print()
    
    try:
        # Start Playwright with visible browser
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,  # Show browser
            slow_mo=1000,    # Slow down by 1 second per action
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            accept_downloads=True,
        )
        
        # Load cookies
        import json
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        print(f"✅ Loaded {len(cookies)} cookies")
        print()
        
        page = await context.new_page()
        
        # Step 1: Navigate
        print("STEP 1: Navigating to profile...")
        print(f"URL: {test_profile}")
        input("Press ENTER to navigate...")
        
        await page.goto(test_profile, wait_until="networkidle")
        await asyncio.sleep(3)
        
        print("✅ Page loaded")
        print()
        input("Press ENTER to continue...")
        print()
        
        # Step 2: Find More button
        print("STEP 2: Looking for 'More actions' button...")
        print("Watch the browser - the button should be highlighted")
        input("Press ENTER to search...")
        
        more_button = await page.query_selector('button[aria-label="More actions"]')
        
        if not more_button:
            print("❌ Button not found with first selector")
            print("Trying alternative selectors...")
            
            alt_selectors = [
                'button.artdeco-dropdown__trigger:has-text("More")',
                'button[id*="profile-overflow-action"]',
            ]
            
            for selector in alt_selectors:
                more_button = await page.query_selector(selector)
                if more_button:
                    print(f"✅ Found with: {selector}")
                    break
        else:
            print("✅ Found 'More actions' button")
        
        if not more_button:
            print("❌ Could not find More button")
            await browser.close()
            return False
        
        # Highlight the button
        await more_button.evaluate("el => el.style.border = '3px solid red'")
        print()
        print("👀 The 'More' button should now have a RED BORDER")
        print()
        input("Press ENTER to click it...")
        
        # Step 3: Click More button
        print()
        print("STEP 3: Clicking 'More' button...")
        await more_button.click()
        await asyncio.sleep(2)
        print("✅ Clicked - menu should be open now")
        print()
        input("Press ENTER to continue...")
        print()
        
        # Step 4: Find Save to PDF
        print("STEP 4: Looking for 'Save to PDF' option...")
        input("Press ENTER to search...")
        
        save_pdf = await page.query_selector('div[aria-label="Save to PDF"][role="button"]')
        
        if not save_pdf:
            print("❌ Not found with first selector")
            print("Trying alternatives...")
            
            alt_selectors = [
                'div[aria-label="Save to PDF"]',
                '[aria-label="Save to PDF"]',
            ]
            
            for selector in alt_selectors:
                save_pdf = await page.query_selector(selector)
                if save_pdf:
                    print(f"✅ Found with: {selector}")
                    break
        else:
            print("✅ Found 'Save to PDF' option")
        
        if not save_pdf:
            print("❌ Could not find Save to PDF")
            await browser.close()
            return False
        
        # Highlight it
        await save_pdf.evaluate("el => el.style.border = '3px solid green'")
        print()
        print("👀 The 'Save to PDF' option should now have a GREEN BORDER")
        print()
        input("Press ENTER to click it and start download...")
        
        # Step 5: Click and capture download
        print()
        print("STEP 5: Clicking 'Save to PDF' and capturing download...")
        print("Setting up download listener...")
        
        try:
            async with page.expect_download(timeout=30000) as download_info:
                await save_pdf.click()
                print("✅ Clicked 'Save to PDF'")
                print("Waiting for download to start...")
            
            download = await download_info.value
            print(f"✅ Download started: {download.suggested_filename}")
            
            download_path = await download.path()
            print(f"✅ Download path: {download_path}")
            
            # Read the PDF
            with open(download_path, 'rb') as f:
                pdf_bytes = f.read()
            
            # Save it
            output_file = "linkedin_profile_watched.pdf"
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            
            print()
            print("=" * 70)
            print("✅ SUCCESS!")
            print("=" * 70)
            print(f"PDF Size: {len(pdf_bytes):,} bytes")
            print(f"Saved to: {output_file}")
            print()
            print("This is LinkedIn's professionally formatted PDF!")
            print()
            
            input("Press ENTER to close browser...")
            await browser.close()
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            print()
            print("This might mean:")
            print("  • LinkedIn's UI changed")
            print("  • Download was blocked")
            print("  • Network issue")
            print()
            input("Press ENTER to close browser...")
            await browser.close()
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(watch_pdf_download())
    sys.exit(0 if success else 1)
