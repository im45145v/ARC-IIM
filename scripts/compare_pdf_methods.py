#!/usr/bin/env python3
"""
Compare the old (page print) vs new (LinkedIn PDF) methods.
This script demonstrates the difference between the two approaches.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.scraper.linkedin_scraper import LinkedInScraper


async def compare_methods():
    """Compare old page print method vs new LinkedIn PDF capture."""
    
    test_profile = os.getenv("TEST_LINKEDIN_PROFILE", "https://www.linkedin.com/in/williamhgates/")
    cookies_file = "cookies/linkedin_cookies_1.json"
    
    print("=" * 70)
    print("PDF Method Comparison")
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
            print("Navigating to profile...")
            await scraper._page.goto(test_profile, wait_until="networkidle")
            await asyncio.sleep(2)
            print("✅ Profile loaded")
            print()
            
            # Method 1: Old way (page print)
            print("Method 1: Page Print (OLD)")
            print("-" * 70)
            print("This method just prints the current browser page to PDF")
            print("Result: Browser-rendered PDF with inconsistent formatting")
            print()
            
            pdf_old = await scraper._page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
            )
            
            with open("comparison_old_method.pdf", "wb") as f:
                f.write(pdf_old)
            
            print(f"✅ Saved: comparison_old_method.pdf ({len(pdf_old):,} bytes)")
            print()
            
            # Method 2: New way (LinkedIn PDF)
            print("Method 2: LinkedIn PDF Capture (NEW)")
            print("-" * 70)
            print("This method:")
            print("  1. Clicks 'More' → 'Save to PDF'")
            print("  2. Waits for LinkedIn to open PDF in new tab")
            print("  3. Captures LinkedIn's formatted PDF")
            print("Result: Professional LinkedIn-formatted PDF")
            print()
            
            pdf_new = await scraper.download_profile_pdf(test_profile)
            
            if pdf_new:
                with open("comparison_new_method.pdf", "wb") as f:
                    f.write(pdf_new)
                
                print(f"✅ Saved: comparison_new_method.pdf ({len(pdf_new):,} bytes)")
                print()
            else:
                print("❌ New method failed")
                print()
            
            # Summary
            print("=" * 70)
            print("Comparison Summary")
            print("=" * 70)
            print()
            print("OLD METHOD (comparison_old_method.pdf):")
            print("  • Browser page print")
            print("  • Inconsistent formatting")
            print("  • May include browser UI elements")
            print(f"  • Size: {len(pdf_old):,} bytes")
            print()
            
            if pdf_new:
                print("NEW METHOD (comparison_new_method.pdf):")
                print("  • LinkedIn's professional PDF")
                print("  • Consistent formatting")
                print("  • Clean, professional appearance")
                print(f"  • Size: {len(pdf_new):,} bytes")
                print()
                
                size_diff = len(pdf_new) - len(pdf_old)
                print(f"Size difference: {size_diff:+,} bytes")
                print()
            
            print("📄 Open both PDFs to see the difference!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(compare_methods())
    sys.exit(0 if success else 1)
