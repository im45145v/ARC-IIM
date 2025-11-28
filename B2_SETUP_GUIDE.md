# 🔧 Backblaze B2 Setup Guide

## Current Issue

Your B2 credentials in `.env` are invalid:
```
B2_APPLICATION_KEY_ID=0055605692c41480000000002
B2_APPLICATION_KEY=K005ODvuu1hSVIUB/GuwqKBQXfJ1Ke0
B2_BUCKET_NAME=ARCIIMR
```

Error: `Invalid authorization token`

---

## Solution: Get Valid B2 Credentials

### Step 1: Create Backblaze B2 Account

1. Go to https://www.backblaze.com/b2/
2. Click "Sign Up"
3. Create account with email and password
4. Verify email

### Step 2: Create Application Key

1. Log into B2 dashboard
2. Go to **Account** → **Application Keys**
3. Click **Create Application Key**
4. Configure:
   - **Key Name:** `alumni-scraper` (or any name)
   - **Capabilities:** Select `listBuckets`, `readBucketInfo`, `listFiles`, `readFiles`, `writeFiles`, `deleteFiles`
   - **Bucket ID:** Leave blank (or select your bucket)
   - **Valid Duration:** Leave blank (no expiration)
5. Click **Create Application Key**
6. **IMPORTANT:** Copy the credentials immediately:
   - **Application Key ID** (starts with `00...`)
   - **Application Key** (long string)

### Step 3: Create B2 Bucket

1. In B2 dashboard, go to **Buckets**
2. Click **Create a Bucket**
3. Configure:
   - **Bucket Name:** `alumni-linkedin-pdfs` (or any name)
   - **Type:** Private (recommended)
   - **Lifecycle:** Keep default
4. Click **Create Bucket**
5. Note the bucket name

### Step 4: Update .env File

Option A: **Automatic Setup**
```bash
python3 scripts/setup_b2.py --setup
```

This will:
1. Ask for your B2 credentials
2. Test them
3. Update `.env` file automatically

Option B: **Manual Setup**

Edit `.env` file and update:
```bash
B2_APPLICATION_KEY_ID=your_key_id_here
B2_APPLICATION_KEY=your_application_key_here
B2_BUCKET_NAME=your_bucket_name_here
```

### Step 5: Test Configuration

```bash
python3 scripts/setup_b2.py --test
```

Should show:
```
✅ B2 client initialized
✅ Connected to bucket: alumni-linkedin-pdfs
✅ Bucket contains 0 files
✅ B2 configuration is working!
```

---

## Troubleshooting

### "Invalid authorization token"

**Causes:**
- Application Key ID is wrong
- Application Key is wrong
- Key has expired
- Key was deleted

**Solution:**
1. Go to B2 dashboard
2. Check Application Keys section
3. Create a new key if needed
4. Copy credentials carefully (no extra spaces)
5. Run setup again: `python3 scripts/setup_b2.py --setup`

### "Bucket not found"

**Causes:**
- Bucket name is wrong
- Bucket was deleted
- Bucket is in different account

**Solution:**
1. Go to B2 dashboard
2. Check Buckets section
3. Verify bucket name exactly
4. Create new bucket if needed
5. Update `.env` with correct name

### "Access denied"

**Causes:**
- Application Key doesn't have required permissions
- Key is restricted to specific bucket

**Solution:**
1. Create new Application Key with full permissions
2. Or update existing key to include:
   - `listBuckets`
   - `readBucketInfo`
   - `listFiles`
   - `readFiles`
   - `writeFiles`
   - `deleteFiles`

---

## Quick Setup (Copy-Paste)

1. **Get credentials from B2 dashboard**
   - Application Key ID
   - Application Key
   - Bucket Name

2. **Run setup script:**
   ```bash
   python3 scripts/setup_b2.py --setup
   ```

3. **Enter credentials when prompted**

4. **Test:**
   ```bash
   python3 scripts/setup_b2.py --test
   ```

---

## Using B2 with Scraper

Once configured, the scraper will automatically:

1. Download LinkedIn profiles as PDFs
2. Upload to B2 storage
3. Store download URL in database
4. Display link in UI

### Run Scraper

```bash
python3 scripts/comprehensive_scraper.py
```

Output will show:
```
☁️  Uploading PDF to Backblaze B2...
✅ PDF saved to B2: linkedin_profiles/M218-23_20251128_101530.pdf
```

### View PDFs

1. In Streamlit app, go to **Browse Alumni**
2. Click **"👁️ View Detailed Profiles"**
3. Expand any alumni
4. Click **LinkedIn PDF** link to download

---

## B2 Pricing

- **Free tier:** 10 GB storage, 1 GB bandwidth/day
- **Paid:** $0.006/GB storage, $0.001/GB bandwidth

For alumni profiles:
- Average PDF: 2-5 MB
- 100 alumni: ~300-500 MB
- Cost: ~$0.002-0.003/month

---

## Security Notes

1. **Never share your Application Key**
   - Treat it like a password
   - Don't commit to version control
   - Keep in `.env` (which is in `.gitignore`)

2. **Rotate keys periodically**
   - Delete old keys
   - Create new ones
   - Update `.env`

3. **Use restricted permissions**
   - Only grant needed capabilities
   - Don't use master key

4. **Monitor usage**
   - Check B2 dashboard regularly
   - Watch for unusual activity

---

## Alternative: Skip B2

If you don't want to use B2:

1. The scraper will still work
2. PDFs won't be saved to cloud
3. All other data will be in database
4. UI will show "No PDF available"

To skip B2:
- Leave B2 credentials blank in `.env`
- Or comment them out
- Scraper will detect and skip PDF upload

---

## Support

**B2 Documentation:** https://www.backblaze.com/b2/docs/

**Common Issues:**
- https://www.backblaze.com/b2/docs/application_keys.html
- https://www.backblaze.com/b2/docs/buckets.html

**Contact B2 Support:** https://www.backblaze.com/b2/contact-us/
