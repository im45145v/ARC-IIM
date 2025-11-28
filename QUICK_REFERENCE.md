# 🚀 Quick Reference Card

## One-Line Commands

```bash
# Test everything works
python3 test_fixes.py

# Add the two alumni
python3 scripts/add_alumni_batch.py

# Start the app
streamlit run alumni_system/frontend/app.py

# Add alumni + scrape LinkedIn
bash scripts/add_and_scrape_alumni.sh
```

---

## Common Tasks

### Start Database
```bash
docker-compose up -d
```

### Stop Database
```bash
docker-compose down
```

### Check Database Status
```bash
docker-compose ps
```

### View Database Logs
```bash
docker-compose logs -f postgres
```

### Add Alumni Manually (via App)
1. Start app: `streamlit run alumni_system/frontend/app.py`
2. Go to "⚙️ Admin" page
3. Fill in the form
4. Click "➕ Add Alumni"

### Add Alumni via Script
```bash
python3 scripts/add_alumni_batch.py
```

### Scrape LinkedIn Profiles
```bash
python3 scripts/scrape_new_alumni.py
```

### Export Alumni Data
1. Go to "👥 Browse Alumni" page
2. Click "📥 Export to Excel"
3. Click "⬇️ Download Excel File"

---

## Troubleshooting

### "Database connection failed"
```bash
# Check if database is running
docker-compose ps

# Start database
docker-compose up -d

# Check .env file has correct credentials
cat .env
```

### "Module not found"
```bash
# Install dependencies
pip install -r requirements.txt
```

### "LinkedIn scraping failed"
```bash
# Check cookies file exists
ls -la cookies/linkedin_cookies_1.json

# See cookie setup guide
cat docs/COOKIE_AUTHENTICATION.md
```

### "Alumni already exists"
- This is normal - the script prevents duplicates
- Alumni won't be added twice

---

## File Locations

| What | Where |
|------|-------|
| Main App | `alumni_system/frontend/app.py` |
| Add Alumni Script | `scripts/add_alumni_batch.py` |
| Scrape Script | `scripts/scrape_new_alumni.py` |
| Database Config | `.env` |
| LinkedIn Cookies | `cookies/linkedin_cookies_1.json` |
| Documentation | `docs/` |

---

## Quick Checks

### Is database running?
```bash
docker-compose ps
# Should show postgres as "Up"
```

### How many alumni in database?
```bash
python3 -c "
from alumni_system.database.connection import get_db_context
from alumni_system.database.crud import get_alumni_count
with get_db_context() as db:
    print(f'Alumni count: {get_alumni_count(db)}')
"
```

### Test app without starting it
```bash
python3 test_fixes.py
```

---

## The Two Alumni Being Added

1. **Akshat Naugir** (M218-23) - Orix Corporation, Mumbai
2. **Narendran T** (BA041-23) - Havells India, Noida

---

## Need Help?

- **Full Guide:** `FIXES_APPLIED.md`
- **Script Docs:** `scripts/README_ADD_ALUMNI.md`
- **Quick Summary:** `QUICK_FIX_SUMMARY.md`
- **Main README:** `README.md`
