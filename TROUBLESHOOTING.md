# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. "No module named 'alumni_system'"

**Error in Streamlit:**
```
Import error: No module named 'alumni_system'
```

**Solution:**

Use the startup script:
```bash
bash start_app.sh
```

Or set PYTHONPATH manually:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
streamlit run alumni_system/frontend/app.py
```

**Why this happens:**
Streamlit changes the working directory, so Python can't find the `alumni_system` module.

---

### 2. Database Connection Failed

**Error:**
```
Database connection failed: could not connect to server
```

**Solutions:**

**Check if database is running:**
```bash
docker-compose ps
```

**Start database:**
```bash
docker-compose up -d
```

**Check database logs:**
```bash
docker-compose logs postgres
```

**Verify .env file:**
```bash
cat .env | grep DB_
```

Should show:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=alumni_db
DB_USER=postgres
DB_PASSWORD=your_password
```

---

### 3. LinkedIn Authentication Failed

**Error:**
```
Cookie authentication failed - not logged in
```

**Solutions:**

**Fix cookies file:**
```bash
python3 -c "
import json
with open('cookies/linkedin_cookies_1.json', 'r') as f:
    cookies = json.load(f)
for cookie in cookies:
    if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
        cookie['sameSite'] = 'Lax'
with open('cookies/linkedin_cookies_1_fixed.json', 'w') as f:
    json.dump(cookies, f, indent=2)
print('✅ Cookies fixed!')
"
```

**Export fresh cookies:**
1. Log into LinkedIn in your browser
2. Use a cookie export extension
3. Save to `cookies/linkedin_cookies_1.json`
4. Run the fix command above

---

### 4. B2 Storage Not Configured

**Warning:**
```
⚠️  B2 Storage not configured
```

**This is optional!** The scraper will work without B2, but PDFs won't be saved to cloud.

**To configure B2:**

Add to `.env` file:
```bash
B2_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_application_key
B2_BUCKET_NAME=your_bucket_name
```

---

### 5. Scraper Not Extracting Data

**Issue:** Scraper runs but no data is extracted

**Possible causes:**
- LinkedIn changed their HTML structure
- Profile is private
- Rate limiting

**Solutions:**

**Wait and retry:**
```bash
# Wait 15 minutes, then try again
sleep 900
python3 scripts/comprehensive_scraper.py
```

**Check if profile is accessible:**
- Open the LinkedIn URL in your browser
- Make sure you're logged in
- Verify the profile is public

**Debug the scraper:**
```bash
python3 debug_scraper.py
```

This will:
- Save page HTML to `linkedin_page_debug.html`
- Take a screenshot to `linkedin_page_debug.png`
- Help identify selector issues

---

### 6. Port Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use
```

**Solution:**

**Check what's using port 5432:**
```bash
sudo lsof -i :5432
```

**Stop the conflicting service:**
```bash
sudo systemctl stop postgresql
```

**Or change the port in docker-compose.yml:**
```yaml
ports:
  - "5433:5432"  # Use 5433 instead
```

Then update `.env`:
```bash
DB_PORT=5433
```

---

### 7. Permission Denied

**Error:**
```
Permission denied: './start_app.sh'
```

**Solution:**
```bash
chmod +x start_app.sh
bash start_app.sh
```

---

### 8. Module Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Or install specific package:**
```bash
pip install streamlit pandas sqlalchemy psycopg2-binary
```

---

### 9. Streamlit Won't Start

**Error:**
```
streamlit: command not found
```

**Solution:**

**Install Streamlit:**
```bash
pip install streamlit
```

**Or use Python module:**
```bash
python3 -m streamlit run alumni_system/frontend/app.py
```

---

### 10. Data Not Showing in UI

**Issue:** App loads but no alumni data appears

**Solutions:**

**Check database:**
```bash
python3 -c "
from alumni_system.database.connection import get_db_context
from alumni_system.database.crud import get_alumni_count

with get_db_context() as db:
    count = get_alumni_count(db)
    print(f'Alumni in database: {count}')
"
```

**Add test data:**
```bash
python3 scripts/add_alumni_batch.py
```

**Refresh the app:**
- Press 'R' in the Streamlit interface
- Or refresh your browser

---

### 11. Job History Not Showing

**Issue:** Alumni details show but no job history

**Possible causes:**
- Data not scraped yet
- Scraper didn't extract job history
- LinkedIn profile has no work experience

**Solutions:**

**Check if job history exists:**
```bash
python3 -c "
from alumni_system.database.connection import get_db_context
from alumni_system.database.crud import get_alumni_by_roll_number, get_job_history_by_alumni

with get_db_context() as db:
    alumni = get_alumni_by_roll_number(db, 'M218-23')
    jobs = get_job_history_by_alumni(db, alumni.id)
    print(f'Job history records: {len(jobs)}')
"
```

**Re-scrape the profile:**
```bash
python3 scripts/comprehensive_scraper.py
```

---

### 12. PDF Download Link Not Working

**Issue:** LinkedIn PDF link shows but doesn't work

**Possible causes:**
- B2 not configured
- PDF not uploaded
- URL expired

**Solutions:**

**Check if PDF URL exists:**
```bash
python3 -c "
from alumni_system.database.connection import get_db_context
from alumni_system.database.crud import get_alumni_by_roll_number

with get_db_context() as db:
    alumni = get_alumni_by_roll_number(db, 'M218-23')
    print(f'PDF URL: {alumni.linkedin_pdf_url}')
"
```

**Re-scrape with B2 configured:**
1. Add B2 credentials to `.env`
2. Run scraper again

---

## Quick Diagnostics

Run this to check everything:

```bash
python3 -c "
import sys
from pathlib import Path

print('🔍 System Diagnostics')
print('=' * 60)

# Check Python path
print(f'Python: {sys.executable}')
print(f'Version: {sys.version.split()[0]}')
print()

# Check if in correct directory
cwd = Path.cwd()
print(f'Current directory: {cwd}')
print(f'alumni_system exists: {(cwd / \"alumni_system\").exists()}')
print()

# Check database
try:
    sys.path.insert(0, str(cwd))
    from alumni_system.database.connection import get_db_context
    from alumni_system.database.crud import get_alumni_count
    
    with get_db_context() as db:
        count = get_alumni_count(db)
    print(f'✅ Database: Connected ({count} alumni)')
except Exception as e:
    print(f'❌ Database: {e}')

# Check cookies
cookies_file = cwd / 'cookies' / 'linkedin_cookies_1_fixed.json'
print(f'✅ Cookies: {\"Found\" if cookies_file.exists() else \"Not found\"}')

# Check .env
env_file = cwd / '.env'
print(f'✅ .env file: {\"Found\" if env_file.exists() else \"Not found\"}')

print('=' * 60)
"
```

---

## Still Having Issues?

1. **Check all documentation:**
   - `START_HERE.md` - Quick start
   - `QUICK_REFERENCE.md` - Commands
   - `SCRAPER_GUIDE.md` - Scraping details
   - `COMPLETE_SOLUTION.md` - Full overview

2. **Verify prerequisites:**
   - Python 3.x installed
   - Docker installed and running
   - Dependencies installed (`pip install -r requirements.txt`)

3. **Start fresh:**
   ```bash
   # Stop everything
   docker-compose down
   
   # Start database
   docker-compose up -d
   
   # Wait for it to be ready
   sleep 5
   
   # Start app
   bash start_app.sh
   ```

4. **Check logs:**
   ```bash
   # Database logs
   docker-compose logs postgres
   
   # Streamlit logs (in terminal where app is running)
   ```
