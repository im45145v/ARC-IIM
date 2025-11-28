# API Reference

Complete reference documentation for the Alumni Management System's Python API.

## Table of Contents

- [Database Operations](#database-operations)
- [LinkedIn Scraper](#linkedin-scraper)
- [Account Rotation](#account-rotation)
- [Human Behavior Simulation](#human-behavior-simulation)
- [Bulk Import](#bulk-import)
- [B2 Storage](#b2-storage)
- [NLP Chatbot](#nlp-chatbot)
- [Scraping Orchestrator](#scraping-orchestrator)
- [Data Models](#data-models)

---

## Database Operations

Module: `alumni_system.database.crud`

### Alumni CRUD

#### `create_alumni(db: Session, **kwargs) -> Alumni`

Create new alumni record or update existing (upsert based on roll_number).

**Parameters:**
- `db` (Session): SQLAlchemy database session
- `**kwargs`: Alumni fields
  - `roll_number` (str, required): Unique student identifier
  - `name` (str): Alumni name
  - `batch` (str): Graduation batch/year
  - `linkedin_url` (str): LinkedIn profile URL
  - `current_company` (str): Current employer
  - `current_designation` (str): Current job title
  - `location` (str): Current location
  - Additional fields as defined in Alumni model

**Returns:**
- `Alumni`: Created or updated alumni record

**Example:**
```python
from alumni_system.database.crud import create_alumni
from alumni_system.database.connection import get_db

db = next(get_db())
alumni = create_alumni(
    db,
    roll_number="2020001",
    name="John Doe",
    batch="2020",
    linkedin_url="https://www.linkedin.com/in/johndoe",
    current_company="Google",
    current_designation="Software Engineer"
)
```

---

#### `get_alumni_by_id(db: Session, alumni_id: int) -> Optional[Alumni]`

Retrieve alumni by database ID.

**Parameters:**
- `db` (Session): Database session
- `alumni_id` (int): Alumni database ID

**Returns:**
- `Alumni` or `None`: Alumni record if found

---

#### `get_alumni_by_roll_number(db: Session, roll_number: str) -> Optional[Alumni]`

Retrieve alumni by roll number.

**Parameters:**
- `db` (Session): Database session
- `roll_number` (str): Student roll number

**Returns:**
- `Alumni` or `None`: Alumni record if found

---

#### `get_all_alumni(db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Alumni]`

Retrieve alumni with pagination and filtering.

**Parameters:**
- `db` (Session): Database session
- `skip` (int): Number of records to skip (for pagination)
- `limit` (int): Maximum records to return
- `**filters`: Optional filters
  - `batch` (str): Filter by batch
  - `current_company` (str): Filter by company
  - `location` (str): Filter by location

**Returns:**
- `List[Alumni]`: List of alumni records

**Example:**
```python
# Get batch 2020 alumni, page 2 (records 50-100)
alumni = get_all_alumni(db, skip=50, limit=50, batch="2020")
```

---

#### `update_alumni(db: Session, alumni_id: int, **kwargs) -> Alumni`

Update alumni record. Preserves `created_at`, updates `updated_at`.

**Parameters:**
- `db` (Session): Database session
- `alumni_id` (int): Alumni ID to update
- `**kwargs`: Fields to update

**Returns:**
- `Alumni`: Updated alumni record

---

#### `delete_alumni(db: Session, alumni_id: int) -> bool`

Delete alumni record. Cascades to job_history and education_history.

**Parameters:**
- `db` (Session): Database session
- `alumni_id` (int): Alumni ID to delete

**Returns:**
- `bool`: True if deleted successfully

---

#### `search_alumni(db: Session, query: str, limit: int = 100) -> List[Alumni]`

Search alumni by name or company (case-insensitive).

**Parameters:**
- `db` (Session): Database session
- `query` (str): Search term
- `limit` (int): Maximum results

**Returns:**
- `List[Alumni]`: Matching alumni records

**Example:**
```python
# Search for "software" in names and companies
results = search_alumni(db, "software", limit=50)
```

---

### Utility Functions

#### `get_unique_batches(db: Session) -> List[str]`

Get list of all unique batch values.

---

#### `get_unique_companies(db: Session) -> List[str]`

Get list of all unique company names.

---

#### `get_unique_locations(db: Session) -> List[str]`

Get list of all unique locations.

---

### Job History Operations

#### `create_job_history(db: Session, alumni_id: int, **kwargs) -> JobHistory`

Create job history entry for an alumni.

**Parameters:**
- `db` (Session): Database session
- `alumni_id` (int): Alumni ID
- `**kwargs`: Job history fields
  - `company_name` (str, required): Company name
  - `designation` (str): Job title
  - `location` (str): Job location
  - `start_date` (datetime): Start date
  - `end_date` (datetime): End date (None if current)
  - `is_current` (bool): True if current position
  - `employment_type` (str): Full-time, Part-time, etc.
  - `description` (str): Job description

**Returns:**
- `JobHistory`: Created job history record

---

#### `get_job_history_by_alumni(db: Session, alumni_id: int) -> List[JobHistory]`

Get all job history for an alumni, sorted by start_date descending.

**Parameters:**
- `db` (Session): Database session
- `alumni_id` (int): Alumni ID

**Returns:**
- `List[JobHistory]`: Job history records (most recent first)

---

### Education History Operations

#### `create_education_history(db: Session, alumni_id: int, **kwargs) -> EducationHistory`

Create education history entry.

**Parameters:**
- `db` (Session): Database session
- `alumni_id` (int): Alumni ID
- `**kwargs`: Education fields
  - `institution_name` (str, required): Institution name
  - `degree` (str): Degree name
  - `field_of_study` (str): Field of study
  - `start_year` (int): Start year
  - `end_year` (int): End year
  - `grade` (str): Grade/GPA
  - `activities` (str): Activities and societies

**Returns:**
- `EducationHistory`: Created education record

---

#### `get_education_history_by_alumni(db: Session, alumni_id: int) -> List[EducationHistory]`

Get all education history for an alumni.

---

### Scraping Queue Operations

#### `add_to_scraping_queue(db: Session, alumni_id: int, priority: int = 0) -> ScrapingQueue`

Add alumni profile to scraping queue.

**Parameters:**
- `db` (Session): Database session
- `alumni_id` (int): Alumni ID to queue
- `priority` (int): Priority (higher = processed first)

**Returns:**
- `ScrapingQueue`: Queue entry

---

#### `get_next_from_queue(db: Session) -> Optional[ScrapingQueue]`

Get next pending profile from queue (highest priority first).

**Returns:**
- `ScrapingQueue` or `None`: Next queue item or None if empty

---

#### `mark_queue_item_complete(db: Session, queue_id: int) -> None`

Mark queue item as completed.

---

#### `mark_queue_item_failed(db: Session, queue_id: int) -> None`

Mark queue item as failed.

---

#### `get_queue_stats(db: Session) -> Dict[str, int]`

Get queue statistics.

**Returns:**
```python
{
    'pending': 45,
    'completed': 120,
    'failed': 5
}
```

---

### Account Usage Operations

#### `get_account_usage(db: Session, account_email: str, date: date) -> int`

Get number of profiles scraped by account on specific date.

---

#### `increment_account_usage(db: Session, account_email: str) -> None`

Increment usage counter for account (today's date).

---

#### `reset_daily_usage(db: Session) -> None`

Reset all account usage counters. Called at midnight UTC.

---

## LinkedIn Scraper

Module: `alumni_system.scraper.linkedin_scraper`

### LinkedInScraper

Playwright-based LinkedIn profile scraper.

#### Usage

```python
from alumni_system.scraper.linkedin_scraper import LinkedInScraper
from alumni_system.scraper.account_rotation import LinkedInAccount

account = LinkedInAccount(
    id="1",
    email="scraper@example.com",
    password="password123",
    profiles_scraped_today=0,
    is_flagged=False,
    last_used=None
)

async with LinkedInScraper() as scraper:
    success = await scraper.login(account)
    if success:
        profile_data = await scraper.scrape_profile(
            "https://www.linkedin.com/in/johndoe"
        )
        pdf_bytes = await scraper.download_profile_pdf(
            "https://www.linkedin.com/in/johndoe"
        )
```

#### Methods

##### `async login(account: LinkedInAccount) -> bool`

Authenticate with LinkedIn.

**Parameters:**
- `account` (LinkedInAccount): Account credentials

**Returns:**
- `bool`: True if login successful

**Raises:**
- `Exception`: If login fails after retries

---

##### `async scrape_profile(linkedin_url: str) -> Optional[ProfileData]`

Scrape LinkedIn profile data.

**Parameters:**
- `linkedin_url` (str): Full LinkedIn profile URL

**Returns:**
- `ProfileData` or `None`: Extracted data or None if failed

**ProfileData fields:**
- `linkedin_url` (str)
- `name` (str)
- `headline` (str)
- `location` (str)
- `current_company` (str)
- `current_designation` (str)
- `job_history` (List[JobEntry])
- `education_history` (List[EducationEntry])
- `contact_info` (ContactInfo)
- `scraped_at` (datetime)

---

##### `async download_profile_pdf(linkedin_url: str) -> Optional[bytes]`

Generate PDF snapshot of profile.

**Parameters:**
- `linkedin_url` (str): LinkedIn profile URL

**Returns:**
- `bytes` or `None`: PDF file content

---

## Account Rotation

Module: `alumni_system.scraper.account_rotation`

### AccountRotationManager

Manages multiple LinkedIn accounts with rate limiting.

#### Constructor

```python
from alumni_system.scraper.account_rotation import (
    AccountRotationManager,
    LinkedInAccount
)

accounts = [
    LinkedInAccount(
        id="1",
        email="scraper1@example.com",
        password="pass1",
        profiles_scraped_today=0,
        is_flagged=False,
        last_used=None
    ),
    LinkedInAccount(
        id="2",
        email="scraper2@example.com",
        password="pass2",
        profiles_scraped_today=0,
        is_flagged=False,
        last_used=None
    )
]

manager = AccountRotationManager(accounts, daily_limit=80)
```

#### Methods

##### `get_next_account() -> Optional[LinkedInAccount]`

Get next available account (not exhausted or flagged).

**Returns:**
- `LinkedInAccount` or `None`: Next account or None if all exhausted

---

##### `mark_account_exhausted(account_id: str) -> None`

Mark account as having reached daily limit.

---

##### `mark_account_flagged(account_id: str) -> None`

Mark account as requiring manual verification.

---

##### `reset_daily_counters() -> None`

Reset all usage counters. Called at midnight UTC.

---

##### `get_usage_stats() -> Dict[str, Dict]`

Get usage statistics for all accounts.

**Returns:**
```python
{
    'scraper1@example.com': {
        'used': 45,
        'limit': 80,
        'flagged': False,
        'exhausted': False
    },
    'scraper2@example.com': {
        'used': 80,
        'limit': 80,
        'flagged': False,
        'exhausted': True
    }
}
```

---

## Human Behavior Simulation

Module: `alumni_system.scraper.human_behavior`

### HumanBehaviorSimulator

Simulates human browsing behavior to avoid detection.

#### Methods

##### `async random_delay(min_sec: float, max_sec: float) -> None`

Random delay between min and max seconds.

**Example:**
```python
simulator = HumanBehaviorSimulator()
await simulator.random_delay(3.0, 8.0)  # Wait 3-8 seconds
```

---

##### `async random_scroll(page: Page) -> None`

Simulate random scrolling on page.

---

##### `async random_mouse_movement(page: Page) -> None`

Simulate random mouse cursor movement.

---

##### `async visit_random_page(page: Page) -> None`

Occasionally visit LinkedIn feed or search page.

---

## Bulk Import

Module: `alumni_system.database.import_utils`

### Functions

#### `import_from_csv(db: Session, file_path: str) -> Dict[str, int]`

Import alumni from CSV file.

**Parameters:**
- `db` (Session): Database session
- `file_path` (str): Path to CSV file

**Returns:**
```python
{
    'imported': 45,      # New records created
    'updated': 12,       # Existing records updated
    'skipped': 3,        # Duplicates skipped
    'queued': 57         # Profiles queued for scraping
}
```

---

#### `import_from_excel(db: Session, file_path: str) -> Dict[str, int]`

Import alumni from Excel file (.xlsx, .xls).

---

#### `detect_columns(df: pd.DataFrame) -> Dict[str, str]`

Detect column mappings from DataFrame.

**Parameters:**
- `df` (DataFrame): Pandas DataFrame

**Returns:**
```python
{
    'roll_number': 'Roll No.',
    'linkedin_id': 'LinkedIn ID',
    'name': 'Name of the Student',
    'batch': 'Batch',
    'mobile_number': 'Mobile No.',
    'personal_email': 'Personal Email Id.'
}
```

---

#### `convert_linkedin_username_to_url(username: str) -> str`

Convert LinkedIn username to full URL.

**Parameters:**
- `username` (str): Username, partial URL, or full URL

**Returns:**
- `str`: Full LinkedIn URL

**Examples:**
```python
convert_linkedin_username_to_url("johndoe")
# Returns: "https://www.linkedin.com/in/johndoe"

convert_linkedin_username_to_url("linkedin.com/in/johndoe")
# Returns: "https://www.linkedin.com/in/johndoe"

convert_linkedin_username_to_url("https://www.linkedin.com/in/johndoe")
# Returns: "https://www.linkedin.com/in/johndoe"
```

---

## B2 Storage

Module: `alumni_system.storage.b2_client`

### B2Client

Backblaze B2 storage client for PDF uploads.

#### Constructor

```python
from alumni_system.storage.b2_client import B2Client

client = B2Client(
    key_id="your_key_id",
    app_key="your_app_key",
    bucket_name="alumni-profiles"
)
```

#### Methods

##### `upload_pdf(pdf_bytes: bytes, roll_number: str) -> str`

Upload PDF to B2 storage.

**Parameters:**
- `pdf_bytes` (bytes): PDF file content
- `roll_number` (str): Alumni roll number

**Returns:**
- `str`: B2 file URL

**File naming:** `linkedin_profiles/{roll_number}_{timestamp}.pdf`

**Raises:**
- `B2Error`: If upload fails

---

##### `download_pdf(file_url: str) -> bytes`

Download PDF from B2.

**Parameters:**
- `file_url` (str): B2 file URL

**Returns:**
- `bytes`: PDF file content

---

##### `get_download_url(file_url: str) -> str`

Get public download URL for PDF.

---

## NLP Chatbot

Module: `alumni_system.chatbot.nlp_chatbot`

### NLPChatbot

Natural language query processor.

#### Constructor

```python
from alumni_system.chatbot.nlp_chatbot import NLPChatbot

chatbot = NLPChatbot(db_session)
```

#### Methods

##### `process_query(user_input: str) -> ChatbotResponse`

Process natural language query.

**Parameters:**
- `user_input` (str): User's natural language query

**Returns:**
- `ChatbotResponse`: Response with text and data

**ChatbotResponse fields:**
- `response` (str): Natural language response
- `alumni` (List[Dict]): Matching alumni records
- `count` (int): Number of results

**Example:**
```python
response = chatbot.process_query("Who works at Google?")
print(response.response)  # "Found 5 alumni working at Google"
print(response.count)     # 5
for alumni in response.alumni:
    print(alumni['name'], alumni['current_company'])
```

**Supported query patterns:**
- Company: "Who works at Google?", "Find alumni at Microsoft"
- Batch: "Show batch 2020", "Alumni from 2019"
- Title: "Find software engineers", "Who are data scientists?"
- Location: "Alumni in Bangalore", "Who lives in San Francisco?"
- Count: "How many alumni?", "Count of alumni at Amazon"
- Combined: "Software engineers at Google from batch 2020"

---

## Scraping Orchestrator

Module: `alumni_system.scraper.job`

### ScrapingJobOrchestrator

Orchestrates scraping jobs with queue processing.

#### Constructor

```python
from alumni_system.scraper.job import ScrapingJobOrchestrator

orchestrator = ScrapingJobOrchestrator(db, account_manager)
```

#### Methods

##### `async process_queue(max_profiles: int = None) -> Dict[str, int]`

Process scraping queue.

**Parameters:**
- `max_profiles` (int, optional): Maximum profiles to scrape

**Returns:**
```python
{
    'processed': 50,
    'successful': 45,
    'failed': 5
}
```

---

##### `async scrape_stale_profiles(threshold_days: int = 180) -> Dict[str, int]`

Scrape profiles not updated within threshold days.

**Parameters:**
- `threshold_days` (int): Days threshold

---

##### `async scrape_batch(batch: str, force_update: bool = False) -> Dict[str, int]`

Scrape all profiles from specific batch.

**Parameters:**
- `batch` (str): Batch to scrape
- `force_update` (bool): Ignore last_scraped_at timestamps

---

## Data Models

### Alumni

```python
class Alumni:
    id: int
    roll_number: str  # Unique
    name: str
    batch: str
    gender: str
    
    # Contact
    mobile_number: str
    whatsapp_number: str
    personal_email: str
    college_email: str
    corporate_email: str
    
    # LinkedIn
    linkedin_id: str
    linkedin_url: str
    linkedin_pdf_url: str
    
    # Current position
    current_company: str
    current_designation: str
    location: str
    
    # Additional
    por: str
    internship: str
    higher_studies: str
    remarks: str
    address: str
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_scraped_at: datetime
    
    # Relationships
    job_history: List[JobHistory]
    education_history: List[EducationHistory]
```

### JobHistory

```python
class JobHistory:
    id: int
    alumni_id: int
    
    company_name: str
    designation: str
    location: str
    start_date: datetime
    end_date: datetime
    is_current: bool
    employment_type: str
    description: str
    
    created_at: datetime
    updated_at: datetime
```

### EducationHistory

```python
class EducationHistory:
    id: int
    alumni_id: int
    
    institution_name: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: int
    grade: str
    activities: str
    
    created_at: datetime
    updated_at: datetime
```

### ScrapingQueue

```python
class ScrapingQueue:
    id: int
    alumni_id: int
    priority: int
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    attempts: int
    last_attempt_at: datetime
    created_at: datetime
```

### AccountUsage

```python
class AccountUsage:
    id: int
    account_email: str
    date: date
    profiles_scraped: int
    is_flagged: bool
    created_at: datetime
    updated_at: datetime
```

### ScrapingLog

```python
class ScrapingLog:
    id: int
    alumni_id: int
    linkedin_url: str
    account_email: str
    status: str  # 'success', 'failed', 'skipped'
    error_message: str
    pdf_stored: bool
    duration_seconds: int
    created_at: datetime
```

---

## Error Handling

All functions may raise:
- `DatabaseError`: Database operation failures
- `ValidationError`: Invalid input data
- `ConfigurationError`: Missing or invalid configuration
- `ScrapingError`: LinkedIn scraping failures
- `B2Error`: B2 storage failures

Always wrap calls in try-except blocks:

```python
try:
    alumni = create_alumni(db, roll_number="2020001", name="John Doe")
except ValidationError as e:
    print(f"Invalid data: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")
```

---

## Configuration

All modules read configuration from environment variables. See `.env.example` for complete list.

Key configuration modules:
- `alumni_system.database.config`: Database settings
- `alumni_system.scraper.config`: Scraper settings
- `alumni_system.storage.config`: B2 storage settings
- `alumni_system.chatbot.config`: Chatbot settings

---

## Best Practices

1. **Always use context managers** for database sessions and scrapers
2. **Handle errors gracefully** - don't let one failure stop batch operations
3. **Use type hints** for better IDE support and error detection
4. **Log important operations** for debugging and auditing
5. **Test with small batches** before large-scale operations
6. **Monitor account usage** to avoid rate limits
7. **Validate input data** before database operations
8. **Use transactions** for multi-step database operations

---

For more examples and usage patterns, see the test files in `tests/` directory.
