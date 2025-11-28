# ⚡ Quick B2 Setup (5 Minutes)

## Problem
Your B2 credentials are invalid. PDFs won't upload.

## Solution

### Option 1: Automatic Setup (Recommended)

```bash
python3 scripts/setup_b2.py --setup
```

Then enter your B2 credentials when prompted.

### Option 2: Manual Setup

1. **Get B2 Credentials:**
   - Go to https://www.backblaze.com/b2/
   - Log in or create account
   - Go to **Account** → **Application Keys**
   - Click **Create Application Key**
   - Copy: **Application Key ID** and **Application Key**
   - Go to **Buckets** and note your **Bucket Name**

2. **Update .env:**
   ```bash
   B2_APPLICATION_KEY_ID=your_key_id
   B2_APPLICATION_KEY=your_app_key
   B2_BUCKET_NAME=your_bucket_name
   ```

3. **Test:**
   ```bash
   python3 scripts/setup_b2.py --test
   ```

### Option 3: Skip B2 (For Now)

If you don't have B2 set up yet:
- Scraper will still work
- PDFs won't be saved to cloud
- All other data will be in database

Just run:
```bash
python3 scripts/comprehensive_scraper.py
```

---

## Full Guide

See `B2_SETUP_GUIDE.md` for complete instructions.

---

## Test It

```bash
# Test B2 configuration
python3 scripts/setup_b2.py --test

# Should show:
# ✅ B2 client initialized
# ✅ Connected to bucket: your-bucket-name
# ✅ B2 configuration is working!
```

---

## Next Steps

Once B2 is configured:

```bash
# Run scraper (will upload PDFs to B2)
python3 scripts/comprehensive_scraper.py

# View in app
bash start_app.sh
```

PDFs will be available as download links in the UI!
