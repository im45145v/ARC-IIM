"""
Alumni Management System - Modern Streamlit Frontend
====================================================

A beautiful, modern interface for managing alumni data.
"""

import io
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Import alumni system modules
DB_AVAILABLE = False
DB_ERROR = None

try:
    from alumni_system.database.connection import get_db_context
    from alumni_system.database.crud import (
        create_alumni, delete_alumni, get_all_alumni, get_alumni_by_id,
        get_alumni_by_roll_number, get_alumni_count, get_job_history_by_alumni,
        get_unique_batches, get_unique_companies, get_unique_locations,
        search_alumni, update_alumni, get_education_history_by_alumni
    )
    from alumni_system.chatbot.nlp_chatbot import get_chatbot
    
    # Test actual database connection
    try:
        with get_db_context() as db:
            get_alumni_count(db)
        DB_AVAILABLE = True
    except Exception as conn_error:
        DB_AVAILABLE = False
        DB_ERROR = f"Database connection failed: {str(conn_error)}"
        
except ImportError as e:
    DB_AVAILABLE = False
    DB_ERROR = f"Import error: {str(e)}"
except Exception as e:
    DB_AVAILABLE = False
    DB_ERROR = f"Unexpected error: {str(e)}"

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
# MODERN STYLING
# =============================================================================
st.markdown("""
<style>
    /* Modern color scheme */
    :root {
        --primary: #2563eb;
        --secondary: #7c3aed;
        --success: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --dark: #1e293b;
        --light: #f8fafc;
    }
    
    /* Clean background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Main content area */
    .main .block-container {
        padding: 2rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin: 2rem auto;
        max-width: 1400px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: white;
    }
    
    /* Headers */
    h1 {
        color: #1e293b;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #475569;
        font-weight: 600;
        margin-top: 2rem;
    }
    
    h3 {
        color: #64748b;
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #2563eb;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.3);
    }
    
    /* Input fields */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* Tables */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Cards */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        margin-bottom: 1rem;
        border-left: 4px solid #2563eb;
    }
    
    .success-card {
        background: #f0fdf4;
        border-left-color: #10b981;
    }
    
    .warning-card {
        background: #fffbeb;
        border-left-color: #f59e0b;
    }
    
    .error-card {
        background: #fef2f2;
        border-left-color: #ef4444;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        color: white;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f8fafc;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def show_header(title, subtitle=None, icon="🎓"):
    """Display a modern header"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); 
                padding: 2rem; border-radius: 12px; margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(37, 99, 235, 0.3);">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">
            {icon} {title}
        </h1>
        {f'<p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem; font-size: 1.1rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def show_metric_card(label, value, icon="📊", delta=None):
    """Display a metric in a card"""
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<div style='font-size: 3rem;'>{icon}</div>", unsafe_allow_html=True)
    with col2:
        st.metric(label, value, delta=delta)

def show_info_box(message, type="info"):
    """Display an info box"""
    colors = {
        "info": ("#2563eb", "#eff6ff"),
        "success": ("#10b981", "#f0fdf4"),
        "warning": ("#f59e0b", "#fffbeb"),
        "error": ("#ef4444", "#fef2f2")
    }
    color, bg = colors.get(type, colors["info"])
    
    st.markdown(f"""
    <div style="background: {bg}; border-left: 4px solid {color}; 
                padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        {message}
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: white; font-size: 2rem;">🎓</h1>
            <h2 style="color: white; font-size: 1.5rem; margin: 0;">Alumni System</h2>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">Manage your alumni network</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Initialize session state for page navigation
        if 'page' not in st.session_state:
            st.session_state.page = "🏠 Dashboard"
        
        page = st.radio(
            "Navigation",
            ["🏠 Dashboard", "👥 Browse Alumni", "🔍 Search", "💬 Chatbot", "⚙️ Admin"],
            label_visibility="collapsed",
            key="navigation",
            index=["🏠 Dashboard", "👥 Browse Alumni", "🔍 Search", "💬 Chatbot", "⚙️ Admin"].index(st.session_state.page) if st.session_state.page in ["🏠 Dashboard", "👥 Browse Alumni", "🔍 Search", "💬 Chatbot", "⚙️ Admin"] else 0
        )
        
        # Update session state when radio changes
        st.session_state.page = page
        
        st.markdown("---")
        
        # Database status
        if DB_AVAILABLE:
            try:
                with get_db_context() as db:
                    count = get_alumni_count(db)
                st.success(f"✅ Database Connected\n\n{count} alumni records")
            except:
                st.error("❌ Database Error")
        else:
            st.warning("⚠️ Database Not Configured")
        
        st.markdown("---")
        st.markdown("""
        <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem; text-align: center;">
            Alumni Management System v2.0<br>
            Built with ❤️ using Streamlit
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    if not DB_AVAILABLE:
        show_header("Database Connection Issue", "Unable to connect to the database", "⚠️")
        
        if DB_ERROR:
            show_info_box(f"""
            <strong>Error Details:</strong><br>
            {DB_ERROR}
            """, "error")
        
        show_info_box("""
        <strong>Troubleshooting Steps:</strong><br>
        1. Verify <code>.env</code> file exists in project root<br>
        2. Check database credentials (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)<br>
        3. Ensure PostgreSQL is running: <code>docker-compose ps</code><br>
        4. Restart the application
        """, "warning")
        
        # Show current environment for debugging
        import os
        st.code(f"""
Current Environment:
DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}
DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}
DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}
DB_USER: {os.getenv('DB_USER', 'NOT SET')}
DB_PASSWORD: {'***' if os.getenv('DB_PASSWORD') else 'NOT SET'}
        """)
        return
    
    # Route to pages
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👥 Browse Alumni":
        show_browse_alumni()
    elif page == "🔍 Search":
        show_search()
    elif page == "💬 Chatbot":
        show_chatbot()
    elif page == "⚙️ Admin":
        show_admin()

# =============================================================================
# PAGES
# =============================================================================

def show_dashboard():
    show_header("Dashboard", "Overview of your alumni network", "📊")
    
    try:
        with get_db_context() as db:
            total_alumni = get_alumni_count(db)
            batches = get_unique_batches(db)
            companies = get_unique_companies(db)
            locations = get_unique_locations(db)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            show_metric_card("Total Alumni", total_alumni, "👥")
        
        with col2:
            show_metric_card("Batches", len(batches), "🎓")
        
        with col3:
            show_metric_card("Companies", len(companies), "🏢")
        
        with col4:
            show_metric_card("Locations", len(locations), "📍")
        
        st.markdown("##")
        
        # Recent activity
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Quick Stats")
            if total_alumni > 0:
                st.info(f"✅ System is active with {total_alumni} alumni records")
            else:
                st.warning("⚠️ No alumni data yet. Add some records to get started!")
        
        with col2:
            st.subheader("🚀 Quick Actions")
            if st.button("➕ Add New Alumni", use_container_width=True):
                st.session_state.page = "⚙️ Admin"
                st.rerun()
            if st.button("📥 Import from Excel", use_container_width=True):
                st.session_state.page = "⚙️ Admin"
                st.rerun()
            if st.button("👥 Browse All Alumni", use_container_width=True):
                st.session_state.page = "👥 Browse Alumni"
                st.rerun()
        
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

def show_browse_alumni():
    show_header("Browse Alumni", "View and manage all alumni records", "👥")
    
    try:
        with get_db_context() as db:
            alumni_list = get_all_alumni(db, limit=1000)
            
            if not alumni_list:
                show_info_box("No alumni records found. Add some records to get started!", "info")
                return
            
            # Convert to DataFrame inside the session context
            df = pd.DataFrame([{
                "Roll No": a.roll_number,
                "Name": a.name,
                "Batch": a.batch,
                "Company": a.current_company or "N/A",
                "Designation": a.current_designation or "N/A",
                "Location": a.location or "N/A",
                "Email": a.college_email or a.personal_email or "N/A",
                "Mobile": a.mobile_number or "N/A",
            } for a in alumni_list])
        
        # Display
        st.dataframe(df, use_container_width=True, height=600)
        
        # Export
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📥 Export to Excel"):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Alumni')
                
                st.download_button(
                    label="⬇️ Download Excel File",
                    data=output.getvalue(),
                    file_name=f"alumni_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col2:
            if st.button("👁️ View Detailed Profiles"):
                st.session_state.show_detailed = True
                st.rerun()
        
        # Show detailed view if requested
        if st.session_state.get('show_detailed', False):
            st.markdown("---")
            show_detailed_alumni_list()
        
    except Exception as e:
        st.error(f"Error loading alumni: {e}")


def show_detailed_alumni_list():
    """Show detailed alumni profiles with job history and education"""
    st.subheader("📋 Detailed Alumni Profiles")
    
    with get_db_context() as db:
        alumni_list = get_all_alumni(db, limit=1000)
        
        for alumni in alumni_list:
            with st.expander(f"👤 {alumni.name} - {alumni.roll_number}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📇 Basic Information")
                    st.write(f"**Name:** {alumni.name}")
                    st.write(f"**Roll Number:** {alumni.roll_number}")
                    st.write(f"**Batch:** {alumni.batch or 'N/A'}")
                    st.write(f"**Gender:** {alumni.gender or 'N/A'}")
                    
                    st.markdown("### 📞 Contact Information")
                    st.write(f"**Mobile:** {alumni.mobile_number or 'N/A'}")
                    st.write(f"**WhatsApp:** {alumni.whatsapp_number or 'N/A'}")
                    st.write(f"**College Email:** {alumni.college_email or 'N/A'}")
                    st.write(f"**Personal Email:** {alumni.personal_email or 'N/A'}")
                    st.write(f"**Corporate Email:** {alumni.corporate_email or 'N/A'}")
                    
                    if alumni.linkedin_url:
                        st.markdown(f"**LinkedIn:** [{alumni.linkedin_url}]({alumni.linkedin_url})")
                    
                    if alumni.linkedin_pdf_url:
                        st.markdown(f"**LinkedIn PDF:** [Download]({alumni.linkedin_pdf_url})")
                
                with col2:
                    st.markdown("### 💼 Current Position")
                    st.write(f"**Company:** {alumni.current_company or 'N/A'}")
                    st.write(f"**Designation:** {alumni.current_designation or 'N/A'}")
                    st.write(f"**Location:** {alumni.location or 'N/A'}")
                    
                    if alumni.por:
                        st.markdown("### 🎯 Position of Responsibility / Headline")
                        st.write(alumni.por)
                    
                    if alumni.internship:
                        st.markdown("### 🏢 Internships")
                        st.write(alumni.internship)
                
                # Job History
                job_history = get_job_history_by_alumni(db, alumni.id)
                if job_history:
                    st.markdown("### 📊 Work Experience")
                    for i, job in enumerate(job_history, 1):
                        st.markdown(f"**{i}. {job.designation or 'Position'} at {job.company_name}**")
                        if job.location:
                            st.write(f"   📍 {job.location}")
                        if job.start_date or job.end_date:
                            start = job.start_date.strftime("%b %Y") if job.start_date else "N/A"
                            end = job.end_date.strftime("%b %Y") if job.end_date else "Present" if job.is_current else "N/A"
                            st.write(f"   📅 {start} - {end}")
                        if job.description:
                            st.write(f"   {job.description}")
                        st.write("")
                
                # Education History
                education_history = get_education_history_by_alumni(db, alumni.id)
                if education_history:
                    st.markdown("### 🎓 Education")
                    for i, edu in enumerate(education_history, 1):
                        st.markdown(f"**{i}. {edu.institution_name}**")
                        if edu.degree:
                            st.write(f"   🎓 {edu.degree}")
                        if edu.field_of_study:
                            st.write(f"   📚 {edu.field_of_study}")
                        if edu.start_year or edu.end_year:
                            years = f"{edu.start_year or 'N/A'} - {edu.end_year or 'N/A'}"
                            st.write(f"   📅 {years}")
                        st.write("")
                
                # Additional Info
                if alumni.higher_studies or alumni.notable_alma_mater or alumni.remarks:
                    st.markdown("### 📝 Additional Information")
                    if alumni.higher_studies:
                        st.write(f"**Higher Studies:** {alumni.higher_studies}")
                    if alumni.notable_alma_mater:
                        st.write(f"**Notable Alma Mater:** {alumni.notable_alma_mater}")
                    if alumni.remarks:
                        st.write(f"**Remarks:** {alumni.remarks}")
                
                # Metadata
                if alumni.last_scraped_at:
                    st.caption(f"Last scraped: {alumni.last_scraped_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if st.button("🔙 Back to Table View"):
        st.session_state.show_detailed = False
        st.rerun()

def show_search():
    show_header("Search Alumni", "Find specific alumni records", "🔍")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search by name or company", placeholder="Enter name or company...")
    
    with col2:
        batch_filter = st.selectbox("Filter by batch", ["All"] + get_unique_batches_safe())
    
    if search_query or batch_filter != "All":
        try:
            with get_db_context() as db:
                if search_query:
                    results = search_alumni(db, search_query)
                else:
                    results = get_all_alumni(db, batch=batch_filter if batch_filter != "All" else None)
                
                if results:
                    st.success(f"Found {len(results)} results")
                    
                    for alumni in results:
                        with st.expander(f"👤 {alumni.name} - {alumni.roll_number}", expanded=False):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("### 📇 Basic Info")
                                st.write(f"**Batch:** {alumni.batch or 'N/A'}")
                                st.write(f"**Gender:** {alumni.gender or 'N/A'}")
                                
                                st.markdown("### 📞 Contact")
                                st.write(f"**Mobile:** {alumni.mobile_number or 'N/A'}")
                                st.write(f"**Email:** {alumni.college_email or alumni.personal_email or 'N/A'}")
                                
                                if alumni.linkedin_url:
                                    st.markdown(f"**LinkedIn:** [{alumni.linkedin_url}]({alumni.linkedin_url})")
                            
                            with col2:
                                st.markdown("### 💼 Current Position")
                                st.write(f"**Company:** {alumni.current_company or 'N/A'}")
                                st.write(f"**Designation:** {alumni.current_designation or 'N/A'}")
                                st.write(f"**Location:** {alumni.location or 'N/A'}")
                                
                                if alumni.por:
                                    st.markdown("### 🎯 Headline")
                                    st.write(alumni.por)
                            
                            # Job History
                            job_history = get_job_history_by_alumni(db, alumni.id)
                            if job_history:
                                st.markdown("### 📊 Work Experience")
                                for i, job in enumerate(job_history[:5], 1):
                                    st.write(f"**{i}. {job.designation or 'Position'} at {job.company_name}**")
                                    if job.location:
                                        st.write(f"   📍 {job.location}")
                            
                            # Education
                            education_history = get_education_history_by_alumni(db, alumni.id)
                            if education_history:
                                st.markdown("### 🎓 Education")
                                for i, edu in enumerate(education_history[:3], 1):
                                    st.write(f"**{i}. {edu.institution_name}**")
                                    if edu.degree:
                                        st.write(f"   {edu.degree}")
                else:
                    show_info_box("No results found. Try a different search term.", "info")
        
        except Exception as e:
            st.error(f"Search error: {e}")

def show_chatbot():
    show_header("AI Chatbot", "Ask questions about your alumni network", "💬")
    
    show_info_box("""
    <strong>Try asking:</strong><br>
    • "How many alumni do we have?"<br>
    • "Who works at Google?"<br>
    • "Show alumni from batch 2024"<br>
    • "Find software engineers"
    """, "info")
    
    query = st.text_input("💬 Ask a question", placeholder="Type your question here...")
    
    if query:
        try:
            chatbot = get_chatbot()
            response = chatbot.process_query(query)
            
            st.markdown("### 🤖 Response")
            st.write(response.response)
            
            if response.alumni:
                st.markdown("### 📋 Results")
                df = pd.DataFrame([{
                    "Name": a.get("name", "N/A"),
                    "Batch": a.get("batch", "N/A"),
                    "Company": a.get("current_company", "N/A"),
                } for a in response.alumni])
                st.dataframe(df, use_container_width=True)
        
        except Exception as e:
            st.error(f"Chatbot error: {e}")

def show_admin():
    show_header("Admin Panel", "Manage alumni records", "⚙️")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Alumni", "✏️ Edit Alumni", "🗑️ Delete Alumni"])
    
    with tab1:
        st.subheader("Add New Alumni")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *")
            roll_number = st.text_input("Roll Number *")
            batch = st.text_input("Batch")
        
        with col2:
            company = st.text_input("Current Company")
            designation = st.text_input("Current Designation")
            location = st.text_input("Location")
        
        if st.button("➕ Add Alumni", type="primary"):
            if name and roll_number:
                try:
                    with get_db_context() as db:
                        create_alumni(
                            db,
                            name=name,
                            roll_number=roll_number,
                            batch=batch,
                            current_company=company,
                            current_designation=designation,
                            location=location
                        )
                    st.success(f"✅ Successfully added {name}!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please fill in required fields (Name and Roll Number)")
    
    with tab2:
        st.subheader("Edit Alumni")
        st.info("Search for an alumni to edit their details")
        # Add edit functionality here
    
    with tab3:
        st.subheader("Delete Alumni")
        st.warning("⚠️ This action cannot be undone!")
        # Add delete functionality here

# Helper functions
def get_unique_batches_safe():
    try:
        with get_db_context() as db:
            return get_unique_batches(db)
    except:
        return []

# =============================================================================
# RUN APP
# =============================================================================

if __name__ == "__main__":
    main()
