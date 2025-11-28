#!/usr/bin/env python3
"""
Debug script to test LinkedIn scraper with visible browser
Shows exactly what's happening step by step
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.scraper.linkedin_scraper import LinkedInScraper


async def test_scraper():
    """Test scraper with debug output"""
    
    print("=" * 70)
    print("LinkedIn Scraper Debug Test")
    print("=" * 70)
    print()
    
    cookies_file = "cookies/linkedin_cookies_1_fixed.json"
    linkedin_url = "https://www.linkedin.com/in/akshat-naugir-4509a9202"
    
    print(f"Cookies file: {cookies_file}")
    print(f"Profile URL: {linkedin_url}")
    print()
    
    # Check if cookies file exists
    if not Path(cookies_file).exists():
        print(f"❌ Cookies file not found: {cookies_file}")
        return
    
    print("✅ Cookies file found")
    print()
    
    # Initialize scraper
    print("Initializing scraper...")
    async with LinkedInScraper(cookies_file=cookies_file) as scraper:
        print("✅ Scraper initialized")
        print()
        
        # Verify authentication
        print("Verifying cookie authentication...")
        print("   (Browser window should open)")
        print()
        
        try:
            if await scraper.verify_cookie_auth():
                print("✅ Authentication successful!")
                print()
                
                # Scrape profile
                print("Scraping profile...")
                print("   (Browser will navigate to profile)")
                print()
                
                profile_data = await scraper.scrape_profile(linkedin_url)
                
                if profile_data:
                    print("✅ Profile scraped successfully!")
                    print()
                    print("Extracted data:")
                    print("-" * 70)
                    
                    for key, value in profile_data.items():
                        if key not in ['job_history', 'education_history']:
                            if value:
                                print(f"  {key}: {value}")
                    
                    if profile_data.get('job_history'):
                        print(f"\n  Job History: {len(profile_data['job_history'])} positions")
                        for i, job in enumerate(profile_data['job_history'][:3], 1):
                            print(f"    {i}. {job.get('designation', 'N/A')} at {job.get('company_name', 'N/A')}")
                    
                    if profile_data.get('education_history'):
                        print(f"\n  Education: {len(profile_data['education_history'])} entries")
                        for i, edu in enumerate(profile_data['education_history'][:2], 1):
                            print(f"    {i}. {edu.get('institution_name', 'N/A')}")
                    
                    print()
                    print("=" * 70)
                    print("✅ Scraper is working!")
                    print("=" * 70)
                else:
                    print("❌ Failed to scrape profile")
                    print()
                    print("Possible causes:")
                    print("1. LinkedIn changed their HTML structure")
                    print("2. Profile is private")
                    print("3. Rate limiting")
                    print("4. Network issues")
            else:
                print("❌ Authentication failed")
                print()
                print("Possible causes:")
                print("1. Cookies are expired")
                print("2. Cookies are invalid")
                print("3. LinkedIn blocked the session")
                print()
                print("Solution:")
                print("1. Export fresh cookies from your browser")
                print("2. Save to: cookies/linkedin_cookies_1.json")
                print("3. Fix cookies: python3 -c \"import json; cookies=json.load(open('cookies/linkedin_cookies_1.json')); [cookie.update({'sameSite':'Lax'}) for cookie in cookies if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict','Lax','None']]; json.dump(cookies,open('cookies/linkedin_cookies_1_fixed.json','w'),indent=2)\"")
                print("4. Try again")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print()
    print("Starting scraper test...")
    print("A browser window should open and show the scraping process.")
    print()
    
    asyncio.run(test_scraper())
