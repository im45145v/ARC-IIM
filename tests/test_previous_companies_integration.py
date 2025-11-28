"""
Integration test for previous companies column in browse table and Excel export.

This test verifies the complete flow from database to display.
"""

import io
import pandas as pd

from alumni_system.database.crud import (
    create_alumni,
    create_job_history,
    get_all_alumni,
)


def alumni_to_dataframe(alumni_list: list) -> pd.DataFrame:
    """
    Convert list of Alumni objects to DataFrame.
    This is the same function used in the frontend.
    """
    data = []
    for alumni in alumni_list:
        # Get previous companies from job history
        previous_companies = []
        if hasattr(alumni, 'job_history') and alumni.job_history:
            for job in alumni.job_history:
                if not job.is_current and job.company_name:
                    role_info = f"{job.company_name}"
                    if job.designation:
                        role_info += f" ({job.designation})"
                    previous_companies.append(role_info)
        
        data.append({
            "ID": alumni.id,
            "Name": alumni.name,
            "Batch": alumni.batch,
            "Roll Number": alumni.roll_number,
            "Gender": alumni.gender,
            "Current Company": alumni.current_company,
            "Current Designation": alumni.current_designation,
            "Location": alumni.location,
            "Previous Companies": "; ".join(previous_companies) if previous_companies else "",
            "Personal Email": alumni.personal_email,
            "College Email": alumni.college_email,
            "Mobile": alumni.mobile_number,
            "LinkedIn": alumni.linkedin_url,
            "Higher Studies": alumni.higher_studies,
            "Last Updated": alumni.updated_at,
        })
    return pd.DataFrame(data)


def export_to_excel(df: pd.DataFrame) -> bytes:
    """Export DataFrame to Excel bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Alumni")
    return output.getvalue()


def test_previous_companies_in_browse_table(clean_db_session):
    """
    Integration test: Verify previous companies appear in browse table.
    
    **Validates: Requirements 4.5, 10.1**
    """
    # Create alumni with job history
    alumni = create_alumni(
        clean_db_session,
        name="John Doe",
        roll_number="INT001",
        batch="2020",
        current_company="Google",
        current_designation="Senior Engineer",
    )
    
    # Add previous jobs
    create_job_history(
        clean_db_session,
        alumni_id=alumni.id,
        company_name="Microsoft",
        designation="Software Engineer",
        is_current=False,
    )
    
    create_job_history(
        clean_db_session,
        alumni_id=alumni.id,
        company_name="Amazon",
        designation="Junior Engineer",
        is_current=False,
    )
    
    # Add current job
    create_job_history(
        clean_db_session,
        alumni_id=alumni.id,
        company_name="Google",
        designation="Senior Engineer",
        is_current=True,
    )
    
    # Fetch alumni (simulating browse page)
    alumni_list = get_all_alumni(clean_db_session, limit=100)
    
    # Convert to DataFrame (as done in frontend)
    df = alumni_to_dataframe(alumni_list)
    
    # Verify Previous Companies column exists
    assert "Previous Companies" in df.columns
    
    # Get the row for our alumni
    row = df[df["Roll Number"] == "INT001"].iloc[0]
    
    # Verify previous companies are present
    previous_companies = row["Previous Companies"]
    assert "Microsoft (Software Engineer)" in previous_companies
    assert "Amazon (Junior Engineer)" in previous_companies
    assert "Google" not in previous_companies  # Current company should not be in previous
    
    # Verify formatting
    assert ";" in previous_companies  # Semicolon separator


def test_previous_companies_in_excel_export(clean_db_session):
    """
    Integration test: Verify previous companies appear in Excel export.
    
    **Validates: Requirements 4.5, 10.1**
    """
    # Create alumni with job history
    alumni = create_alumni(
        clean_db_session,
        name="Jane Smith",
        roll_number="INT002",
        batch="2021",
        current_company="Apple",
        current_designation="Product Manager",
    )
    
    # Add previous jobs
    create_job_history(
        clean_db_session,
        alumni_id=alumni.id,
        company_name="Facebook",
        designation="Associate PM",
        is_current=False,
    )
    
    create_job_history(
        clean_db_session,
        alumni_id=alumni.id,
        company_name="Startup Inc",
        designation="Intern",
        is_current=False,
    )
    
    # Add current job
    create_job_history(
        clean_db_session,
        alumni_id=alumni.id,
        company_name="Apple",
        designation="Product Manager",
        is_current=True,
    )
    
    # Fetch alumni
    alumni_list = get_all_alumni(clean_db_session, limit=100)
    
    # Convert to DataFrame
    df = alumni_to_dataframe(alumni_list)
    
    # Export to Excel
    excel_bytes = export_to_excel(df)
    
    # Read back from Excel to verify
    excel_df = pd.read_excel(io.BytesIO(excel_bytes))
    
    # Verify Previous Companies column exists in Excel
    assert "Previous Companies" in excel_df.columns
    
    # Get the row for our alumni
    row = excel_df[excel_df["Roll Number"] == "INT002"].iloc[0]
    
    # Verify previous companies are in Excel export
    previous_companies = row["Previous Companies"]
    assert "Facebook (Associate PM)" in previous_companies
    assert "Startup Inc (Intern)" in previous_companies
    assert "Apple" not in previous_companies  # Current company should not be in previous


def test_previous_companies_with_multiple_alumni(clean_db_session):
    """
    Integration test: Verify previous companies work correctly with multiple alumni.
    
    **Validates: Requirements 4.5, 10.1**
    """
    # Create first alumni with 2 previous jobs
    alumni1 = create_alumni(
        clean_db_session,
        name="Alumni One",
        roll_number="INT003",
        batch="2020",
    )
    
    create_job_history(
        clean_db_session,
        alumni_id=alumni1.id,
        company_name="Company A",
        designation="Role A",
        is_current=False,
    )
    
    create_job_history(
        clean_db_session,
        alumni_id=alumni1.id,
        company_name="Company B",
        designation="Role B",
        is_current=False,
    )
    
    # Create second alumni with no previous jobs
    alumni2 = create_alumni(
        clean_db_session,
        name="Alumni Two",
        roll_number="INT004",
        batch="2021",
        current_company="Current Corp",
    )
    
    create_job_history(
        clean_db_session,
        alumni_id=alumni2.id,
        company_name="Current Corp",
        designation="Current Role",
        is_current=True,
    )
    
    # Create third alumni with 1 previous job
    alumni3 = create_alumni(
        clean_db_session,
        name="Alumni Three",
        roll_number="INT005",
        batch="2022",
    )
    
    create_job_history(
        clean_db_session,
        alumni_id=alumni3.id,
        company_name="Company C",
        designation="Role C",
        is_current=False,
    )
    
    # Fetch all alumni
    alumni_list = get_all_alumni(clean_db_session, limit=100)
    
    # Convert to DataFrame
    df = alumni_to_dataframe(alumni_list)
    
    # Verify each alumni has correct previous companies
    row1 = df[df["Roll Number"] == "INT003"].iloc[0]
    assert "Company A (Role A)" in row1["Previous Companies"]
    assert "Company B (Role B)" in row1["Previous Companies"]
    
    row2 = df[df["Roll Number"] == "INT004"].iloc[0]
    assert row2["Previous Companies"] == ""  # No previous companies
    
    row3 = df[df["Roll Number"] == "INT005"].iloc[0]
    assert row3["Previous Companies"] == "Company C (Role C)"
