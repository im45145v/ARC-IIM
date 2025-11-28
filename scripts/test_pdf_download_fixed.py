#!/usr/bin/env python3
"""
Test script to verify the fixed PDF download functionality.
This script tests that the scraper properly waits for LinkedIn's
PDF generation and captures the actual PDF (not just a page print).
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.scraper.linkedin_scraper import LinkedInScraper


async def test_pdf_download():
    """Test PDF download with the fixed implementation."""
    
    # Get test profile URL from environment or use default
    test_profile = os.getenv("TEST_LINKEDIN_PROFILE", "https://www.linkedin.com/in/williamhgates/")
    cookies_file = "cookies/linkedin_cookies_1.json"
    
    print("=" * 70)
    print("Testing Fixed PDF Download")
    print("=" * 70)
    print(f"Profile: {test_profile}")
    print(f"Cookies: {cookies_file}")
    print()
    
    if not os.path.exists(cookies_file):
        print(f"❌ Cookies file not found: {cookies_file}")
        print("Please run manual_login_and_save.py first to save cookies.")
        return False
    
    try:
        async with LinkedInScraper(cookies_file=cookies_file) as scraper:
            print("Step 1: Verifying authentication...")
            if not await scraper.verify_cookie_auth():
                print("❌ Cookie authentication failed")
                return False
            print("✅ Authenticated successfully")
            print()
            
            print("Step 2: Downloading profile PDF...")
            print("This will:")
            print("  1. Navigate to the profile")
            print("  2. Click 'More' button")
            print("  3. Click 'Save to PDF'")
            print("  4. Wait for new tab to open")
            print("  5. Capture the PDF from the new tab")
            print()
            
            pdf_bytes = await scraper.download_profile_pdf(test_profile)
            
            if pdf_bytes:
                # Save the PDF
                output_file = "test_profile_fixed.pdf"
                with open(output_file, "wb") as f:
                    f.write(pdf_bytes)
                
                print()
                print("=" * 70)
                print("✅ SUCCESS!")
                print("=" * 70)
                print(f"PDF Size: {len(pdf_bytes):,} bytes")
                print(f"Saved to: {output_file}")
                print()
                print("Please open the PDF and verify:")
                print("  ✓ It's LinkedIn's formatted PDF (not a page print)")
                print("  ✓ It has proper formatting and layout")
                print("  ✓ All sections are included")
                return True
            else:
                print()
                print("❌ Failed to download PDF")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_pdf_download())
    sys.exit(0 if success else 1)
