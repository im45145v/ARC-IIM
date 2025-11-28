#!/usr/bin/env python3
"""
Test PDF download with detailed debugging to see what's happening.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright


async def test_pdf_download_debug():
    """Test PDF download with full debugging."""
    
    test_profile = os.getenv("TEST_LINKEDIN_PROFILE", "https://www.linkedin.com/in/williamhgates/")
    cookies_file = "cookies/linkedin_cookies_1.json"
    
    print("=" * 70)
    print("PDF Download Test with Debugging")
    print("=" * 70)
    print(f"Profile: {test_profile}")
    print()
    
    if not os.path.exists(cookies_file):
        print(f"❌ Cookies file not found: {cookies_file}")
        return False
    
    try:
        # Start Playwright
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,  # Show browser so we can see what's happening
            slow_mo=500,     # Slow down so we can see
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            accept_downloads=True,  # CRITICAL: Enable downloads
        )
        
        # Load cookies
        import json
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        print(f"✅ Loaded {len(cookies)} cookies")
        
        page = await context.new_page()
        
        # Navigate to profile
        print(f"Navigating to: {test_profile}")
        await page.goto(test_profile, wait_until="networkidle")
        await asyncio.sleep(3)
        print("✅ Page loaded")
        print()
        
        # Take screenshot
        await page.screenshot(path="before_click.png")
        print("📸 Screenshot saved: before_click.png")
        print()
        
        # Look for More button
        print("Looking for 'More' button...")
        print()
        
        # Try to find it
        more_button = await page.query_selector('button[aria-label="More actions"]')
        if not more_button:
            print("❌ 'More actions' button not found")
            print("Trying alternative selectors...")
            
            # Try other selectors
            alt_selectors = [
                'button:has-text("More")',
                'button[aria-label*="More"]',
                '.pvs-profile-actions button',
            ]
            
            for selector in alt_selectors:
                more_button = await page.query_selector(selector)
                if more_button:
                    print(f"✅ Found with: {selector}")
                    break
        else:
            print("✅ Found 'More actions' button")
        
        if not more_button:
            print("❌ Could not find More button at all")
            await browser.close()
            return False
        
        print()
        print("Clicking 'More' button...")
        await more_button.click()
        await asyncio.sleep(2)
        print("✅ Clicked")
        print()
        
        # Take screenshot of menu
        await page.screenshot(path="after_more_click.png")
        print("📸 Screenshot saved: after_more_click.png")
        print()
        
        # Now set up download listener and click "Save to PDF"
        print("Setting up download listener...")
        print("Clicking 'Save to PDF'...")
        print()
        
        try:
            # Set up download listener BEFORE clicking
            async with page.expect_download(timeout=30000) as download_info:
                # Click "Save to PDF"
                await page.locator('text=Save to PDF').click()
                print("✅ Clicked 'Save to PDF'")
            
            # Wait for download
            download = await download_info.value
            print(f"✅ Download started: {download.suggested_filename}")
            
            # Get download path
            download_path = await download.path()
            print(f"✅ Download path: {download_path}")
            
            # Read the PDF
            with open(download_path, 'rb') as f:
                pdf_bytes = f.read()
            
            # Save it
            output_file = "linkedin_profile_real.pdf"
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
            print("Open it to verify the clean layout and formatting.")
            
            await browser.close()
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            await page.screenshot(path="error_state.png")
            print("📸 Error screenshot saved: error_state.png")
            await browser.close()
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_pdf_download_debug())
    sys.exit(0 if success else 1)
