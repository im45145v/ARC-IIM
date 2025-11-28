# Alumni Management System - Complete Setup Guide

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

### 2. Set Up LinkedIn Authentication

**🔐 Cookie-Based (Recommended)**

```bash
# Export cookies from your LinkedIn account
python scripts/export_linkedin_cookies.py

# This creates: cookies/linkedin_cookies_1.json
```

Add to `.env`:
```bash
LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json
```

**Why cookies?**
- ✅ More secure (no passwords in files)
- ✅ Supports 2FA
- ✅ Longer sessions (weeks vs. hours)
- ✅ Less likely to trigger LinkedIn security

### 3. Configure Database & Storage

```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Minimum required in `.env`:**
```bash
# Database (local testing)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=alumni_db
DB_USER=postgres
DB_PASSWORD=alumni_dev_password

# LinkedIn (cookie-based)
LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json

# B2 Storage
B2_APPLICATION_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_app_key
B2_BUCKET_NAME=your_bucket
```

### 4. Start Database

```bash
# Start PostgreSQL in Docker
docker-compose up -d

# Initialize tables
python -c "from alumni_system.database.init_db import init_database; init_database()"
```

### 5. Run the Application

```bash
streamlit run alumni_system/frontend/app.py
```

Open browser to `http://localhost:8501` 🎉

---

## 📚 Authentication Methods Comparison

| Feature | Cookie-Based | Credential-Based |
|---------|-------------|------------------|
| **Security** | ✅ High | ❌ Low |
| **2FA Support** | ✅ Yes | ❌ No |
| **Setup** | Medium | Easy |
| **Session Duration** | Weeks/Months | Hours/Days |
| **Recommended** | ✅ Yes | ❌ No |

---

## 🔐 Cookie Authentication (Detailed)

### Export Cookies

```bash
python scripts/export_linkedin_cookies.py
```

**What happens:**
1. Browser opens
2. You log in to LinkedIn (with 2FA if enabled)
3. Script exports cookies to `cookies/linkedin_cookies_1.json`
4. Done!

### Multiple Accounts

```bash
# Export 3 accounts
python scripts/export_linkedin_cookies.py
# Enter "3" when prompted

# Add to .env
LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json
LINKEDIN_COOKIES_FILE_2=cookies/linkedin_cookies_2.json
LINKEDIN_COOKIES_FILE_3=cookies/linkedin_cookies_3.json
```

### When to Re-Export

Re-export cookies every **2-4 weeks** or when you see:
- "Authentication failed" errors
- "Please log in" messages
- Scraper can't access profiles

---

## 🔑 Credential Authentication (Legacy)

**⚠️ Not recommended - use cookies instead!**

If you must use credentials:

```bash
# Add to .env
LINKEDIN_EMAIL_1=scraper1@example.com
LINKEDIN_PASSWORD_1=password123

# Optional: Add more accounts
LINKEDIN_EMAIL_2=scraper2@example.com
LINKEDIN_PASSWORD_2=password456
```

**Requirements:**
- ❌ Must disable 2FA
- ❌ Passwords in plain text
- ❌ More likely to trigger security checks

---

## 📊 Using the System

### Option 1: Bulk Import + Auto-Scrape

1. **Prepare Excel/CSV** with columns:
   - `Roll No.` (required)
   - `LinkedIn ID` (required)
   - `Name`, `Batch`, etc. (optional)

2. **Import:**
   - Go to **Admin Panel** → **Bulk Import**
   - Upload file
   - Click "Import and Queue for Scraping"

3. **Scrape:**
   - Go to **Admin Panel** → **Scraping Control**
   - Click "Start Scraping"
   - Watch real-time progress

### Option 2: Manual Entry

- Go to **Admin Panel** → **Add Alumni**
- Fill form and submit

### Option 3: Command Line

```bash
# Scrape specific batch
python -m alumni_system.scraper.run --batch 2020 --max-profiles 50

# Force update all
python -m alumni_system.scraper.run --force-update
```

---

## 🎯 Key Features

### Dashboard
- Total alumni, batches, companies, locations
- Quick overview of your data

### Browse & Search
- Paginated table with all records
- Filter by batch, company, location
- Search by name or company
- Export to Excel

### Alumni Details
- Complete career history
- All previous companies and roles
- Education history
- Download LinkedIn PDF

### Chatbot
Natural language queries:
- "Who works at Google?"
- "Find alumni from batch 2020"
- "Show all software engineers"

### Admin Panel
- Add/Edit/Delete alumni
- Bulk import from Excel/CSV
- Scraping control with real-time progress
- Monitor account usage

---

## 🔧 Configuration

### Rate Limiting

```bash
# .env
SCRAPER_DAILY_LIMIT_PER_ACCOUNT=80  # Max profiles per account per day
SCRAPER_MIN_DELAY=3                  # Min seconds between requests
SCRAPER_MAX_DELAY=8                  # Max seconds between requests
```

### Human Behavior Simulation

```bash
SCRAPER_SLOW_MO=100  # Milliseconds between browser actions
```

### Browser Settings

```bash
SCRAPER_HEADLESS=true   # Run without visible window
```

---

## 🐛 Troubleshooting

### "Could not connect to database"

```bash
# Start database
docker-compose up -d

# Check status
docker-compose ps
```

### "Cookie authentication failed"

```bash
# Re-export cookies
python scripts/export_linkedin_cookies.py
```

### "Login failed"

```bash
# Check credentials in .env
# Or switch to cookie-based auth
```

### "All accounts exhausted"

- Wait until midnight UTC for reset
- Or add more accounts

### "Playwright not found"

```bash
playwright install chromium
```

---

## 📖 Documentation

- **[Cookie Authentication Guide](docs/QUICK_START_COOKIES.md)** - Quick start with cookies
- **[Full Cookie Documentation](docs/COOKIE_AUTHENTICATION.md)** - Complete guide
- **[README.md](README.md)** - Full system documentation
- **[API Reference](API_REFERENCE.md)** - Function interfaces

---

## ⚠️ Important Notes

### Security
- ✅ Use dedicated LinkedIn accounts (not personal)
- ✅ Keep cookies secure (add to .gitignore)
- ✅ Never commit `.env` or cookies to git
- ✅ Rotate credentials/cookies regularly

### LinkedIn Terms of Service
- ⚠️ Web scraping may violate LinkedIn's ToS
- ⚠️ Use responsibly and at your own risk
- ⚠️ Respect rate limits to avoid account suspension
- ⚠️ Consider LinkedIn's official APIs for production use

### Rate Limiting
- ✅ Recommended: 50-80 profiles per account per day
- ✅ Use 3-8 second delays between requests
- ✅ Use multiple accounts for larger batches
- ✅ Monitor account usage in Scraping Control tab

---

## 🎉 You're Ready!

Your Alumni Management System is now set up with secure cookie-based authentication!

**Next steps:**
1. Import your alumni data (Excel/CSV)
2. Start scraping profiles
3. Browse and search your data
4. Use the chatbot for queries

**Need help?**
- Check the troubleshooting section above
- Read the full documentation
- Review the example files

Happy scraping! 🚀
