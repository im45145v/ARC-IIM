#!/usr/bin/env python3
"""
Comprehensive LinkedIn scraper that:
1. Scrapes LinkedIn profiles
2. Saves PDFs to Backblaze B2
3. Updates database with all scraped data including job history and education
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.database.connection import get_db_context
from alumni_system.database.crud import (
    get_alumni_by_roll_number,
    update_alumni,
    create_job_history,
    create_education_history,
    get_job_history_by_alumni,
    get_education_history_by_alumni,
)
from alumni_system.scraper.linkedin_scraper import LinkedInScraper
from alumni_system.storage.b2_client import get_storage_client


async def scrape_and_save_alumni(roll_numbers: list[str], cookies_file: str):
    """
    Scrape alumni profiles, save PDFs to B2, and update database
    
    Args:
        roll_numbers: List of roll numbers to scrape
        cookies_file: Path to LinkedIn cookies file
    """
    
    print("=" * 80)
    print("Comprehensive LinkedIn Scraper")
    print("=" * 80)
    print()
    
    # Initialize B2 storage client
    storage_client = None
    try:
        storage_client = get_storage_client()
        # Test connection
        bucket = storage_client._get_bucket()
        print(f"✅ B2 Storage client initialized (bucket: {bucket.name})")
    except Exception as e:
        print(f"⚠️  B2 Storage not available: {str(e)[:100]}")
        print("   PDFs will not be saved to cloud storage")
        print("   To setup B2, run: python3 scripts/setup_b2.py --setup")
        storage_client = None
    
    print()
    
    # Initialize scraper with cookies
    async with LinkedInScraper(cookies_file=cookies_file) as scraper:
        print(f"✅ Scraper initialized with cookies: {cookies_file}")
        print()
        
        # Verify authentication using cookies
        print("🔐 Verifying cookie authentication...")
        print("   (Browser will open and navigate to LinkedIn feed)")
        print()
        
        try:
            # Force login with cookies only
            if not await scraper.login():
                print("❌ Authentication failed!")
                print("   Cookies may be expired or invalid")
                print()
                print("   Solution:")
                print("   1. Export fresh cookies from your browser")
                print("   2. Save to: cookies/linkedin_cookies_1.json")
                print("   3. Fix them: python3 -c \"import json; cookies=json.load(open('cookies/linkedin_cookies_1.json')); [cookie.update({'sameSite':'Lax'}) for cookie in cookies if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict','Lax','None']]; json.dump(cookies,open('cookies/linkedin_cookies_1_fixed.json','w'),indent=2)\"")
                print("   4. Try again")
                return
            
            print("✅ Authentication successful!")
            print()
            print("=" * 80)
            print()
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return
        
        # Process each alumni
        for roll_no in roll_numbers:
            with get_db_context() as db:
                alumni = get_alumni_by_roll_number(db, roll_no)
                
                if not alumni:
                    print(f"❌ Alumni with roll number {roll_no} not found in database")
                    print()
                    continue
                
                if not alumni.linkedin_url:
                    print(f"⚠️  No LinkedIn URL for {alumni.name} ({roll_no})")
                    print()
                    continue
                
                print(f"🔍 Processing: {alumni.name} ({roll_no})")
                print(f"   LinkedIn: {alumni.linkedin_url}")
                print()
                
                try:
                    # Scrape the profile
                    print("   📥 Scraping profile data...")
                    profile_data = await scraper.scrape_profile(alumni.linkedin_url)
                    
                    if not profile_data:
                        print("   ❌ Failed to scrape profile")
                        print()
                        continue
                    
                    print("   ✅ Profile data scraped successfully")
                    
                    # Download PDF
                    pdf_url = None
                    if storage_client:
                        try:
                            print("   📄 Downloading profile as PDF...")
                            pdf_bytes = await scraper.download_profile_pdf(alumni.linkedin_url)
                            
                            if pdf_bytes:
                                print("   ☁️  Uploading PDF to Backblaze B2...")
                                upload_result = storage_client.upload_pdf_bytes(
                                    pdf_bytes,
                                    alumni.roll_number
                                )
                                pdf_url = upload_result["download_url"]
                                print(f"   ✅ PDF saved to B2: {upload_result['file_name']}")
                            else:
                                print("   ⚠️  Failed to download PDF")
                        except Exception as e:
                            print(f"   ⚠️  PDF upload failed: {e}")
                    
                    # Update alumni basic info
                    print("   💾 Updating alumni record...")
                    update_data = {
                        "last_scraped_at": datetime.utcnow()
                    }
                    
                    if "name" in profile_data and profile_data["name"]:
                        update_data["name"] = profile_data["name"]
                    
                    if "headline" in profile_data and profile_data["headline"]:
                        # Store headline in POR field
                        update_data["por"] = profile_data["headline"]
                    
                    if "location" in profile_data and profile_data["location"]:
                        update_data["location"] = profile_data["location"]
                    
                    if "current_company" in profile_data and profile_data["current_company"]:
                        update_data["current_company"] = profile_data["current_company"]
                    
                    if "current_designation" in profile_data and profile_data["current_designation"]:
                        update_data["current_designation"] = profile_data["current_designation"]
                    
                    if pdf_url:
                        update_data["linkedin_pdf_url"] = pdf_url
                    
                    if "email" in profile_data and profile_data["email"]:
                        # Try to determine which email field to use
                        email = profile_data["email"]
                        if "corporate" in email.lower() or "@" in email:
                            update_data["corporate_email"] = email
                    
                    update_alumni(db, alumni.id, **update_data)
                    print(f"   ✅ Updated basic info ({len(update_data)} fields)")
                    
                    # Add job history
                    if "job_history" in profile_data and profile_data["job_history"]:
                        print(f"   💼 Adding job history ({len(profile_data['job_history'])} positions)...")
                        
                        # Clear existing job history to avoid duplicates
                        existing_jobs = get_job_history_by_alumni(db, alumni.id)
                        if existing_jobs:
                            print(f"      (Replacing {len(existing_jobs)} existing records)")
                        
                        for job in profile_data["job_history"]:
                            try:
                                job_data = {
                                    "company_name": job.get("company_name", "Unknown"),
                                    "designation": job.get("designation"),
                                    "location": job.get("location"),
                                    "description": job.get("duration"),
                                    "is_current": job.get("is_current", False),
                                }
                                
                                # Parse dates if available
                                if "start_date" in job:
                                    job_data["start_date"] = job["start_date"]
                                if "end_date" in job:
                                    job_data["end_date"] = job["end_date"]
                                
                                create_job_history(db, alumni.id, **job_data)
                            except Exception as e:
                                print(f"      ⚠️  Failed to add job: {e}")
                        
                        print(f"   ✅ Job history added")
                    
                    # Add education history
                    if "education_history" in profile_data and profile_data["education_history"]:
                        print(f"   🎓 Adding education history ({len(profile_data['education_history'])} entries)...")
                        
                        # Clear existing education to avoid duplicates
                        existing_edu = get_education_history_by_alumni(db, alumni.id)
                        if existing_edu:
                            print(f"      (Replacing {len(existing_edu)} existing records)")
                        
                        for edu in profile_data["education_history"]:
                            try:
                                edu_data = {
                                    "institution_name": edu.get("institution_name", "Unknown"),
                                    "degree": edu.get("degree"),
                                    "field_of_study": edu.get("field_of_study"),
                                }
                                
                                # Parse years if available
                                if "start_year" in edu:
                                    edu_data["start_year"] = edu["start_year"]
                                if "end_year" in edu:
                                    edu_data["end_year"] = edu["end_year"]
                                
                                create_education_history(db, alumni.id, **edu_data)
                            except Exception as e:
                                print(f"      ⚠️  Failed to add education: {e}")
                        
                        print(f"   ✅ Education history added")
                    
                    print()
                    print(f"   🎉 Successfully processed {alumni.name}!")
                    print()
                    
                except Exception as e:
                    print(f"   ❌ Error processing {alumni.name}: {e}")
                    print()
                    continue
                
                print("=" * 80)
                print()
    
    print("✨ Scraping complete!")
    print()


async def main():
    """Main function"""
    
    # Alumni to scrape
    roll_numbers = ["M218-23", "BA041-23"]
    
    # Use fixed cookies file
    cookies_file = "cookies/linkedin_cookies_1_fixed.json"
    
    if not Path(cookies_file).exists():
        print(f"❌ Cookies file not found: {cookies_file}")
        print()
        print("Please ensure you have a valid LinkedIn cookies file.")
        print("See docs/COOKIE_AUTHENTICATION.md for setup instructions.")
        return
    
    await scrape_and_save_alumni(roll_numbers, cookies_file)


if __name__ == "__main__":
    asyncio.run(main())
