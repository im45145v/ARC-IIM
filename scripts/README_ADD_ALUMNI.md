# Add Alumni Scripts

## Quick Start

### Option 1: Add Alumni Only
```bash
python3 scripts/add_alumni_batch.py
```

### Option 2: Add Alumni + Scrape LinkedIn (Recommended)
```bash
bash scripts/add_and_scrape_alumni.sh
```

### Option 3: Scrape Existing Alumni
```bash
python3 scripts/scrape_new_alumni.py
```

## What These Scripts Do

### `add_alumni_batch.py`
- Adds the two new alumni records to the database:
  - Akshat Naugir (M218-23)
  - Narendran T (BA041-23)
- Checks for duplicates before adding
- Includes all their basic information

### `scrape_new_alumni.py`
- Scrapes LinkedIn profiles for the two alumni
- Updates database with latest information from LinkedIn
- Requires LinkedIn cookies to be configured

### `add_and_scrape_alumni.sh`
- Runs both scripts in sequence
- First adds alumni, then scrapes their profiles
- Complete automation

## Prerequisites

1. **Database Running**
   ```bash
   docker-compose up -d
   ```

2. **LinkedIn Cookies** (for scraping)
   - Make sure `cookies/linkedin_cookies_1.json` is configured
   - See `docs/COOKIE_AUTHENTICATION.md` for setup

3. **Environment Variables**
   - Ensure `.env` file has correct database credentials

## Troubleshooting

### "Alumni already exists"
- The script checks for duplicates
- If alumni already exist, they won't be added again

### "No LinkedIn URL"
- Check that the LinkedIn URL is valid in the script

### "Failed to scrape"
- Verify LinkedIn cookies are valid
- Check your internet connection
- LinkedIn may be rate-limiting requests

## Adding More Alumni

Edit `scripts/add_alumni_batch.py` and add more records to the `alumni_data` list:

```python
alumni_data = [
    {
        "name": "Your Name",
        "roll_number": "ROLL123",
        "batch": "MBA (2023-25)",
        "linkedin_url": "https://linkedin.com/in/yourprofile",
        # ... more fields
    },
    # Add more alumni here
]
```
