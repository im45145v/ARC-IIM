#!/usr/bin/env python3
"""
Test script to verify PDF download capture.
This tests that the scraper properly captures the downloaded PDF file
(with random filename) that LinkedIn generates.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.scraper.linkedin_scraper import LinkedInScraper


async def test_pdf_download():
    """Test PDF download with actual file capture."""
    
    test_profile = os.getenv("TEST_LINKEDIN_PROFILE", "https://www.linkedin.com/in/williamhgates/")
    cookies_file = "cookies/linkedin_cookies_1.json"
    
    print("=" * 70)
    print("Testing PDF Download Capture (Real Download)")
    print("=" * 70)
    print(f"Profile: {test_profile}")
    print(f"Cookies: {cookies_file}")
    print()
    print("This test will:")
    print("  1. Click 'Save to PDF' on LinkedIn")
    print("  2. Wait for the download to start")
    print("  3. Capture the downloaded PDF file")
    print("  4. Read and return the PDF bytes")
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
            print()
            
            pdf_bytes = await scraper.download_profile_pdf(test_profile)
            
            if pdf_bytes:
                # Save the PDF
                output_file = "test_profile_real_download.pdf"
                with open(output_file, "wb") as f:
                    f.write(pdf_bytes)
                
                print()
                print("=" * 70)
                print("✅ SUCCESS!")
                print("=" * 70)
                print(f"PDF Size: {len(pdf_bytes):,} bytes")
                print(f"Saved to: {output_file}")
                print()
                print("Verification checklist:")
                print("  ✓ Open the PDF file")
                print("  ✓ Check if it's LinkedIn's formatted PDF")
                print("  ✓ Verify all sections are included")
                print("  ✓ Confirm professional appearance")
                print()
                print("Expected output:")
                print("  • LinkedIn's professional PDF layout")
                print("  • Clean formatting and styling")
                print("  • All profile sections (experience, education, etc.)")
                print("  • No browser UI elements")
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
