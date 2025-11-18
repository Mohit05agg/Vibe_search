"""
Pinterest scraper using Playwright.
"""

import re
import time
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Browser, Page
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper


class PinterestScraper(BaseScraper):
    """Scraper for Pinterest boards and pins."""
    
    def __init__(self, headless: bool = True, **kwargs):
        """
        Initialize Pinterest scraper.
        
        Args:
            headless: Run browser in headless mode
        """
        super().__init__(**kwargs)
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
    
    def __enter__(self):
        """Context manager entry."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        if not text:
            return []
        hashtags = re.findall(r'#(\w+)', text)
        return [tag.lower() for tag in hashtags]
    
    def scrape_board(self, board_url: str, limit: int = 50) -> List[Dict]:
        """
        Scrape images from a Pinterest board.
        
        Args:
            board_url: URL of the Pinterest board
            limit: Maximum number of images to scrape
            
        Returns:
            List of scraped image data
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use context manager.")
        
        page = self.browser.new_page()
        page.set_extra_http_headers({
            'User-Agent': self.get_random_user_agent()
        })
        
        scraped_images = []
        
        try:
            print(f"Loading Pinterest board: {board_url}")
            page.goto(board_url, wait_until="networkidle", timeout=30000)
            self.random_delay()
            
            # Scroll to load more pins
            scroll_count = 0
            max_scrolls = 10
            
            while len(scraped_images) < limit and scroll_count < max_scrolls:
                # Extract pins from current page
                pins = page.query_selector_all('div[data-test-id="pin"]')
                
                for pin in pins:
                    if len(scraped_images) >= limit:
                        break
                    
                    try:
                        # Get pin link
                        pin_link_elem = pin.query_selector('a[href*="/pin/"]')
                        if not pin_link_elem:
                            continue
                        
                        pin_url = pin_link_elem.get_attribute('href')
                        if not pin_url or not pin_url.startswith('http'):
                            pin_url = f"https://www.pinterest.com{pin_url}"
                        
                        # Get image
                        img_elem = pin.query_selector('img')
                        if not img_elem:
                            continue
                        
                        image_url = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                        if not image_url:
                            continue
                        
                        # Get caption/description
                        alt_text = img_elem.get_attribute('alt') or ''
                        
                        # Extract hashtags
                        hashtags = self.extract_hashtags(alt_text)
                        
                        # Get engagement (likes) - approximate
                        engagement = 0
                        like_elem = pin.query_selector('[data-test-id="pinrep-like-count"]')
                        if like_elem:
                            like_text = like_elem.inner_text()
                            engagement = self._parse_engagement(like_text)
                        
                        image_data = {
                            'source': 'pinterest',
                            'source_url': pin_url,
                            'image_url': image_url,
                            'caption': alt_text if alt_text else None,
                            'hashtags': hashtags,
                            'engagement_count': engagement,
                            'username': None,  # Can be extracted from board URL
                            'board_name': self._extract_board_name(board_url)
                        }
                        
                        # Save to database
                        if self.save_scraped_image(**image_data):
                            scraped_images.append(image_data)
                            print(f"Scraped {len(scraped_images)}/{limit} images...")
                        
                        self.random_delay()
                        
                    except Exception as e:
                        print(f"Error scraping pin: {e}")
                        continue
                
                # Scroll down to load more
                if len(scraped_images) < limit:
                    page.evaluate("window.scrollBy(0, window.innerHeight)")
                    self.random_delay()
                    scroll_count += 1
            
            print(f"Scraped {len(scraped_images)} images from Pinterest board")
            
        except Exception as e:
            print(f"Error scraping Pinterest board: {e}")
        finally:
            page.close()
        
        return scraped_images
    
    def _parse_engagement(self, text: str) -> int:
        """Parse engagement count from text (e.g., '1.2K' -> 1200)."""
        if not text:
            return 0
        
        text = text.strip().upper()
        multipliers = {'K': 1000, 'M': 1000000}
        
        for suffix, mult in multipliers.items():
            if suffix in text:
                try:
                    num = float(text.replace(suffix, ''))
                    return int(num * mult)
                except:
                    return 0
        
        try:
            return int(text.replace(',', ''))
        except:
            return 0
    
    def _extract_board_name(self, url: str) -> Optional[str]:
        """Extract board name from URL."""
        match = re.search(r'/board/([^/]+)', url)
        if match:
            return match.group(1).replace('-', ' ').title()
        return None
    
    def scrape(self, target: str, limit: int = 50) -> List[Dict]:
        """
        Scrape from Pinterest target (board URL or username).
        
        Args:
            target: Board URL or username
            limit: Maximum number of images to scrape
        """
        if 'pinterest.com' in target or target.startswith('http'):
            return self.scrape_board(target, limit)
        else:
            # Assume it's a username, construct board URL
            board_url = f"https://www.pinterest.com/{target}"
            return self.scrape_board(board_url, limit)

