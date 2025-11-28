# 📄 LinkedIn PDF Download Guide

## What We're Doing

Instead of taking a screenshot of the profile, we're now:
1. ✅ Clicking the "More" button (three dots)
2. ✅ Clicking "Save to PDF"
3. ✅ Capturing the official LinkedIn PDF
4. ✅ Uploading to Backblaze B2

---

## How It Works

### The Process

```
1. Navigate to LinkedIn profile
   ↓
2. Click "More" button (...)
   ↓
3. Click "Save to PDF" option
   ↓
4. LinkedIn generates official PDF
   ↓
5. Capture PDF content
   ↓
6. Upload to B2 storage
   ↓
7. Store download link in database
```

### What You'll See

When the scraper runs:
```
🔍 Processing: Akshat Naugir (M218-23)
   📥 Scraping profile data...
   ✅ Profile data scraped successfully
   📄 Downloading profile as PDF...
   Clicking 'More' button...
   ✅ More menu opened
   Clicking 'Save to PDF'...
   ✅ Save to PDF clicked
   Generating PDF from page...
   ☁️  Uploading PDF to Backblaze B2...
   ✅ PDF saved to B2: linkedin_profiles/M218-23_20251128_101530.pdf
```

---

## Test PDF Download

To test if PDF download works:

```bash
python3 scripts/test_pdf_download.py
```

This will:
1. Open browser
2. Log in with cookies
3. Navigate to a profile
4. Click "More" → "Save to PDF"
5. Save PDF to `test_profile.pdf`
6. Show you the result

---

## How to Use

### Option 1: Run Full Scraper (Recommended)

```bash
python3 scripts/comprehensive_scraper.py
```

This will:
- Scrape both alumni profiles
- Download PDFs using "Save to PDF"
- Upload to B2
- Update database
- Add job history and education

### Option 2: Test First

```bash
# Test PDF download
python3 scripts/test_pdf_download.py

# If successful, run full scraper
python3 scripts/comprehensive_scraper.py
```

### Option 3: View in App

```bash
bash start_app.sh
```

Then:
1. Go to **Browse Alumni**
2. Click **"👁️ View Detailed Profiles"**
3. Expand any alumni
4. Click **LinkedIn PDF** link to download from B2

---

## What Gets Saved

### PDF Content
- ✅ Profile photo
- ✅ Name and headline
- ✅ About section
- ✅ Experience
- ✅ Education
- ✅ Skills
- ✅ Recommendations
- ✅ All profile information

### Storage
- **Location:** Backblaze B2 bucket `ARCIIMR`
- **Path:** `linkedin_profiles/{roll_number}_{timestamp}.pdf`
- **Example:** `linkedin_profiles/M218-23_20251128_101530.pdf`
- **Access:** Download link stored in database

---

## Troubleshooting

### "More button not found"
- LinkedIn might have changed the UI
- Try updating the selector in the code
- Or use fallback PDF generation

### "Save to PDF button not found"
- LinkedIn might have changed the menu
- Fallback will generate PDF from page
- Still works, just different format

### "PDF is blank or incomplete"
- Wait a moment for page to fully load
- Increase timeout in `.env`:
  ```
  SCRAPER_TIMEOUT=90000
  ```

### "PDF upload to B2 fails"
- Check B2 credentials: `python3 scripts/diagnose_b2.py`
- Verify bucket exists
- Check internet connection

---

## PDF Quality

The official LinkedIn "Save to PDF" generates:
- ✅ High-quality PDF
- ✅ All profile information
- ✅ Professional formatting
- ✅ Includes profile photo
- ✅ Includes all sections

---

## Next Steps

1. **Test PDF download:**
   ```bash
   python3 scripts/test_pdf_download.py
   ```

2. **Run full scraper:**
   ```bash
   python3 scripts/comprehensive_scraper.py
   ```

3. **View in app:**
   ```bash
   bash start_app.sh
   ```

4. **Download PDFs:**
   - Browse Alumni → View Detailed Profiles
   - Expand any alumni
   - Click LinkedIn PDF link

---

## Success Indicators

✅ **PDF download working:**
- Browser shows "More" menu
- "Save to PDF" is clicked
- PDF file is generated
- PDF is uploaded to B2
- Download link appears in app

❌ **PDF download not working:**
- "More" button not found
- "Save to PDF" not found
- PDF is blank
- Upload to B2 fails

---

## Technical Details

### Selectors Used
```python
# More button
'button[aria-label*="More"]'
'button:has-text("More")'

# Save to PDF
'button:has-text("Save to PDF")'
'a:has-text("Save to PDF")'
'[data-test-id="save-to-pdf-button"]'
'button[aria-label*="Save to PDF"]'
```

### Fallback Method
If "Save to PDF" button not found:
- Uses Playwright's `page.pdf()` method
- Generates PDF from rendered page
- Still captures all profile information

---

## Questions?

See:
- `COOKIES_GUIDE.md` - Cookie setup
- `SCRAPER_GUIDE.md` - Scraper details
- `TROUBLESHOOTING.md` - Common issues
