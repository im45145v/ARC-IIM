"""
Property-based tests for search and filter functionality.

Tests correctness properties for multi-filter support and search functionality.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlalchemy.orm import Session

from alumni_system.database.crud import create_alumni, get_all_alumni, search_alumni
from alumni_system.database.models import Alumni


# =============================================================================
# GENERATORS
# =============================================================================

@st.composite
def alumni_data(draw):
    """Generate random alumni data."""
    batches = ["2018", "2019", "2020", "2021", "2022"]
    companies = ["Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Tesla"]
    locations = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai"]
    names = ["John Smith", "Jane Doe", "Alice Johnson", "Bob Williams", "Charlie Brown", 
             "David Miller", "Emma Davis", "Frank Wilson", "Grace Taylor", "Henry Anderson"]
    
    return {
        "name": draw(st.sampled_from(names)),
        "roll_number": draw(st.text(min_size=5, max_size=20, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")),
        "batch": draw(st.sampled_from(batches)),
        "current_company": draw(st.sampled_from(companies)),
        "location": draw(st.sampled_from(locations)),
        "current_designation": draw(st.sampled_from(["Software Engineer", "Data Scientist", "Product Manager", "Designer"])),
    }


# =============================================================================
# PROPERTY TESTS
# =============================================================================

@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    alumni_list=st.lists(alumni_data(), min_size=5, max_size=20),
    filter_batch=st.sampled_from(["2018", "2019", "2020", "2021", "2022"]),
    filter_company=st.sampled_from(["Google", "Microsoft", "Amazon", "Apple", "Meta"]),
    filter_location=st.sampled_from(["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune"]),
)
def test_property_26_multiple_filters_return_intersection(
    db_session: Session,
    alumni_list: list,
    filter_batch: str,
    filter_company: str,
    filter_location: str,
):
    """
    **Feature: alumni-management-system, Property 26: Multiple filters return intersection**
    **Validates: Requirements 4.3**
    
    Property: For any combination of filters (batch, company, location), 
    the results should match all filter criteria simultaneously.
    
    This tests that when multiple filters are applied, the system returns
    only alumni that satisfy ALL filter conditions (AND logic, not OR).
    """
    # Create alumni records
    created_alumni = []
    for alumni_data_dict in alumni_list:
        try:
            alumni = create_alumni(db_session, **alumni_data_dict)
            created_alumni.append(alumni)
        except Exception:
            # Skip duplicates
            pass
    
    # Apply multiple filters
    results = get_all_alumni(
        db_session,
        skip=0,
        limit=1000,
        batch=filter_batch,
        company=filter_company,
        location=filter_location,
    )
    
    # Verify all results match ALL filter criteria
    for alumni in results:
        assert alumni.batch == filter_batch, (
            f"Alumni {alumni.name} has batch {alumni.batch}, expected {filter_batch}"
        )
        assert filter_company.lower() in (alumni.current_company or "").lower(), (
            f"Alumni {alumni.name} has company {alumni.current_company}, expected to contain {filter_company}"
        )
        assert filter_location.lower() in (alumni.location or "").lower(), (
            f"Alumni {alumni.name} has location {alumni.location}, expected to contain {filter_location}"
        )


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    alumni_list=st.lists(alumni_data(), min_size=5, max_size=20),
    search_term=st.sampled_from(["Google", "Microsoft", "John", "Smith", "Engineer"]),
)
def test_property_27_search_results_contain_search_term(
    db_session: Session,
    alumni_list: list,
    search_term: str,
):
    """
    **Feature: alumni-management-system, Property 27: Search results contain search term**
    **Validates: Requirements 4.4**
    
    Property: For any search query Q, all returned alumni should have Q as a 
    substring in either name or current_company.
    
    This tests that the search functionality correctly filters results to only
    include alumni whose name or company contains the search term.
    """
    # Create alumni records
    created_alumni = []
    for alumni_data_dict in alumni_list:
        try:
            alumni = create_alumni(db_session, **alumni_data_dict)
            created_alumni.append(alumni)
        except Exception:
            # Skip duplicates
            pass
    
    # Perform search
    results = search_alumni(db_session, search_term, skip=0, limit=1000)
    
    # Verify all results contain the search term in name or company
    search_term_lower = search_term.lower()
    for alumni in results:
        name_match = search_term_lower in (alumni.name or "").lower()
        company_match = search_term_lower in (alumni.current_company or "").lower()
        
        assert name_match or company_match, (
            f"Alumni {alumni.name} (company: {alumni.current_company}) does not contain "
            f"search term '{search_term}' in name or company"
        )


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    alumni_list=st.lists(alumni_data(), min_size=5, max_size=20),
    search_term=st.sampled_from(["Google", "Microsoft", "Amazon"]),
    filter_batch=st.sampled_from(["2018", "2019", "2020", "2021", "2022"]),
    filter_location=st.sampled_from(["Bangalore", "Mumbai", "Delhi"]),
)
def test_property_combined_search_and_filters(
    db_session: Session,
    alumni_list: list,
    search_term: str,
    filter_batch: str,
    filter_location: str,
):
    """
    Property: Search combined with filters should return intersection.
    
    This tests that when both search and filters are applied, the system
    returns only alumni that match the search term AND all filter criteria.
    """
    # Create alumni records
    created_alumni = []
    for alumni_data_dict in alumni_list:
        try:
            alumni = create_alumni(db_session, **alumni_data_dict)
            created_alumni.append(alumni)
        except Exception:
            # Skip duplicates
            pass
    
    # Apply search with filters
    results = search_alumni(
        db_session,
        search_term,
        skip=0,
        limit=1000,
        batch=filter_batch,
        location=filter_location,
    )
    
    # Verify all results match search term AND all filters
    search_term_lower = search_term.lower()
    for alumni in results:
        # Check search term
        name_match = search_term_lower in (alumni.name or "").lower()
        company_match = search_term_lower in (alumni.current_company or "").lower()
        assert name_match or company_match, (
            f"Alumni {alumni.name} does not contain search term '{search_term}'"
        )
        
        # Check filters
        assert alumni.batch == filter_batch, (
            f"Alumni {alumni.name} has batch {alumni.batch}, expected {filter_batch}"
        )
        assert filter_location.lower() in (alumni.location or "").lower(), (
            f"Alumni {alumni.name} has location {alumni.location}, expected to contain {filter_location}"
        )
