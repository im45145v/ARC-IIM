# 🏗️ System Overview

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Alumni Management System                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   Streamlit UI   │◄────►│   Database       │◄────►│  LinkedIn        │
│   (Frontend)     │      │   (PostgreSQL)   │      │  Scraper         │
└──────────────────┘      └──────────────────┘      └──────────────────┘
        │                          │                          │
        │                          │                          │
        ▼                          ▼                          ▼
   Dashboard              Alumni Records              Profile Data
   Browse Alumni          Job History                 Company Info
   Search                 Education                   Location
   Chatbot                Scraping Logs               Experience
   Admin Panel            Queue Management
```

---

## Components

### 1. Frontend (Streamlit)
**Location:** `alumni_system/frontend/app.py`

**Pages:**
- 🏠 Dashboard - Overview and metrics
- 👥 Browse Alumni - View all records
- 🔍 Search - Find specific alumni
- 💬 Chatbot - AI-powered queries
- ⚙️ Admin - Add/Edit/Delete records

**Fixed Issues:**
- ✅ Navigation now uses session state
- ✅ Proper SQLAlchemy session handling

### 2. Database Layer
**Location:** `alumni_system/database/`

**Files:**
- `connection.py` - Database connections
- `models.py` - Data models (Alumni, JobHistory, etc.)
- `crud.py` - Create, Read, Update, Delete operations
- `config.py` - Database configuration

**Features:**
- PostgreSQL database
- SQLAlchemy ORM
- Connection pooling
- Transaction management

### 3. LinkedIn Scraper
**Location:** `alumni_system/scraper/`

**Features:**
- Playwright-based scraping
- Cookie authentication
- Rate limiting
- Human-like behavior
- Queue management

### 4. Automation Scripts
**Location:** `scripts/`

**New Scripts:**
- `add_alumni_batch.py` - Add alumni to database
- `scrape_new_alumni.py` - Scrape LinkedIn profiles
- `add_and_scrape_alumni.sh` - Combined automation

---

## Data Flow

### Adding Alumni Manually

```
User Input (UI)
    ↓
Streamlit Form
    ↓
create_alumni() function
    ↓
Database (PostgreSQL)
    ↓
Success Message
```

### Adding Alumni via Script

```
Python Script
    ↓
Alumni Data (dict)
    ↓
create_alumni() function
    ↓
Database (PostgreSQL)
    ↓
Console Output
```

### LinkedIn Scraping

```
Alumni Record (with LinkedIn URL)
    ↓
Scraping Queue
    ↓
LinkedIn Scraper (Playwright)
    ↓
Profile Data
    ↓
update_alumni() function
    ↓
Database (PostgreSQL)
    ↓
Scraping Log
```

---

## Database Schema

### Alumni Table
```
┌─────────────────────────────────────────┐
│ Alumni                                  │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ name                                    │
│ roll_number (UNIQUE)                    │
│ batch                                   │
│ email                                   │
│ phone                                   │
│ linkedin_url                            │
│ current_company                         │
│ current_designation                     │
│ location                                │
│ created_at                              │
│ updated_at                              │
└─────────────────────────────────────────┘
```

### Related Tables
- **JobHistory** - Previous employment records
- **EducationHistory** - Educational background
- **ScrapingLog** - Scraping activity logs
- **ScrapingQueue** - Pending scraping tasks

---

## File Structure

```
alumni-management-system/
├── alumni_system/
│   ├── frontend/
│   │   └── app.py              ← Main Streamlit app (FIXED)
│   ├── database/
│   │   ├── connection.py       ← DB connections
│   │   ├── models.py           ← Data models
│   │   ├── crud.py             ← CRUD operations
│   │   └── config.py           ← Configuration
│   ├── scraper/
│   │   └── linkedin_scraper.py ← LinkedIn scraping
│   └── chatbot/
│       └── nlp_chatbot.py      ← AI chatbot
├── scripts/
│   ├── add_alumni_batch.py     ← NEW: Add alumni
│   ├── scrape_new_alumni.py    ← NEW: Scrape profiles
│   └── add_and_scrape_alumni.sh ← NEW: Combined
├── docs/                        ← Documentation
├── tests/                       ← Test files
├── .env                         ← Environment config
├── docker-compose.yml           ← Database setup
├── requirements.txt             ← Python dependencies
└── START_HERE.md               ← Quick start guide
```

---

## Environment Variables

Required in `.env` file:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=alumni_db
DB_USER=alumni_user
DB_PASSWORD=your_password

# LinkedIn (optional, for scraping)
LINKEDIN_EMAIL=your_email
LINKEDIN_PASSWORD=your_password

# Backblaze B2 (optional, for backups)
B2_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_app_key
B2_BUCKET_NAME=your_bucket
```

---

## Key Features

### ✅ Working Features
- Dashboard with metrics
- Browse all alumni
- Search by name/company
- Filter by batch/location
- Add alumni manually
- Add alumni via script
- Export to Excel
- AI chatbot queries
- LinkedIn scraping (with cookies)

### 🔧 Fixed Issues
- Navigation between pages
- SQLAlchemy session handling
- Streamlit compatibility

### 🆕 New Features
- Automated alumni addition
- Batch import scripts
- LinkedIn auto-scraping
- Comprehensive documentation

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Backend | Python 3.x |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Scraping | Playwright |
| Data Processing | Pandas |
| Testing | Pytest, Hypothesis |
| Containerization | Docker |

---

## Next Steps

1. **Start using the system**
   ```bash
   docker-compose up -d
   python3 scripts/add_alumni_batch.py
   streamlit run alumni_system/frontend/app.py
   ```

2. **Add more alumni**
   - Edit `scripts/add_alumni_batch.py`
   - Or use the Admin panel in the UI

3. **Enable LinkedIn scraping**
   - Configure cookies (see `docs/COOKIE_AUTHENTICATION.md`)
   - Run `python3 scripts/scrape_new_alumni.py`

4. **Customize the system**
   - Modify UI in `alumni_system/frontend/app.py`
   - Add new features as needed

---

## Support

- **Quick Reference:** `QUICK_REFERENCE.md`
- **Complete Guide:** `FIXES_APPLIED.md`
- **Script Documentation:** `scripts/README_ADD_ALUMNI.md`
- **Main README:** `README.md`
