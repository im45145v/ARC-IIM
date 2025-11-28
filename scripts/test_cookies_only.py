#!/usr/bin/env python3
"""
Test LinkedIn authentication using cookies only
Shows browser window so you can see what's happening
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.scraper.linkedin_scraper import LinkedInScraper


async def test_cookies():
    """Test cookie-based authentication"""
    
    print("=" * 70)
    print("LinkedIn Cookie Authentication Test")
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
        print("3. Fix them:")
        print()
        print("python3 -c \"")
        print("import json")
        print("cookies = json.load(open('cookies/linkedin_cookies_1.json'))")
        print("for cookie in cookies:")
        print("    if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict','Lax','None']:")
        print("        cookie['sameSite'] = 'Lax'")
        print("json.dump(cookies, open('cookies/linkedin_cookies_1_fixed.json', 'w'), indent=2)")
        print("\"")
        print()
        return
    
    print(f"✅ Cookies file found: {cookies_file}")
    print()
    
    print("Starting browser...")
    print("(A browser window should open)")
    print()
    
    try:
        async with LinkedInScraper(cookies_file=cookies_file) as scraper:
            print("✅ Scraper initialized")
            print()
            
            print("Attempting to login with cookies...")
            print("(Browser will navigate to LinkedIn feed)")
            print()
            
            if await scraper.login():
                print("✅ Login successful!")
                print()
                print("Now testing profile scraping...")
                print()
                
                # Try to scrape a profile
                profile_url = "https://www.linkedin.com/in/akshat-naugir-4509a9202"
                print(f"Scraping: {profile_url}")
                print()
                
                profile_data = await scraper.scrape_profile(profile_url)
                
                if profile_data:
                    print("✅ Profile scraped successfully!")
                    print()
                    print("Extracted data:")
                    print("-" * 70)
                    
                    if profile_data.get('name'):
                        print(f"  Name: {profile_data['name']}")
                    if profile_data.get('headline'):
                        print(f"  Headline: {profile_data['headline']}")
                    if profile_data.get('location'):
                        print(f"  Location: {profile_data['location']}")
                    if profile_data.get('current_company'):
                        print(f"  Company: {profile_data['current_company']}")
                    if profile_data.get('current_designation'):
                        print(f"  Designation: {profile_data['current_designation']}")
                    
                    if profile_data.get('job_history'):
                        print(f"\n  Job History: {len(profile_data['job_history'])} positions")
                    
                    if profile_data.get('education_history'):
                        print(f"  Education: {len(profile_data['education_history'])} entries")
                    
                    print()
                    print("=" * 70)
                    print("✅ Cookies are working perfectly!")
                    print("=" * 70)
                else:
                    print("⚠️  Profile data not extracted")
                    print()
                    print("Possible causes:")
                    print("1. LinkedIn changed their HTML structure")
                    print("2. Profile is private")
                    print("3. Rate limiting")
                    print()
                    print("But authentication worked, so cookies are valid!")
            else:
                print("❌ Login failed")
                print()
                print("Possible causes:")
                print("1. Cookies are expired")
                print("2. Cookies are invalid")
                print("3. LinkedIn blocked the session")
                print()
                print("Solution:")
                print("1. Export fresh cookies from your browser")
                print("2. Make sure you're logged into LinkedIn in your browser")
                print("3. Use a cookie export extension")
                print("4. Save to: cookies/linkedin_cookies_1.json")
                print("5. Fix them and try again")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print()
    asyncio.run(test_cookies())
    print()
