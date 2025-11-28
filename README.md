# Alumni Management System

A comprehensive system for managing alumni data with LinkedIn profile scraping, database storage, cloud PDF backup, and an NLP-powered chatbot interface.

## Features

- 🔍 **LinkedIn Scraping**: Automated scraping of LinkedIn profiles using Playwright with human behavior simulation
- 🔄 **Multi-Account Rotation**: Distribute scraping load across multiple LinkedIn accounts with automatic rotation
- 📊 **Rate Limiting**: Configurable daily limits per account to avoid detection and account suspension
- 📋 **Scraping Queue**: Queue-based processing system for managing bulk scraping operations
- 🗄️ **PostgreSQL Database**: Structured storage for alumni data including job and education history
- ☁️ **Cloud Storage**: Backblaze B2 integration for storing LinkedIn profile PDFs with failure resilience
- 🌐 **Web Interface**: Streamlit application for browsing, filtering, and exporting alumni data
- 📥 **Bulk Import**: Import alumni data from Excel/CSV files with automatic queue population
- 🎛️ **Scraping Control**: Real-time progress tracking and control interface in admin panel
- 🤖 **NLP Chatbot**: Natural language interface for querying alumni information
- 🔄 **Automation**: GitHub Actions workflow for periodic scraping every 6 months
- 🔐 **Secure**: All sensitive credentials managed via environment variables
- 🛡️ **Error Resilience**: Graceful degradation and error isolation across components

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Docker & Docker Compose (for local database)
- A LinkedIn account (for scraping)
- A Backblaze B2 account (for PDF storage)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/im45145v/ARC-IIM.git
cd ARC-IIM
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

4. **Set up LinkedIn authentication** (Choose one method):

   **Option A: Cookie-Based (Recommended - More Secure, Supports 2FA)**
   ```bash
   # Export cookies from your LinkedIn account
   python scripts/export_linkedin_cookies.py
   
   # Add to .env
   echo "LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json" >> .env
   ```
   
   **Option B: Credential-Based (Legacy - Requires disabling 2FA)**
   ```bash
   cp .env.example .env
   # Edit .env and add:
   # LINKEDIN_EMAIL_1=your_email@example.com
   # LINKEDIN_PASSWORD_1=your_password
   ```
   
   📖 **See [Cookie Authentication Guide](docs/QUICK_START_COOKIES.md) for detailed instructions**

5. Configure other environment variables:
```bash
# Edit .env with your database and B2 credentials
nano .env
```

6. **Start the local database (for testing)**:
```bash
docker-compose up -d
```

7. Initialize the database:
```bash
python -c "from alumni_system.database.init_db import init_database; init_database()"
```

8. Run the Streamlit application:
```bash
streamlit run alumni_system/frontend/app.py
```

## Local Database Setup (Testing Mode)

For local development and testing, use Docker Compose to spin up a PostgreSQL database:

```bash
# Start PostgreSQL database
docker-compose up -d

# The database will be available at:
# - Host: localhost
# - Port: 5432
# - Database: alumni_db
# - User: postgres
# - Password: alumni_dev_password

# To stop the database
docker-compose down

# To stop and remove all data
docker-compose down -v

# Optional: Start with pgAdmin UI for database management
docker-compose --profile admin up -d
# Access pgAdmin at http://localhost:5050
# Email: admin@alumni.local
# Password: admin123
```

Update your `.env` file for local testing:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=alumni_db
DB_USER=postgres
DB_PASSWORD=alumni_dev_password
```

## Multi-Account Setup and Rate Limiting

The system supports multiple LinkedIn accounts to distribute scraping load and avoid rate limits. This is the recommended approach for large-scale scraping operations.

### Why Multiple Accounts?

- **Rate Limit Distribution**: LinkedIn limits the number of profile views per account per day
- **Automatic Rotation**: System automatically switches accounts when one reaches its daily limit
- **Increased Throughput**: Scrape more profiles per day by using multiple accounts
- **Resilience**: If one account is flagged, others continue working

### Setting Up Multiple LinkedIn Accounts

1. **Create Dedicated Accounts**: Create 2-3 dedicated LinkedIn accounts (not your personal accounts)
   - Use different email addresses
   - Complete the profile setup to avoid looking like bot accounts
   - Disable 2FA for automated access

2. **Configure Environment Variables**:

```bash
# Account 1 (Required)
LINKEDIN_EMAIL_1=scraper1@example.com
LINKEDIN_PASSWORD_1=password123

# Account 2 (Optional but recommended)
LINKEDIN_EMAIL_2=scraper2@example.com
LINKEDIN_PASSWORD_2=password456

# Account 3 (Optional)
LINKEDIN_EMAIL_3=scraper3@example.com
LINKEDIN_PASSWORD_3=password789

# Configure daily limit per account (default: 80)
SCRAPER_DAILY_LIMIT_PER_ACCOUNT=80
```

3. **How Account Rotation Works**:
   - System loads all numbered accounts sequentially (1, 2, 3, ...)
   - Tracks usage for each account in the database
   - Automatically rotates to next account when current reaches daily limit
   - Resets all counters at midnight UTC
   - Flags accounts that encounter security checkpoints

### Recommended Configuration

| Scenario | Accounts | Daily Limit | Total Capacity |
|----------|----------|-------------|----------------|
| Small (< 100 profiles) | 1 account | 80 profiles | 80/day |
| Medium (100-200 profiles) | 2 accounts | 80 profiles | 160/day |
| Large (200-300 profiles) | 3 accounts | 80 profiles | 240/day |

### Human Behavior Simulation

To avoid detection, the scraper includes:

- **Random Delays**: Variable wait times between requests (configurable min/max)
- **Random Scrolling**: Simulates human scrolling patterns on profile pages
- **Random Mouse Movement**: Mimics natural mouse cursor movement
- **Page Diversification**: Occasionally visits LinkedIn feed/search pages
- **Action Randomization**: Varies the sequence of scraping actions

Configure behavior simulation:

```bash
SCRAPER_MIN_DELAY=3    # Minimum seconds between profiles
SCRAPER_MAX_DELAY=8    # Maximum seconds between profiles
SCRAPER_SLOW_MO=100    # Milliseconds between browser actions
```

### Security Considerations

- **Dedicated Accounts**: Never use personal LinkedIn accounts for scraping
- **2FA Limitation**: Disable 2FA on scraping accounts (system cannot bypass it)
- **Rate Limiting**: Respect daily limits to avoid account suspension
- **Account Risk**: LinkedIn may suspend accounts that violate Terms of Service
- **Checkpoint Handling**: System automatically flags and rotates accounts that hit security checkpoints
- **Manual Verification**: Flagged accounts may need manual login to clear checkpoints

### Monitoring Account Usage

The admin panel's "Scraping Control" tab shows:
- Current usage for each account (progress bars)
- Profiles scraped today vs. daily limit
- Account status (active, exhausted, flagged)
- Estimated time remaining before account exhaustion

### Troubleshooting Multi-Account Setup

| Issue | Solution |
|-------|----------|
| Only one account loading | Check numbering is sequential (1, 2, 3...) with no gaps |
| Account exhausted immediately | Verify daily limit is set correctly |
| All accounts flagged | Accounts may need manual verification; log in manually |
| Login failures | Verify credentials are correct for each account |
| Security checkpoints | System will auto-rotate; manually verify flagged accounts later |

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following:

#### Database Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DB_HOST` | PostgreSQL host | Yes | `localhost` |
| `DB_PORT` | PostgreSQL port | Yes | `5432` |
| `DB_NAME` | Database name | Yes | `alumni_db` |
| `DB_USER` | Database username | Yes | - |
| `DB_PASSWORD` | Database password | Yes | - |

#### LinkedIn Account Configuration (Multi-Account Support)

The system supports multiple LinkedIn accounts for rate limiting and load distribution. Configure accounts using numbered environment variables:

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `LINKEDIN_EMAIL_1` | First LinkedIn account email | Yes | `scraper1@example.com` |
| `LINKEDIN_PASSWORD_1` | First LinkedIn account password | Yes | `password123` |
| `LINKEDIN_EMAIL_2` | Second LinkedIn account email | No | `scraper2@example.com` |
| `LINKEDIN_PASSWORD_2` | Second LinkedIn account password | No | `password456` |
| `LINKEDIN_EMAIL_3` | Third LinkedIn account email | No | `scraper3@example.com` |
| `LINKEDIN_PASSWORD_3` | Third LinkedIn account password | No | `password789` |

**Note**: The system will automatically detect and load all numbered accounts sequentially (1, 2, 3, ...) until it encounters a missing number. You can configure as many accounts as needed.

#### Scraper Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SCRAPER_DAILY_LIMIT_PER_ACCOUNT` | Maximum profiles per account per day | No | `80` |
| `SCRAPER_MIN_DELAY` | Minimum delay between requests (seconds) | No | `3` |
| `SCRAPER_MAX_DELAY` | Maximum delay between requests (seconds) | No | `8` |
| `SCRAPER_MAX_RETRIES` | Maximum retry attempts for failed scrapes | No | `3` |
| `SCRAPER_HEADLESS` | Run browser in headless mode | No | `true` |
| `SCRAPER_SLOW_MO` | Milliseconds delay between actions | No | `100` |

#### Backblaze B2 Storage Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `B2_APPLICATION_KEY_ID` | Backblaze B2 key ID | Yes |
| `B2_APPLICATION_KEY` | Backblaze B2 application key | Yes |
| `B2_BUCKET_NAME` | B2 bucket name for PDFs | Yes |

### GitHub Secrets (for automation)

For the GitHub Actions workflow, configure these repository secrets. See the [Automated Scraping with GitHub Actions](#automated-scraping-with-github-actions) section below for detailed setup instructions.

Required secrets include database credentials, LinkedIn account credentials (supports multiple accounts), and B2 storage credentials.

## Project Structure

```
ARC-IIM/
├── alumni_system/                    # Main application package
│   ├── __init__.py
│   ├── chatbot/                      # NLP chatbot module
│   │   ├── __init__.py
│   │   ├── config.py                 # Chatbot configuration
│   │   ├── nlp_chatbot.py           # Main chatbot class
│   │   ├── query_parser.py          # Natural language query parser
│   │   └── query_executor.py        # Query execution and formatting
│   ├── database/                     # Database module
│   │   ├── __init__.py
│   │   ├── config.py                 # Database configuration
│   │   ├── connection.py             # Connection management
│   │   ├── crud.py                   # CRUD operations
│   │   ├── init_db.py               # Database initialization
│   │   ├── migrations.py            # Schema migrations
│   │   ├── models.py                # SQLAlchemy models
│   │   └── import_utils.py          # Bulk import utilities
│   ├── frontend/                     # Web interface module
│   │   ├── __init__.py
│   │   ├── app.py                   # Main Streamlit application
│   │   └── demo_mode.py             # Demo mode with sample data
│   ├── scraper/                      # LinkedIn scraper module
│   │   ├── __init__.py
│   │   ├── config.py                 # Scraper configuration
│   │   ├── linkedin_scraper.py      # Main scraper class
│   │   ├── account_rotation.py      # Multi-account rotation manager
│   │   ├── human_behavior.py        # Human behavior simulation
│   │   ├── job.py                   # Scraping job orchestrator
│   │   └── run.py                   # CLI runner for manual scraping
│   ├── storage/                      # Cloud storage module
│   │   ├── __init__.py
│   │   ├── b2_client.py             # Backblaze B2 client
│   │   └── config.py                # Storage configuration
│   └── utils/                        # Utility modules
│       ├── __init__.py
│       └── error_handling.py        # Error handling utilities
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration and fixtures
│   ├── test_account_rotation.py     # Account rotation tests
│   ├── test_alumni_details_*.py     # Alumni details tests
│   ├── test_b2_*.py                 # B2 storage tests
│   ├── test_chatbot_*.py            # Chatbot tests
│   ├── test_crud_*.py               # CRUD operation tests
│   ├── test_dashboard_*.py          # Dashboard tests
│   ├── test_database_*.py           # Database tests
│   ├── test_error_*.py              # Error handling tests
│   ├── test_export_*.py             # Export functionality tests
│   ├── test_human_behavior.py       # Human behavior simulation tests
│   ├── test_import_utils.py         # Import utilities tests
│   ├── test_linkedin_scraper.py     # LinkedIn scraper tests
│   ├── test_pagination_*.py         # Pagination tests
│   ├── test_previous_companies*.py  # Previous companies tests
│   ├── test_progress_tracking.py    # Progress tracking tests
│   ├── test_query_parser.py         # Query parser tests
│   ├── test_scraping_*.py           # Scraping tests
│   └── test_search_filter_*.py      # Search and filter tests
├── .github/                          # GitHub configuration
│   └── workflows/
│       └── scraper.yml              # Automated scraping workflow
├── scripts/                          # Utility scripts
│   └── init_db.sql                  # Database initialization SQL
├── docker-compose.yml               # Docker Compose for local PostgreSQL
├── .env.example                     # Example environment variables
├── .gitignore                       # Git ignore rules
├── README.md                        # This file
└── requirements.txt                 # Python dependencies
```

## Usage

### Web Interface

The Streamlit application provides:

- **Dashboard**: Overview of alumni statistics (total count, batches, companies, locations)
- **Browse Alumni**: Paginated view of all alumni records with previous companies column
- **Search & Filter**: Filter by batch, company, location, or search by name
- **Alumni Details**: View detailed career history with all past companies and roles
- **Chatbot**: Natural language queries about alumni data
- **Admin Panel**: Comprehensive management interface with multiple tabs:
  - **Add Alumni**: Create new alumni records manually
  - **Edit Alumni**: Update existing alumni information
  - **Delete Alumni**: Remove alumni records (with cascade deletion)
  - **Bulk Import**: Import from Excel/CSV files
  - **Scraping Control**: Monitor and control scraping operations

### Scraping Control Interface

The Scraping Control tab in the Admin Panel provides real-time monitoring and control:

#### Queue Statistics
- **Profiles in Queue**: Number of profiles waiting to be scraped
- **Profiles Completed**: Successfully scraped profiles
- **Profiles Failed**: Failed scraping attempts

#### Account Usage Monitoring
- **Progress Bars**: Visual representation of usage for each account
- **Usage Counters**: Shows "45/80" format (used/limit)
- **Account Status**: Indicates if account is active, exhausted, or flagged
- **Estimated Capacity**: Shows remaining capacity across all accounts

#### Scraping Controls
- **Start Scraping**: Begin processing the queue
- **Pause/Resume**: Control scraping execution (if implemented)
- **Real-time Progress**: Updates as profiles are processed
- **Current Status**: Shows which profile is being scraped and which account is in use

#### Features
- ✅ Real-time progress updates
- ✅ Multi-account usage visualization
- ✅ Queue management and statistics
- ✅ Error tracking and reporting
- ✅ Automatic account rotation display
- ✅ Daily limit enforcement visualization

### Bulk Import Workflow

The system provides a comprehensive bulk import feature that automatically queues profiles for scraping.

#### Step 1: Prepare Your Data File

Create an Excel (.xlsx, .xls) or CSV file with alumni data. The system uses flexible column name detection.

**Required columns** (any variation will work):

| Column Variations | Description |
|-------------------|-------------|
| `Roll No.`, `roll_number`, `Roll Number`, `RollNo` | Student roll number (unique identifier) |
| `LinkedIn ID`, `linkedin_url`, `LinkedIn`, `linkedin_id` | LinkedIn profile URL or username |

**Optional columns** (recommended):

| Column Variations | Description |
|-------------------|-------------|
| `Name`, `Name of the Student`, `Student Name` | Alumni name |
| `Batch`, `Year`, `Graduation Year` | Graduation batch/year |
| `Mobile No.`, `phone`, `Phone Number` | Phone number |
| `Personal Email Id.`, `email`, `Personal Email` | Personal email |
| `College mail Id`, `college_email`, `College Email` | College email |

**Example Excel format:**

| Roll No. | Name of the Student | LinkedIn ID | Batch | Mobile No. | Personal Email Id. | College mail Id |
|----------|---------------------|-------------|-------|------------|-------------------|-----------------|
| 2020001 | John Doe | johndoe123 | 2020 | 9876543210 | john@gmail.com | john@college.edu |
| 2020002 | Jane Smith | linkedin.com/in/janesmith | 2020 | 9876543211 | jane@gmail.com | jane@college.edu |
| 2020003 | Bob Wilson | https://www.linkedin.com/in/bobwilson | 2020 | 9876543212 | bob@gmail.com | bob@college.edu |

#### Step 2: Import the File

1. Open the web interface and navigate to **Admin Panel**
2. Click on the **Bulk Import** tab
3. Click "Upload Excel/CSV" and select your file
4. Review the import preview showing detected columns and data

#### Step 3: Review Import Summary

The system will display:
- **Total rows** in the file
- **New records** that will be created
- **Updates** to existing records (matched by roll number)
- **Duplicates** that will be skipped
- **Validation errors** if any required columns are missing

#### Step 4: Confirm Import

Click "Import and Queue for Scraping" to:
- Create/update alumni records in the database
- Automatically add all profiles to the scraping queue
- Convert LinkedIn usernames to full URLs (e.g., `johndoe` → `https://www.linkedin.com/in/johndoe`)

#### Step 5: Start Scraping

1. Navigate to the **Scraping Control** tab in Admin Panel
2. Review queue statistics:
   - Profiles in queue (pending)
   - Profiles completed
   - Profiles failed
3. Check account usage (progress bars for each account)
4. Click **"Start Scraping"** to begin processing the queue

#### Step 6: Monitor Progress

The scraping control interface shows real-time updates:
- Current profile being scraped
- Account in use
- Progress percentage
- Estimated time remaining
- Profiles completed / total profiles

#### What Gets Scraped?

For each profile in the queue, the system extracts:
- ✅ Current company and designation
- ✅ Location
- ✅ Complete job history (all previous companies and roles)
- ✅ Education history (degrees, institutions, years)
- ✅ Contact information (if available)
- ✅ PDF snapshot of the LinkedIn profile (stored in B2)

#### Import Features

- **Flexible Column Detection**: Automatically recognizes common column name variations
- **Duplicate Handling**: Skips duplicate roll numbers, updates existing records
- **URL Conversion**: Converts LinkedIn usernames to full URLs automatically
- **Validation**: Checks for required columns before import
- **Queue Population**: Automatically queues all imported profiles for scraping
- **Summary Report**: Shows exactly what will be imported before confirmation

#### Troubleshooting Import Issues

| Issue | Solution |
|-------|----------|
| "Missing required columns" error | Ensure file has Roll No. and LinkedIn ID columns |
| Duplicates not detected | Check that roll numbers are consistent (no extra spaces) |
| LinkedIn URLs not working | System auto-converts usernames; both formats work |
| Import succeeds but scraping fails | Check LinkedIn account credentials and rate limits |
| Some profiles skipped | Review import summary for duplicate or invalid entries |

### Chatbot Queries

Example queries the chatbot can handle:

- "Who works at Google?"
- "Find alumni from batch 2020"
- "Show all software engineers"
- "How many alumni do we have?"
- "Alumni in Bangalore"

### Manual Scraping

Run the scraper manually:

```bash
python -m alumni_system.scraper.run --batch 2020 --max-profiles 50
```

Options:
- `--batch`: Filter by specific batch
- `--max-profiles`: Maximum profiles to scrape (default: 100)
- `--force-update`: Update all profiles regardless of last scrape time
- `--update-threshold-days`: Days threshold for updates (default: 180)

### Automated Scraping with GitHub Actions

The system includes a GitHub Actions workflow that automatically scrapes alumni profiles on a schedule.

#### Schedule

The workflow runs automatically:
- **January 1st at 00:00 UTC** - Start of year update
- **July 1st at 00:00 UTC** - Mid-year update

#### Manual Triggering

You can also trigger the workflow manually:

1. Go to your repository on GitHub
2. Click on the **Actions** tab
3. Select **LinkedIn Profile Scraper** workflow
4. Click **Run workflow**
5. Configure options:
   - **Batch**: Filter by specific batch (optional)
   - **Max Profiles**: Maximum number of profiles to scrape (default: 100)
   - **Force Update**: Update all profiles regardless of last scrape time
   - **Update Threshold Days**: Only update profiles not scraped within this many days (default: 180)

#### Setting Up GitHub Secrets

To enable the automated workflow, configure these repository secrets:

1. Go to your repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add each of the following:

**Required Secrets:**

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DB_HOST` | PostgreSQL database host | `your-db-host.com` |
| `DB_PORT` | PostgreSQL database port | `5432` |
| `DB_NAME` | Database name | `alumni_db` |
| `DB_USER` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | `your-secure-password` |
| `LINKEDIN_EMAIL_1` | First LinkedIn account email | `scraper1@example.com` |
| `LINKEDIN_PASSWORD_1` | First LinkedIn account password | `password123` |
| `B2_KEY_ID` | Backblaze B2 application key ID | `0001234567890abcdef` |
| `B2_APPLICATION_KEY` | Backblaze B2 application key | `K001abcdefghijklmnopqrstuvwxyz` |
| `B2_BUCKET_NAME` | B2 bucket name for PDFs | `alumni-profiles` |

**Optional Secrets (for multiple accounts):**

| Secret Name | Description |
|-------------|-------------|
| `LINKEDIN_EMAIL_2` | Second LinkedIn account email |
| `LINKEDIN_PASSWORD_2` | Second LinkedIn account password |
| `LINKEDIN_EMAIL_3` | Third LinkedIn account email |
| `LINKEDIN_PASSWORD_3` | Third LinkedIn account password |
| `SCRAPER_DAILY_LIMIT_PER_ACCOUNT` | Daily scraping limit per account (default: 80) |
| `SCRAPER_MIN_DELAY` | Minimum delay between requests in seconds (default: 3) |
| `SCRAPER_MAX_DELAY` | Maximum delay between requests in seconds (default: 8) |
| `SCRAPER_MAX_RETRIES` | Maximum retry attempts for failed scrapes (default: 3) |

#### Multi-Account Setup

The workflow supports multiple LinkedIn accounts for rate limiting:

1. Add credentials for each account using numbered environment variables:
   - `LINKEDIN_EMAIL_1`, `LINKEDIN_PASSWORD_1`
   - `LINKEDIN_EMAIL_2`, `LINKEDIN_PASSWORD_2`
   - `LINKEDIN_EMAIL_3`, `LINKEDIN_PASSWORD_3`
   - And so on...

2. The system will automatically rotate between accounts when one reaches its daily limit

3. Recommended: Use 2-3 dedicated LinkedIn accounts with daily limits of 50-80 profiles each

#### Workflow Features

- ✅ **Automatic scheduling** - Runs twice a year without manual intervention
- ✅ **Manual triggering** - Run on-demand with custom parameters
- ✅ **Multi-account rotation** - Distributes load across multiple LinkedIn accounts
- ✅ **Error notifications** - Creates GitHub issues when scraping fails
- ✅ **Log artifacts** - Uploads scraping logs for debugging
- ✅ **Configurable parameters** - Customize batch, profile count, and update threshold
- ✅ **Update threshold** - Only scrapes profiles older than 180 days (configurable)

#### Monitoring Workflow Runs

1. Go to the **Actions** tab in your repository
2. Click on a workflow run to see details
3. View logs for each step
4. Download artifacts (scraping logs) if needed

#### Error Notifications

When a scraping job fails:
- An issue is automatically created in your repository
- The issue includes:
  - Workflow run number and link
  - Trigger details (scheduled or manual)
  - Configuration parameters used
  - Link to detailed logs

#### Troubleshooting GitHub Actions

| Issue | Solution |
|-------|----------|
| Workflow not running | Check that secrets are configured correctly |
| Login failures | Verify LinkedIn credentials in secrets |
| Database connection errors | Ensure DB_HOST is accessible from GitHub Actions runners |
| Rate limiting | Add more LinkedIn accounts or reduce max_profiles |
| Security checkpoints | LinkedIn accounts may need manual verification |

## API and Function Interfaces

### Database CRUD Operations

Located in `alumni_system/database/crud.py`

#### Alumni Operations

```python
# Create or update alumni record
def create_alumni(db: Session, **kwargs) -> Alumni
    """
    Create new alumni or update existing (upsert based on roll_number).
    
    Args:
        db: Database session
        **kwargs: Alumni fields (name, roll_number, batch, etc.)
    
    Returns:
        Alumni: Created or updated alumni record
    """

# Retrieve alumni
def get_alumni_by_id(db: Session, alumni_id: int) -> Optional[Alumni]
def get_alumni_by_roll_number(db: Session, roll_number: str) -> Optional[Alumni]
def get_all_alumni(db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Alumni]

# Update alumni
def update_alumni(db: Session, alumni_id: int, **kwargs) -> Alumni
    """
    Update alumni record. Preserves created_at, updates updated_at.
    """

# Delete alumni (cascades to job_history and education_history)
def delete_alumni(db: Session, alumni_id: int) -> bool

# Search alumni
def search_alumni(db: Session, query: str, limit: int = 100) -> List[Alumni]
    """
    Search alumni by name or current company (case-insensitive).
    """

# Utility functions
def get_unique_batches(db: Session) -> List[str]
def get_unique_companies(db: Session) -> List[str]
def get_unique_locations(db: Session) -> List[str]
```

#### Job History Operations

```python
def create_job_history(db: Session, alumni_id: int, **kwargs) -> JobHistory
    """
    Create job history entry for an alumni.
    
    Args:
        alumni_id: Alumni ID
        company_name: Company name
        designation: Job title
        start_date: Start date
        end_date: End date (None if current)
        is_current: Boolean flag for current position
        location: Job location
        employment_type: Full-time, Part-time, etc.
    """

def get_job_history_by_alumni(db: Session, alumni_id: int) -> List[JobHistory]
    """
    Get all job history for an alumni, sorted by start_date descending.
    """
```

#### Education History Operations

```python
def create_education_history(db: Session, alumni_id: int, **kwargs) -> EducationHistory
def get_education_history_by_alumni(db: Session, alumni_id: int) -> List[EducationHistory]
```

#### Scraping Queue Operations

```python
def add_to_scraping_queue(db: Session, alumni_id: int, priority: int = 0) -> ScrapingQueue
    """
    Add alumni profile to scraping queue.
    
    Args:
        alumni_id: Alumni ID to scrape
        priority: Higher priority profiles scraped first (default: 0)
    """

def get_next_from_queue(db: Session) -> Optional[ScrapingQueue]
    """
    Get next pending profile from queue (highest priority first).
    """

def mark_queue_item_complete(db: Session, queue_id: int) -> None
def mark_queue_item_failed(db: Session, queue_id: int) -> None

def get_queue_stats(db: Session) -> Dict[str, int]
    """
    Returns: {'pending': N, 'completed': M, 'failed': K}
    """
```

#### Account Usage Operations

```python
def get_account_usage(db: Session, account_email: str, date: date) -> int
    """
    Get number of profiles scraped by account on specific date.
    """

def increment_account_usage(db: Session, account_email: str) -> None
    """
    Increment usage counter for account (today's date).
    """

def reset_daily_usage(db: Session) -> None
    """
    Reset all account usage counters (called at midnight UTC).
    """
```

### LinkedIn Scraper

Located in `alumni_system/scraper/linkedin_scraper.py`

```python
class LinkedInScraper:
    """
    Playwright-based LinkedIn profile scraper with multi-account support.
    """
    
    async def __aenter__(self) -> 'LinkedInScraper':
        """Context manager entry - initializes browser."""
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - closes browser."""
    
    async def login(self, account: LinkedInAccount) -> bool:
        """
        Authenticate with LinkedIn using account credentials.
        
        Args:
            account: LinkedInAccount with email and password
        
        Returns:
            bool: True if login successful
        """
    
    async def scrape_profile(self, linkedin_url: str) -> Optional[ProfileData]:
        """
        Scrape LinkedIn profile data.
        
        Args:
            linkedin_url: Full LinkedIn profile URL
        
        Returns:
            ProfileData: Extracted profile data or None if failed
        """
    
    async def download_profile_pdf(self, linkedin_url: str) -> Optional[bytes]:
        """
        Generate PDF snapshot of LinkedIn profile.
        
        Returns:
            bytes: PDF file content or None if failed
        """
```

### Account Rotation Manager

Located in `alumni_system/scraper/account_rotation.py`

```python
class AccountRotationManager:
    """
    Manages multiple LinkedIn accounts with rate limiting.
    """
    
    def __init__(self, accounts: List[LinkedInAccount], daily_limit: int):
        """
        Args:
            accounts: List of LinkedIn accounts
            daily_limit: Max profiles per account per day
        """
    
    def get_next_account(self) -> Optional[LinkedInAccount]:
        """
        Get next available account (not exhausted or flagged).
        
        Returns:
            LinkedInAccount or None if all exhausted
        """
    
    def mark_account_exhausted(self, account_id: str) -> None:
        """Mark account as having reached daily limit."""
    
    def mark_account_flagged(self, account_id: str) -> None:
        """Mark account as requiring manual verification."""
    
    def reset_daily_counters(self) -> None:
        """Reset all usage counters (called at midnight UTC)."""
    
    def get_usage_stats(self) -> Dict[str, Dict]:
        """
        Returns usage statistics for all accounts.
        
        Returns:
            {
                'account1@example.com': {
                    'used': 45,
                    'limit': 80,
                    'flagged': False
                },
                ...
            }
        """
```

### Human Behavior Simulator

Located in `alumni_system/scraper/human_behavior.py`

```python
class HumanBehaviorSimulator:
    """
    Simulates human browsing behavior to avoid detection.
    """
    
    async def random_delay(self, min_sec: float, max_sec: float) -> None:
        """Random delay between min and max seconds."""
    
    async def random_scroll(self, page: Page) -> None:
        """Simulate random scrolling on page."""
    
    async def random_mouse_movement(self, page: Page) -> None:
        """Simulate random mouse cursor movement."""
    
    async def visit_random_page(self, page: Page) -> None:
        """Occasionally visit LinkedIn feed or search page."""
```

### Bulk Import Utilities

Located in `alumni_system/database/import_utils.py`

```python
def import_from_csv(db: Session, file_path: str) -> Dict[str, int]:
    """
    Import alumni from CSV file.
    
    Returns:
        {
            'imported': N,
            'updated': M,
            'skipped': K,
            'queued': N+M
        }
    """

def import_from_excel(db: Session, file_path: str) -> Dict[str, int]:
    """Import alumni from Excel file."""

def detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect column mappings from DataFrame.
    
    Returns:
        {
            'roll_number': 'Roll No.',
            'linkedin_id': 'LinkedIn ID',
            'name': 'Name of the Student',
            ...
        }
    """

def convert_linkedin_username_to_url(username: str) -> str:
    """
    Convert LinkedIn username to full URL.
    
    Args:
        username: 'johndoe' or 'linkedin.com/in/johndoe' or full URL
    
    Returns:
        'https://www.linkedin.com/in/johndoe'
    """
```

### B2 Storage Client

Located in `alumni_system/storage/b2_client.py`

```python
class B2Client:
    """
    Backblaze B2 storage client for PDF uploads.
    """
    
    def __init__(self, key_id: str, app_key: str, bucket_name: str):
        """Initialize B2 client with credentials."""
    
    def upload_pdf(self, pdf_bytes: bytes, roll_number: str) -> str:
        """
        Upload PDF to B2 storage.
        
        Args:
            pdf_bytes: PDF file content
            roll_number: Alumni roll number
        
        Returns:
            str: B2 file URL
        
        Raises:
            B2Error: If upload fails
        """
    
    def download_pdf(self, file_url: str) -> bytes:
        """Download PDF from B2."""
    
    def get_download_url(self, file_url: str) -> str:
        """Get public download URL for PDF."""
```

### NLP Chatbot

Located in `alumni_system/chatbot/nlp_chatbot.py`

```python
class NLPChatbot:
    """
    Natural language query processor for alumni data.
    """
    
    def __init__(self, db_session: Session):
        """Initialize chatbot with database session."""
    
    def process_query(self, user_input: str) -> ChatbotResponse:
        """
        Process natural language query.
        
        Args:
            user_input: User's natural language query
        
        Returns:
            ChatbotResponse with text response and alumni data
        
        Example:
            >>> chatbot.process_query("Who works at Google?")
            ChatbotResponse(
                response="Found 5 alumni working at Google",
                alumni=[...],
                count=5
            )
        """
```

### Scraping Job Orchestrator

Located in `alumni_system/scraper/job.py`

```python
class ScrapingJobOrchestrator:
    """
    Orchestrates scraping jobs with queue processing and account rotation.
    """
    
    def __init__(self, db: Session, account_manager: AccountRotationManager):
        """Initialize orchestrator."""
    
    async def process_queue(self, max_profiles: int = None) -> Dict[str, int]:
        """
        Process scraping queue.
        
        Args:
            max_profiles: Maximum profiles to scrape (None = all)
        
        Returns:
            {
                'processed': N,
                'successful': M,
                'failed': K
            }
        """
    
    async def scrape_stale_profiles(self, threshold_days: int = 180) -> Dict[str, int]:
        """
        Scrape profiles not updated within threshold days.
        """
    
    async def scrape_batch(self, batch: str, force_update: bool = False) -> Dict[str, int]:
        """
        Scrape all profiles from specific batch.
        """
```

## Database Schema

### Alumni Table
- **Primary Key**: `id` (auto-increment)
- **Unique Constraints**: `roll_number`, `linkedin_id`
- **Indexes**: `batch`, `roll_number`, `name`, `linkedin_id`, `current_company`, `current_designation`
- **Timestamps**: `created_at`, `updated_at`, `last_scraped_at`

**Fields**:
- Personal info: `name`, `gender`, `batch`, `roll_number`
- Contact info: `mobile_number`, `whatsapp_number`, `personal_email`, `college_email`, `corporate_email`
- LinkedIn info: `linkedin_id`, `linkedin_url`, `linkedin_pdf_url`
- Current position: `current_company`, `current_designation`, `location`
- Additional: `por`, `internship`, `higher_studies`, `remarks`, `address`

### Job History Table
- **Primary Key**: `id` (auto-increment)
- **Foreign Key**: `alumni_id` → `alumni.id` (CASCADE DELETE)
- **Indexes**: `alumni_id`, `company_name`

**Fields**:
- `company_name`, `designation`, `location`
- `start_date`, `end_date`, `is_current`
- `employment_type`, `description`

### Education History Table
- **Primary Key**: `id` (auto-increment)
- **Foreign Key**: `alumni_id` → `alumni.id` (CASCADE DELETE)
- **Indexes**: `alumni_id`, `institution_name`

**Fields**:
- `institution_name`, `degree`, `field_of_study`
- `start_year`, `end_year`, `grade`
- `activities`, `description`

### Scraping Queue Table
- **Primary Key**: `id` (auto-increment)
- **Foreign Key**: `alumni_id` → `alumni.id` (CASCADE DELETE)
- **Indexes**: `status`, `priority`

**Fields**:
- `alumni_id`, `priority`, `status`
- `attempts`, `last_attempt_at`, `created_at`

**Status Values**: `pending`, `in_progress`, `completed`, `failed`

### Account Usage Table
- **Primary Key**: `id` (auto-increment)
- **Unique Constraint**: (`account_email`, `date`)

**Fields**:
- `account_email`, `date`, `profiles_scraped`
- `is_flagged`, `created_at`, `updated_at`

### Scraping Logs Table
- **Primary Key**: `id` (auto-increment)
- **Foreign Key**: `alumni_id` → `alumni.id` (optional)

**Fields**:
- `alumni_id`, `linkedin_url`, `account_email`
- `status`, `error_message`, `pdf_stored`
- `duration_seconds`, `created_at`

**Status Values**: `success`, `failed`, `skipped`

## Security Considerations

- **Never commit** the `.env` file or any credentials to version control
- Use strong, unique passwords for all services
- Rotate credentials periodically
- Be mindful of LinkedIn's Terms of Service regarding scraping
- Enable 2FA on your LinkedIn account for security

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational purposes. Be aware of and comply with LinkedIn's Terms of Service when using the scraping functionality.

## Troubleshooting Guide

### Database Issues

#### Connection Failures

**Symptom**: "Could not connect to database" error

**Solutions**:
1. Verify PostgreSQL is running:
   ```bash
   docker-compose ps
   ```
2. Check environment variables in `.env`:
   ```bash
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=alumni_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```
3. Test connection manually:
   ```bash
   psql -h localhost -p 5432 -U postgres -d alumni_db
   ```
4. Restart database:
   ```bash
   docker-compose restart
   ```

#### Database Initialization Errors

**Symptom**: Tables not created or migration errors

**Solutions**:
1. Run initialization manually:
   ```bash
   python -c "from alumni_system.database.init_db import init_database; init_database()"
   ```
2. Check database logs:
   ```bash
   docker-compose logs db
   ```
3. Reset database (WARNING: deletes all data):
   ```bash
   docker-compose down -v
   docker-compose up -d
   python -c "from alumni_system.database.init_db import init_database; init_database()"
   ```

#### Demo Mode Activation

**Symptom**: Web interface shows "Running in Demo Mode"

**Cause**: Database connection failed; system is using sample data

**Solutions**:
1. Fix database connection (see above)
2. Restart the Streamlit application
3. Verify database credentials are correct

### LinkedIn Scraping Issues

#### Login Failures

**Symptom**: "Login failed" or "Authentication error"

**Solutions**:
1. Verify credentials in `.env`:
   ```bash
   LINKEDIN_EMAIL_1=your_email@example.com
   LINKEDIN_PASSWORD_1=your_password
   ```
2. Test login manually in a browser
3. Check for typos in email/password
4. Ensure account is not suspended
5. Disable 2FA on the scraping account

#### Security Checkpoints

**Symptom**: "Security checkpoint detected" in logs

**Cause**: LinkedIn requires manual verification (CAPTCHA, email verification)

**Solutions**:
1. Log in manually to the flagged account
2. Complete the security verification
3. System will automatically rotate to next account
4. Flagged accounts will be skipped until manually verified
5. Consider using longer delays between requests

#### Account Exhaustion

**Symptom**: "All accounts exhausted" message

**Cause**: All configured accounts reached their daily limit

**Solutions**:
1. Wait until midnight UTC for automatic reset
2. Add more LinkedIn accounts to `.env`
3. Increase `SCRAPER_DAILY_LIMIT_PER_ACCOUNT` (not recommended)
4. Reduce the number of profiles to scrape per day

#### Rate Limiting / Account Suspension

**Symptom**: Account suspended or blocked by LinkedIn

**Prevention**:
1. Use reasonable delays (3-8 seconds recommended)
2. Don't exceed 80 profiles per account per day
3. Use multiple accounts to distribute load
4. Enable human behavior simulation
5. Use dedicated accounts, not personal ones

**Recovery**:
1. Create new dedicated LinkedIn accounts
2. Use longer delays between requests
3. Reduce daily limit per account
4. Consider using residential proxies (advanced)

#### Scraping Failures

**Symptom**: Profiles marked as "failed" in queue

**Solutions**:
1. Check scraping logs in admin panel
2. Verify LinkedIn URLs are correct
3. Check if profile is public (private profiles can't be scraped)
4. Increase `SCRAPER_MAX_RETRIES` in `.env`
5. Review error messages in scraping logs table

### Bulk Import Issues

#### Column Detection Failures

**Symptom**: "Missing required columns" error

**Solutions**:
1. Ensure file has "Roll No." and "LinkedIn ID" columns
2. Check for typos in column headers
3. Use one of the recognized column name variations
4. Remove extra spaces from column headers
5. Ensure file is properly formatted (Excel or CSV)

#### Duplicate Handling

**Symptom**: Duplicates not being detected or skipped

**Solutions**:
1. Check roll numbers are consistent (no extra spaces)
2. Verify roll numbers are unique in the file
3. Review import summary before confirming
4. Check database for existing records with same roll number

#### LinkedIn URL Conversion

**Symptom**: LinkedIn URLs not working after import

**Solutions**:
1. System auto-converts usernames to full URLs
2. Both formats work: `johndoe` or `https://www.linkedin.com/in/johndoe`
3. Verify LinkedIn IDs don't have extra characters
4. Check scraping logs for specific URL errors

### Scraping Queue Issues

#### Queue Not Processing

**Symptom**: Profiles stuck in "pending" status

**Solutions**:
1. Click "Start Scraping" in Scraping Control tab
2. Check if all accounts are exhausted
3. Verify LinkedIn credentials are valid
4. Check for errors in scraping logs
5. Restart the scraping job

#### Progress Not Updating

**Symptom**: Progress bar stuck or not moving

**Solutions**:
1. Refresh the page
2. Check if scraping is actually running (check logs)
3. Verify accounts are not all exhausted
4. Look for errors in terminal/logs

### B2 Storage Issues

#### Upload Failures

**Symptom**: "PDF storage failed" in scraping logs

**Impact**: Scraping continues; only PDF storage fails (by design)

**Solutions**:
1. Verify B2 credentials in `.env`:
   ```bash
   B2_APPLICATION_KEY_ID=your_key_id
   B2_APPLICATION_KEY=your_app_key
   B2_BUCKET_NAME=your_bucket_name
   ```
2. Check bucket exists and is accessible
3. Verify bucket permissions allow uploads
4. Check B2 account is active and not suspended
5. Review B2 storage quota and limits

#### PDF Download Issues

**Symptom**: Cannot download PDF from alumni details page

**Solutions**:
1. Verify `linkedin_pdf_url` is set in database
2. Check B2 bucket permissions allow public downloads
3. Verify file exists in B2 bucket
4. Check B2 URL is not expired (if using temporary URLs)

### Web Interface Issues

#### Streamlit Errors

**Symptom**: Application crashes or shows errors

**Solutions**:
1. Check terminal for error messages
2. Restart the application:
   ```bash
   streamlit run alumni_system/frontend/app.py
   ```
3. Clear Streamlit cache:
   ```bash
   rm -rf ~/.streamlit/cache
   ```
4. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

#### Slow Performance

**Symptom**: Pages load slowly or timeout

**Solutions**:
1. Check database query performance
2. Add indexes to frequently queried columns
3. Reduce page size in pagination settings
4. Optimize filters (use specific criteria)
5. Check database connection pool settings

#### Data Not Updating

**Symptom**: Changes not reflected in web interface

**Solutions**:
1. Refresh the page (Ctrl+R or Cmd+R)
2. Clear browser cache
3. Check if changes were saved to database
4. Verify database connection is active
5. Restart Streamlit application

### Chatbot Issues

#### Query Not Understood

**Symptom**: "I couldn't understand your query" message

**Solutions**:
1. Use simpler, more direct queries
2. Follow example query patterns:
   - "Who works at Google?"
   - "Find alumni from batch 2020"
   - "Show software engineers"
3. Avoid complex or ambiguous phrasing
4. Check spelling of company names and titles

#### Incorrect Results

**Symptom**: Chatbot returns wrong or incomplete results

**Solutions**:
1. Verify data exists in database
2. Check query parsing in logs
3. Use exact company/batch names from database
4. Try alternative phrasing
5. Use web interface filters for complex queries

### GitHub Actions Issues

#### Workflow Not Running

**Symptom**: Scheduled workflow doesn't execute

**Solutions**:
1. Check GitHub Actions is enabled for repository
2. Verify workflow file syntax is correct
3. Check repository secrets are configured
4. Review workflow run history for errors
5. Manually trigger workflow to test

#### Workflow Failures

**Symptom**: Workflow runs but fails

**Solutions**:
1. Check workflow logs in Actions tab
2. Verify all secrets are configured correctly
3. Test database connection from GitHub Actions
4. Check LinkedIn credentials are valid
5. Review error notifications (GitHub issues)

#### Secret Configuration

**Symptom**: "Missing environment variable" errors

**Solutions**:
1. Go to Settings → Secrets and variables → Actions
2. Verify all required secrets are added
3. Check secret names match exactly (case-sensitive)
4. Re-add secrets if they were recently changed
5. Test with manual workflow trigger

### Common Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `psycopg2.OperationalError` | Database connection failed | Check DB credentials and PostgreSQL is running |
| `playwright._impl._api_types.Error` | Browser automation failed | Install Playwright: `playwright install chromium` |
| `b2sdk.exception.NonExistentBucket` | B2 bucket not found | Verify bucket name and B2 credentials |
| `KeyError: 'LINKEDIN_EMAIL_1'` | Missing environment variable | Add required variable to `.env` file |
| `Security checkpoint detected` | LinkedIn verification required | Log in manually to clear checkpoint |
| `All accounts exhausted` | Daily limit reached | Wait for reset or add more accounts |
| `Duplicate roll number` | Roll number already exists | Update existing record or use different roll number |
| `Missing required columns` | Import file format issue | Check column headers match required format |

### Getting Help

If you encounter issues not covered here:

1. **Check Logs**: Review application logs and scraping logs in admin panel
2. **Search Issues**: Look for similar issues in the GitHub repository
3. **Create Issue**: Open a new issue with:
   - Error message (full stack trace)
   - Steps to reproduce
   - Environment details (OS, Python version)
   - Configuration (without sensitive data)
4. **Community**: Ask in discussions or forums

### Best Practices to Avoid Issues

1. **Use dedicated LinkedIn accounts** for scraping (not personal accounts)
2. **Configure multiple accounts** for better rate limit distribution
3. **Use reasonable delays** (3-8 seconds) between requests
4. **Monitor account usage** regularly in Scraping Control tab
5. **Keep credentials secure** (never commit `.env` file)
6. **Regular backups** of database and B2 storage
7. **Test with small batches** before large-scale scraping
8. **Review logs regularly** to catch issues early
9. **Update dependencies** periodically for security patches
10. **Follow LinkedIn's Terms of Service** to avoid account suspension
