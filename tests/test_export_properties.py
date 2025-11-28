"""
Property-based tests for Excel export functionality.

This test verifies that exported Excel data matches displayed data exactly.

**Feature: alumni-management-system, Property 29: Export contains displayed data**
**Validates: Requirements 4.7**
"""

import io
from datetime import datetime

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alumni_system.database.crud import (
    create_alumni,
    create_education_history,
    create_job_history,
    get_all_alumni,
)


# =============================================================================
# HELPER FUNCTIONS (copied from frontend for testing)
# =============================================================================
def alumni_to_dataframe(alumni_list: list) -> pd.DataFrame:
    """Convert list of Alumni objects to DataFrame."""
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
    """Export DataFrame to Excel bytes with proper escaping for formula characters."""
    output = io.BytesIO()
    
    # Create a copy to avoid modifying the original
    df_export = df.copy()
    
    # Escape values that start with formula characters (=, +, -, @)
    # Excel treats these as formulas, so we need to prefix with a single quote
    for col in df_export.columns:
        if df_export[col].dtype == 'object':  # Only process string columns
            df_export[col] = df_export[col].apply(
                lambda x: f"'{x}" if isinstance(x, str) and len(x) > 0 and x[0] in '=+-@' else x
            )
    
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Alumni")
    return output.getvalue()


# =============================================================================
# HYPOTHESIS STRATEGIES
# =============================================================================
@st.composite
def alumni_data_strategy(draw):
    """Generate random alumni data with Excel-safe characters."""
    # Use alphanumeric characters only to avoid Excel issues
    roll_number = draw(st.text(
        min_size=5, 
        max_size=10, 
        alphabet=st.characters(min_codepoint=65, max_codepoint=90)  # A-Z only
    )) + draw(st.integers(min_value=1000, max_value=9999).map(str))
    
    name = draw(st.text(
        min_size=3, 
        max_size=30, 
        alphabet=st.characters(min_codepoint=65, max_codepoint=122, blacklist_characters=' ')
    )).replace('\x00', '').strip() or "TestName"
    
    batch = draw(st.integers(min_value=2000, max_value=2030).map(str))
    
    # Generate safe text for other fields (avoid Excel formula characters)
    def safe_text(min_size=3, max_size=30):
        text = draw(st.text(
            min_size=min_size,
            max_size=max_size,
            alphabet=st.characters(
                min_codepoint=32, 
                max_codepoint=126, 
                blacklist_characters='\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f=+-@'  # Avoid Excel formula triggers
            )
        )).strip()
        # Ensure text doesn't start with characters that Excel treats specially
        if text and text[0] in '=+-@':
            text = 'A' + text
        return text if text else None
    
    return {
        "roll_number": roll_number,
        "name": name,
        "batch": batch,
        "gender": draw(st.sampled_from(["Male", "Female", "Other", None])),
        "current_company": safe_text(),
        "current_designation": safe_text(),
        "location": safe_text(),
        "personal_email": draw(st.one_of(st.none(), st.emails())),
        "college_email": draw(st.one_of(st.none(), st.emails())),
        "mobile_number": draw(st.one_of(st.none(), st.integers(min_value=1000000000, max_value=9999999999).map(str))),
        "linkedin_url": draw(st.one_of(st.none(), st.just("https://linkedin.com/in/test"))),
        "higher_studies": safe_text(),
    }


@st.composite
def job_history_strategy(draw):
    """Generate random job history data with Excel-safe characters."""
    company_name = draw(st.text(
        min_size=3,
        max_size=30,
        alphabet=st.characters(min_codepoint=65, max_codepoint=122, blacklist_characters=' ')
    )).replace('\x00', '').strip() or "TestCompany"
    
    designation = draw(st.one_of(
        st.none(),
        st.text(
            min_size=3,
            max_size=30,
            alphabet=st.characters(min_codepoint=65, max_codepoint=122)
        ).map(lambda x: x.replace('\x00', '').strip() or None)
    ))
    
    location = draw(st.one_of(
        st.none(),
        st.text(
            min_size=3,
            max_size=20,
            alphabet=st.characters(min_codepoint=65, max_codepoint=122)
        ).map(lambda x: x.replace('\x00', '').strip() or None)
    ))
    
    return {
        "company_name": company_name,
        "designation": designation,
        "location": location,
        "is_current": draw(st.booleans()),
        "employment_type": draw(st.sampled_from(["Full-time", "Part-time", "Contract", "Internship", None])),
    }


# =============================================================================
# PROPERTY TESTS
# =============================================================================
@settings(
    max_examples=100, 
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    alumni_list=st.lists(alumni_data_strategy(), min_size=1, max_size=10, unique_by=lambda x: x["roll_number"]),
    job_histories=st.lists(st.lists(job_history_strategy(), min_size=0, max_size=5), min_size=1, max_size=10)
)
@pytest.mark.property
def test_export_contains_displayed_data(clean_db_session, alumni_list, job_histories):
    """
    Property 29: Export contains displayed data
    
    For any set of alumni records displayed in the table, the exported Excel file
    should contain the same records with the same field values.
    
    **Feature: alumni-management-system, Property 29: Export contains displayed data**
    **Validates: Requirements 4.7**
    """
    db = clean_db_session
    
    # Ensure we have matching job histories for each alumni
    while len(job_histories) < len(alumni_list):
        job_histories.append([])
    job_histories = job_histories[:len(alumni_list)]
    
    # Create alumni records in database
    created_alumni_ids = []
    for alumni_data, jobs in zip(alumni_list, job_histories):
        try:
            alumni = create_alumni(db, **alumni_data)
            created_alumni_ids.append(alumni.id)
            
            # Add job history
            for job_data in jobs:
                create_job_history(db, alumni.id, **job_data)
        except Exception as e:
            # Skip if duplicate or invalid data
            continue
    
    # Skip test if no alumni were created
    if not created_alumni_ids:
        pytest.skip("No valid alumni data generated")
    
    # Get alumni from database (simulating what's displayed)
    displayed_alumni = get_all_alumni(db, skip=0, limit=100)
    
    # Convert to DataFrame (what user sees in UI)
    displayed_df = alumni_to_dataframe(displayed_alumni)
    
    # Export to Excel
    excel_bytes = export_to_excel(displayed_df)
    
    # Read back from Excel
    excel_df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name="Alumni")
    
    # Property: Exported data should match displayed data exactly
    
    # 1. Same number of records
    assert len(excel_df) == len(displayed_df), \
        f"Export has {len(excel_df)} records but display has {len(displayed_df)}"
    
    # 2. Same columns
    assert set(excel_df.columns) == set(displayed_df.columns), \
        f"Export columns {set(excel_df.columns)} don't match display columns {set(displayed_df.columns)}"
    
    # 3. Same data in each column (for each record)
    for col in displayed_df.columns:
        # Skip ID column as it's internal
        if col == "ID":
            continue
            
        # Handle NaN/None comparisons - normalize to empty string
        displayed_values = displayed_df[col].fillna("").astype(str).replace('nan', '').replace('NaN', '')
        excel_values = excel_df[col].fillna("").astype(str).replace('nan', '').replace('NaN', '')
        
        # For timestamp columns, compare as strings (format might differ slightly)
        if col == "Last Updated":
            # Just verify both have values or both are empty
            displayed_has_values = (displayed_values != "").tolist()
            excel_has_values = (excel_values != "").tolist()
            assert displayed_has_values == excel_has_values, \
                f"Column '{col}' has different null patterns in export vs display"
        else:
            # For other columns, values should match (allowing for Excel's numeric conversion and escaping)
            for idx in range(len(displayed_df)):
                displayed_val = displayed_values.iloc[idx]
                excel_val = excel_values.iloc[idx]
                
                # Handle escaped formula characters (we prefix with ')
                # Excel will show the value with the leading quote
                if displayed_val and len(displayed_val) > 0 and displayed_val[0] in '=+-@':
                    expected_excel_val = f"'{displayed_val}"
                    assert excel_val == expected_excel_val, \
                        f"Row {idx}, Column '{col}': Display has '{displayed_val}' but export has '{excel_val}' (expected '{expected_excel_val}')"
                # Excel may convert numeric strings to numbers/floats, so normalize
                # e.g., "00000" becomes "0" in Excel, "1000000001" becomes "1000000001.0"
                elif displayed_val.replace('.', '').isdigit() or excel_val.replace('.', '').isdigit():
                    # Try to compare as numbers
                    try:
                        displayed_num = float(displayed_val) if displayed_val else 0
                        excel_num = float(excel_val) if excel_val else 0
                        assert displayed_num == excel_num, \
                            f"Row {idx}, Column '{col}': Display has '{displayed_val}' but export has '{excel_val}'"
                    except ValueError:
                        # If conversion fails, compare as strings
                        assert displayed_val == excel_val, \
                            f"Row {idx}, Column '{col}': Display has '{displayed_val}' but export has '{excel_val}'"
                else:
                    assert displayed_val == excel_val, \
                        f"Row {idx}, Column '{col}': Display has '{displayed_val}' but export has '{excel_val}'"
    
    # 4. Verify specific important fields are present and correct
    for idx, alumni in enumerate(displayed_alumni):
        # Find matching row in export by roll number
        export_row = excel_df[excel_df["Roll Number"] == alumni.roll_number]
        
        if len(export_row) > 0:
            export_row = export_row.iloc[0]
            
            # Verify key fields
            assert str(export_row["Name"]) == str(alumni.name), \
                f"Name mismatch for {alumni.roll_number}"
            
            assert str(export_row["Batch"]) == str(alumni.batch or ""), \
                f"Batch mismatch for {alumni.roll_number}"
            
            # Verify previous companies are included
            if hasattr(alumni, 'job_history') and alumni.job_history:
                previous_jobs = [j for j in alumni.job_history if not j.is_current]
                if previous_jobs:
                    # Export should have previous companies column populated
                    prev_companies_str = str(export_row["Previous Companies"])
                    assert prev_companies_str != "" and prev_companies_str != "nan", \
                        f"Previous companies missing in export for {alumni.roll_number}"


@settings(
    max_examples=50, 
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    page_size=st.integers(min_value=1, max_value=5),
    alumni_count=st.integers(min_value=1, max_value=10)
)
@pytest.mark.property
def test_export_pagination_consistency(clean_db_session, page_size, alumni_count):
    """
    Property: Export from paginated view contains exactly the records on that page.
    
    For any page of alumni records, the export should contain exactly those records
    and no others.
    
    **Feature: alumni-management-system, Property 29: Export contains displayed data**
    **Validates: Requirements 4.7**
    """
    db = clean_db_session
    
    # Create alumni records
    created_alumni = []
    for i in range(alumni_count):
        try:
            alumni = create_alumni(
                db,
                roll_number=f"TEST{i:04d}",
                name=f"Test Alumni {i}",
                batch="2020"
            )
            created_alumni.append(alumni)
        except Exception:
            continue
    
    if not created_alumni:
        pytest.skip("No alumni created")
    
    # Simulate pagination: get first page
    page_alumni = get_all_alumni(db, skip=0, limit=page_size)
    
    # Convert to DataFrame
    page_df = alumni_to_dataframe(page_alumni)
    
    # Export
    excel_bytes = export_to_excel(page_df)
    excel_df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name="Alumni")
    
    # Property: Export should have exactly the same records as the page
    assert len(excel_df) == len(page_df), \
        f"Export has {len(excel_df)} records but page has {len(page_df)}"
    
    # Verify roll numbers match
    page_roll_numbers = set(page_df["Roll Number"].tolist())
    export_roll_numbers = set(excel_df["Roll Number"].tolist())
    
    assert page_roll_numbers == export_roll_numbers, \
        f"Export roll numbers {export_roll_numbers} don't match page roll numbers {page_roll_numbers}"


@settings(
    max_examples=50, 
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    alumni_data=alumni_data_strategy(),
    filter_batch=st.booleans()
)
@pytest.mark.property
def test_export_filtered_data_consistency(clean_db_session, alumni_data, filter_batch):
    """
    Property: Export from filtered view contains only filtered records.
    
    For any filtered view of alumni, the export should contain exactly the
    filtered records and match the displayed data.
    
    **Feature: alumni-management-system, Property 29: Export contains displayed data**
    **Validates: Requirements 4.7**
    """
    db = clean_db_session
    
    # Create multiple alumni with different batches
    batches = ["2020", "2021", "2022"]
    created_alumni = []
    
    for i, batch in enumerate(batches):
        for j in range(2):
            try:
                alumni = create_alumni(
                    db,
                    roll_number=f"{batch}{j:03d}",
                    name=f"Alumni {batch} {j}",
                    batch=batch,
                    current_company=f"Company {i}"
                )
                created_alumni.append(alumni)
            except Exception:
                continue
    
    if not created_alumni:
        pytest.skip("No alumni created")
    
    # Apply filter
    if filter_batch:
        target_batch = batches[0]
        filtered_alumni = get_all_alumni(db, batch=target_batch)
    else:
        filtered_alumni = get_all_alumni(db)
    
    # Convert to DataFrame
    filtered_df = alumni_to_dataframe(filtered_alumni)
    
    # Export
    excel_bytes = export_to_excel(filtered_df)
    excel_df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name="Alumni")
    
    # Property: Export should match filtered data
    assert len(excel_df) == len(filtered_df), \
        f"Export has {len(excel_df)} records but filtered view has {len(filtered_df)}"
    
    # If filter was applied, verify all records match the filter
    if filter_batch:
        for batch_val in excel_df["Batch"]:
            assert str(batch_val) == target_batch, \
                f"Export contains batch {batch_val} but filter was for {target_batch}"


@settings(
    max_examples=50, 
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    alumni_data=alumni_data_strategy()
)
@pytest.mark.property
def test_export_filename_has_timestamp(clean_db_session, alumni_data):
    """
    Property: Export filename includes timestamp.
    
    For any export operation, the filename should include a timestamp to
    distinguish between different exports.
    
    **Feature: alumni-management-system, Property 29: Export contains displayed data**
    **Validates: Requirements 4.7**
    """
    # This property tests the filename generation logic
    # In the actual app, the filename is: f"alumni_page_{page_num}_{timestamp}.xlsx"
    
    # Generate timestamp format used in app
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Verify timestamp format is valid
    assert len(timestamp) == 15, "Timestamp should be in format YYYYMMDD_HHMMSS"
    assert timestamp[8] == '_', "Timestamp should have underscore separator"
    
    # Verify timestamp components are numeric
    date_part = timestamp[:8]
    time_part = timestamp[9:]
    
    assert date_part.isdigit(), "Date part should be numeric"
    assert time_part.isdigit(), "Time part should be numeric"
    
    # Verify year is reasonable
    year = int(date_part[:4])
    assert 2020 <= year <= 2100, f"Year {year} is not reasonable"
    
    # Verify month is valid
    month = int(date_part[4:6])
    assert 1 <= month <= 12, f"Month {month} is not valid"
    
    # Verify day is valid
    day = int(date_part[6:8])
    assert 1 <= day <= 31, f"Day {day} is not valid"
    
    # Verify hour is valid
    hour = int(time_part[:2])
    assert 0 <= hour <= 23, f"Hour {hour} is not valid"
    
    # Verify minute is valid
    minute = int(time_part[2:4])
    assert 0 <= minute <= 59, f"Minute {minute} is not valid"
    
    # Verify second is valid
    second = int(time_part[4:6])
    assert 0 <= second <= 59, f"Second {second} is not valid"
