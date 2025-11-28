# 🔧 Fix B2 Authentication Error

## Problem
```
❌ Authorization Error: Invalid authorization token
```

Your B2 application key is not working.

---

## Solution: Create a Fresh Application Key

### Step 1: Go to B2 Dashboard

1. Open https://secure.backblaze.com/
2. Log in with your B2 account
3. Click **Account** (top right)
4. Select **Application Keys**

### Step 2: Check Existing Keys

Look for your key:
- **Key ID:** `0055605692c41480000000003`
- **Key Name:** `ARCIIMRKEY3`

**If you see it:**
- Check if it's still active
- If not, delete it and create a new one

**If you don't see it:**
- It was deleted or revoked
- Create a new one

### Step 3: Create New Application Key

1. Click **Create Application Key**
2. Fill in:
   - **Key Name:** `alumni-scraper` (or any name)
   - **Capabilities:** Select these:
     - ✅ listBuckets
     - ✅ readBucketInfo
     - ✅ listFiles
     - ✅ readFiles
     - ✅ writeFiles
     - ✅ deleteFiles
   - **Bucket ID:** Leave blank (or select ARCIIMR)
   - **Valid Duration:** Leave blank (no expiration)

3. Click **Create Application Key**

### Step 4: Copy Credentials

**IMPORTANT:** Copy immediately! You won't see them again.

You'll see:
```
Application Key ID: 00556...
Application Key: K005...
```

Copy both exactly (no extra spaces or characters).

### Step 5: Update .env

Edit `.env` file:

```bash
B2_APPLICATION_KEY_ID=00556...
B2_APPLICATION_KEY=K005...
B2_BUCKET_NAME=ARCIIMR
```

**Make sure:**
- No extra spaces
- No quotes
- Exact copy from B2 dashboard

### Step 6: Test

```bash
python3 scripts/diagnose_b2.py
```

Should show:
```
✅ Authorization successful!
✅ Connected to bucket: ARCIIMR
✅ B2 Configuration is WORKING!
```

---

## Troubleshooting

### Still getting "Invalid authorization token"?

**Check:**
1. Did you copy the credentials exactly?
2. Are there any extra spaces?
3. Did you save the .env file?
4. Is the key still in B2 dashboard?

**Try:**
1. Delete the old key from B2 dashboard
2. Create a completely new key
3. Copy credentials again
4. Update .env
5. Test again

### Key doesn't appear in B2 dashboard?

1. Refresh the page
2. Log out and log back in
3. Check if you're in the right account
4. Try creating a new key

### Still not working?

1. Go to B2 dashboard
2. Delete ALL old keys
3. Create one fresh key
4. Copy credentials immediately
5. Update .env
6. Test

---

## Alternative: Use B2 CLI

If web dashboard doesn't work:

```bash
# Install B2 CLI
pip install b2-cli-tool

# Authorize
b2 authorize-account <account_id> <application_key>

# List buckets
b2 ls

# Test upload
b2 upload-file ARCIIMR test.txt test.txt
```

---

## If All Else Fails

**Option 1: Skip B2 for now**
- Scraper will still work
- PDFs won't upload to cloud
- All data stays in database

**Option 2: Use different cloud storage**
- AWS S3
- Google Cloud Storage
- Azure Blob Storage

**Option 3: Contact B2 Support**
- https://www.backblaze.com/b2/contact-us/

---

## Quick Checklist

- [ ] Logged into B2 dashboard
- [ ] Found Application Keys section
- [ ] Created new application key
- [ ] Copied Key ID exactly
- [ ] Copied Application Key exactly
- [ ] Updated .env file
- [ ] Saved .env file
- [ ] Ran `python3 scripts/diagnose_b2.py`
- [ ] Got "✅ B2 Configuration is WORKING!"

Once all checked, you're ready to scrape!
