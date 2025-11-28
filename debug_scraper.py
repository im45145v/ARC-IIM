#!/usr/bin/env python3
"""
Debug script to see what's on the LinkedIn page
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from alumni_system.scraper.linkedin_scraper import LinkedInScraper


async def debug_profile():
    """Debug what we can see on the profile page"""
    
    linkedin_url = "https://www.linkedin.com/in/akshat-naugir-4509a9202"
    cookies_file = "cookies/linkedin_cookies_1_fixed.json"
    
    print("🔍 Debugging LinkedIn Profile Scraper")
    print(f"URL: {linkedin_url}")
    print()
    
    async with LinkedInScraper(cookies_file=cookies_file) as scraper:
        # Verify auth
        if not await scraper.verify_cookie_auth():
            print("❌ Authentication failed!")
            return
        
        print("✅ Authenticated")
        print()
        
        # Navigate to profile
        await scraper._page.goto(linkedin_url)
        await scraper._page.wait_for_load_state("networkidle")
        
        print("📄 Page loaded")
        print()
        
        # Try to find the name with different selectors
        print("🔍 Looking for name...")
        name_selectors = [
            'h1.text-heading-xlarge',
            'h1',
            '[class*="text-heading"]',
            '[class*="profile"]  h1',
        ]
        
        for selector in name_selectors:
            try:
                element = await scraper._page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    print(f"   ✅ Found with '{selector}': {text}")
                    break
            except:
                pass
        
        # Try to find headline
        print()
        print("🔍 Looking for headline...")
        headline_selectors = [
            'div.text-body-medium',
            '[class*="headline"]',
            '[class*="text-body"]',
            'div.mt2',
        ]
        
        for selector in headline_selectors:
            try:
                element = await scraper._page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if text and len(text) > 5:  # Skip empty or very short text
                        print(f"   ✅ Found with '{selector}': {text[:100]}")
                        break
            except:
                pass
        
        # Save page HTML for inspection
        print()
        print("💾 Saving page HTML...")
        html = await scraper._page.content()
        with open("linkedin_page_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("   Saved to: linkedin_page_debug.html")
        
        # Take a screenshot
        print()
        print("📸 Taking screenshot...")
        await scraper._page.screenshot(path="linkedin_page_debug.png", full_page=True)
        print("   Saved to: linkedin_page_debug.png")
        
        print()
        print("✨ Debug complete!")
        print()
        print("Check these files:")
        print("  - linkedin_page_debug.html (full page HTML)")
        print("  - linkedin_page_debug.png (screenshot)")


if __name__ == "__main__":
    asyncio.run(debug_profile())
