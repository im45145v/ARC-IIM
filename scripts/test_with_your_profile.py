#!/usr/bin/env python3
"""
Test scraper with your LinkedIn profile
https://www.linkedin.com/in/im45145v
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.scraper.linkedin_scraper import LinkedInScraper


async def test_your_profile():
    """Test scraping your profile"""
    
    print("=" * 70)
    print("Testing Scraper with Your Profile")
    print("=" * 70)
    print()
    
    cookies_file = "cookies/linkedin_cookies_1_fixed.json"
    your_profile = "https://www.linkedin.com/in/im45145v"
    
    # Check if cookies exist
    if not Path(cookies_file).exists():
        print(f"❌ Cookies file not found: {cookies_file}")
        print()
        print("Run this first:")
        print("  python3 scripts/manual_login_and_save.py")
        return
    
    print(f"✅ Cookies file found: {cookies_file}")
    print(f"✅ Profile URL: {your_profile}")
    print()
    
    try:
        async with LinkedInScraper(cookies_file=cookies_file) as scraper:
            print("Logging in...")
            if not await scraper.login():
                print("❌ Login failed")
                return
            
            print("✅ Logged in")
            print()
            
            print("Scraping your profile...")
            profile_data = await scraper.scrape_profile(your_profile)
            
            if profile_data:
                print("✅ Profile scraped successfully!")
                print()
                print("Extracted data:")
                print("-" * 70)
                
                if profile_data.get('name'):
                    print(f"Name: {profile_data['name']}")
                if profile_data.get('headline'):
                    print(f"Headline: {profile_data['headline']}")
                if profile_data.get('location'):
                    print(f"Location: {profile_data['location']}")
                if profile_data.get('current_company'):
                    print(f"Company: {profile_data['current_company']}")
                if profile_data.get('current_designation'):
                    print(f"Designation: {profile_data['current_designation']}")
                
                if profile_data.get('job_history'):
                    print(f"\nJob History: {len(profile_data['job_history'])} positions")
                    for i, job in enumerate(profile_data['job_history'][:3], 1):
                        print(f"  {i}. {job.get('designation', 'N/A')} at {job.get('company_name', 'N/A')}")
                
                if profile_data.get('education_history'):
                    print(f"\nEducation: {len(profile_data['education_history'])} entries")
                    for i, edu in enumerate(profile_data['education_history'][:2], 1):
                        print(f"  {i}. {edu.get('institution_name', 'N/A')}")
                
                print()
                print("=" * 70)
                print("✅ Scraper is working!")
                print("=" * 70)
                print()
                print("Now testing PDF download...")
                print()
                
                # Test PDF download
                pdf_bytes = await scraper.download_profile_pdf(your_profile)
                
                if pdf_bytes:
                    print(f"✅ PDF downloaded! Size: {len(pdf_bytes)} bytes")
                    
                    # Save to file
                    output_file = "test_your_profile.pdf"
                    with open(output_file, "wb") as f:
                        f.write(pdf_bytes)
                    
                    print(f"✅ Saved to: {output_file}")
                    print()
                    print("=" * 70)
                    print("✅ ALL TESTS PASSED!")
                    print("=" * 70)
                    print()
                    print("Your setup is working perfectly!")
                    print()
                    print("You can now run the full scraper:")
                    print("  python3 scripts/comprehensive_scraper.py")
                else:
                    print("❌ PDF download failed")
            else:
                print("❌ Failed to scrape profile")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print()
    asyncio.run(test_your_profile())
    print()
