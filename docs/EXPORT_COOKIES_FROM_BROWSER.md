# Export Cookies from Your Default Browser

**The easiest way:** Use your default browser where you're already logged in to LinkedIn!

## Why Use Your Default Browser?

✅ **Already logged in** - No need to log in again  
✅ **2FA already done** - Your session is active  
✅ **Familiar interface** - Use the browser you know  
✅ **Quick and easy** - Takes 2 minutes  

---

## Method 1: Browser Extension (Recommended)

### For Chrome / Edge / Brave

1. **Install Extension:**
   - Go to [Chrome Web Store](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
   - Search for "EditThisCookie" or "Cookie-Editor"
   - Click "Add to Chrome/Edge"

2. **Export Cookies:**
   - Log in to LinkedIn (if not already)
   - Go to https://www.linkedin.com/feed/
   - Click the extension icon in toolbar
   - Click "Export" → "JSON"
   - Copy the JSON

3. **Save to File:**
   ```bash
   # Create cookies directory
   mkdir -p cookies
   
   # Paste the JSON into a file
   nano cookies/linkedin_cookies_1.json
   # (Paste the JSON, then Ctrl+X, Y, Enter to save)
   ```

### For Firefox

1. **Install Extension:**
   - Go to [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)
   - Search for "Cookie-Editor"
   - Click "Add to Firefox"

2. **Export Cookies:**
   - Log in to LinkedIn (if not already)
   - Go to https://www.linkedin.com/feed/
   - Click the extension icon
   - Click "Export" → "JSON"
   - Copy the JSON

3. **Save to File:**
   ```bash
   mkdir -p cookies
   nano cookies/linkedin_cookies_1.json
   # Paste and save
   ```

### For Safari

1. **Use Web Inspector:**
   - Enable Developer menu: Safari → Preferences → Advanced → Show Develop menu
   - Go to LinkedIn and log in
   - Develop → Show Web Inspector
   - Storage tab → Cookies → linkedin.com
   - Copy cookies manually (see Method 2 below)

---

## Method 2: Browser DevTools (No Extension Needed)

### Step 1: Open DevTools

**Chrome / Edge / Brave:**
- Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
- Press `Cmd+Option+I` (Mac)

**Firefox:**
- Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
- Press `Cmd+Option+I` (Mac)

**Safari:**
- Enable Developer menu first (Preferences → Advanced)
- Press `Cmd+Option+I`

### Step 2: Navigate to Cookies

**Chrome / Edge / Brave:**
1. Click "Application" tab
2. Expand "Cookies" in left sidebar
3. Click "https://www.linkedin.com"

**Firefox:**
1. Click "Storage" tab
2. Expand "Cookies"
3. Click "https://www.linkedin.com"

**Safari:**
1. Click "Storage" tab
2. Click "Cookies"
3. Select "linkedin.com"

### Step 3: Export Cookies

You'll see a table with cookies. Look for these important ones:

| Cookie Name | Description |
|-------------|-------------|
| `li_at` | **Most important** - Authentication token |
| `JSESSIONID` | Session identifier |
| `liap` | Additional auth parameter |

**Option A: Use Console to Export All Cookies**

1. Click "Console" tab in DevTools
2. Paste this code and press Enter:

```javascript
// Export all LinkedIn cookies as JSON
copy(JSON.stringify(
  document.cookie.split(';').map(c => {
    const [name, value] = c.trim().split('=');
    return {
      name: name,
      value: value,
      domain: '.linkedin.com',
      path: '/',
      expires: -1,
      httpOnly: false,
      secure: true,
      sameSite: 'None'
    };
  }),
  null,
  2
));
console.log('Cookies copied to clipboard!');
```

3. Cookies are now in your clipboard!
4. Paste into `cookies/linkedin_cookies_1.json`

**Option B: Manual Copy (More Accurate)**

1. Right-click in the cookies table
2. Select "Copy all" or "Export"
3. Format as JSON (see format below)

### Step 4: Save to File

```bash
# Create directory
mkdir -p cookies

# Create file and paste cookies
nano cookies/linkedin_cookies_1.json
```

Paste the JSON, then save (Ctrl+X, Y, Enter)

---

## Cookie File Format

Your `cookies/linkedin_cookies_1.json` should look like this:

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
  },
  {
    "name": "liap",
    "value": "true",
    "domain": ".linkedin.com",
    "path": "/",
    "expires": 1735689600,
    "httpOnly": false,
    "secure": true,
    "sameSite": "None"
  }
]
```

**Important fields:**
- `name`: Cookie name
- `value`: Cookie value (keep this secret!)
- `domain`: Usually `.linkedin.com`
- `path`: Usually `/`
- `expires`: Expiration timestamp (-1 for session cookies)
- `httpOnly`: true/false
- `secure`: Usually true
- `sameSite`: Usually "None" or "Lax"

---

## Verify Your Cookies

After saving, verify the file:

```bash
# Check file exists
ls -la cookies/linkedin_cookies_1.json

# Check it's valid JSON
python -m json.tool cookies/linkedin_cookies_1.json > /dev/null && echo "✅ Valid JSON" || echo "❌ Invalid JSON"

# Check for important cookies
grep -q "li_at" cookies/linkedin_cookies_1.json && echo "✅ Found li_at cookie" || echo "❌ Missing li_at cookie"
```

---

## Configure and Test

### 1. Add to .env

```bash
echo "LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json" >> .env
```

### 2. Test Authentication

```python
# test_cookies.py
import asyncio
from alumni_system.scraper.linkedin_scraper import LinkedInScraper

async def test():
    async with LinkedInScraper(cookies_file="cookies/linkedin_cookies_1.json") as scraper:
        if await scraper.verify_cookie_auth():
            print("✅ Cookie authentication successful!")
        else:
            print("❌ Cookie authentication failed")

asyncio.run(test())
```

Run test:
```bash
python test_cookies.py
```

### 3. Run the Application

```bash
streamlit run alumni_system/frontend/app.py
```

---

## Multiple Accounts

To export cookies for multiple accounts:

### Option 1: Use Different Browser Profiles

1. **Chrome/Edge:** Create new profile
   - Click profile icon → Add profile
   - Log in to LinkedIn with different account
   - Export cookies to `linkedin_cookies_2.json`

2. **Firefox:** Create new profile
   - about:profiles → Create new profile
   - Log in to LinkedIn with different account
   - Export cookies to `linkedin_cookies_2.json`

### Option 2: Use Incognito/Private Windows

1. Open incognito/private window
2. Log in to LinkedIn with different account
3. Export cookies using extension or DevTools
4. Save to `linkedin_cookies_2.json`

### Option 3: Log Out and Log In

1. Log out of LinkedIn
2. Log in with different account
3. Export cookies
4. Save to `linkedin_cookies_2.json`
5. Repeat for account 3, 4, etc.

---

## Troubleshooting

### Problem: Extension not showing cookies

**Solution:** Make sure you're on linkedin.com domain. Extensions only show cookies for current site.

### Problem: Cookies not working

**Solutions:**
1. Make sure you're logged in to LinkedIn before exporting
2. Check that `li_at` cookie is present
3. Verify JSON format is correct
4. Try exporting fresh cookies

### Problem: "Invalid JSON" error

**Solutions:**
1. Use a JSON validator: https://jsonlint.com/
2. Check for missing commas or brackets
3. Make sure strings are in double quotes
4. Re-export using the console method above

### Problem: Can't find cookies directory

**Solution:**
```bash
# Create it
mkdir -p cookies

# Verify
ls -la cookies/
```

---

## Security Tips

✅ **Do:**
- Keep cookies files private
- Add `cookies/` to `.gitignore`
- Use dedicated LinkedIn accounts
- Re-export every few weeks

❌ **Don't:**
- Share cookies files
- Commit cookies to git
- Use personal LinkedIn accounts
- Reuse cookies across machines

---

## Summary

**Easiest method:**
1. Install browser extension (EditThisCookie or Cookie-Editor)
2. Go to LinkedIn (already logged in)
3. Click extension → Export → JSON
4. Save to `cookies/linkedin_cookies_1.json`
5. Add to `.env`: `LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json`
6. Done! 🎉

**Time required:** 2-3 minutes per account

**Advantages:**
- Use your existing browser session
- No need to log in again
- 2FA already handled
- Quick and easy

---

## Next Steps

After exporting cookies:

1. **Configure .env:**
   ```bash
   LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json
   ```

2. **Test authentication:**
   ```bash
   python test_cookies.py
   ```

3. **Run the app:**
   ```bash
   streamlit run alumni_system/frontend/app.py
   ```

4. **Start scraping!** 🚀

---

## Need Help?

- **Full guide:** [COOKIE_AUTHENTICATION.md](./COOKIE_AUTHENTICATION.md)
- **Quick start:** [QUICK_START_COOKIES.md](./QUICK_START_COOKIES.md)
- **Setup guide:** [../SETUP_GUIDE.md](../SETUP_GUIDE.md)
