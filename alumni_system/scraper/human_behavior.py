"""
Human behavior simulation for LinkedIn scraping.

This module adds randomization to scraping actions to simulate human browsing
patterns and avoid detection as a bot.
"""

import asyncio
import random
from typing import List, Optional

from playwright.async_api import Page


class HumanBehaviorSimulator:
    """
    Simulates human browsing behavior to avoid bot detection.
    
    Features:
    - Random delays between actions
    - Random scroll patterns
    - Random mouse movements
    - Occasional visits to other LinkedIn pages
    """
    
    def __init__(self, min_delay: float = 5.0, max_delay: float = 15.0):
        """
        Initialize the human behavior simulator.
        
        Args:
            min_delay: Minimum delay in seconds between actions.
            max_delay: Maximum delay in seconds between actions.
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
    
    async def random_delay(self, min_sec: Optional[float] = None, max_sec: Optional[float] = None) -> None:
        """
        Add a random delay to simulate human reading/thinking time.
        
        Args:
            min_sec: Minimum delay in seconds. If None, uses instance default.
            max_sec: Maximum delay in seconds. If None, uses instance default.
        """
        min_delay = min_sec if min_sec is not None else self.min_delay
        max_delay = max_sec if max_sec is not None else self.max_delay
        
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    async def random_scroll(self, page: Page) -> None:
        """
        Perform random scrolling on the page to simulate reading.
        
        Args:
            page: Playwright page object.
        """
        try:
            # Get page height
            page_height = await page.evaluate("document.body.scrollHeight")
            
            # Scroll to random positions
            num_scrolls = random.randint(2, 5)
            
            for _ in range(num_scrolls):
                # Random scroll position (0 to 80% of page height)
                scroll_to = random.randint(0, int(page_height * 0.8))
                
                await page.evaluate(f"window.scrollTo(0, {scroll_to})")
                
                # Short delay between scrolls
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Scroll back to top
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(random.uniform(0.3, 0.8))
            
        except Exception as e:
            print(f"Error during random scroll: {e}")
    
    async def random_mouse_movement(self, page: Page) -> None:
        """
        Simulate random mouse movements on the page.
        
        Args:
            page: Playwright page object.
        """
        try:
            # Get viewport size
            viewport = page.viewport_size
            if not viewport:
                return
            
            width = viewport['width']
            height = viewport['height']
            
            # Move mouse to random positions
            num_moves = random.randint(2, 4)
            
            for _ in range(num_moves):
                x = random.randint(100, width - 100)
                y = random.randint(100, height - 100)
                
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
        except Exception as e:
            print(f"Error during random mouse movement: {e}")
    
    async def visit_random_page(self, page: Page) -> None:
        """
        Occasionally visit other LinkedIn pages to avoid predictable patterns.
        
        Visits pages like feed, search, or notifications with low probability.
        
        Args:
            page: Playwright page object.
        """
        try:
            # Only visit random page 20% of the time
            if random.random() > 0.2:
                return
            
            # List of pages to visit
            pages = [
                "https://www.linkedin.com/feed/",
                "https://www.linkedin.com/mynetwork/",
                "https://www.linkedin.com/jobs/",
            ]
            
            random_page = random.choice(pages)
            
            # Visit the page
            await page.goto(random_page)
            await page.wait_for_load_state("networkidle")
            
            # Stay for a short time
            await asyncio.sleep(random.uniform(2, 5))
            
            # Maybe scroll a bit
            if random.random() > 0.5:
                await self.random_scroll(page)
                
        except Exception as e:
            print(f"Error visiting random page: {e}")
    
    async def simulate_reading(self, page: Page) -> None:
        """
        Simulate reading a profile by scrolling and pausing.
        
        Args:
            page: Playwright page object.
        """
        try:
            # Initial delay (reading top of profile)
            await asyncio.sleep(random.uniform(2, 4))
            
            # Scroll down slowly
            await self.random_scroll(page)
            
            # Random mouse movements
            await self.random_mouse_movement(page)
            
            # Final delay
            await asyncio.sleep(random.uniform(1, 3))
            
        except Exception as e:
            print(f"Error simulating reading: {e}")
    
    def randomize_action_sequence(self, actions: List[str]) -> List[str]:
        """
        Randomize the order of non-critical actions.
        
        Some actions must happen in order (e.g., login before scraping),
        but others can be shuffled to appear more human.
        
        Args:
            actions: List of action names.
        
        Returns:
            Shuffled list of actions.
        """
        # Create a copy to avoid modifying original
        shuffled = actions.copy()
        random.shuffle(shuffled)
        return shuffled
