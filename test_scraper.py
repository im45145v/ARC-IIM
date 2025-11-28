#!/usr/bin/env python3
"""
Test script to scrape the two new alumni LinkedIn profiles
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from alumni_system.database.connection import get_db_context
from alumni_system.database.crud import get_alumni_by_roll_number, update_alumni
from alumni_system.scraper.linkedin_scraper import LinkedInScraper


async def test_scrape_alumni():
    """Test scraping both alumni profiles"""
    
    # Alumni to scrape
    alumni_to_scrape = [
        {
            "roll_number": "M218-23",
            "name": "Akshat Naugir",
            "linkedin_url": "https://www.linkedin.com/in/akshat-naugir-4509a9202"
        },
        {
            "roll_number": "BA041-23",
            "name": "Narendran T",
            "linkedin_url": "http://linkedin.com/in/narendrant1998"
        }
    ]
    
    print("=" * 70)
    print("LinkedIn Scraper Test")
    print("=" * 70)
    print()
    
    # Initialize scraper with cookies
    cookies_file = "cookies/linkedin_cookies_1.json"
    
    async with LinkedInScraper(cookies_file=cookies_file) as scraper:
        print(f"✅ Scraper initialized with cookies from: {cookies_file}")
        print()
        
        # Verify authentication
        print("🔐 Verifying cookie authentication...")
        if await scraper.verify_cookie_auth():
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed!")
            print("Please check your cookies file or try logging in manually.")
            return
        
        print()
        print("=" * 70)
        print()
        
        # Scrape each alumni
        for alumni in alumni_to_scrape:
            print(f"🔍 Scraping: {alumni['name']} ({alumni['roll_number']})")
            print(f"   LinkedIn: {alumni['linkedin_url']}")
            print()
            
            try:
                # Scrape the profile
                profile_data = await scraper.scrape_profile(alumni['linkedin_url'])
                
                if profile_data:
                    print("✅ Successfully scraped profile!")
                    print()
                    print("📊 Extracted Data:")
                    print("-" * 70)
                    
                    # Display basic info
                    if "name" in profile_data:
                        print(f"   Name: {profile_data['name']}")
                    if "headline" in profile_data:
                        print(f"   Headline: {profile_data['headline']}")
                    if "location" in profile_data:
                        print(f"   Location: {profile_data['location']}")
                    if "current_company" in profile_data:
                        print(f"   Current Company: {profile_data['current_company']}")
                    if "current_designation" in profile_data:
                        print(f"   Current Designation: {profile_data['current_designation']}")
                    
                    # Display job history
                    if "job_history" in profile_data and profile_data["job_history"]:
                        print(f"\n   📋 Job History ({len(profile_data['job_history'])} positions):")
                        for i, job in enumerate(profile_data["job_history"][:5], 1):
                            print(f"      {i}. {job.get('designation', 'N/A')} at {job.get('company_name', 'N/A')}")
                            if "duration" in job:
                                print(f"         Duration: {job['duration']}")
                    
                    # Display education
                    if "education_history" in profile_data and profile_data["education_history"]:
                        print(f"\n   🎓 Education ({len(profile_data['education_history'])} entries):")
                        for i, edu in enumerate(profile_data["education_history"][:3], 1):
                            print(f"      {i}. {edu.get('institution_name', 'N/A')}")
                            if "degree" in edu:
                                print(f"         Degree: {edu['degree']}")
                    
                    # Display contact info
                    if "email" in profile_data:
                        print(f"\n   📧 Email: {profile_data['email']}")
                    
                    print()
                    print("-" * 70)
                    print()
                    
                    # Save full data to JSON for inspection
                    output_file = f"scraped_{alumni['roll_number']}.json"
                    with open(output_file, 'w') as f:
                        json.dump(profile_data, f, indent=2)
                    print(f"💾 Full data saved to: {output_file}")
                    print()
                    
                    # Update database
                    print("💾 Updating database...")
                    with get_db_context() as db:
                        alumni_record = get_alumni_by_roll_number(db, alumni['roll_number'])
                        if alumni_record:
                            update_data = {}
                            
                            if "name" in profile_data:
                                update_data["name"] = profile_data["name"]
                            if "headline" in profile_data:
                                update_data["por"] = profile_data["headline"]
                            if "location" in profile_data:
                                update_data["location"] = profile_data["location"]
                            if "current_company" in profile_data:
                                update_data["current_company"] = profile_data["current_company"]
                            if "current_designation" in profile_data:
                                update_data["current_designation"] = profile_data["current_designation"]
                            
                            if update_data:
                                update_alumni(db, alumni_record.id, **update_data)
                                print(f"✅ Database updated for {alumni['name']}")
                            else:
                                print(f"⚠️  No new data to update for {alumni['name']}")
                    
                else:
                    print(f"❌ Failed to scrape profile for {alumni['name']}")
                
            except Exception as e:
                print(f"❌ Error scraping {alumni['name']}: {e}")
            
            print()
            print("=" * 70)
            print()
    
    print("✨ Scraping test complete!")
    print()
    print("📁 Check the generated JSON files for full scraped data:")
    print("   - scraped_M218-23.json")
    print("   - scraped_BA041-23.json")


if __name__ == "__main__":
    print()
    asyncio.run(test_scrape_alumni())
