#!/usr/bin/env python3
"""
Diagnostic script to find the correct selectors for PDF download.
This will show us what buttons and elements are actually on the page.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.scraper.linkedin_scraper import LinkedInScraper


async def diagnose_buttons():
    """Diagnose and find the correct button selectors."""
    
    test_profile = os.getenv("TEST_LINKEDIN_PROFILE", "https://www.linkedin.com/in/williamhgates/")
    cookies_file = "cookies/linkedin_cookies_1.json"
    
    print("=" * 70)
    print("PDF Button Diagnostic Tool")
    print("=" * 70)
    print(f"Profile: {test_profile}")
    print()
    
    if not os.path.exists(cookies_file):
        print(f"❌ Cookies file not found: {cookies_file}")
        return False
    
    try:
        async with LinkedInScraper(cookies_file=cookies_file) as scraper:
            # Authenticate
            if not await scraper.verify_cookie_auth():
                print("❌ Authentication failed")
                return False
            
            print("✅ Authenticated")
            print()
            
            # Navigate to profile
            print(f"Navigating to: {test_profile}")
            await scraper._page.goto(test_profile, wait_until="networkidle")
            await asyncio.sleep(3)
            print("✅ Page loaded")
            print()
            
            # Take a screenshot for reference
            await scraper._page.screenshot(path="profile_page_screenshot.png")
            print("📸 Screenshot saved: profile_page_screenshot.png")
            print()
            
            # Search for all buttons on the page
            print("=" * 70)
            print("SEARCHING FOR BUTTONS...")
            print("=" * 70)
            print()
            
            # Method 1: Find all buttons
            print("1. All <button> elements:")
            print("-" * 70)
            buttons = await scraper._page.query_selector_all('button')
            print(f"Found {len(buttons)} button elements")
            
            for i, button in enumerate(buttons[:20]):  # Show first 20
                try:
                    aria_label = await button.get_attribute('aria-label')
                    text = await button.inner_text()
                    class_name = await button.get_attribute('class')
                    
                    if aria_label or text:
                        print(f"\nButton {i+1}:")
                        if aria_label:
                            print(f"  aria-label: {aria_label}")
                        if text and text.strip():
                            print(f"  text: {text.strip()[:50]}")
                        if class_name:
                            print(f"  class: {class_name[:80]}")
                except:
                    pass
            
            print()
            print("=" * 70)
            print("SEARCHING FOR 'MORE' BUTTON...")
            print("=" * 70)
            print()
            
            # Try different selectors for "More" button
            more_selectors = [
                ('button[aria-label*="More"]', 'aria-label contains "More"'),
                ('button:has-text("More")', 'button with text "More"'),
                ('button[aria-label="More actions"]', 'aria-label = "More actions"'),
                ('button.artdeco-dropdown__trigger', 'artdeco dropdown trigger'),
                ('button[id*="ember"]', 'button with ember ID'),
                ('button.pvs-profile-actions__action', 'profile actions button'),
                ('.pvs-profile-actions button', 'button in profile actions'),
            ]
            
            for selector, description in more_selectors:
                try:
                    element = await scraper._page.query_selector(selector)
                    if element:
                        aria_label = await element.get_attribute('aria-label')
                        text = await element.inner_text()
                        print(f"✅ FOUND with selector: {selector}")
                        print(f"   Description: {description}")
                        if aria_label:
                            print(f"   aria-label: {aria_label}")
                        if text:
                            print(f"   text: {text.strip()}")
                        print()
                except Exception as e:
                    print(f"❌ Failed: {selector} - {e}")
            
            print()
            print("=" * 70)
            print("SEARCHING FOR DROPDOWN MENUS...")
            print("=" * 70)
            print()
            
            # Look for dropdown triggers
            dropdowns = await scraper._page.query_selector_all('[class*="dropdown"]')
            print(f"Found {len(dropdowns)} dropdown-related elements")
            
            for i, dropdown in enumerate(dropdowns[:10]):
                try:
                    html = await dropdown.evaluate('el => el.outerHTML')
                    print(f"\nDropdown {i+1}:")
                    print(html[:200])
                except:
                    pass
            
            print()
            print("=" * 70)
            print("SEARCHING FOR PROFILE ACTIONS...")
            print("=" * 70)
            print()
            
            # Look for profile action buttons
            action_selectors = [
                '.pvs-profile-actions',
                '[class*="profile-actions"]',
                '.pv-top-card-v2-ctas',
                '[class*="top-card"]',
            ]
            
            for selector in action_selectors:
                try:
                    element = await scraper._page.query_selector(selector)
                    if element:
                        html = await element.evaluate('el => el.outerHTML')
                        print(f"✅ Found: {selector}")
                        print(html[:300])
                        print()
                except:
                    pass
            
            print()
            print("=" * 70)
            print("GETTING PAGE HTML STRUCTURE...")
            print("=" * 70)
            print()
            
            # Save the page HTML for manual inspection
            html_content = await scraper._page.content()
            with open("profile_page_structure.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print("✅ Full HTML saved to: profile_page_structure.html")
            print()
            print("You can open this file to manually search for:")
            print("  - 'More' button")
            print("  - 'Save to PDF' option")
            print("  - Dropdown menus")
            print()
            
            # Try to find any element with "PDF" in it
            print("=" * 70)
            print("SEARCHING FOR 'PDF' TEXT...")
            print("=" * 70)
            print()
            
            pdf_elements = await scraper._page.query_selector_all('text=/PDF/i')
            print(f"Found {len(pdf_elements)} elements containing 'PDF'")
            
            for i, elem in enumerate(pdf_elements[:5]):
                try:
                    text = await elem.inner_text()
                    html = await elem.evaluate('el => el.outerHTML')
                    print(f"\nPDF Element {i+1}:")
                    print(f"  Text: {text}")
                    print(f"  HTML: {html[:150]}")
                except:
                    pass
            
            print()
            print("=" * 70)
            print("DIAGNOSTIC COMPLETE")
            print("=" * 70)
            print()
            print("Files created:")
            print("  1. profile_page_screenshot.png - Visual reference")
            print("  2. profile_page_structure.html - Full HTML for inspection")
            print()
            print("Next steps:")
            print("  1. Open the screenshot to see the page visually")
            print("  2. Open the HTML file and search for 'More' or 'PDF'")
            print("  3. Find the correct selectors")
            print("  4. Update the scraper code with correct selectors")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(diagnose_buttons())
    sys.exit(0 if success else 1)
