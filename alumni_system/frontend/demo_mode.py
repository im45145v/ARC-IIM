"""
Demo mode data for the Alumni Management System frontend.

Provides sample data when database is not available.
"""

from typing import List, Dict, Any


def get_demo_alumni() -> List[Dict[str, Any]]:
    """
    Get sample alumni data for demo mode.
    
    Returns:
        List of alumni dictionaries
    """
    return [
        {
            "id": 1,
            "name": "John Doe",
            "batch": "2020",
            "roll_number": "2020001",
            "current_company": "Google",
            "current_designation": "Software Engineer",
            "location": "San Francisco, CA",
            "personal_email": "john.doe@example.com",
            "linkedin_url": "https://www.linkedin.com/in/johndoe",
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "batch": "2020",
            "roll_number": "2020002",
            "current_company": "Microsoft",
            "current_designation": "Product Manager",
            "location": "Seattle, WA",
            "personal_email": "jane.smith@example.com",
            "linkedin_url": "https://www.linkedin.com/in/janesmith",
        },
        {
            "id": 3,
            "name": "Bob Johnson",
            "batch": "2019",
            "roll_number": "2019001",
            "current_company": "Amazon",
            "current_designation": "Data Scientist",
            "location": "Seattle, WA",
            "personal_email": "bob.johnson@example.com",
            "linkedin_url": "https://www.linkedin.com/in/bobjohnson",
        },
        {
            "id": 4,
            "name": "Alice Williams",
            "batch": "2019",
            "roll_number": "2019002",
            "current_company": "Meta",
            "current_designation": "Software Engineer",
            "location": "Menlo Park, CA",
            "personal_email": "alice.williams@example.com",
            "linkedin_url": "https://www.linkedin.com/in/alicewilliams",
        },
        {
            "id": 5,
            "name": "Charlie Brown",
            "batch": "2021",
            "roll_number": "2021001",
            "current_company": "Apple",
            "current_designation": "iOS Developer",
            "location": "Cupertino, CA",
            "personal_email": "charlie.brown@example.com",
            "linkedin_url": "https://www.linkedin.com/in/charliebrown",
        },
    ]


def get_demo_stats() -> Dict[str, Any]:
    """
    Get sample statistics for demo mode.
    
    Returns:
        Dictionary with statistics
    """
    return {
        "total_alumni": 5,
        "batches": ["2019", "2020", "2021"],
        "companies": ["Google", "Microsoft", "Amazon", "Meta", "Apple"],
        "locations": ["San Francisco, CA", "Seattle, WA", "Menlo Park, CA", "Cupertino, CA"],
    }


def get_demo_job_history(alumni_id: int) -> List[Dict[str, Any]]:
    """
    Get sample job history for demo mode.
    
    Args:
        alumni_id: ID of alumni
    
    Returns:
        List of job history dictionaries
    """
    if alumni_id == 1:
        return [
            {
                "company_name": "Google",
                "designation": "Software Engineer",
                "location": "San Francisco, CA",
                "start_date": "2022-01-01",
                "end_date": None,
                "is_current": True,
                "employment_type": "Full-time",
            },
            {
                "company_name": "Startup Inc",
                "designation": "Junior Developer",
                "location": "San Francisco, CA",
                "start_date": "2020-06-01",
                "end_date": "2021-12-31",
                "is_current": False,
                "employment_type": "Full-time",
            },
        ]
    return []


def get_demo_education_history(alumni_id: int) -> List[Dict[str, Any]]:
    """
    Get sample education history for demo mode.
    
    Args:
        alumni_id: ID of alumni
    
    Returns:
        List of education history dictionaries
    """
    if alumni_id == 1:
        return [
            {
                "institution_name": "Sample University",
                "degree": "Bachelor of Technology",
                "field_of_study": "Computer Science",
                "start_year": 2016,
                "end_year": 2020,
                "grade": "3.8 GPA",
            },
        ]
    return []
