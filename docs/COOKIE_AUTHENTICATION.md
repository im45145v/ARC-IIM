# Cookie-Based Authentication for LinkedIn Scraping

This guide explains how to use cookie-based authentication instead of hardcoding credentials. This method is **more secure**, **supports 2FA**, and is **more reliable** than credential-based authentication.

## Why Use Cookie-Based Authentication?

### ✅ Advantages

1. **Security**: No passwords stored in environment variables
2. **2FA Support**: You can keep 2FA enabled on your LinkedIn accounts
3. **Longer Sessions**: Cookies typically last weeks/months vs. session-based logins
4. **More Reliable**: Avoids repeated login attempts that might trigger security checks
5. **Easier Management**: Export once, use for weeks

### ❌ Disadvantages of Credential-Based Auth

1. **Security Risk**: Passwords in plain text in `.env` file
2. **No 2FA**: Must disable 2FA for automation to work
3. **More Detectable**: Repeated logins can trigger LinkedIn security
4. **Session Expiry**: May need to re-authenticate frequently

---

## Quick Start: Cookie-Based Authentication

### Step 1: Export Cookies from Your Browser

We provide a helper script that makes this easy:

```bash
python scripts/export_linkedin_cookies.py
```

**What this script does:**
1. Opens a browser window
2. Navigates to LinkedIn login
3. Waits for you to log in manually (including 2FA)
4. Exports your cookies to `cookies/linkedin_cookies_1.json`

**Follow the prompts:**
- Enter how many accounts you want to export (1-5)
- Log in to each account when prompted
- Complete 2FA if enabled
- Press Enter after successful login

### Step 2: Configure Environment Variables

Add the cookie file paths to your `.env`:

```bash
# Cookie-based authentication (recommended)
LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json
LINKEDIN_COOKIES_FILE_2=cookies/linkedin_cookies_2.json
LINKEDIN_COOKIES_FILE_3=cookies/linkedin_cookies_3.json
```

### Step 3: Use the Scraper

The scraper will automatically use cookies if available:

```python
from alumni_system.scraper.linkedin_scraper import LinkedInScraper

# Cookies are loaded automatically from environment variables
async with LinkedInScraper() as scraper:
    profile = await scraper.scrape_profile("https://linkedin.com/in/username")
```

Or specify cookies file directly:

```python
# Use specific cookies file
async with LinkedInScraper(cookies_file="cookies/linkedin_cookies_1.json") as scraper:
    profile = await scraper.scrape_profile("https://linkedin.com/in/username")
```

---

## Manual Cookie Export (Alternative Methods)

If you prefer to export cookies manually from your browser:

### Method 1: Using Browser Extension (Easiest)

1. **Install a cookie export extension:**
   - Chrome/Edge: [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - Firefox: [Cookie-Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)

2. **Export cookies:**
   - Log in to LinkedIn in your browser
   - Click the extension icon
   - Click "Export" → "JSON"
   - Save to `cookies/linkedin_cookies_1.json`

### Method 2: Using Browser DevTools (Advanced)

1. **Open DevTools:**
   - Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
   - Press `Cmd+Option+I` (Mac)

2. **Navigate to Application/Storage tab:**
   - Chrome/Edge: Application → Cookies → https://www.linkedin.com
   - Firefox: Storage → Cookies → https://www.linkedin.com

3. **Copy cookies:**
   - Right-click → Copy all cookies
   - Format as JSON array (see format below)

### Method 3: Using Playwright Script

```python
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # Navigate and log in manually
    page.goto("https://www.linkedin.com/login")
    input("Press Enter after logging in...")
    
    # Export cookies
    cookies = context.cookies()
    with open("cookies/linkedin_cookies_1.json", "w") as f:
        json.dump(cookies, f, indent=2)
    
    browser.close()
```

---

## Cookie File Format

The cookies file should be a JSON array of cookie objects:

```json
[
  {
    "name": "li_at",
    "value": "AQEDATxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "domain": ".linkedin.com",
    "path": "/",
    "expires": 1735689600,
    "httpOnly": true,
    "secure": true,
    "sameSite": "None"
  },
  {
    "name": "JSESSIONID",
    "value": "ajax:1234567890123456789",
    "domain": ".www.linkedin.com",
    "path": "/",
    "expires": -1,
    "httpOnly": true,
    "secure": true,
    "sameSite": "None"
  }
]
```

**Important cookies:**
- `li_at`: Main authentication token (most important)
- `JSESSIONID`: Session identifier
- `liap`: Additional auth parameter

---

## Multi-Account Setup with Cookies

### Export Cookies for Multiple Accounts

```bash
# Run the export script
python scripts/export_linkedin_cookies.py

# When prompted, enter the number of accounts (e.g., 3)
# Log in to each account when prompted
```

This creates:
- `cookies/linkedin_cookies_1.json`
- `cookies/linkedin_cookies_2.json`
- `cookies/linkedin_cookies_3.json`

### Configure in .env

```bash
# Account 1
LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json

# Account 2
LINKEDIN_COOKIES_FILE_2=cookies/linkedin_cookies_2.json

# Account 3
LINKEDIN_COOKIES_FILE_3=cookies/linkedin_cookies_3.json
```

### Account Rotation

The system will automatically rotate between accounts:

```python
from alumni_system.scraper.account_rotation import AccountRotationManager, LinkedInAccount

# Load accounts with cookies
accounts = [
    LinkedInAccount(
        id="1",
        email="account1@example.com",
        password="",  # Not needed with cookies
        cookies_file="cookies/linkedin_cookies_1.json"
    ),
    LinkedInAccount(
        id="2",
        email="account2@example.com",
        password="",
        cookies_file="cookies/linkedin_cookies_2.json"
    ),
]

manager = AccountRotationManager(accounts, daily_limit=80)
```

---

## Cookie Maintenance

### How Long Do Cookies Last?

- LinkedIn cookies typically last **2-4 weeks**
- Some cookies may last **several months**
- Depends on LinkedIn's session management

### When to Re-Export Cookies

Re-export cookies when you see:
- "Authentication failed" errors
- "Please log in" messages
- 401/403 HTTP errors
- Scraper unable to access profiles

### Automatic Cookie Refresh (Optional)

You can save cookies after successful login:

```python
async with LinkedInScraper() as scraper:
    await scraper.login()
    
    # Save cookies for future use
    await scraper.save_cookies("cookies/linkedin_cookies_1.json")
```

---

## Security Best Practices

### ✅ Do's

1. **Store cookies securely**: Keep `cookies/` directory private
2. **Add to .gitignore**: Never commit cookies to version control
3. **Use dedicated accounts**: Don't use personal LinkedIn accounts
4. **Rotate regularly**: Re-export cookies every few weeks
5. **Monitor usage**: Check for unusual activity on accounts

### ❌ Don'ts

1. **Don't share cookies**: Each account should have unique cookies
2. **Don't commit to git**: Cookies are as sensitive as passwords
3. **Don't use personal accounts**: Risk of account suspension
4. **Don't reuse across machines**: Export fresh cookies per environment

### .gitignore Configuration

Ensure your `.gitignore` includes:

```gitignore
# Cookies directory
cookies/
*.json

# Environment variables
.env
.env.local
```

---

## Troubleshooting

### Problem: "Cookie authentication failed"

**Solutions:**
1. Re-export cookies using the script
2. Verify cookies file exists and is valid JSON
3. Check file path in `.env` is correct
4. Ensure you logged in successfully before exporting

### Problem: "Cookies expired"

**Solutions:**
1. Re-export fresh cookies
2. Log in to LinkedIn manually to refresh session
3. Check if account was suspended or flagged

### Problem: "Security checkpoint detected"

**Solutions:**
1. Log in manually to clear checkpoint
2. Complete any verification LinkedIn requires
3. Re-export cookies after clearing checkpoint
4. System will automatically rotate to next account

### Problem: Script can't find cookies file

**Solutions:**
1. Check file path is relative to project root
2. Verify file exists: `ls -la cookies/`
3. Check file permissions: `chmod 644 cookies/*.json`
4. Use absolute path if needed

---

## Comparison: Cookies vs. Credentials

| Feature | Cookie-Based | Credential-Based |
|---------|-------------|------------------|
| **Security** | ✅ High (no passwords) | ❌ Low (plain text passwords) |
| **2FA Support** | ✅ Yes | ❌ No (must disable) |
| **Setup Complexity** | Medium (one-time export) | Easy (just add to .env) |
| **Session Duration** | ✅ Weeks/months | ❌ Hours/days |
| **Detection Risk** | ✅ Lower | ❌ Higher (repeated logins) |
| **Maintenance** | Re-export every few weeks | Update if password changes |
| **Automation** | ✅ Fully automated | ✅ Fully automated |

**Recommendation:** Use cookie-based authentication for production. Use credential-based only for quick testing.

---

## Advanced: Programmatic Cookie Management

### Load Cookies in Code

```python
import json
from alumni_system.scraper.linkedin_scraper import LinkedInScraper

# Load cookies from file
with open("cookies/linkedin_cookies_1.json") as f:
    cookies = json.load(f)

# Use with scraper
async with LinkedInScraper(cookies_file="cookies/linkedin_cookies_1.json") as scraper:
    # Scraper automatically loads cookies
    profile = await scraper.scrape_profile("https://linkedin.com/in/username")
```

### Save Cookies After Login

```python
async with LinkedInScraper() as scraper:
    # Login with credentials
    await scraper.login()
    
    # Save cookies for future use
    await scraper.save_cookies("cookies/linkedin_cookies_backup.json")
```

### Verify Cookie Authentication

```python
async with LinkedInScraper(cookies_file="cookies/linkedin_cookies_1.json") as scraper:
    # Verify cookies work
    if await scraper.verify_cookie_auth():
        print("✅ Cookie authentication successful!")
    else:
        print("❌ Cookie authentication failed")
```

---

## FAQ

**Q: Can I use the same cookies on multiple machines?**
A: Yes, but it's not recommended. LinkedIn may detect simultaneous usage from different IPs and flag the account.

**Q: Do I need to disable 2FA?**
A: No! That's the main advantage of cookie-based auth. Keep 2FA enabled for security.

**Q: How often should I re-export cookies?**
A: Every 2-4 weeks, or when you see authentication errors.

**Q: Can I automate cookie refresh?**
A: Partially. You can save cookies after login, but initial manual login is required for 2FA.

**Q: What if my cookies get stolen?**
A: Immediately log out of LinkedIn on all devices, change your password, and re-export fresh cookies.

**Q: Can I mix cookie and credential authentication?**
A: Yes! The system tries cookies first, then falls back to credentials if cookies fail.

---

## Summary

Cookie-based authentication is the **recommended approach** for LinkedIn scraping because it's:
- ✅ More secure (no passwords in files)
- ✅ Supports 2FA
- ✅ More reliable (longer sessions)
- ✅ Less detectable (no repeated logins)

**Quick setup:**
```bash
# 1. Export cookies
python scripts/export_linkedin_cookies.py

# 2. Add to .env
echo "LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json" >> .env

# 3. Run scraper (automatically uses cookies)
streamlit run alumni_system/frontend/app.py
```

That's it! Your scraper will now use secure cookie-based authentication. 🎉
