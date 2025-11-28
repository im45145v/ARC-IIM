#!/usr/bin/env python3
"""
Test LinkedIn PDF download using "Save to PDF" button
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.scraper.linkedin_scraper import LinkedInScraper


async def test_pdf_download():
    """Test PDF download"""
    
    print("=" * 70)
    print("LinkedIn PDF Download Test")
    print("=" * 70)
    print()
    
    cookies_file = "cookies/linkedin_cookies_1_fixed.json"
    profile_url = "https://www.linkedin.com/in/akshat-naugir-4509a9202"
    
    if not Path(cookies_file).exists():
        print(f"❌ Cookies file not found: {cookies_file}")
        return
    
    print(f"Profile: {profile_url}")
    print()
    
    try:
        async with LinkedInScraper(cookies_file=cookies_file) as scraper:
            print("Logging in...")
            if not await scraper.login():
                print("❌ Login failed")
                return
            
            print("✅ Logged in")
            print()
            
            print("Downloading PDF...")
            print("(Watch the browser - it should click More → Save to PDF)")
            print()
            
            pdf_bytes = await scraper.download_profile_pdf(profile_url)
            
            if pdf_bytes:
                print(f"✅ PDF downloaded! Size: {len(pdf_bytes)} bytes")
                
                # Save to file
                output_file = "test_profile.pdf"
                with open(output_file, "wb") as f:
                    f.write(pdf_bytes)
                
                print(f"✅ Saved to: {output_file}")
                print()
                print("You can now open the PDF to verify it's correct!")
            else:
                print("❌ Failed to download PDF")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print()
    asyncio.run(test_pdf_download())
    print()
