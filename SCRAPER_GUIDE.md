# 🔍 Comprehensive LinkedIn Scraper Guide

## What It Does

The comprehensive scraper will:

1. ✅ **Scrape LinkedIn profiles** - Extract all data from LinkedIn
2. ✅ **Save PDFs to Backblaze B2** - Store profile PDFs in cloud storage
3. ✅ **Update database** - Save all scraped data including:
   - Basic info (name, headline, location)
   - Current position (company, designation)
   - **Job history** (all previous positions)
   - **Education history** (all degrees and institutions)
   - Contact information (email if available)
4. ✅ **Display in UI** - All data visible in the Streamlit app

---

## Prerequisites

### 1. LinkedIn Cookies (Required)
You need valid LinkedIn cookies for authentication.

**Check if you have them:**
```bash
ls -la cookies/linkedin_cookies_1_fixed.json
```

**If not, create them:**
See `docs/COOKIE_AUTHENTICATION.md` for instructions.

### 2. Backblaze B2 (Optional but Recommended)
Configure B2 credentials in `.env` file:

```bash
B2_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_application_key
B2_BUCKET_NAME=your_bucket_name
```

**Note:** Scraper will work without B2, but PDFs won't be saved to cloud.

### 3. Database Running
```bash
docker-compose up -d
```

---

## How to Run

### Quick Start
```bash
python3 scripts/comprehensive_scraper.py
```

This will scrape both alumni:
- Akshat Naugir (M218-23)
- Narendran T (BA041-23)

### What Happens

```
1. Initialize B2 Storage ✅
2. Initialize LinkedIn Scraper ✅
3. Verify Authentication ✅
4. For each alumni:
   a. Scrape profile data 📥
   b. Download profile as PDF 📄
   c. Upload PDF to B2 ☁️
   d. Update alumni basic info 💾
   e. Add job history 💼
   f. Add education history 🎓
5. Complete! ✨
```

---

## What Gets Scraped

### Basic Information
- Full name
- Headline/current position
- Location
- Email (if visible)

### Current Position
- Company name
- Job title/designation
- Location

### Job History
For each previous position:
- Company name
- Job title
- Location
- Duration (start date - end date)
- Whether it's current position

### Education History
For each degree:
- Institution name
- Degree type
- Field of study
- Years attended (start - end)

### PDF Storage
- Full LinkedIn profile saved as PDF
- Stored in Backblaze B2
- Accessible via download URL
- Naming: `linkedin_profiles/{roll_number}_{timestamp}.pdf`

---

## View Scraped Data

### In Streamlit App

1. **Start the app:**
   ```bash
   streamlit run alumni_system/frontend/app.py
   ```

2. **Browse Alumni Page:**
   - See basic info in table
   - Click "👁️ View Detailed Profiles"
   - Expand any alumni to see:
     - Contact information
     - Current position
     - Full job history
     - Education history
     - LinkedIn PDF link

3. **Search Page:**
   - Search by name or company
   - Expand results to see full details
   - Job history and education included

4. **Dashboard:**
   - See total alumni count
   - Quick stats

---

## Troubleshooting

### "Authentication failed"
**Problem:** LinkedIn cookies are invalid or expired

**Solution:**
1. Export fresh cookies from your browser
2. Fix the cookies file:
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
   print('✅ Fixed!')
   "
   ```

### "B2 Storage not configured"
**Problem:** Backblaze B2 credentials not set

**Solution:**
1. Add to `.env` file:
   ```
   B2_KEY_ID=your_key_id
   B2_APPLICATION_KEY=your_app_key
   B2_BUCKET_NAME=your_bucket
   ```
2. Or skip B2 - scraper will still work, just won't save PDFs

### "Failed to scrape profile"
**Possible causes:**
- LinkedIn changed their HTML structure
- Rate limiting (wait and try again)
- Profile is private
- Network issues

**Solution:**
- Wait 10-15 minutes and try again
- Check if you can access the profile manually
- Verify cookies are still valid

### "No data extracted"
**Problem:** Selectors might be outdated

**Solution:**
- LinkedIn frequently changes their HTML
- May need to update selectors in `alumni_system/scraper/config.py`
- Check `linkedin_page_debug.html` for current structure

---

## Advanced Usage

### Scrape Specific Alumni

Edit `scripts/comprehensive_scraper.py`:

```python
# Change this line:
roll_numbers = ["M218-23", "BA041-23"]

# To your desired roll numbers:
roll_numbers = ["YOUR-ROLL-1", "YOUR-ROLL-2", "YOUR-ROLL-3"]
```

### Scrape All Alumni

Create a new script:

```python
from alumni_system.database.connection import get_db_context
from alumni_system.database.crud import get_all_alumni

with get_db_context() as db:
    all_alumni = get_all_alumni(db, limit=1000)
    roll_numbers = [a.roll_number for a in all_alumni if a.linkedin_url]

# Then use roll_numbers in scraper
```

### Batch Processing

For large numbers of alumni:
1. Split into batches of 10-20
2. Add delays between batches
3. Monitor for rate limiting

---

## Data in Database

### Alumni Table
Updated fields:
- `name`
- `por` (headline)
- `location`
- `current_company`
- `current_designation`
- `corporate_email`
- `linkedin_pdf_url`
- `last_scraped_at`

### Job History Table
New records created:
- `company_name`
- `designation`
- `location`
- `start_date`
- `end_date`
- `is_current`
- `description`

### Education History Table
New records created:
- `institution_name`
- `degree`
- `field_of_study`
- `start_year`
- `end_year`

---

## Best Practices

1. **Rate Limiting**
   - Don't scrape too many profiles at once
   - Add delays between requests (built-in)
   - Respect LinkedIn's terms of service

2. **Cookie Management**
   - Keep cookies fresh
   - Export new cookies every few weeks
   - Use dedicated LinkedIn account

3. **Data Privacy**
   - Only scrape publicly available data
   - Comply with GDPR/privacy regulations
   - Store data securely

4. **Monitoring**
   - Check scraper output for errors
   - Verify data in database
   - Review PDFs in B2 storage

---

## Success Indicators

✅ **Scraping Successful:**
- "✅ Profile data scraped successfully"
- "✅ PDF saved to B2"
- "✅ Updated basic info"
- "✅ Job history added"
- "✅ Education history added"

❌ **Scraping Failed:**
- "❌ Authentication failed"
- "❌ Failed to scrape profile"
- "⚠️ PDF upload failed"

---

## Next Steps

After scraping:

1. **Verify in App**
   ```bash
   streamlit run alumni_system/frontend/app.py
   ```

2. **Check Database**
   ```bash
   python3 -c "
   from alumni_system.database.connection import get_db_context
   from alumni_system.database.crud import get_alumni_by_roll_number, get_job_history_by_alumni
   
   with get_db_context() as db:
       alumni = get_alumni_by_roll_number(db, 'M218-23')
       print(f'Name: {alumni.name}')
       print(f'Company: {alumni.current_company}')
       
       jobs = get_job_history_by_alumni(db, alumni.id)
       print(f'Job history: {len(jobs)} positions')
   "
   ```

3. **View PDFs in B2**
   - Log into Backblaze B2 console
   - Navigate to your bucket
   - Check `linkedin_profiles/` folder

---

## Support

- **Cookie Setup:** `docs/COOKIE_AUTHENTICATION.md`
- **B2 Setup:** `docs/` (if available)
- **Main README:** `README.md`
- **Quick Reference:** `QUICK_REFERENCE.md`
