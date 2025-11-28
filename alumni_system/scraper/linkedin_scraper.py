"""
LinkedIn profile scraper using Playwright.

This module provides functionality to scrape LinkedIn profiles
and extract alumni information such as name, current company,
email, job history, and education.

IMPORTANT LEGAL AND ETHICAL CONSIDERATIONS:
============================================
1. Terms of Service: Web scraping LinkedIn may violate their Terms of Service.
   Review https://www.linkedin.com/legal/user-agreement before use.

2. Rate Limiting: This scraper implements delays between requests to avoid
   overwhelming LinkedIn's servers. Configure SCRAPER_MIN_DELAY and 
   SCRAPER_MAX_DELAY environment variables appropriately.

3. robots.txt: LinkedIn's robots.txt (https://www.linkedin.com/robots.txt)
   should be reviewed. Note that robots.txt is advisory for logged-in sessions.

4. Account Suspension Risk: Automated access may result in account suspension.
   Use a dedicated account and avoid scraping during peak hours.

5. Data Privacy: Ensure compliance with GDPR, CCPA, and other privacy regulations
   when storing and processing scraped personal data.

6. Best Practices:
   - Use reasonable delays (10-30 seconds between requests)
   - Avoid scraping during peak usage hours
   - Limit concurrent scraping sessions
   - Store only necessary data
   - Implement proper data retention policies

Use responsibly and ensure compliance with all applicable laws and policies.
"""

import asyncio
import json
import os
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from .account_rotation import LinkedInAccount
from .config import (
    HEADLESS_MODE,
    MAX_DELAY_SECONDS,
    MAX_RETRIES,
    MIN_DELAY_SECONDS,
    SELECTORS,
    SLOW_MO,
    TIMEOUT,
    get_linkedin_credentials,
)


class LinkedInScraper:
    """
    Scraper for extracting alumni information from LinkedIn profiles.
    
    Uses Playwright for browser automation and supports:
    - Profile data extraction (name, headline, location)
    - Job history extraction
    - Education history extraction
    - PDF download of profiles
    """

    def __init__(self, account: Optional[LinkedInAccount] = None, cookies_file: Optional[str] = None):
        """
        Initialize the LinkedIn scraper.
        
        Args:
            account: LinkedInAccount to use for authentication. If None, uses legacy credentials.
            cookies_file: Path to cookies JSON file for cookie-based authentication.
                         If provided, takes precedence over account credentials.
        """
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._logged_in = False
        self._account = account
        self._cookies_file = cookies_file
        self._current_account_email: Optional[str] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Start the browser and initialize context."""
        playwright = await async_playwright().start()
        self._browser = await playwright.chromium.launch(
            headless=HEADLESS_MODE,
            slow_mo=SLOW_MO,
        )
        self._context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            accept_downloads=True,  # Enable download handling
        )
        
        # Load cookies BEFORE creating page
        if self._cookies_file and os.path.exists(self._cookies_file):
            print(f"Loading cookies from: {self._cookies_file}")
            await self._load_cookies()
            print("✅ Cookies loaded into context")
        
        self._page = await self._context.new_page()
        self._page.set_default_timeout(TIMEOUT)

    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        if self._page:
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()

    async def _random_delay(self) -> None:
        """Add a random delay to avoid detection."""
        delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
        await asyncio.sleep(delay)
    
    async def _load_cookies(self) -> bool:
        """
        Load cookies from file into browser context.
        
        Returns:
            True if cookies loaded successfully, False otherwise.
        """
        try:
            with open(self._cookies_file, 'r') as f:
                cookies = json.load(f)
            
            await self._context.add_cookies(cookies)
            print(f"Loaded {len(cookies)} cookies from {self._cookies_file}")
            
            # Try to extract email from cookies for tracking
            for cookie in cookies:
                if cookie.get('name') == 'li_at':  # LinkedIn auth token
                    self._current_account_email = "cookie_auth"
                    self._logged_in = True
                    break
            
            return True
        except Exception as e:
            print(f"Error loading cookies: {e}")
            return False
    
    async def save_cookies(self, output_file: str) -> bool:
        """
        Save current browser cookies to file.
        
        Args:
            output_file: Path to save cookies JSON file.
        
        Returns:
            True if cookies saved successfully, False otherwise.
        """
        try:
            cookies = await self._context.cookies()
            
            # Create directory if it doesn't exist
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            
            print(f"Saved {len(cookies)} cookies to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving cookies: {e}")
            return False
    
    async def verify_cookie_auth(self) -> bool:
        """
        Verify that cookie-based authentication is working.
        
        Returns:
            True if authenticated, False otherwise.
        """
        try:
            print("Navigating to LinkedIn feed...")
            await self._page.goto("https://www.linkedin.com/feed/", wait_until="networkidle")
            
            # Wait a bit for page to fully load
            await asyncio.sleep(2)
            
            # Check multiple indicators of being logged in
            current_url = self._page.url
            print(f"Current URL: {current_url}")
            
            # Check if we're on feed or home (logged in)
            if "feed" in current_url or "home" in current_url:
                print("✅ Successfully logged in!")
                self._logged_in = True
                return True
            
            # Check if login page is shown (not logged in)
            if "login" in current_url or "checkpoint" in current_url:
                print("❌ Not logged in - login page shown")
                return False
            
            # Try to find logged-in indicators on page
            try:
                # Look for profile menu or other logged-in elements
                profile_menu = await self._page.query_selector('[data-test-id="profile-menu-trigger"]')
                if profile_menu:
                    print("✅ Found profile menu - logged in!")
                    self._logged_in = True
                    return True
            except:
                pass
            
            # If we got here, assume logged in if URL is reasonable
            if "linkedin.com" in current_url and "login" not in current_url:
                print("✅ Appears to be logged in")
                self._logged_in = True
                return True
            
            print("❌ Could not verify login status")
            return False
            
        except Exception as e:
            print(f"Error verifying cookie auth: {e}")
            return False

    async def login(self, account: Optional[LinkedInAccount] = None) -> bool:
        """
        Log in to LinkedIn using cookies (if available) or credentials.
        
        Priority order:
        1. Cookie-based authentication (if cookies loaded)
        2. Account credentials (if provided)
        3. Legacy environment variable credentials
        
        Args:
            account: LinkedInAccount to use for login. If None, uses instance account or legacy credentials.
        
        Returns:
            True if login successful, False otherwise.
        
        Raises:
            Exception: If security checkpoint is detected.
        """
        if self._logged_in:
            return True

        # Try cookie-based authentication first
        if self._cookies_file and os.path.exists(self._cookies_file):
            print("Attempting cookie-based authentication...")
            if await self.verify_cookie_auth():
                return True
            else:
                print("Cookie authentication failed, falling back to credentials...")

        # Determine which account to use for credential-based login
        login_account = account or self._account
        
        if login_account:
            email = login_account.email
            password = login_account.password
            self._current_account_email = email
        else:
            # Fall back to legacy credentials
            credentials = get_linkedin_credentials()
            email = credentials["email"]
            password = credentials["password"]
            self._current_account_email = email
            
        if not email or not password:
            raise ValueError("LinkedIn credentials not configured and no valid cookies found")

        try:
            # Navigate to login page
            await self._page.goto("https://www.linkedin.com/login")
            await self._random_delay()

            # Fill in credentials
            await self._page.fill(SELECTORS["login_email"], email)
            await self._page.fill(SELECTORS["login_password"], password)

            # Click login button
            await self._page.click(SELECTORS["login_button"])
            await self._page.wait_for_load_state("networkidle")

            # Check if login was successful
            if "feed" in self._page.url or "mynetwork" in self._page.url:
                self._logged_in = True
                return True

            # Check for security verification or error
            if "checkpoint" in self._page.url or "challenge" in self._page.url:
                raise Exception("LinkedIn security checkpoint detected")

            return False

        except Exception as e:
            # Re-raise checkpoint exceptions so they can be handled by caller
            if "checkpoint" in str(e).lower() or "challenge" in str(e).lower():
                raise
            print(f"Login failed: {e}")
            return False

    async def scrape_profile(self, linkedin_url: str, max_retries: Optional[int] = None) -> Optional[dict]:
        """
        Scrape a LinkedIn profile and extract relevant information.
        
        Args:
            linkedin_url: URL of the LinkedIn profile to scrape.
            max_retries: Maximum number of retry attempts. If None, uses MAX_RETRIES from config.
        
        Returns:
            Dictionary containing extracted profile data, or None if failed.
        
        Raises:
            Exception: If security checkpoint is detected (to trigger account rotation).
        """
        if not self._logged_in:
            print("Not logged in, attempting login...")
            if not await self.login():
                raise Exception("Failed to login to LinkedIn")
            print("✅ Login successful")

        retries = max_retries if max_retries is not None else MAX_RETRIES
        
        for attempt in range(retries):
            try:
                await self._random_delay()
                print(f"Navigating to profile: {linkedin_url}")
                await self._page.goto(linkedin_url, wait_until="networkidle")
                
                # Wait for page to fully load
                await asyncio.sleep(2)
                
                # Check for security checkpoint after navigation
                if "checkpoint" in self._page.url or "challenge" in self._page.url:
                    raise Exception("LinkedIn security checkpoint detected")

                # Extract profile data
                profile_data = {
                    "linkedin_url": linkedin_url,
                    "scraped_at": datetime.utcnow().isoformat(),
                    "account_email": self._current_account_email,
                }

                # Extract basic info
                profile_data.update(await self._extract_basic_info())

                # Extract experience
                profile_data["job_history"] = await self._extract_experience()

                # Extract education
                profile_data["education_history"] = await self._extract_education()

                # Extract contact info if available
                profile_data.update(await self._extract_contact_info())

                return profile_data

            except Exception as e:
                # Re-raise checkpoint exceptions immediately (don't retry)
                if "checkpoint" in str(e).lower() or "challenge" in str(e).lower():
                    raise
                    
                print(f"Attempt {attempt + 1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    await self._random_delay()
                    continue
                else:
                    # All retries exhausted
                    return None

        return None

    async def _extract_basic_info(self) -> dict:
        """Extract basic profile information."""
        data = {}

        try:
            # Name
            name_element = await self._page.query_selector(SELECTORS["profile_name"])
            if name_element:
                data["name"] = await name_element.inner_text()

            # Headline/Current position
            headline_element = await self._page.query_selector(SELECTORS["profile_headline"])
            if headline_element:
                data["headline"] = await headline_element.inner_text()

            # Location
            location_selector = 'span.text-body-small.inline.t-black--light.break-words'
            location_element = await self._page.query_selector(location_selector)
            if location_element:
                data["location"] = await location_element.inner_text()

            # Extract current company from headline
            if "headline" in data:
                headline = data["headline"]
                if " at " in headline.lower():
                    parts = headline.split(" at ", 1)
                    if len(parts) == 2:
                        data["current_designation"] = parts[0].strip()
                        data["current_company"] = parts[1].strip()

        except Exception as e:
            print(f"Error extracting basic info: {e}")

        return data

    async def _extract_experience(self) -> list[dict]:
        """Extract work experience history."""
        experiences = []

        try:
            # Navigate to experience section or click "Show all" if needed
            experience_section = await self._page.query_selector(SELECTORS["experience_section"])
            if not experience_section:
                return experiences

            # Get all experience items
            exp_items = await experience_section.query_selector_all('li.artdeco-list__item')

            for item in exp_items[:10]:  # Limit to prevent excessive scraping
                try:
                    exp_data = {}

                    # Company name
                    company_el = await item.query_selector('span.t-14.t-normal')
                    if company_el:
                        exp_data["company_name"] = await company_el.inner_text()

                    # Job title
                    title_el = await item.query_selector('span.t-14.t-bold')
                    if title_el:
                        exp_data["designation"] = await title_el.inner_text()

                    # Duration
                    duration_el = await item.query_selector('span.t-14.t-normal.t-black--light')
                    if duration_el:
                        duration_text = await duration_el.inner_text()
                        exp_data["duration"] = duration_text
                        # Parse dates from duration
                        dates = self._parse_dates(duration_text)
                        exp_data.update(dates)

                    # Location
                    location_el = await item.query_selector('span.t-14.t-normal.t-black--light:nth-child(2)')
                    if location_el:
                        exp_data["location"] = await location_el.inner_text()

                    if exp_data:
                        experiences.append(exp_data)

                except Exception as e:
                    print(f"Error extracting experience item: {e}")
                    continue

        except Exception as e:
            print(f"Error extracting experience: {e}")

        return experiences

    async def _extract_education(self) -> list[dict]:
        """Extract education history."""
        education = []

        try:
            education_section = await self._page.query_selector(SELECTORS["education_section"])
            if not education_section:
                return education

            edu_items = await education_section.query_selector_all('li.artdeco-list__item')

            for item in edu_items[:5]:  # Limit results
                try:
                    edu_data = {}

                    # Institution name
                    inst_el = await item.query_selector('span.t-14.t-bold')
                    if inst_el:
                        edu_data["institution_name"] = await inst_el.inner_text()

                    # Degree
                    degree_el = await item.query_selector('span.t-14.t-normal')
                    if degree_el:
                        degree_text = await degree_el.inner_text()
                        if "," in degree_text:
                            parts = degree_text.split(",", 1)
                            edu_data["degree"] = parts[0].strip()
                            edu_data["field_of_study"] = parts[1].strip()
                        else:
                            edu_data["degree"] = degree_text

                    # Years
                    years_el = await item.query_selector('span.t-14.t-normal.t-black--light')
                    if years_el:
                        years_text = await years_el.inner_text()
                        years = self._parse_years(years_text)
                        edu_data.update(years)

                    if edu_data:
                        education.append(edu_data)

                except Exception as e:
                    print(f"Error extracting education item: {e}")
                    continue

        except Exception as e:
            print(f"Error extracting education: {e}")

        return education

    async def _extract_contact_info(self) -> dict:
        """Extract contact information from profile."""
        data = {}

        try:
            # Click on contact info link
            contact_link = await self._page.query_selector('a[id="top-card-text-details-contact-info"]')
            if contact_link:
                await contact_link.click()
                await asyncio.sleep(2)

                # Extract email if visible
                email_section = await self._page.query_selector('section.ci-email')
                if email_section:
                    email_el = await email_section.query_selector('a')
                    if email_el:
                        email = await email_el.inner_text()
                        data["email"] = email

                # Close modal
                close_button = await self._page.query_selector('button[aria-label="Dismiss"]')
                if close_button:
                    await close_button.click()

        except Exception as e:
            print(f"Error extracting contact info: {e}")

        return data

    def _parse_dates(self, duration_text: str) -> dict:
        """Parse start and end dates from duration text."""
        dates = {}

        try:
            # Pattern: "Jan 2020 - Present" or "Jan 2020 - Dec 2023"
            match = re.search(
                r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|Present)',
                duration_text,
                re.IGNORECASE
            )
            if match:
                start_str = match.group(1)
                end_str = match.group(2)

                try:
                    dates["start_date"] = datetime.strptime(start_str, "%b %Y").isoformat()
                except ValueError:
                    pass

                if end_str.lower() != "present":
                    try:
                        dates["end_date"] = datetime.strptime(end_str, "%b %Y").isoformat()
                    except ValueError:
                        pass
                else:
                    dates["is_current"] = True

        except Exception:
            pass

        return dates

    def _parse_years(self, years_text: str) -> dict:
        """Parse start and end years from education years text."""
        years = {}

        try:
            # Pattern: "2018 - 2022" or "2020"
            match = re.search(r'(\d{4})\s*[-–]\s*(\d{4})', years_text)
            if match:
                years["start_year"] = int(match.group(1))
                years["end_year"] = int(match.group(2))
            else:
                # Single year
                match = re.search(r'(\d{4})', years_text)
                if match:
                    years["end_year"] = int(match.group(1))

        except Exception:
            pass

        return years

    async def download_profile_pdf(self, linkedin_url: str) -> Optional[bytes]:
        """
        Download LinkedIn profile as PDF using the "Save to PDF" button.
        
        LinkedIn's "Save to PDF" triggers a backend API call that returns a real PDF file.
        This method properly captures that download event.
        
        Args:
            linkedin_url: URL of the LinkedIn profile.
        
        Returns:
            PDF content as bytes, or None if failed.
        
        Raises:
            Exception: If security checkpoint is detected.
        """
        if not self._logged_in:
            if not await self.login():
                raise Exception("Failed to login to LinkedIn")

        try:
            await self._random_delay()
            print(f"   Navigating to profile: {linkedin_url}")
            await self._page.goto(linkedin_url, wait_until="networkidle")
            
            # Wait for page to fully load
            await asyncio.sleep(3)
            
            # Check for security checkpoint
            if "checkpoint" in self._page.url or "challenge" in self._page.url:
                raise Exception("LinkedIn security checkpoint detected")

            print("   📄 Attempting to download PDF using 'Save to PDF'...")
            print()
            
            # Step 1: Wait for and click the "More actions" button
            print("   Step 1: Looking for 'More actions' button...")
            
            # Try to find the More button with various selectors
            more_selectors = [
                'button[aria-label="More actions"]',
                'button.artdeco-dropdown__trigger:has-text("More")',
                'button[id*="profile-overflow-action"]',
                'button[aria-label*="More"]',
            ]
            
            more_button = None
            for selector in more_selectors:
                try:
                    await self._page.wait_for_selector(selector, timeout=5000)
                    more_button = await self._page.query_selector(selector)
                    if more_button:
                        print(f"   ✅ Found 'More' button: {selector}")
                        break
                except:
                    continue
            
            if not more_button:
                print("   ⚠️  'More' button not found, falling back to page PDF...")
                pdf_bytes = await self._page.pdf(
                    format="A4",
                    print_background=True,
                    margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
                )
                return pdf_bytes
            
            # Click the More button
            print("   Clicking 'More' button...")
            await more_button.click()
            await asyncio.sleep(1.5)
            print("   ✅ 'More' menu opened")
            print()
            
            # Step 2: Set up download listener and click "Save to PDF"
            print("   Step 2: Setting up download listener...")
            
            try:
                # Set up download listener BEFORE clicking "Save to PDF"
                async with self._page.expect_download(timeout=30000) as download_info:
                    print("   Clicking 'Save to PDF'...")
                    
                    # Click "Save to PDF" - try multiple selectors based on actual HTML
                    save_pdf_selectors = [
                        'div[aria-label="Save to PDF"][role="button"]',
                        'div[aria-label="Save to PDF"]',
                        '[aria-label="Save to PDF"]',
                        'text=Save to PDF',
                    ]
                    
                    clicked = False
                    for selector in save_pdf_selectors:
                        try:
                            element = await self._page.query_selector(selector)
                            if element:
                                await element.click()
                                clicked = True
                                print(f"   ✅ Clicked 'Save to PDF' with: {selector}")
                                break
                        except:
                            continue
                    
                    if not clicked:
                        raise Exception("Could not click 'Save to PDF'")
                
                # Wait for the download to complete
                print("   Waiting for download...")
                download = await download_info.value
                
                print(f"   ✅ Download started: {download.suggested_filename}")
                
                # Get the download path
                download_path = await download.path()
                
                if not download_path:
                    raise Exception("Download path is None")
                
                print(f"   ✅ Download completed: {download_path}")
                
                # Read the downloaded PDF file
                with open(download_path, 'rb') as f:
                    pdf_bytes = f.read()
                
                print(f"   ✅ PDF captured from LinkedIn download ({len(pdf_bytes):,} bytes)")
                print()
                return pdf_bytes
                
            except Exception as download_error:
                print(f"   ⚠️  Download capture failed: {download_error}")
                print("   Falling back to page PDF generation...")
                pdf_bytes = await self._page.pdf(
                    format="A4",
                    print_background=True,
                    margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
                )
                print(f"   ✅ PDF generated using fallback ({len(pdf_bytes):,} bytes)")
                return pdf_bytes

        except Exception as e:
            # Re-raise checkpoint exceptions
            if "checkpoint" in str(e).lower() or "challenge" in str(e).lower():
                raise
            print(f"   ❌ Error downloading PDF: {e}")
            print("   Falling back to simple PDF generation...")
            try:
                pdf_bytes = await self._page.pdf(
                    format="A4",
                    print_background=True,
                    margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
                )
                print(f"   ✅ PDF generated using fallback ({len(pdf_bytes):,} bytes)")
                return pdf_bytes
            except Exception as fallback_error:
                print(f"   ❌ Fallback also failed: {fallback_error}")
                return None
    
    def get_current_account_email(self) -> Optional[str]:
        """
        Get the email of the currently logged-in account.
        
        Returns:
            Email address of current account, or None if not logged in.
        """
        return self._current_account_email


async def scrape_linkedin_profile(linkedin_url: str) -> Optional[dict]:
    """
    Convenience function to scrape a single LinkedIn profile.
    
    Args:
        linkedin_url: URL of the LinkedIn profile.
    
    Returns:
        Dictionary containing profile data, or None if failed.
    """
    async with LinkedInScraper() as scraper:
        return await scraper.scrape_profile(linkedin_url)


async def scrape_multiple_profiles(linkedin_urls: list[str]) -> list[dict]:
    """
    Scrape multiple LinkedIn profiles.
    
    Args:
        linkedin_urls: List of LinkedIn profile URLs.
    
    Returns:
        List of dictionaries containing profile data.
    """
    results = []

    async with LinkedInScraper() as scraper:
        for url in linkedin_urls:
            profile_data = await scraper.scrape_profile(url)
            if profile_data:
                results.append(profile_data)

    return results
