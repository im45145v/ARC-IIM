"""
Alumni Management System - Streamlit Frontend
=============================================

A comprehensive Streamlit application for managing alumni data including:
- Alumni data browsing and filtering
- Export to Excel functionality
- Admin interface for manual updates
- NLP chatbot for queries
"""

import io
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import alumni system modules
DB_AVAILABLE = False
_import_error = None

try:
    from alumni_system.chatbot.nlp_chatbot import get_chatbot
    from alumni_system.database.connection import get_db_context
    from alumni_system.database.crud import (
        create_alumni,
        delete_alumni,
        get_all_alumni,
        get_alumni_by_id,
        get_alumni_by_roll_number,
        get_alumni_count,
        get_job_history_by_alumni,
        get_scraping_logs,
        get_unique_batches,
        get_unique_companies,
        get_unique_locations,
        search_alumni,
        update_alumni,
    )
    from alumni_system.database.init_db import check_database_connection, init_database
    from alumni_system.database.models import Alumni

    DB_AVAILABLE = True
except ImportError as e:
    _import_error = str(e)
    DB_AVAILABLE = False


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Alumni Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# CUSTOM STYLING
# =============================================================================
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .header-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .header-title {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .header-subtitle {
        color: #a0aec0;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid #1e3a5f;
    }
    
    /* Chat styling */
    .chat-message {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    }
    
    .chat-user {
        background: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    
    .chat-bot {
        background: #f3e5f5;
        border-left: 4px solid #7b1fa2;
    }
    
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Button styling */
    .stButton > button {
        background-color: #1e3a5f;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    
    .stButton > button:hover {
        background-color: #2d4a6f;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_alumni" not in st.session_state:
    st.session_state.selected_alumni = None


# =============================================================================
# HELPER FUNCTIONS
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
# SIDEBAR NAVIGATION
# =============================================================================
def render_sidebar() -> str:
    """Render sidebar with navigation."""
    st.sidebar.markdown("## 🎓 Alumni System")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "👥 Browse Alumni",
            "🔍 Search & Filter",
            "📋 Alumni Details",
            "💬 Chatbot",
            "⚙️ Admin Panel",
        ],
        label_visibility="collapsed",
    )
    
    st.sidebar.markdown("---")
    
    # Database status
    st.sidebar.markdown("### 📁 Database Status")
    if DB_AVAILABLE:
        try:
            if check_database_connection():
                st.sidebar.success("✅ Connected")
            else:
                st.sidebar.error("❌ Connection Failed")
        except Exception:
            st.sidebar.warning("⚠️ Not Configured")
    else:
        st.sidebar.info("ℹ️ Demo Mode")
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Alumni Management System v1.0")
    
    return page


# =============================================================================
# PAGE RENDERERS
# =============================================================================
def render_dashboard():
    """Render the dashboard page."""
    st.markdown("""
    <div class="header-card">
        <h1 class="header-title">🎓 Alumni Management Dashboard</h1>
        <p class="header-subtitle">Overview of alumni data and system status</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Database connection status indicator
    if DB_AVAILABLE:
        try:
            db_connected = check_database_connection()
            if db_connected:
                st.success("✅ Database Connected")
            else:
                st.error("❌ Database Connection Failed")
                st.info("Please check your database configuration in environment variables.")
        except Exception as e:
            st.warning(f"⚠️ Database Status Unknown: {str(e)}")
            db_connected = False
    else:
        st.info("ℹ️ Running in Demo Mode - Database not configured")
        db_connected = False
    
    st.markdown("---")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    if DB_AVAILABLE and db_connected:
        try:
            with get_db_context() as db:
                # Use efficient count function instead of loading all records
                total_count = get_alumni_count(db)
                batches = get_unique_batches(db)
                companies = get_unique_companies(db)
                locations = get_unique_locations(db)
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
            total_count = 0
            batches = []
            companies = []
            locations = []
    else:
        total_count = 0
        batches = []
        companies = []
        locations = []
    
    with col1:
        st.metric("📊 Total Alumni", total_count)
    
    with col2:
        st.metric("🎒 Batches", len(batches))
    
    with col3:
        st.metric("🏢 Companies", len(companies))
    
    with col4:
        st.metric("📍 Locations", len(locations))
    
    st.markdown("---")
    
    # Quick stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Quick Stats")
        if batches:
            st.write(f"**Batches:** {', '.join(sorted(batches)[:5])}" + 
                    ("..." if len(batches) > 5 else ""))
        if companies:
            st.write(f"**Top Companies:** {', '.join(sorted(companies)[:5])}" +
                    ("..." if len(companies) > 5 else ""))
    
    with col2:
        st.markdown("### 🔄 Recent Activity")
        st.info("System initialized. Configure database to see activity.")
    
    # Getting started
    st.markdown("---")
    st.markdown("### 🚀 Getting Started")
    st.markdown("""
    1. **Configure Database**: Set up PostgreSQL and configure environment variables
    2. **Import Data**: Upload your alumni data CSV or add records manually
    3. **Set up LinkedIn Scraping**: Configure LinkedIn credentials for profile updates
    4. **Configure B2 Storage**: Set up Backblaze B2 for PDF storage
    5. **Use the Chatbot**: Ask natural language questions about alumni
    """)


def render_browse_alumni():
    """Render the browse alumni page with pagination."""
    st.markdown("### 👥 Browse Alumni")
    
    if not DB_AVAILABLE:
        st.warning("Database not configured. Please set up environment variables.")
        return
    
    try:
        with get_db_context() as db:
            # Get total count for pagination
            total_records = get_alumni_count(db)
            
            # Initialize session state for pagination if not exists
            if "browse_page_num" not in st.session_state:
                st.session_state.browse_page_num = 1
            if "browse_page_size" not in st.session_state:
                st.session_state.browse_page_size = 25
            
            # Pagination controls at the top
            st.markdown("#### Pagination Controls")
            col1, col2, col3 = st.columns([2, 2, 3])
            
            with col1:
                # Page size selector
                page_size = st.selectbox(
                    "Records per page", 
                    [25, 50, 100], 
                    index=[25, 50, 100].index(st.session_state.browse_page_size),
                    key="page_size_selector"
                )
                
                # Update session state if page size changed
                if page_size != st.session_state.browse_page_size:
                    st.session_state.browse_page_size = page_size
                    st.session_state.browse_page_num = 1  # Reset to first page
                    st.rerun()
            
            with col2:
                # Calculate total pages
                total_pages = math.ceil(total_records / page_size) if total_records > 0 else 0
                
                # Page number input
                page_num = st.number_input(
                    f"Page (1-{total_pages})", 
                    min_value=1, 
                    max_value=max(1, total_pages),
                    value=min(st.session_state.browse_page_num, max(1, total_pages)),
                    step=1,
                    key="page_num_input"
                )
                
                # Update session state if page number changed
                if page_num != st.session_state.browse_page_num:
                    st.session_state.browse_page_num = page_num
                    st.rerun()
            
            with col3:
                # Display pagination info
                if total_records > 0:
                    start_record = (st.session_state.browse_page_num - 1) * page_size + 1
                    end_record = min(st.session_state.browse_page_num * page_size, total_records)
                    st.info(f"📊 Showing {start_record}-{end_record} of {total_records} records | Page {st.session_state.browse_page_num} of {total_pages}")
                else:
                    st.info("📊 No records found")
            
            # Navigation buttons
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮️ First", disabled=(st.session_state.browse_page_num == 1), use_container_width=True):
                    st.session_state.browse_page_num = 1
                    st.rerun()
            
            with col2:
                if st.button("◀️ Previous", disabled=(st.session_state.browse_page_num == 1), use_container_width=True):
                    st.session_state.browse_page_num = max(1, st.session_state.browse_page_num - 1)
                    st.rerun()
            
            with col3:
                st.empty()  # Spacer
            
            with col4:
                if st.button("Next ▶️", disabled=(st.session_state.browse_page_num >= total_pages), use_container_width=True):
                    st.session_state.browse_page_num = min(total_pages, st.session_state.browse_page_num + 1)
                    st.rerun()
            
            with col5:
                if st.button("Last ⏭️", disabled=(st.session_state.browse_page_num >= total_pages), use_container_width=True):
                    st.session_state.browse_page_num = total_pages
                    st.rerun()
            
            st.markdown("---")
            
            # Fetch and display current page of records
            if total_records > 0:
                skip = (st.session_state.browse_page_num - 1) * page_size
                alumni_list = get_all_alumni(db, skip=skip, limit=page_size)
                
                if alumni_list:
                    df = alumni_to_dataframe(alumni_list)
                    
                    # Display table
                    st.dataframe(df, use_container_width=True, height=500)
                    
                    # Export button
                    excel_data = export_to_excel(df)
                    st.download_button(
                        label="📥 Export Current Page to Excel",
                        data=excel_data,
                        file_name=f"alumni_page_{st.session_state.browse_page_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                else:
                    st.info("No alumni records found on this page.")
            else:
                st.info("No alumni records found. Add some records in the Admin Panel.")
    
    except Exception as e:
        st.error(f"Error loading alumni data: {e}")


def render_search_filter():
    """Render the search and filter page."""
    st.markdown("### 🔍 Search & Filter Alumni")
    
    if not DB_AVAILABLE:
        st.warning("Database not configured. Please set up environment variables.")
        return
    
    try:
        with get_db_context() as db:
            # Initialize session state for filters if not exists
            if "filter_batch" not in st.session_state:
                st.session_state.filter_batch = "All"
            if "filter_company" not in st.session_state:
                st.session_state.filter_company = "All"
            if "filter_location" not in st.session_state:
                st.session_state.filter_location = "All"
            if "filter_search_query" not in st.session_state:
                st.session_state.filter_search_query = ""
            
            # Filter options
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
            
            batches = ["All"] + get_unique_batches(db)
            companies = ["All"] + get_unique_companies(db)
            locations = ["All"] + get_unique_locations(db)
            
            with col1:
                selected_batch = st.selectbox(
                    "Batch", 
                    batches,
                    index=batches.index(st.session_state.filter_batch) if st.session_state.filter_batch in batches else 0,
                    key="batch_selector"
                )
                st.session_state.filter_batch = selected_batch
            
            with col2:
                selected_company = st.selectbox(
                    "Company", 
                    companies,
                    index=companies.index(st.session_state.filter_company) if st.session_state.filter_company in companies else 0,
                    key="company_selector"
                )
                st.session_state.filter_company = selected_company
            
            with col3:
                selected_location = st.selectbox(
                    "Location", 
                    locations,
                    index=locations.index(st.session_state.filter_location) if st.session_state.filter_location in locations else 0,
                    key="location_selector"
                )
                st.session_state.filter_location = selected_location
            
            with col4:
                search_query = st.text_input(
                    "Search Name/Company",
                    value=st.session_state.filter_search_query,
                    key="search_input"
                )
                st.session_state.filter_search_query = search_query
            
            with col5:
                # Reset button
                st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state.filter_batch = "All"
                    st.session_state.filter_company = "All"
                    st.session_state.filter_location = "All"
                    st.session_state.filter_search_query = ""
                    st.rerun()
            
            # Apply filters - combine filters AND search
            filters = {}
            if selected_batch != "All":
                filters["batch"] = selected_batch
            if selected_company != "All":
                filters["company"] = selected_company
            if selected_location != "All":
                filters["location"] = selected_location
            
            # Get results with both filters and search
            if search_query:
                # Apply search with filters
                results = search_alumni(db, search_query, skip=0, limit=1000, **filters)
            else:
                # Apply only filters
                results = get_all_alumni(db, skip=0, limit=1000, **filters)
            
            # Display result count
            st.markdown("---")
            result_count = len(results)
            
            # Show active filters
            active_filters = []
            if selected_batch != "All":
                active_filters.append(f"Batch: {selected_batch}")
            if selected_company != "All":
                active_filters.append(f"Company: {selected_company}")
            if selected_location != "All":
                active_filters.append(f"Location: {selected_location}")
            if search_query:
                active_filters.append(f"Search: '{search_query}'")
            
            if active_filters:
                st.info(f"🔍 Active filters: {' | '.join(active_filters)}")
            
            st.markdown(f"### 📊 Found {result_count} alumni")
            
            if results:
                df = alumni_to_dataframe(results)
                st.dataframe(df, use_container_width=True, height=400)
                
                # Export button
                excel_data = export_to_excel(df)
                st.download_button(
                    label="📥 Export Results to Excel",
                    data=excel_data,
                    file_name=f"alumni_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                st.info("No alumni found matching the selected criteria. Try adjusting your filters.")
    
    except Exception as e:
        st.error(f"Error searching alumni: {e}")


def render_alumni_details():
    """Render the alumni details page with job history."""
    st.markdown("### 📋 Alumni Details & Career History")
    st.markdown("View detailed information including past companies and roles.")
    
    if not DB_AVAILABLE:
        st.warning("Database not configured. Please set up environment variables.")
        return
    
    try:
        with get_db_context() as db:
            # Alumni selection
            alumni_id = st.number_input("Enter Alumni ID", min_value=1, step=1, value=1)
            
            if st.button("Load Alumni Details"):
                alumni = get_alumni_by_id(db, alumni_id)
                
                if alumni:
                    st.session_state.viewing_alumni_id = alumni_id
                else:
                    st.error("Alumni not found.")
                    return
            
            # Display alumni details if selected
            if hasattr(st.session_state, 'viewing_alumni_id') and st.session_state.viewing_alumni_id:
                alumni = get_alumni_by_id(db, st.session_state.viewing_alumni_id)
                
                if alumni:
                    # Basic Information Card
                    st.markdown("---")
                    st.markdown("#### 👤 Basic Information")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Name:** {alumni.name or 'N/A'}")
                        st.markdown(f"**Batch:** {alumni.batch or 'N/A'}")
                        st.markdown(f"**Roll Number:** {alumni.roll_number or 'N/A'}")
                        st.markdown(f"**Gender:** {alumni.gender or 'N/A'}")
                    
                    with col2:
                        st.markdown(f"**Personal Email:** {alumni.personal_email or 'N/A'}")
                        st.markdown(f"**College Email:** {alumni.college_email or 'N/A'}")
                        st.markdown(f"**Mobile:** {alumni.mobile_number or 'N/A'}")
                        st.markdown(f"**WhatsApp:** {alumni.whatsapp_number or 'N/A'}")
                    
                    with col3:
                        if alumni.linkedin_url:
                            st.markdown(f"**LinkedIn:** [Profile]({alumni.linkedin_url})")
                        else:
                            st.markdown("**LinkedIn:** N/A")
                        
                        # PDF download link if available
                        if alumni.linkedin_pdf_url:
                            st.markdown(f"**LinkedIn PDF:** [Download]({alumni.linkedin_pdf_url})")
                        else:
                            st.markdown("**LinkedIn PDF:** Not available")
                        
                        st.markdown(f"**Higher Studies:** {alumni.higher_studies or 'N/A'}")
                        st.markdown(f"**Location:** {alumni.location or 'N/A'}")
                    
                    # Current Position Card
                    st.markdown("---")
                    st.markdown("#### 💼 Current Position")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Company:** {alumni.current_company or 'N/A'}")
                        st.markdown(f"**Designation:** {alumni.current_designation or 'N/A'}")
                    
                    with col2:
                        st.markdown(f"**Location:** {alumni.location or 'N/A'}")
                        st.markdown(f"**Corporate Email:** {alumni.corporate_email or 'N/A'}")
                    
                    # Job History Card
                    st.markdown("---")
                    st.markdown("#### 📊 Career History (Past Companies & Roles)")
                    
                    job_history = get_job_history_by_alumni(db, alumni.id)
                    
                    if job_history:
                        # Create a table for job history
                        job_data = []
                        for job in job_history:
                            start = job.start_date.strftime("%b %Y") if job.start_date else "N/A"
                            end = job.end_date.strftime("%b %Y") if job.end_date else ("Present" if job.is_current else "N/A")
                            job_data.append({
                                "Company": job.company_name,
                                "Role/Designation": job.designation or "N/A",
                                "Location": job.location or "N/A",
                                "Duration": f"{start} - {end}",
                                "Type": job.employment_type or "Full-time",
                                "Current": "✓" if job.is_current else "",
                            })
                        
                        job_df = pd.DataFrame(job_data)
                        st.dataframe(job_df, use_container_width=True, hide_index=True)
                        
                        # Summary stats
                        total_companies = len(set(j.company_name for j in job_history))
                        st.info(f"📈 Total companies worked at: **{total_companies}** | Total positions: **{len(job_history)}**")
                    else:
                        st.info("No job history records found for this alumni.")
                    
                    # Education History (if available)
                    if alumni.education_history:
                        st.markdown("---")
                        st.markdown("#### 🎓 Education History")
                        
                        edu_data = []
                        for edu in alumni.education_history:
                            edu_data.append({
                                "Institution": edu.institution_name,
                                "Degree": edu.degree or "N/A",
                                "Field of Study": edu.field_of_study or "N/A",
                                "Years": f"{edu.start_year or 'N/A'} - {edu.end_year or 'N/A'}",
                                "Grade": edu.grade or "N/A",
                            })
                        
                        edu_df = pd.DataFrame(edu_data)
                        st.dataframe(edu_df, use_container_width=True, hide_index=True)
                    
                    # Additional Information
                    st.markdown("---")
                    st.markdown("#### 📝 Additional Information")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Internship:** {alumni.internship or 'N/A'}")
                        st.markdown(f"**POR (Positions of Responsibility):** {alumni.por or 'N/A'}")
                    
                    with col2:
                        st.markdown(f"**Notable Alma Mater:** {alumni.notable_alma_mater or 'N/A'}")
                        st.markdown(f"**STEP Programme:** {alumni.step_programme or 'N/A'}")
                    
                    if alumni.remarks:
                        st.markdown(f"**Remarks:** {alumni.remarks}")
    
    except Exception as e:
        st.error(f"Error loading alumni details: {e}")


def render_chatbot():
    """Render the chatbot page."""
    st.markdown("### 💬 Alumni Chatbot")
    st.markdown("Ask questions about alumni in natural language!")
    
    if not DB_AVAILABLE:
        st.warning("Database not configured. Chatbot requires database connection.")
        st.markdown("""
        **Example questions you can ask:**
        - "Who works at Google?"
        - "Find alumni from batch 2020"
        - "Show software engineers"
        - "How many alumni do we have?"
        """)
        return
    
    # Chat history display
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message chat-user">👤 **You:** {message["content"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message chat-bot">🤖 **Bot:** {message["content"]}</div>', 
                       unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Ask a question about alumni...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
        })
        
        # Get chatbot response
        try:
            chatbot = get_chatbot()
            response = chatbot.process_query(user_input)
            
            # Add bot response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response["response"],
            })
            
            # Display alumni results if any
            if response.get("alumni"):
                st.markdown("#### Results:")
                results_df = pd.DataFrame(response["alumni"])
                st.dataframe(results_df, use_container_width=True)
            
        except Exception as e:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Sorry, I encountered an error: {str(e)}",
            })
        
        st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


def render_admin_panel():
    """Render the admin panel page."""
    st.markdown("### ⚙️ Admin Panel")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "➕ Add Alumni",
        "✏️ Edit Alumni",
        "🗑️ Delete Alumni",
        "🔧 Database",
        "🔄 Scraping Control",
        "📋 Scraping Logs",
    ])
    
    with tab1:
        render_add_alumni_form()
    
    with tab2:
        render_edit_alumni_form()
    
    with tab3:
        render_delete_alumni_form()
    
    with tab4:
        render_database_tools()
    
    with tab5:
        render_scraping_control()
    
    with tab6:
        render_scraping_logs()


def render_add_alumni_form():
    """Render form to add new alumni with validation."""
    st.markdown("#### Add New Alumni")
    st.markdown("Fill in the required fields to add a new alumni record.")
    
    if not DB_AVAILABLE:
        st.warning("Database not configured.")
        return
    
    with st.form("add_alumni_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *", help="Required field")
            batch = st.text_input("Batch (e.g., 2020)")
            roll_number = st.text_input("Roll Number *", help="Required field - must be unique")
            gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
            mobile = st.text_input("Mobile Number")
            personal_email = st.text_input("Personal Email")
        
        with col2:
            current_company = st.text_input("Current Company")
            current_designation = st.text_input("Current Designation")
            location = st.text_input("Location")
            linkedin_url = st.text_input("LinkedIn URL")
            college_email = st.text_input("College Email")
            higher_studies = st.text_input("Higher Studies")
        
        submitted = st.form_submit_button("➕ Add Alumni", type="primary")
        
        if submitted:
            # Validation
            if not name or not roll_number:
                st.error("❌ Name and Roll Number are required fields.")
            elif not name.strip():
                st.error("❌ Name cannot be empty or whitespace only.")
            elif not roll_number.strip():
                st.error("❌ Roll Number cannot be empty or whitespace only.")
            else:
                try:
                    with get_db_context() as db:
                        # Check if roll number already exists
                        existing = get_alumni_by_roll_number(db, roll_number.strip())
                        if existing:
                            st.error(f"❌ Duplicate roll number! An alumni with roll number '{roll_number}' already exists (ID: {existing.id}, Name: {existing.name}).")
                            st.info("💡 Use the Edit tab to update existing alumni records.")
                        else:
                            # Create new alumni
                            new_alumni = create_alumni(
                                db,
                                name=name.strip(),
                                batch=batch.strip() if batch else None,
                                roll_number=roll_number.strip(),
                                gender=gender if gender else None,
                                mobile_number=mobile.strip() if mobile else None,
                                personal_email=personal_email.strip() if personal_email else None,
                                current_company=current_company.strip() if current_company else None,
                                current_designation=current_designation.strip() if current_designation else None,
                                location=location.strip() if location else None,
                                linkedin_url=linkedin_url.strip() if linkedin_url else None,
                                college_email=college_email.strip() if college_email else None,
                                higher_studies=higher_studies.strip() if higher_studies else None,
                            )
                            st.success(f"✅ Alumni '{name}' added successfully! (ID: {new_alumni.id})")
                            st.info("You can now view this alumni in the Browse Alumni page.")
                except Exception as e:
                    st.error(f"❌ Error adding alumni: {e}")
                    st.info("Please check your input and try again.")


def render_edit_alumni_form():
    """Render form to edit existing alumni with data loading."""
    st.markdown("#### Edit Alumni")
    st.markdown("Load an alumni record by ID or Roll Number to edit their information.")
    
    if not DB_AVAILABLE:
        st.warning("Database not configured.")
        return
    
    # Search options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_method = st.radio(
            "Search by:",
            ["Alumni ID", "Roll Number"],
            horizontal=True,
            key="edit_search_method"
        )
    
    with col2:
        st.empty()  # Spacer
    
    # Search input based on method
    if search_method == "Alumni ID":
        search_value = st.number_input("Alumni ID to edit", min_value=1, step=1, key="edit_alumni_id")
    else:
        search_value = st.text_input("Roll Number to edit", key="edit_roll_number")
    
    if st.button("🔍 Load Alumni", type="primary"):
        try:
            with get_db_context() as db:
                # Load alumni based on search method
                if search_method == "Alumni ID":
                    alumni = get_alumni_by_id(db, search_value)
                else:
                    alumni = get_alumni_by_roll_number(db, search_value)
                
                if alumni:
                    # Store all fields for round-trip preservation
                    st.session_state.selected_alumni = {
                        "id": alumni.id,
                        "name": alumni.name or "",
                        "batch": alumni.batch or "",
                        "roll_number": alumni.roll_number or "",
                        "gender": alumni.gender or "",
                        "current_company": alumni.current_company or "",
                        "current_designation": alumni.current_designation or "",
                        "location": alumni.location or "",
                        "personal_email": alumni.personal_email or "",
                        "college_email": alumni.college_email or "",
                        "mobile_number": alumni.mobile_number or "",
                        "whatsapp_number": alumni.whatsapp_number or "",
                        "linkedin_url": alumni.linkedin_url or "",
                        "higher_studies": alumni.higher_studies or "",
                    }
                    st.success(f"✅ Loaded alumni: {alumni.name} (ID: {alumni.id}, Roll: {alumni.roll_number})")
                else:
                    st.error(f"❌ Alumni not found with {search_method}: {search_value}")
                    st.session_state.selected_alumni = None
        except Exception as e:
            st.error(f"❌ Error loading alumni: {e}")
            st.session_state.selected_alumni = None
    
    # Display edit form if alumni is loaded
    if st.session_state.get("selected_alumni"):
        st.markdown("---")
        st.markdown("##### Edit Alumni Information")
        
        with st.form("edit_alumni_form"):
            alumni_data = st.session_state.selected_alumni
            
            # Display read-only info
            st.info(f"📝 Editing: **{alumni_data.get('name')}** (ID: {alumni_data.get('id')}, Roll: {alumni_data.get('roll_number')})")
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name *", value=alumni_data.get("name", ""))
                batch = st.text_input("Batch", value=alumni_data.get("batch", ""))
                gender = st.selectbox(
                    "Gender", 
                    ["", "Male", "Female", "Other"],
                    index=["", "Male", "Female", "Other"].index(alumni_data.get("gender", "")) if alumni_data.get("gender") in ["", "Male", "Female", "Other"] else 0
                )
                current_company = st.text_input("Current Company", 
                                               value=alumni_data.get("current_company", ""))
                location = st.text_input("Location", value=alumni_data.get("location", ""))
                personal_email = st.text_input("Personal Email",
                                              value=alumni_data.get("personal_email", ""))
                college_email = st.text_input("College Email",
                                             value=alumni_data.get("college_email", ""))
            
            with col2:
                current_designation = st.text_input("Current Designation",
                                                   value=alumni_data.get("current_designation", ""))
                mobile = st.text_input("Mobile Number", value=alumni_data.get("mobile_number", ""))
                whatsapp = st.text_input("WhatsApp Number", value=alumni_data.get("whatsapp_number", ""))
                linkedin_url = st.text_input("LinkedIn URL",
                                            value=alumni_data.get("linkedin_url", ""))
                higher_studies = st.text_input("Higher Studies",
                                              value=alumni_data.get("higher_studies", ""))
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                submitted = st.form_submit_button("💾 Update Alumni", type="primary", use_container_width=True)
            
            with col2:
                cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancelled:
                st.session_state.selected_alumni = None
                st.info("Edit cancelled.")
                st.rerun()
            
            if submitted:
                # Validation
                if not name or not name.strip():
                    st.error("❌ Name is required and cannot be empty.")
                else:
                    try:
                        with get_db_context() as db:
                            # Update alumni using the update_alumni function
                            from alumni_system.database.crud import update_alumni
                            
                            updated_alumni = update_alumni(
                                db,
                                alumni_data["id"],
                                name=name.strip(),
                                batch=batch.strip() if batch else None,
                                gender=gender if gender else None,
                                current_company=current_company.strip() if current_company else None,
                                current_designation=current_designation.strip() if current_designation else None,
                                location=location.strip() if location else None,
                                personal_email=personal_email.strip() if personal_email else None,
                                college_email=college_email.strip() if college_email else None,
                                mobile_number=mobile.strip() if mobile else None,
                                whatsapp_number=whatsapp.strip() if whatsapp else None,
                                linkedin_url=linkedin_url.strip() if linkedin_url else None,
                                higher_studies=higher_studies.strip() if higher_studies else None,
                            )
                            
                            st.success(f"✅ Alumni '{name}' updated successfully!")
                            st.info("Changes have been saved to the database.")
                            st.session_state.selected_alumni = None
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error updating alumni: {e}")
                        st.info("Please check your input and try again.")


def render_delete_alumni_form():
    """Render form to delete alumni with confirmation dialog and cascade deletion."""
    st.markdown("#### Delete Alumni")
    st.error("⚠️ **WARNING:** This action cannot be undone! Deleting an alumni will also remove all associated job history and education history records.")
    
    if not DB_AVAILABLE:
        st.warning("Database not configured.")
        return
    
    # Initialize session state for confirmation
    if "delete_confirmation" not in st.session_state:
        st.session_state.delete_confirmation = False
    if "delete_alumni_id" not in st.session_state:
        st.session_state.delete_alumni_id = None
    if "delete_alumni_preview" not in st.session_state:
        st.session_state.delete_alumni_preview = None
    
    # Search options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_method = st.radio(
            "Search by:",
            ["Alumni ID", "Roll Number"],
            horizontal=True,
            key="delete_search_method"
        )
    
    with col2:
        st.empty()  # Spacer
    
    # Search input based on method
    if search_method == "Alumni ID":
        search_value = st.number_input("Alumni ID to delete", min_value=1, step=1, key="delete_id")
    else:
        search_value = st.text_input("Roll Number to delete", key="delete_roll_number")
    
    # Preview alumni before deletion
    if st.button("🔍 Preview Alumni", key="preview_delete"):
        try:
            with get_db_context() as db:
                # Load alumni based on search method
                if search_method == "Alumni ID":
                    alumni = get_alumni_by_id(db, search_value)
                else:
                    alumni = get_alumni_by_roll_number(db, search_value)
                
                if alumni:
                    # Get related records count
                    job_count = len(get_job_history_by_alumni(db, alumni.id))
                    edu_count = len(get_education_history_by_alumni(db, alumni.id)) if hasattr(alumni, 'education_history') else 0
                    
                    st.session_state.delete_alumni_preview = {
                        "id": alumni.id,
                        "name": alumni.name,
                        "roll_number": alumni.roll_number,
                        "batch": alumni.batch,
                        "current_company": alumni.current_company,
                        "job_count": job_count,
                        "edu_count": edu_count,
                    }
                    st.session_state.delete_alumni_id = alumni.id
                    st.session_state.delete_confirmation = False
                else:
                    st.error(f"❌ Alumni not found with {search_method}: {search_value}")
                    st.session_state.delete_alumni_preview = None
                    st.session_state.delete_alumni_id = None
        except Exception as e:
            st.error(f"❌ Error loading alumni: {e}")
            st.session_state.delete_alumni_preview = None
    
    # Display preview and confirmation
    if st.session_state.delete_alumni_preview:
        preview = st.session_state.delete_alumni_preview
        
        st.markdown("---")
        st.markdown("##### Alumni to be Deleted")
        
        # Display alumni information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Name:** {preview['name']}")
            st.markdown(f"**Roll Number:** {preview['roll_number']}")
            st.markdown(f"**Batch:** {preview['batch'] or 'N/A'}")
        
        with col2:
            st.markdown(f"**Current Company:** {preview['current_company'] or 'N/A'}")
            st.markdown(f"**Job History Records:** {preview['job_count']}")
            st.markdown(f"**Education History Records:** {preview['edu_count']}")
        
        # Warning about cascade deletion
        if preview['job_count'] > 0 or preview['edu_count'] > 0:
            st.warning(f"⚠️ This will also delete **{preview['job_count']} job history** and **{preview['edu_count']} education history** records associated with this alumni.")
        
        st.markdown("---")
        
        # Confirmation checkbox
        confirm = st.checkbox(
            f"I confirm that I want to permanently delete {preview['name']} (ID: {preview['id']}) and all associated records.",
            key="delete_confirm_checkbox"
        )
        
        st.session_state.delete_confirmation = confirm
        
        # Delete button (only enabled if confirmed)
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button(
                "🗑️ Delete Alumni",
                type="primary",
                disabled=not st.session_state.delete_confirmation,
                use_container_width=True
            ):
                try:
                    with get_db_context() as db:
                        # Perform deletion
                        success = delete_alumni(db, st.session_state.delete_alumni_id)
                        
                        if success:
                            st.success(f"✅ Alumni '{preview['name']}' (ID: {preview['id']}) and all associated records have been permanently deleted.")
                            # Clear session state
                            st.session_state.delete_confirmation = False
                            st.session_state.delete_alumni_id = None
                            st.session_state.delete_alumni_preview = None
                            st.rerun()
                        else:
                            st.error("❌ Alumni not found or already deleted.")
                except Exception as e:
                    st.error(f"❌ Error deleting alumni: {e}")
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.delete_confirmation = False
                st.session_state.delete_alumni_id = None
                st.session_state.delete_alumni_preview = None
                st.info("Deletion cancelled.")
                st.rerun()
        
        with col3:
            st.empty()  # Spacer
    
    else:
        st.info("👆 Enter an Alumni ID or Roll Number and click 'Preview Alumni' to see details before deletion.")


def render_database_tools():
    """Render database management tools."""
    st.markdown("#### Database Tools")
    
    if not DB_AVAILABLE:
        st.warning("Database not configured. Set the following environment variables:")
        st.code("""
DB_HOST=localhost
DB_PORT=5432
DB_NAME=alumni_db
DB_USER=postgres
DB_PASSWORD=your_password
        """)
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Initialize Database")
        if st.button("Create Tables"):
            try:
                init_database()
                st.success("Database tables created successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        st.markdown("##### Connection Test")
        if st.button("Test Connection"):
            try:
                if check_database_connection():
                    st.success("Database connection successful!")
                else:
                    st.error("Database connection failed!")
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    st.markdown("##### Import Alumni Data (Excel/CSV)")
    st.markdown("""
    **Required columns in your file:**
    - `LinkedIn ID` or `linkedin_url` - LinkedIn profile URL or username
    - `Roll No.` or `roll_number` - Student roll number
    - `Mobile No.` or `phone` - Phone number  
    - `Personal Email Id.` or `email` - Personal email
    - `College mail Id` or `college_email` - College email
    
    *Other columns like Name, Batch will be imported if present. LinkedIn data (current company, job history) will be fetched by the scraper.*
    """)
    
    uploaded_file = st.file_uploader(
        "Upload Alumni Excel/CSV", 
        type=["csv", "xlsx", "xls"],
        help="Upload an Excel (.xlsx, .xls) or CSV file with alumni data"
    )
    
    if uploaded_file:
        try:
            # Read file based on type
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write(f"**Preview ({len(df)} records):**")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Show column mapping
            st.markdown("##### Column Mapping")
            st.markdown("The following columns were detected:")
            
            # Map common column names to database fields
            column_mapping = {
                'linkedin_id': ['LinkedIn ID', 'linkedin_url', 'Linkedin ID', 'LinkedIn', 'linkedin'],
                'roll_number': ['Roll No.', 'roll_number', 'Roll Number', 'rollno', 'roll'],
                'name': ['Name of the Student', 'Name', 'name', 'Student Name'],
                'batch': ['Batch', 'batch', 'Year', 'year'],
                'mobile_number': ['Mobile No.', 'phone', 'Phone', 'mobile', 'Mobile', 'WhatsApp Number'],
                'personal_email': ['Personal Email Id.', 'email', 'Email', 'personal_email', 'Personal Email'],
                'college_email': ['College mail Id', 'college_email', 'College Email', 'college email'],
            }
            
            detected_columns = {}
            for db_field, possible_names in column_mapping.items():
                for col_name in possible_names:
                    if col_name in df.columns:
                        detected_columns[db_field] = col_name
                        break
            
            if detected_columns:
                mapping_df = pd.DataFrame([
                    {"Database Field": k, "Excel/CSV Column": v} 
                    for k, v in detected_columns.items()
                ])
                st.dataframe(mapping_df, use_container_width=True, hide_index=True)
            else:
                st.warning("Could not auto-detect columns. Please ensure your file has the required columns.")
            
            # Import button
            if st.button("📥 Import Data", type="primary"):
                if 'linkedin_id' not in detected_columns and 'roll_number' not in detected_columns:
                    st.error("At least LinkedIn ID or Roll Number column is required!")
                else:
                    with st.spinner("Importing alumni data..."):
                        try:
                            imported = 0
                            skipped = 0
                            errors = []
                            
                            with get_db_context() as db:
                                for idx, row in df.iterrows():
                                    try:
                                        # Get values from mapped columns
                                        alumni_data = {}
                                        
                                        for db_field, csv_col in detected_columns.items():
                                            value = row.get(csv_col)
                                            if pd.notna(value):
                                                alumni_data[db_field] = str(value).strip()
                                        
                                        # Process LinkedIn URL/ID
                                        if 'linkedin_id' in alumni_data:
                                            linkedin_val = alumni_data['linkedin_id']
                                            if 'linkedin.com' in linkedin_val:
                                                alumni_data['linkedin_url'] = linkedin_val
                                                # Extract ID from URL
                                                if '/in/' in linkedin_val:
                                                    alumni_data['linkedin_id'] = linkedin_val.split('/in/')[-1].rstrip('/')
                                            else:
                                                alumni_data['linkedin_url'] = f"https://www.linkedin.com/in/{linkedin_val}"
                                        
                                        # Check if already exists
                                        if 'roll_number' in alumni_data:
                                            from alumni_system.database.crud import get_alumni_by_roll_number
                                            existing = get_alumni_by_roll_number(db, alumni_data['roll_number'])
                                            if existing:
                                                skipped += 1
                                                continue
                                        
                                        # Set name if not provided
                                        if 'name' not in alumni_data:
                                            alumni_data['name'] = alumni_data.get('roll_number', f'Alumni_{idx}')
                                        
                                        # Create alumni record
                                        create_alumni(db, **alumni_data)
                                        imported += 1
                                        
                                    except Exception as e:
                                        errors.append(f"Row {idx + 2}: {str(e)}")
                            
                            st.success(f"✅ Import complete! {imported} records imported, {skipped} skipped (duplicates)")
                            
                            if errors:
                                with st.expander(f"⚠️ {len(errors)} errors occurred"):
                                    for error in errors[:20]:
                                        st.text(error)
                                    if len(errors) > 20:
                                        st.text(f"... and {len(errors) - 20} more errors")
                        
                        except Exception as e:
                            st.error(f"Import failed: {e}")
        
        except Exception as e:
            st.error(f"Error reading file: {e}")


def render_scraping_control():
    """Render the scraping control interface."""
    st.markdown("#### 🔄 Scraping Control")
    st.markdown("Monitor and control LinkedIn profile scraping operations.")
    
    if not DB_AVAILABLE:
        st.warning("Database not configured. Scraping control requires database connection.")
        return
    
    # Initialize session state for scraping
    if "scraping_active" not in st.session_state:
        st.session_state.scraping_active = False
    if "scraping_paused" not in st.session_state:
        st.session_state.scraping_paused = False
    if "scraping_progress" not in st.session_state:
        st.session_state.scraping_progress = {"completed": 0, "total": 0, "current_account": None}
    
    try:
        with get_db_context() as db:
            from alumni_system.database.crud import get_queue_statistics
            
            # Display queue statistics
            st.markdown("##### 📊 Queue Statistics")
            queue_stats = get_queue_statistics(db)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("⏳ Pending", queue_stats['pending'])
            
            with col2:
                st.metric("🔄 In Progress", queue_stats['in_progress'])
            
            with col3:
                st.metric("✅ Completed", queue_stats['completed'])
            
            with col4:
                st.metric("❌ Failed", queue_stats['failed'])
            
            st.markdown("---")
            
            # Display account usage
            st.markdown("##### 👥 Account Usage")
            
            try:
                from alumni_system.scraper.account_rotation import AccountRotationManager
                
                # Initialize account rotation manager
                rotation_manager = AccountRotationManager()
                usage_stats = rotation_manager.get_usage_stats()
                
                if usage_stats:
                    for account_email, stats in usage_stats.items():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            # Progress bar for account usage
                            progress = stats['profiles_scraped'] / stats['limit'] if stats['limit'] > 0 else 0
                            
                            # Color based on status
                            if stats['is_flagged']:
                                status_text = "🚫 Flagged"
                                bar_color = "red"
                            elif not stats['available']:
                                status_text = "⚠️ Exhausted"
                                bar_color = "orange"
                            else:
                                status_text = "✅ Available"
                                bar_color = "green"
                            
                            st.progress(
                                progress,
                                text=f"{account_email}: {stats['profiles_scraped']}/{stats['limit']} - {status_text}"
                            )
                        
                        with col2:
                            remaining = stats['limit'] - stats['profiles_scraped']
                            if remaining > 0 and not stats['is_flagged']:
                                st.metric("Remaining", remaining)
                            else:
                                st.metric("Remaining", 0)
                    
                    # Total capacity
                    total_capacity = rotation_manager.get_total_available_capacity()
                    
                    if total_capacity > 0:
                        st.info(f"📈 Total remaining capacity today: **{total_capacity}** profiles")
                    else:
                        # All accounts exhausted
                        from alumni_system.utils.error_handling import get_account_exhaustion_message
                        st.warning(get_account_exhaustion_message())
                else:
                    st.warning("No LinkedIn accounts configured. Set LINKEDIN_EMAIL_1, LINKEDIN_PASSWORD_1, etc.")
            
            except Exception as e:
                st.warning(f"Could not load account information: {e}")
                st.info("Configure LinkedIn accounts in environment variables to enable scraping.")
            
            st.markdown("---")
            
            # Scraping controls
            st.markdown("##### 🎮 Scraping Controls")
            
            # Display current scraping status
            if st.session_state.scraping_active:
                progress = st.session_state.scraping_progress
                
                if progress['total'] > 0:
                    progress_pct = progress['completed'] / progress['total']
                    st.progress(
                        progress_pct,
                        text=f"Progress: {progress['completed']}/{progress['total']} profiles"
                    )
                
                if progress['current_account']:
                    st.info(f"🔄 Currently using account: **{progress['current_account']}**")
                
                # Estimate time remaining
                if progress['completed'] > 0 and progress['total'] > progress['completed']:
                    # Rough estimate: 10-15 seconds per profile
                    remaining_profiles = progress['total'] - progress['completed']
                    estimated_seconds = remaining_profiles * 12.5  # Average of 10-15
                    estimated_minutes = estimated_seconds / 60
                    
                    if estimated_minutes < 60:
                        st.info(f"⏱️ Estimated time remaining: ~{int(estimated_minutes)} minutes")
                    else:
                        estimated_hours = estimated_minutes / 60
                        st.info(f"⏱️ Estimated time remaining: ~{estimated_hours:.1f} hours")
                
                # Pause/Resume button
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.session_state.scraping_paused:
                        if st.button("▶️ Resume Scraping", type="primary"):
                            st.session_state.scraping_paused = False
                            st.success("Scraping resumed!")
                            st.rerun()
                    else:
                        if st.button("⏸️ Pause Scraping"):
                            st.session_state.scraping_paused = True
                            st.warning("Scraping paused. Click Resume to continue.")
                            st.rerun()
                
                with col2:
                    if st.button("⏹️ Stop Scraping"):
                        st.session_state.scraping_active = False
                        st.session_state.scraping_paused = False
                        st.session_state.scraping_progress = {"completed": 0, "total": 0, "current_account": None}
                        st.info("Scraping stopped.")
                        st.rerun()
            
            else:
                # Start scraping button
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if queue_stats['pending'] > 0:
                        if st.button("🚀 Start Scraping", type="primary"):
                            st.session_state.scraping_active = True
                            st.session_state.scraping_paused = False
                            st.session_state.scraping_progress = {
                                "completed": 0,
                                "total": queue_stats['pending'],
                                "current_account": None
                            }
                            st.success(f"Starting scraping for {queue_stats['pending']} profiles...")
                            st.info("⚠️ Note: This is a demo interface. Actual scraping requires background job implementation.")
                            st.rerun()
                    else:
                        st.button("🚀 Start Scraping", disabled=True)
                        st.info("No profiles in queue. Import alumni data to populate the queue.")
                
                with col2:
                    st.metric("Profiles to Scrape", queue_stats['pending'])
            
            # Scraping logs
            st.markdown("---")
            st.markdown("##### 📋 Recent Scraping Logs")
            
            from alumni_system.database.crud import get_scraping_logs
            
            logs = get_scraping_logs(db, limit=10)
            
            if logs:
                log_data = []
                for log in logs:
                    log_data.append({
                        "Time": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "N/A",
                        "Alumni ID": log.alumni_id or "N/A",
                        "Account": log.account_email or "N/A",
                        "Status": log.status,
                        "Duration (s)": log.duration_seconds or "N/A",
                        "PDF Stored": "✓" if log.pdf_stored else "✗",
                        "Error": log.error_message[:50] + "..." if log.error_message and len(log.error_message) > 50 else (log.error_message or "")
                    })
                
                log_df = pd.DataFrame(log_data)
                st.dataframe(log_df, use_container_width=True, hide_index=True)
            else:
                st.info("No scraping logs yet. Logs will appear here after scraping operations.")
    
    except Exception as e:
        st.error(f"Error loading scraping control: {e}")


def render_scraping_logs():
    """Render the scraping logs view with filtering and detailed information."""
    st.markdown("#### 📋 Scraping Logs")
    st.markdown("View detailed logs of all scraping operations including status, duration, errors, and account usage.")
    
    if not DB_AVAILABLE:
        st.warning("Database not configured.")
        return
    
    try:
        with get_db_context() as db:
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox(
                    "Filter by Status",
                    ["All", "success", "failed", "skipped"],
                    key="log_status_filter"
                )
            
            with col2:
                limit = st.number_input(
                    "Number of logs to display",
                    min_value=10,
                    max_value=500,
                    value=50,
                    step=10,
                    key="log_limit"
                )
            
            with col3:
                st.empty()  # Spacer
            
            # Get logs with optional status filter
            if status_filter == "All":
                logs = get_scraping_logs(db, limit=limit)
            else:
                logs = get_scraping_logs(db, limit=limit, status=status_filter)
            
            # Display statistics
            st.markdown("---")
            st.markdown("##### 📊 Log Statistics")
            
            if logs:
                total_logs = len(logs)
                success_count = sum(1 for log in logs if log.status == "success")
                failed_count = sum(1 for log in logs if log.status == "failed")
                skipped_count = sum(1 for log in logs if log.status == "skipped")
                pdf_stored_count = sum(1 for log in logs if log.pdf_stored)
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Total Logs", total_logs)
                
                with col2:
                    st.metric("✅ Success", success_count)
                
                with col3:
                    st.metric("❌ Failed", failed_count)
                
                with col4:
                    st.metric("⏭️ Skipped", skipped_count)
                
                with col5:
                    st.metric("📄 PDFs Stored", pdf_stored_count)
                
                # Display logs table
                st.markdown("---")
                st.markdown("##### 📝 Log Entries")
                
                log_data = []
                for log in logs:
                    # Format status with emoji
                    status_display = {
                        "success": "✅ Success",
                        "failed": "❌ Failed",
                        "skipped": "⏭️ Skipped"
                    }.get(log.status, log.status)
                    
                    log_data.append({
                        "ID": log.id,
                        "Time": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "N/A",
                        "Alumni ID": log.alumni_id or "N/A",
                        "LinkedIn URL": log.linkedin_url[:40] + "..." if log.linkedin_url and len(log.linkedin_url) > 40 else (log.linkedin_url or "N/A"),
                        "Account": log.account_email or "N/A",
                        "Status": status_display,
                        "Duration (s)": log.duration_seconds if log.duration_seconds is not None else "N/A",
                        "PDF Stored": "✓" if log.pdf_stored else "✗",
                        "Error": log.error_message[:50] + "..." if log.error_message and len(log.error_message) > 50 else (log.error_message or "")
                    })
                
                log_df = pd.DataFrame(log_data)
                st.dataframe(log_df, use_container_width=True, hide_index=True)
                
                # Detailed view for selected log
                st.markdown("---")
                st.markdown("##### 🔍 View Detailed Log")
                
                log_id = st.number_input(
                    "Enter Log ID to view details",
                    min_value=1,
                    step=1,
                    key="detailed_log_id"
                )
                
                if st.button("View Details", key="view_log_details"):
                    selected_log = next((log for log in logs if log.id == log_id), None)
                    
                    if selected_log:
                        st.markdown("**Log Details:**")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Log ID:** {selected_log.id}")
                            st.markdown(f"**Alumni ID:** {selected_log.alumni_id or 'N/A'}")
                            st.markdown(f"**Status:** {selected_log.status}")
                            st.markdown(f"**Duration:** {selected_log.duration_seconds} seconds" if selected_log.duration_seconds else "**Duration:** N/A")
                            st.markdown(f"**PDF Stored:** {'Yes ✓' if selected_log.pdf_stored else 'No ✗'}")
                        
                        with col2:
                            st.markdown(f"**Created At:** {selected_log.created_at.strftime('%Y-%m-%d %H:%M:%S') if selected_log.created_at else 'N/A'}")
                            st.markdown(f"**Account Email:** {selected_log.account_email or 'N/A'}")
                            st.markdown(f"**LinkedIn URL:** {selected_log.linkedin_url or 'N/A'}")
                        
                        if selected_log.error_message:
                            st.markdown("**Error Message:**")
                            st.error(selected_log.error_message)
                        
                        # Link to alumni details if available
                        if selected_log.alumni_id:
                            st.markdown("---")
                            if st.button(f"View Alumni #{selected_log.alumni_id}", key="view_alumni_from_log"):
                                st.session_state.selected_alumni_id = selected_log.alumni_id
                                st.info(f"Navigate to Alumni Details page to view alumni #{selected_log.alumni_id}")
                    else:
                        st.warning(f"Log with ID {log_id} not found in the current filtered results.")
                
            else:
                st.info("No scraping logs found. Logs will appear here after scraping operations.")
                st.markdown("**Note:** Scraping logs are created automatically when:")
                st.markdown("- ✅ A profile is successfully scraped")
                st.markdown("- ❌ A scraping attempt fails")
                st.markdown("- ⏭️ A profile is skipped")
    
    except Exception as e:
        st.error(f"Error loading scraping logs: {e}")
        import traceback
        st.code(traceback.format_exc())


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    """Main application entry point."""
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render selected page
    if page == "📊 Dashboard":
        render_dashboard()
    elif page == "👥 Browse Alumni":
        render_browse_alumni()
    elif page == "🔍 Search & Filter":
        render_search_filter()
    elif page == "📋 Alumni Details":
        render_alumni_details()
    elif page == "💬 Chatbot":
        render_chatbot()
    elif page == "⚙️ Admin Panel":
        render_admin_panel()


if __name__ == "__main__":
    main()
