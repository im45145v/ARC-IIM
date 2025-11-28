"""
Bulk import utilities for the Alumni Management System.

Provides functions for importing alumni data from Excel/CSV files
with flexible column name detection, duplicate handling, and automatic
queue population for scraping.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from .crud import (
    add_to_scraping_queue,
    create_alumni,
    get_alumni_by_roll_number,
    update_alumni,
)


@dataclass
class ImportSummary:
    """Summary of import operation results."""
    
    total_rows: int
    new_records: int
    updated_records: int
    skipped_records: int
    queued_for_scraping: int
    errors: List[str]


# Column name variations for flexible detection
COLUMN_MAPPINGS = {
    'roll_number': [
        'Roll No.', 'roll_number', 'Roll Number', 'rollno', 'roll',
        'Roll No', 'ROLL NO', 'Roll_Number', 'RollNumber', 'roll no'
    ],
    'name': [
        'Name of the Student', 'Name', 'name', 'Student Name',
        'NAME', 'Student_Name', 'StudentName', 'student name'
    ],
    'batch': [
        'Batch', 'batch', 'Year', 'year', 'BATCH', 'YEAR',
        'Graduation Year', 'graduation_year'
    ],
    'linkedin_id': [
        'LinkedIn ID', 'linkedin_url', 'Linkedin ID', 'LinkedIn', 'linkedin',
        'LINKEDIN ID', 'LinkedIn_ID', 'linkedin_id', 'LinkedIn URL',
        'linkedin url', 'LinkedIn Profile', 'linkedin_profile'
    ],
    'mobile_number': [
        'Mobile No.', 'phone', 'Phone', 'mobile', 'Mobile', 'WhatsApp Number',
        'Mobile No', 'MOBILE NO', 'Mobile_Number', 'mobile_number',
        'Contact Number', 'contact_number'
    ],
    'personal_email': [
        'Personal Email Id.', 'email', 'Email', 'personal_email', 'Personal Email',
        'PERSONAL EMAIL', 'Personal_Email', 'PersonalEmail', 'personal email'
    ],
    'college_email': [
        'College mail Id', 'college_email', 'College Email', 'college email',
        'COLLEGE EMAIL', 'College_Email', 'CollegeEmail', 'College Mail'
    ],
    'gender': [
        'Gender', 'gender', 'GENDER', 'Sex', 'sex'
    ],
    'whatsapp_number': [
        'WhatsApp Number', 'whatsapp_number', 'WhatsApp', 'whatsapp',
        'WHATSAPP NUMBER', 'WhatsApp_Number'
    ],
    'current_company': [
        'Current Company', 'current_company', 'Company', 'company',
        'CURRENT COMPANY', 'Current_Company', 'CurrentCompany'
    ],
    'current_designation': [
        'Current Designation', 'current_designation', 'Designation', 'designation',
        'CURRENT DESIGNATION', 'Current_Designation', 'CurrentDesignation',
        'Job Title', 'job_title', 'Title', 'title'
    ],
    'location': [
        'Location', 'location', 'LOCATION', 'City', 'city',
        'Current Location', 'current_location'
    ],
}


def detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect and map column names from DataFrame to database fields.
    
    Supports flexible column name variations (e.g., "Roll No.", "roll_number").
    
    Args:
        df: Input DataFrame with alumni data.
    
    Returns:
        Dictionary mapping database field names to detected column names.
        Example: {'roll_number': 'Roll No.', 'name': 'Name'}
    """
    detected = {}
    
    for db_field, possible_names in COLUMN_MAPPINGS.items():
        for col_name in possible_names:
            if col_name in df.columns:
                detected[db_field] = col_name
                break
    
    return detected


def normalize_linkedin_url(linkedin_value: str) -> tuple[Optional[str], Optional[str]]:
    """
    Convert LinkedIn username to full URL and extract ID.
    
    Handles both full URLs and plain usernames.
    
    Args:
        linkedin_value: LinkedIn URL or username.
    
    Returns:
        Tuple of (linkedin_url, linkedin_id).
        Example: ("https://www.linkedin.com/in/johndoe", "johndoe")
    """
    if not linkedin_value or pd.isna(linkedin_value):
        return None, None
    
    linkedin_value = str(linkedin_value).strip()
    
    if not linkedin_value:
        return None, None
    
    # If it's already a full URL
    if 'linkedin.com' in linkedin_value:
        linkedin_url = linkedin_value
        # Extract ID from URL
        if '/in/' in linkedin_value:
            linkedin_id = linkedin_value.split('/in/')[-1].rstrip('/').split('?')[0]
        else:
            linkedin_id = None
        return linkedin_url, linkedin_id
    
    # If it's just a username, convert to full URL
    linkedin_id = linkedin_value
    linkedin_url = f"https://www.linkedin.com/in/{linkedin_id}"
    return linkedin_url, linkedin_id


def validate_required_columns(detected_columns: Dict[str, str]) -> List[str]:
    """
    Validate that required columns are present.
    
    Args:
        detected_columns: Dictionary of detected column mappings.
    
    Returns:
        List of missing required column names (empty if all present).
    """
    required_fields = ['roll_number']
    missing = []
    
    for field in required_fields:
        if field not in detected_columns:
            missing.append(field)
    
    return missing


def import_from_dataframe(
    db: Session,
    df: pd.DataFrame,
    queue_for_scraping: bool = True,
    skip_duplicates: bool = True,
) -> ImportSummary:
    """
    Import alumni data from a pandas DataFrame.
    
    Features:
    - Flexible column name detection
    - LinkedIn username to URL conversion
    - Duplicate detection and handling
    - Automatic queue population for scraping
    - Import summary generation
    
    Args:
        db: Database session.
        df: DataFrame containing alumni data.
        queue_for_scraping: Whether to add profiles to scraping queue.
        skip_duplicates: Whether to skip duplicate roll numbers.
    
    Returns:
        ImportSummary with results of the import operation.
    """
    summary = ImportSummary(
        total_rows=len(df),
        new_records=0,
        updated_records=0,
        skipped_records=0,
        queued_for_scraping=0,
        errors=[]
    )
    
    # Detect columns
    detected_columns = detect_columns(df)
    
    # Validate required columns
    missing = validate_required_columns(detected_columns)
    if missing:
        summary.errors.append(
            f"Missing required columns: {', '.join(missing)}. "
            f"Please ensure your file has columns for: roll_number"
        )
        return summary
    
    # Process each row
    for idx, row in df.iterrows():
        try:
            # Extract data from mapped columns
            alumni_data = {}
            
            for db_field, csv_col in detected_columns.items():
                value = row.get(csv_col)
                if pd.notna(value) and str(value).strip():
                    alumni_data[db_field] = str(value).strip()
            
            # Process LinkedIn URL/ID
            if 'linkedin_id' in alumni_data:
                linkedin_url, linkedin_id = normalize_linkedin_url(alumni_data['linkedin_id'])
                if linkedin_url:
                    alumni_data['linkedin_url'] = linkedin_url
                if linkedin_id:
                    alumni_data['linkedin_id'] = linkedin_id
            
            # Ensure roll_number exists
            if 'roll_number' not in alumni_data:
                summary.errors.append(f"Row {idx + 2}: Missing roll number")
                summary.skipped_records += 1
                continue
            
            roll_number = alumni_data['roll_number']
            
            # Check for existing record
            existing = get_alumni_by_roll_number(db, roll_number)
            
            if existing:
                if skip_duplicates:
                    summary.skipped_records += 1
                    continue
                else:
                    # Update existing record
                    # Preserve created_at by not including it in update
                    alumni_data.pop('created_at', None)
                    update_alumni(db, existing.id, **alumni_data)
                    summary.updated_records += 1
                    
                    # Queue for scraping if requested and has LinkedIn URL
                    if queue_for_scraping and alumni_data.get('linkedin_url'):
                        add_to_scraping_queue(db, existing.id)
                        summary.queued_for_scraping += 1
            else:
                # Set name if not provided
                if 'name' not in alumni_data:
                    alumni_data['name'] = roll_number
                
                # Create new record
                try:
                    new_alumni = create_alumni(db, **alumni_data)
                    summary.new_records += 1
                    
                    # Queue for scraping if requested and has LinkedIn URL
                    if queue_for_scraping and alumni_data.get('linkedin_url'):
                        add_to_scraping_queue(db, new_alumni.id)
                        summary.queued_for_scraping += 1
                except Exception as create_error:
                    # Handle database constraint violations (e.g., duplicate linkedin_id)
                    db.rollback()
                    summary.errors.append(f"Row {idx + 2}: {str(create_error)}")
                    summary.skipped_records += 1
        
        except Exception as e:
            db.rollback()
            summary.errors.append(f"Row {idx + 2}: {str(e)}")
            summary.skipped_records += 1
    
    return summary


def import_from_csv(
    db: Session,
    csv_path: str,
    queue_for_scraping: bool = True,
    skip_duplicates: bool = True,
) -> ImportSummary:
    """
    Import alumni data from a CSV file.
    
    Args:
        db: Database session.
        csv_path: Path to CSV file.
        queue_for_scraping: Whether to add profiles to scraping queue.
        skip_duplicates: Whether to skip duplicate roll numbers.
    
    Returns:
        ImportSummary with results of the import operation.
    """
    df = pd.read_csv(csv_path)
    return import_from_dataframe(db, df, queue_for_scraping, skip_duplicates)


def import_from_excel(
    db: Session,
    excel_path: str,
    sheet_name: int | str = 0,
    queue_for_scraping: bool = True,
    skip_duplicates: bool = True,
) -> ImportSummary:
    """
    Import alumni data from an Excel file.
    
    Args:
        db: Database session.
        excel_path: Path to Excel file.
        sheet_name: Sheet name or index to read (default: first sheet).
        queue_for_scraping: Whether to add profiles to scraping queue.
        skip_duplicates: Whether to skip duplicate roll numbers.
    
    Returns:
        ImportSummary with results of the import operation.
    """
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    return import_from_dataframe(db, df, queue_for_scraping, skip_duplicates)
