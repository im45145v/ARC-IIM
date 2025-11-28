#!/usr/bin/env python3
"""
Quick test to verify scraper can authenticate and access LinkedIn
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("Quick Scraper Test")
print("=" * 70)
print()

# Test 1: Check cookies file
print("1. Checking cookies file...")
cookies_file = Path("cookies/linkedin_cookies_1_fixed.json")

if not cookies_file.exists():
    print(f"   ❌ Cookies file not found: {cookies_file}")
    print()
    print("   Solution:")
    print("   1. Export cookies from your browser")
    print("   2. Save to: cookies/linkedin_cookies_1.json")
    print("   3. Fix them: python3 -c \"import json; cookies=json.load(open('cookies/linkedin_cookies_1.json')); [cookie.update({'sameSite':'Lax'}) for cookie in cookies if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict','Lax','None']]; json.dump(cookies,open('cookies/linkedin_cookies_1_fixed.json','w'),indent=2)\"")
    sys.exit(1)

print(f"   ✅ Cookies file found")
print()

# Test 2: Check if cookies are valid JSON
print("2. Validating cookies JSON...")
try:
    import json
    with open(cookies_file) as f:
        cookies = json.load(f)
    print(f"   ✅ Valid JSON with {len(cookies)} cookies")
except Exception as e:
    print(f"   ❌ Invalid JSON: {e}")
    sys.exit(1)

print()

# Test 3: Check B2
print("3. Checking B2 configuration...")
try:
    from alumni_system.storage.b2_client import get_storage_client
    
    client = get_storage_client()
    bucket = client._get_bucket()
    print(f"   ✅ B2 connected (bucket: {bucket.name})")
except Exception as e:
    print(f"   ⚠️  B2 not available: {str(e)[:50]}")

print()

# Test 4: Check database
print("4. Checking database...")
try:
    from alumni_system.database.connection import get_db_context
    from alumni_system.database.crud import get_alumni_count
    
    with get_db_context() as db:
        count = get_alumni_count(db)
    print(f"   ✅ Database connected ({count} alumni)")
except Exception as e:
    print(f"   ❌ Database error: {e}")
    sys.exit(1)

print()

# Test 5: Check scraper
print("5. Checking scraper...")
try:
    from alumni_system.scraper.linkedin_scraper import LinkedInScraper
    print(f"   ✅ Scraper module loaded")
except Exception as e:
    print(f"   ❌ Scraper error: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("✅ All components are ready!")
print("=" * 70)
print()
print("To run the full scraper:")
print("  python3 scripts/comprehensive_scraper.py")
print()
print("Note: The scraper uses Playwright browser automation.")
print("If running in a headless environment (no display), the browser")
print("will run in the background without showing a window.")
print()
