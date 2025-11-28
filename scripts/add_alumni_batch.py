#!/usr/bin/env python3
"""
Script to add alumni records to the database
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alumni_system.database.connection import get_db_context
from alumni_system.database.crud import create_alumni

def add_alumni_records():
    """Add the two alumni records"""
    
    alumni_data = [
        {
            "name": "Akshat Naugir",
            "roll_number": "M218-23",
            "batch": "MBA (2023-25)",
            "gender": "Male",
            "mobile_number": "9910704279",
            "whatsapp_number": "9910704279",
            "college_email": "akshat.naugir23@iimranchi.ac.in",
            "personal_email": "akshatnaugir2000@gmail.com",
            "linkedin_url": "https://www.linkedin.com/in/akshat-naugir-4509a9202",
            "current_company": "Orix Corporation India Ltd",
            "current_designation": "Management Trainee",
            "location": "Mumbai",
            "por": "Junior Executive Member at Infrastructure and Technology Committee",
            "internship": "Genpact India Pvt Ltd, ICICI Bank",
            "notable_alma_mater": "Shaheed Bhagat Singh College"
        },
        {
            "name": "Narendran T",
            "roll_number": "BA041-23",
            "batch": "MBA BA (2023-25)",
            "gender": "Male",
            "mobile_number": "9500866024",
            "whatsapp_number": "9500866024",
            "college_email": "narendran.t23@iimranchi.ac.in",
            "personal_email": "narensurya1998@gmail.com",
            "linkedin_url": "http://linkedin.com/in/narendrant1998",
            "current_company": "Havells India Ltd",
            "current_designation": "Management Trainee - Analytics",
            "location": "Noida",
            "internship": "Amber, Resojet"
        }
    ]
    
    with get_db_context() as db:
        for alumni in alumni_data:
            try:
                # Check if already exists
                from alumni_system.database.crud import get_alumni_by_roll_number
                existing = get_alumni_by_roll_number(db, alumni["roll_number"])
                
                if existing:
                    print(f"⚠️  Alumni {alumni['name']} ({alumni['roll_number']}) already exists. Skipping.")
                    continue
                
                # Create new alumni record
                new_alumni = create_alumni(
                    db,
                    name=alumni["name"],
                    roll_number=alumni["roll_number"],
                    batch=alumni.get("batch"),
                    gender=alumni.get("gender"),
                    mobile_number=alumni.get("mobile_number"),
                    whatsapp_number=alumni.get("whatsapp_number"),
                    college_email=alumni.get("college_email"),
                    personal_email=alumni.get("personal_email"),
                    linkedin_url=alumni.get("linkedin_url"),
                    current_company=alumni.get("current_company"),
                    current_designation=alumni.get("current_designation"),
                    location=alumni.get("location"),
                    por=alumni.get("por"),
                    internship=alumni.get("internship"),
                    notable_alma_mater=alumni.get("notable_alma_mater")
                )
                
                print(f"✅ Successfully added: {alumni['name']} ({alumni['roll_number']})")
                
            except Exception as e:
                print(f"❌ Error adding {alumni['name']}: {e}")
                continue
    
    print("\n✨ Done! Alumni records have been added to the database.")

if __name__ == "__main__":
    print("Adding alumni records to database...\n")
    add_alumni_records()
