#!/usr/bin/env python3
"""
Manual LinkedIn login with Playwright
1. Opens browser
2. You login manually
3. Saves cookies automatically
4. Tests with your profile
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright


async def manual_login_and_save():
    """Open browser, let user login, save cookies"""
    
    print("=" * 70)
    print("Manual LinkedIn Login & Cookie Saver")
    print("=" * 70)
    print()
    
    print("This script will:")
    print("1. Open a browser")
    print("2. Navigate to LinkedIn")
    print("3. Wait for YOU to login manually")
    print("4. Save cookies automatically")
    print("5. Test with your profile")
    print()
    
    input("Press Enter to start...")
    print()
    
    # Start Playwright
    print("Starting Playwright browser...")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    )
    
    page = await context.new_page()
    
    print("✅ Browser opened")
    print()
    
    # Navigate to LinkedIn
    print("Navigating to LinkedIn...")
    await page.goto("https://www.linkedin.com/login")
    
    print("✅ LinkedIn login page loaded")
    print()
    print("=" * 70)
    print("MANUAL LOGIN REQUIRED")
    print("=" * 70)
    print()
    print("Please:")
    print("1. Enter your LinkedIn email")
    print("2. Enter your password")
    print("3. Complete any 2FA if needed")
    print("4. Wait until you see your LinkedIn feed")
    print("5. Then press Enter here to save cookies")
    print()
    
    input("Press Enter after you've logged in...")
    print()
    
    # Check if logged in
    current_url = page.url
    print(f"Current URL: {current_url}")
    print()
    
    if "login" in current_url or "checkpoint" in current_url:
        print("⚠️  Still on login page. Make sure you're fully logged in!")
        input("Press Enter after logging in...")
    
    # Save cookies
    print("Saving cookies...")
    cookies = await context.cookies()
    
    # Fix sameSite attribute
    for cookie in cookies:
        if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
            cookie['sameSite'] = 'Lax'
    
    # Save to file
    cookies_file = Path("cookies/linkedin_cookies_1.json")
    cookies_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(cookies_file, 'w') as f:
        json.dump(cookies, f, indent=2)
    
    print(f"✅ Saved {len(cookies)} cookies to: {cookies_file}")
    print()
    
    # Also save fixed version
    fixed_file = Path("cookies/linkedin_cookies_1_fixed.json")
    with open(fixed_file, 'w') as f:
        json.dump(cookies, f, indent=2)
    
    print(f"✅ Saved fixed version to: {fixed_file}")
    print()
    
    # Test with your profile
    print("=" * 70)
    print("Testing with your profile")
    print("=" * 70)
    print()
    
    your_profile = "https://www.linkedin.com/in/im45145v"
    print(f"Navigating to: {your_profile}")
    
    await page.goto(your_profile, wait_until="networkidle")
    await asyncio.sleep(2)
    
    print("✅ Profile loaded")
    print()
    
    # Check for "More" button
    print("Looking for 'More' button...")
    more_button = await page.query_selector('button[aria-label*="More"]')
    
    if not more_button:
        more_button = await page.query_selector('button:has-text("More")')
    
    if more_button:
        print("✅ Found 'More' button!")
        print()
        print("Clicking 'More' button...")
        await more_button.click()
        await asyncio.sleep(1)
        
        # Look for "Save to PDF"
        save_pdf = await page.query_selector('button:has-text("Save to PDF")')
        
        if save_pdf:
            print("✅ Found 'Save to PDF' button!")
            print()
            print("=" * 70)
            print("✅ SUCCESS!")
            print("=" * 70)
            print()
            print("Your cookies are saved and working!")
            print()
            print("Next steps:")
            print("1. Close this browser window")
            print("2. Run the scraper: python3 scripts/comprehensive_scraper.py")
            print()
        else:
            print("❌ 'Save to PDF' button not found")
            print()
            print("Trying to find it manually...")
            await asyncio.sleep(2)
    else:
        print("❌ 'More' button not found")
        print()
        print("You might not be logged in properly")
    
    print()
    print("=" * 70)
    print("NOW DO THE MANUAL PROCESS")
    print("=" * 70)
    print()
    print("Please perform these steps in the browser:")
    print("1. Click the 'More' button (three dots)")
    print("2. Click 'Save to PDF'")
    print("3. Watch the PDF download process")
    print("4. Press Enter here when done")
    print()
    
    input("Press Enter after clicking 'More' and 'Save to PDF'...")
    print()
    
    print("✅ Process observed!")
    print()
    print("Keeping browser open for inspection...")
    print("You can see the page and verify everything worked")
    print()
    
    input("Press Enter to close browser and save cookies...")
    print()
    
    # Close browser
    await browser.close()
    await playwright.stop()
    
    print("✅ Browser closed")
    print()
    print("=" * 70)
    print("✅ COOKIES SAVED!")
    print("=" * 70)
    print()
    print("Cookies saved to:")
    print(f"  - {cookies_file}")
    print(f"  - {fixed_file}")
    print()
    print("Now I understand the process!")
    print()
    print("Next steps:")
    print("1. Run: python3 scripts/test_with_your_profile.py")
    print("2. This will automate the 'More' → 'Save to PDF' process")
    print("3. Then run: python3 scripts/comprehensive_scraper.py")
    print()


if __name__ == "__main__":
    print()
    asyncio.run(manual_login_and_save())
    print()
