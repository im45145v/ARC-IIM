# 🍪 LinkedIn Cookies Setup Guide

## Problem
The scraper is opening a browser but not signing in properly. We need to use cookies from your browser instead.

---

## Solution: Export Cookies from Your Browser

### Step 1: Install Cookie Export Extension

**For Chrome/Edge:**
1. Go to Chrome Web Store
2. Search for "Cookie Editor" or "EditThisCookie"
3. Install the extension
4. Pin it to your toolbar

**For Firefox:**
1. Go to Firefox Add-ons
2. Search for "Cookie Editor"
3. Install the extension
4. Pin it to your toolbar

### Step 2: Log Into LinkedIn

1. Open https://www.linkedin.com
2. Log in with your account
3. Make sure you're fully logged in (can see your profile)

### Step 3: Export Cookies

**Using Cookie Editor (Chrome/Edge):**
1. Click the Cookie Editor extension icon
2. Click **Export** (or the export button)
3. Select **JSON** format
4. Save the file as `cookies/linkedin_cookies_1.json`

**Using EditThisCookie (Chrome/Edge):**
1. Click the EditThisCookie extension icon
2. Click **Export** (or the export button)
3. Save the file as `cookies/linkedin_cookies_1.json`

**Using Cookie Editor (Firefox):**
1. Click the Cookie Editor extension icon
2. Click **Export**
3. Select **JSON** format
4. Save the file as `cookies/linkedin_cookies_1.json`

### Step 4: Fix Cookies Format

LinkedIn cookies need the `sameSite` attribute fixed:

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

### Step 5: Test Cookies

```bash
python3 scripts/test_cookies_only.py
```

Should show:
```
✅ Scraper initialized
✅ Login successful!
✅ Profile scraped successfully!
✅ Cookies are working perfectly!
```

---

## Troubleshooting

### "Cookies file not found"
- Make sure you saved the file to: `cookies/linkedin_cookies_1.json`
- Check the file exists: `ls -la cookies/linkedin_cookies_1.json`

### "Login failed"
**Possible causes:**
1. Cookies are expired
2. Cookies are from a different browser
3. LinkedIn session expired

**Solution:**
1. Log out of LinkedIn in your browser
2. Log back in
3. Export fresh cookies
4. Fix them
5. Try again

### "Profile data not extracted"
- Cookies are working but selectors might be outdated
- LinkedIn changes their HTML frequently
- Try a different profile URL

### "Browser opens but nothing happens"
- Check if you're logged into LinkedIn in your browser
- Make sure cookies are valid
- Try exporting fresh cookies

---

## Important Notes

1. **Cookies expire** - Export fresh cookies every few days
2. **Browser-specific** - Cookies from Chrome won't work in Firefox
3. **Account-specific** - Cookies are tied to your LinkedIn account
4. **Keep them safe** - Don't share your cookies file
5. **Use dedicated account** - Don't use your personal LinkedIn account

---

## Quick Commands

```bash
# Test cookies
python3 scripts/test_cookies_only.py

# Run scraper with cookies
python3 scripts/comprehensive_scraper.py

# View in app
bash start_app.sh
```

---

## If Cookies Still Don't Work

**Option 1: Use Credential-Based Login**
- Add to `.env`:
  ```
  LINKEDIN_EMAIL_1=your_email@gmail.com
  LINKEDIN_PASSWORD_1=your_password
  ```
- Remove or comment out `LINKEDIN_COOKIES_FILE_1`
- Run scraper

**Option 2: Use Different Browser**
- Try exporting cookies from a different browser
- Some browsers handle cookies differently

**Option 3: Manual LinkedIn Profile Download**
- Download profiles manually as PDFs
- Upload to B2 manually
- Update database manually

---

## Success Indicators

✅ **Cookies are working:**
- Browser opens and shows LinkedIn
- You're logged in (can see profile)
- Profile data is extracted
- PDFs download successfully
- Data appears in database

❌ **Cookies are not working:**
- Browser opens but shows login page
- "Login failed" error
- No profile data extracted

---

## Next Steps

1. Export cookies from your browser
2. Fix the format
3. Test with: `python3 scripts/test_cookies_only.py`
4. Run scraper: `python3 scripts/comprehensive_scraper.py`
5. View results: `bash start_app.sh`
