#!/usr/bin/env python3
"""
Helper script to export LinkedIn cookies from your browser.

This script provides two methods to export cookies:
1. Automated: Opens a Playwright browser, you log in, script exports cookies
2. Manual: Instructions to export from your default browser using extensions

Usage:
    python scripts/export_linkedin_cookies.py

The script will:
1. Ask which method you prefer
2. Guide you through the export process
3. Save cookies to cookies/linkedin_cookies_1.json (or _2, _3, etc.)
"""

import asyncio
import json
import os
from pathlib import Path

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


async def export_cookies(account_number: int = 1):
    """
    Export LinkedIn cookies after manual login.
    
    Args:
        account_number: Account number for naming the cookies file (1, 2, 3, etc.)
    """
    print("=" * 60)
    print("LinkedIn Cookie Exporter")
    print("=" * 60)
    print()
    print("This script will:")
    print("1. Open a browser window")
    print("2. Navigate to LinkedIn login")
    print("3. Wait for you to log in manually (including 2FA)")
    print("4. Export your cookies to a file")
    print()
    print("IMPORTANT: Use a dedicated LinkedIn account for scraping,")
    print("           not your personal account!")
    print()
    input("Press Enter to continue...")
    
    async with async_playwright() as p:
        # Launch browser in non-headless mode so user can log in
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        
        # Navigate to LinkedIn login
        print("\nNavigating to LinkedIn login page...")
        await page.goto("https://www.linkedin.com/login")
        
        print("\n" + "=" * 60)
        print("PLEASE LOG IN TO LINKEDIN IN THE BROWSER WINDOW")
        print("=" * 60)
        print()
        print("Steps:")
        print("1. Enter your email and password")
        print("2. Complete 2FA verification if prompted")
        print("3. Wait until you see your LinkedIn feed")
        print("4. Come back here and press Enter")
        print()
        print("NOTE: The browser window will stay open until you press Enter")
        print()
        
        # Wait for user to log in manually
        input("Press Enter after you've successfully logged in...")
        
        # Verify we're logged in
        current_url = page.url
        if "feed" not in current_url and "mynetwork" not in current_url:
            print("\n⚠️  WARNING: You don't appear to be logged in.")
            print(f"Current URL: {current_url}")
            print()
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                await browser.close()
                return
        
        # Export cookies
        print("\nExporting cookies...")
        cookies = await context.cookies()
        
        # Create cookies directory
        cookies_dir = Path("cookies")
        cookies_dir.mkdir(exist_ok=True)
        
        # Save cookies to file
        cookies_file = cookies_dir / f"linkedin_cookies_{account_number}.json"
        with open(cookies_file, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"\n✅ Success! Cookies exported to: {cookies_file}")
        print(f"   Total cookies: {len(cookies)}")
        
        # Show important cookies
        important_cookies = ['li_at', 'JSESSIONID', 'liap']
        found_cookies = [c['name'] for c in cookies if c['name'] in important_cookies]
        if found_cookies:
            print(f"   Important cookies found: {', '.join(found_cookies)}")
        
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print()
        print(f"1. Update your .env file with:")
        print(f"   LINKEDIN_COOKIES_FILE_{account_number}={cookies_file}")
        print()
        print("2. Or use the cookies file directly in your code:")
        print(f"   scraper = LinkedInScraper(cookies_file='{cookies_file}')")
        print()
        print("3. Cookies typically last for several weeks/months")
        print("   Re-export if you get authentication errors")
        print()
        
        await browser.close()


def show_manual_export_instructions():
    """Show instructions for manually exporting cookies from default browser."""
    print("\n" + "=" * 70)
    print("MANUAL COOKIE EXPORT - Use Your Default Browser")
    print("=" * 70)
    print()
    print("This method lets you export cookies from your default browser")
    print("(Chrome, Firefox, Edge, Safari, etc.) where you're already logged in.")
    print()
    print("=" * 70)
    print("METHOD 1: Using Browser Extension (EASIEST)")
    print("=" * 70)
    print()
    print("1. Install a cookie export extension:")
    print()
    print("   Chrome/Edge:")
    print("   → https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg")
    print("   → Search for 'EditThisCookie' or 'Cookie-Editor'")
    print()
    print("   Firefox:")
    print("   → https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/")
    print("   → Search for 'Cookie-Editor'")
    print()
    print("2. Log in to LinkedIn in your browser (if not already logged in)")
    print()
    print("3. Navigate to: https://www.linkedin.com/feed/")
    print()
    print("4. Click the extension icon in your browser toolbar")
    print()
    print("5. Click 'Export' → 'JSON' (or similar option)")
    print()
    print("6. Save the file as: cookies/linkedin_cookies_1.json")
    print()
    print("=" * 70)
    print("METHOD 2: Using Browser DevTools (ADVANCED)")
    print("=" * 70)
    print()
    print("1. Log in to LinkedIn in your browser")
    print()
    print("2. Press F12 (or Ctrl+Shift+I / Cmd+Option+I) to open DevTools")
    print()
    print("3. Go to 'Application' tab (Chrome/Edge) or 'Storage' tab (Firefox)")
    print()
    print("4. Expand 'Cookies' → 'https://www.linkedin.com'")
    print()
    print("5. Look for these important cookies:")
    print("   - li_at (most important - authentication token)")
    print("   - JSESSIONID")
    print("   - liap")
    print()
    print("6. Copy all cookies and format as JSON array (see docs for format)")
    print()
    print("7. Save to: cookies/linkedin_cookies_1.json")
    print()
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print()
    print("After exporting cookies:")
    print()
    print("1. Verify the file exists:")
    print("   ls -la cookies/linkedin_cookies_1.json")
    print()
    print("2. Add to your .env file:")
    print("   LINKEDIN_COOKIES_FILE_1=cookies/linkedin_cookies_1.json")
    print()
    print("3. Run the application:")
    print("   streamlit run alumni_system/frontend/app.py")
    print()
    print("=" * 70)
    print()
    print("📖 For detailed instructions, see: docs/COOKIE_AUTHENTICATION.md")
    print()


async def main():
    """Main function to handle multiple accounts."""
    print("\n" + "=" * 70)
    print("LinkedIn Cookie Exporter")
    print("=" * 70)
    print()
    print("Choose your export method:")
    print()
    print("1. Automated (Playwright) - Opens a new browser window")
    print("   ✓ Automated process")
    print("   ✓ Works with any browser")
    print("   ✗ Requires Playwright installed")
    print()
    print("2. Manual (Your Browser) - Use your default browser")
    print("   ✓ Use browser where you're already logged in")
    print("   ✓ No additional software needed")
    print("   ✗ Requires browser extension or manual steps")
    print()
    
    if not PLAYWRIGHT_AVAILABLE:
        print("⚠️  Playwright not available. Only manual method is available.")
        print("   To use automated method, install: pip install playwright")
        print("   Then run: playwright install chromium")
        print()
        choice = "2"
    else:
        choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        if not PLAYWRIGHT_AVAILABLE:
            print("\n❌ Playwright is not installed.")
            print("Install with: pip install playwright && playwright install chromium")
            return
        
        print("\nHow many LinkedIn accounts do you want to export cookies for?")
        try:
            num_accounts = int(input("Enter number (1-5): "))
            if num_accounts < 1 or num_accounts > 5:
                print("Please enter a number between 1 and 5")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
        
        for i in range(1, num_accounts + 1):
            print(f"\n{'=' * 60}")
            print(f"EXPORTING COOKIES FOR ACCOUNT {i}")
            print(f"{'=' * 60}")
            await export_cookies(i)
            
            if i < num_accounts:
                print("\n" + "=" * 60)
                input(f"Press Enter to continue with account {i + 1}...")
    
    elif choice == "2":
        show_manual_export_instructions()
    
    else:
        print("\n❌ Invalid choice. Please run the script again and choose 1 or 2.")


if __name__ == "__main__":
    asyncio.run(main())
