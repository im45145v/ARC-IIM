# 🔐 Manual LinkedIn Login Guide

## The Plan

1. ✅ Open Playwright browser
2. ✅ You login manually to LinkedIn
3. ✅ Script saves cookies automatically
4. ✅ Test with your profile
5. ✅ Run full scraper

---

## Step 1: Open Browser & Login

```bash
python3 scripts/manual_login_and_save.py
```

This will:
1. Open a browser window
2. Navigate to LinkedIn login
3. Wait for you to login
4. Save cookies automatically
5. Test with your profile

### What to do:
1. Enter your LinkedIn email
2. Enter your password
3. Complete 2FA if needed
4. Wait for feed to load
5. Press Enter in terminal

---

## Step 2: Cookies Saved

The script will save:
- `cookies/linkedin_cookies_1.json` - Original cookies
- `cookies/linkedin_cookies_1_fixed.json` - Fixed version

Both are ready to use!

---

## Step 3: Test with Your Profile

```bash
python3 scripts/test_with_your_profile.py
```

This will:
1. Load your saved cookies
2. Login to LinkedIn
3. Scrape your profile: `https://www.linkedin.com/in/im45145v`
4. Extract all data
5. Download PDF
6. Show results

Should show:
```
✅ Logged in
✅ Profile scraped successfully!
✅ PDF downloaded!
✅ ALL TESTS PASSED!
```

---

## Step 4: Run Full Scraper

Once tests pass:

```bash
python3 scripts/comprehensive_scraper.py
```

This will scrape all alumni profiles and upload PDFs to B2.

---

## Step 5: View Results

```bash
bash start_app.sh
```

Then:
- Browse Alumni → View Detailed Profiles
- Expand any alumni
- Click LinkedIn PDF link

---

## Quick Commands

```bash
# 1. Manual login and save cookies
python3 scripts/manual_login_and_save.py

# 2. Test with your profile
python3 scripts/test_with_your_profile.py

# 3. Run full scraper
python3 scripts/comprehensive_scraper.py

# 4. View in app
bash start_app.sh
```

---

## What Gets Saved

### Cookies
- All LinkedIn session cookies
- Authentication tokens
- User preferences
- Saved in JSON format

### Profile Data
- Name, headline, location
- Current company and role
- Job history (all positions)
- Education history
- Contact information

### PDFs
- Official LinkedIn PDFs
- Uploaded to Backblaze B2
- Download links stored in database

---

## Troubleshooting

### "Browser won't open"
- Make sure Playwright is installed: `pip install playwright`
- Make sure you have display (not headless)

### "Login page still showing"
- Make sure you completed 2FA
- Wait for feed to fully load
- Then press Enter

### "Cookies not saved"
- Check if `cookies/` directory exists
- Check file permissions
- Try running with `sudo` if needed

### "Profile scraping failed"
- Make sure you're logged in
- Check if profile URL is correct
- Try a different profile

### "PDF download failed"
- Make sure "More" button is visible
- Make sure "Save to PDF" option exists
- Try clicking manually first

---

## Success Indicators

✅ **Everything working:**
- Browser opens and shows LinkedIn
- You can login manually
- Cookies are saved
- Profile data is extracted
- PDF is downloaded
- All tests pass

❌ **Something wrong:**
- Browser won't open
- Can't login
- Cookies not saved
- Profile not scraped
- PDF not downloaded

---

## Next Steps

1. Run: `python3 scripts/manual_login_and_save.py`
2. Login manually
3. Run: `python3 scripts/test_with_your_profile.py`
4. If tests pass, run: `python3 scripts/comprehensive_scraper.py`
5. View results: `bash start_app.sh`

---

## Files Created

- `scripts/manual_login_and_save.py` - Manual login & cookie saver
- `scripts/test_with_your_profile.py` - Test with your profile
- `MANUAL_LOGIN_GUIDE.md` - This guide

---

## That's It!

Your cookies will be saved and the scraper will work for all profiles!
