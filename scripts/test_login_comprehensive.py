#!/usr/bin/env python3
"""
Comprehensive LinkedIn login test
Verifies that cookies are loaded and account is signed in
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.scraper.linkedin_scraper import LinkedInScraper


async def test_login():
    """Test LinkedIn login with cookies"""
    
    print("=" * 70)
    print("Comprehensive LinkedIn Login Test")
    print("=" * 70)
    print()
    
    cookies_file = "cookies/linkedin_cookies_1_fixed.json"
    
    # Check if cookies file exists
    if not Path(cookies_file).exists():
        print(f"❌ Cookies file not found: {cookies_file}")
        print()
        print("Solution:")
        print("1. Export cookies from your browser")
        print("2. Save to: cookies/linkedin_cookies_1.json")
        print("3. Fix them using the command in COOKIES_GUIDE.md")
        return False
    
    print(f"✅ Cookies file found: {cookies_file}")
    print()
    
    print("=" * 70)
    print("Step 1: Initialize Scraper")
    print("=" * 70)
    print()
    
    try:
        scraper = LinkedInScraper(cookies_file=cookies_file)
        await scraper.start()
        print("✅ Scraper started")
        print()
    except Exception as e:
        print(f"❌ Failed to start scraper: {e}")
        return False
    
    print("=" * 70)
    print("Step 2: Verify Cookie Authentication")
    print("=" * 70)
    print()
    print("(Browser will open and navigate to LinkedIn feed)")
    print()
    
    try:
        if await scraper.verify_cookie_auth():
            print()
            print("✅ Authentication successful!")
            print()
        else:
            print()
            print("❌ Authentication failed!")
            print()
            print("Possible causes:")
            print("1. Cookies are expired")
            print("2. Cookies are invalid")
            print("3. LinkedIn blocked the session")
            print()
            await scraper.close()
            return False
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        await scraper.close()
        return False
    
    print("=" * 70)
    print("Step 3: Test Profile Access")
    print("=" * 70)
    print()
    
    profile_url = "https://www.linkedin.com/in/akshat-naugir-4509a9202"
    print(f"Testing profile access: {profile_url}")
    print()
    
    try:
        # Navigate to profile
        await scraper._page.goto(profile_url, wait_until="networkidle")
        await asyncio.sleep(2)
        
        current_url = scraper._page.url
        print(f"Current URL: {current_url}")
        print()
        
        # Check if we can see the "More" button
        print("Looking for 'More' button...")
        more_button = await scraper._page.query_selector('button[aria-label*="More"]')
        
        if more_button:
            print("✅ Found 'More' button!")
            print()
            print("This means:")
            print("- ✅ You're logged in")
            print("- ✅ Profile is accessible")
            print("- ✅ 'Save to PDF' will work")
            print()
        else:
            print("⚠️  'More' button not found")
            print()
            print("Trying alternative selector...")
            more_button = await scraper._page.query_selector('button:has-text("More")')
            
            if more_button:
                print("✅ Found 'More' button (alternative selector)!")
            else:
                print("❌ Could not find 'More' button")
                print()
                print("This might mean:")
                print("- You're not logged in")
                print("- LinkedIn changed the UI")
                print("- Profile is not accessible")
        
        print()
        print("=" * 70)
        print("Step 4: Test 'Save to PDF' Button")
        print("=" * 70)
        print()
        
        if more_button:
            print("Clicking 'More' button...")
            await more_button.click()
            await asyncio.sleep(1)
            
            # Look for "Save to PDF"
            save_pdf = await scraper._page.query_selector('button:has-text("Save to PDF")')
            
            if save_pdf:
                print("✅ Found 'Save to PDF' button!")
                print()
                print("=" * 70)
                print("✅ ALL TESTS PASSED!")
                print("=" * 70)
                print()
                print("Your setup is working correctly:")
                print("- ✅ Cookies are valid")
                print("- ✅ Account is logged in")
                print("- ✅ Profile is accessible")
                print("- ✅ 'More' button is visible")
                print("- ✅ 'Save to PDF' is available")
                print()
                print("You can now run the full scraper:")
                print("  python3 scripts/comprehensive_scraper.py")
                print()
            else:
                print("❌ 'Save to PDF' button not found")
                print()
                print("Possible causes:")
                print("1. Menu didn't open properly")
                print("2. LinkedIn changed the UI")
                print("3. Not fully logged in")
        
    except Exception as e:
        print(f"❌ Error accessing profile: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await scraper.close()
    
    return True


if __name__ == "__main__":
    print()
    asyncio.run(test_login())
    print()
