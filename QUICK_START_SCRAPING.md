# 🚀 Quick Start - LinkedIn Scraping

## 3 Simple Steps

### 1️⃣ Fix Cookies (One-Time Setup)
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
print('✅ Cookies ready!')
"
```

### 2️⃣ Run Scraper
```bash
python3 scripts/comprehensive_scraper.py
```

Wait for:
- ✅ Authentication successful
- ✅ Profile data scraped
- ✅ PDF saved to B2
- ✅ Database updated
- ✅ Job history added
- ✅ Education added

### 3️⃣ View Results
```bash
bash start_app.sh
```

Or manually:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
streamlit run alumni_system/frontend/app.py
```

Then:
1. Go to **Browse Alumni**
2. Click **"👁️ View Detailed Profiles"**
3. Expand any alumni to see everything!

---

## What You'll See

✅ **All Contact Info** - Mobile, emails, LinkedIn  
✅ **Current Role** - Company, designation, location  
✅ **Past Roles** - Complete work history  
✅ **Education** - All degrees and institutions  
✅ **LinkedIn PDF** - Download link  
✅ **Misc** - POR, internships, remarks  

---

## Optional: Configure B2 Storage

Add to `.env` file:
```bash
B2_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_app_key
B2_BUCKET_NAME=your_bucket
```

**Note:** Scraper works without B2, but PDFs won't be saved to cloud.

---

## That's It!

Your complete LinkedIn scraping solution is ready to use.

**For detailed guide:** See `SCRAPER_GUIDE.md`  
**For complete solution:** See `COMPLETE_SOLUTION.md`
