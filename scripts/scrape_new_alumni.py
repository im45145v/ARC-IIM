#!/usr/bin/env python3
"""
Script to scrape LinkedIn profiles for newly added alumni
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.database.connection import get_db_context
from alumni_system.database.crud import get_alumni_by_roll_number, update_alumni
from alumni_system.scraper.linkedin_scraper import LinkedInScraper

def scrape_alumni_profiles():
    """Scrape LinkedIn profiles for the two new alumni"""
    
    roll_numbers = ["M218-23", "BA041-23"]
    
    # Initialize scraper
    scraper = LinkedInScraper()
    
    with get_db_context() as db:
        for roll_no in roll_numbers:
            try:
                # Get alumni record
                alumni = get_alumni_by_roll_number(db, roll_no)
                
                if not alumni:
                    print(f"❌ Alumni with roll number {roll_no} not found in database")
                    continue
                
                if not alumni.linkedin_url:
                    print(f"⚠️  No LinkedIn URL for {alumni.name} ({roll_no})")
                    continue
                
                print(f"\n🔍 Scraping LinkedIn profile for {alumni.name}...")
                print(f"   LinkedIn: {alumni.linkedin_url}")
                
                # Scrape the profile
                profile_data = scraper.scrape_profile(alumni.linkedin_url)
                
                if profile_data:
                    # Update the database with scraped data
                    update_data = {}
                    
                    if profile_data.get("current_company"):
                        update_data["current_company"] = profile_data["current_company"]
                    
                    if profile_data.get("current_designation"):
                        update_data["current_designation"] = profile_data["current_designation"]
                    
                    if profile_data.get("location"):
                        update_data["location"] = profile_data["location"]
                    
                    if profile_data.get("headline"):
                        update_data["headline"] = profile_data["headline"]
                    
                    if update_data:
                        update_alumni(db, alumni.id, **update_data)
                        print(f"✅ Successfully updated {alumni.name} with scraped data")
                    else:
                        print(f"⚠️  No new data found for {alumni.name}")
                else:
                    print(f"❌ Failed to scrape profile for {alumni.name}")
                
            except Exception as e:
                print(f"❌ Error scraping {roll_no}: {e}")
                continue
    
    print("\n✨ Scraping complete!")

if __name__ == "__main__":
    print("Starting LinkedIn profile scraping...\n")
    scrape_alumni_profiles()
