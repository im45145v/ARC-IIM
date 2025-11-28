#!/usr/bin/env python3
"""
Record the exact PDF download process
Opens browser, you do it manually, I record everything
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright


async def record_pdf_process():
    """Record the manual PDF download process"""
    
    print("=" * 70)
    print("Recording LinkedIn PDF Download Process")
    print("=" * 70)
    print()
    
    cookies_file = "cookies/linkedin_cookies_1_fixed.json"
    your_profile = "https://www.linkedin.com/in/im45145v"
    
    if not Path(cookies_file).exists():
        print(f"❌ Cookies file not found: {cookies_file}")
        return
    
    print("This script will:")
    print("1. Open browser with your cookies")
    print("2. Navigate to your profile")
    print("3. You click 'More' → 'Save to PDF' manually")
    print("4. I'll record the exact elements and process")
    print("5. Update the scraper to automate it")
    print()
    
    input("Press Enter to start...")
    print()
    
    # Start Playwright
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False, slow_mo=500)
    
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    )
    
    # Load cookies
    print("Loading cookies...")
    import json
    with open(cookies_file) as f:
        cookies = json.load(f)
    await context.add_cookies(cookies)
    print(f"✅ Loaded {len(cookies)} cookies")
    print()
    
    page = await context.new_page()
    
    # Navigate to profile
    print(f"Navigating to: {your_profile}")
    await page.goto(your_profile, wait_until="networkidle")
    await asyncio.sleep(2)
    
    print("✅ Profile loaded")
    print()
    print("=" * 70)
    print("NOW DO THE MANUAL PROCESS")
    print("=" * 70)
    print()
    print("Please do these steps in the browser:")
    print("1. Click the 'More' button (three dots)")
    print("2. Click 'Save to PDF'")
    print("3. Wait for the PDF to download/open")
    print()
    print("I'll keep the browser open so you can do this.")
    print("Press Enter here AFTER you've clicked 'Save to PDF'")
    print()
    
    input("Press Enter after clicking 'Save to PDF'...")
    print()
    
    print("✅ Process completed!")
    print()
    print("Now let me inspect the page...")
    print()
    
    # Try to find what elements exist
    print("Analyzing page elements...")
    print()
    
    # Check for More button
    more_selectors = [
        'button[aria-label*="More"]',
        'button:has-text("More")',
        'button[aria-label="More actions"]',
        '.artdeco-dropdown__trigger',
    ]
    
    print("Looking for 'More' button selectors:")
    for selector in more_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                is_visible = await element.is_visible()
                print(f"  ✅ Found: {selector} (visible: {is_visible})")
        except:
            print(f"  ❌ Not found: {selector}")
    
    print()
    print("Keeping browser open for 60 seconds...")
    print("You can inspect the page and see what worked")
    print()
    
    await asyncio.sleep(60)
    
    await browser.close()
    await playwright.stop()
    
    print("✅ Browser closed")
    print()
    print("Based on what you did, I'll now update the scraper")
    print("to automate the exact same process.")


if __name__ == "__main__":
    print()
    asyncio.run(record_pdf_process())
    print()
