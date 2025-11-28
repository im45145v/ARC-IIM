# Quick Start: Cookie-Based Authentication

**The easiest and most secure way to authenticate with LinkedIn.**

## 3-Step Setup

### Step 1: Export Your Cookies

**Option A: Use Your Default Browser (Easiest)**

1. Install browser extension: [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg) (Chrome/Edge) or [Cookie-Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/) (Firefox)
2. Go to LinkedIn (already logged in)
3. Click extension → Export → JSON
4. Save to `cookies/linkedin_cookies_1.json`

📖 **Detailed instructions:** [EXPORT_COOKIES_FROM_BROWSER.md](./EXPORT_COOKIES_FROM_BROWSER.md)

**Option B: Use Automated Script**

```bash
python scripts/export_linkedin_cookies.py
```

Follow the prompts:
1. Choose "Automated" method
2. Browser window opens
3. Log in to LinkedIn (2FA is fine!)
4. Press Enter after login
5. Cookies saved to `cookies/linkedin_cookies_1.json`

### Step 2: Configure .env

```bash
# Add this line to your .env file
LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json
```

### Step 3: Run the App

```bash
streamlit run alumni_system/frontend/app.py
```

That's it! The scraper will automatically use your cookies.

---

## Multiple Accounts

Export cookies for multiple accounts:

```bash
python scripts/export_linkedin_cookies.py
# Enter "3" when asked how many accounts
```

Then add to `.env`:

```bash
LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json
LINKEDIN_COOKIES_FILE_2=cookies/linkedin_cookies_2.json
LINKEDIN_COOKIES_FILE_3=cookies/linkedin_cookies_3.json
```

---

## Why Cookies?

✅ **More Secure** - No passwords in files  
✅ **2FA Support** - Keep 2FA enabled  
✅ **Longer Sessions** - Cookies last weeks/months  
✅ **Less Detectable** - No repeated logins  

---

## When to Re-Export

Re-export cookies when you see:
- "Authentication failed" errors
- "Please log in" messages
- Scraper can't access profiles

Usually every **2-4 weeks**.

---

## Troubleshooting

**Problem:** Script says "Cookie authentication failed"

**Solution:** Re-run `python scripts/export_linkedin_cookies.py`

**Problem:** Can't find cookies file

**Solution:** Check path in `.env` matches actual file location

---

## Full Documentation

See [COOKIE_AUTHENTICATION.md](./COOKIE_AUTHENTICATION.md) for complete guide.
