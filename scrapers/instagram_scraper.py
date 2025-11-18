"""
Instagram scraper using Playwright.
Note: Instagram has strict anti-bot measures. This scraper uses basic techniques.
For production, consider using Instagram API or specialized tools.
"""

import re
import time
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Browser, Page

from scrapers.base_scraper import BaseScraper


class InstagramScraper(BaseScraper):
    """Scraper for Instagram posts and profiles."""
    
    def __init__(self, headless: bool = True, **kwargs):
        """
        Initialize Instagram scraper.
        
        Args:
            headless: Run browser in headless mode
        """
        super().__init__(min_delay=3.0, max_delay=7.0, **kwargs)  # Longer delays for Instagram
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
    
    def scrape_profile(self, username: str, limit: int = 50) -> List[Dict]:
        """
        Scrape images from an Instagram profile.
        
        Args:
            username: Instagram username (without @)
            limit: Maximum number of images to scrape
            
        Returns:
            List of scraped image data
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use context manager.")
        
        profile_url = f"https://www.instagram.com/{username}/"
        page = self.browser.new_page()
        page.set_extra_http_headers({
            'User-Agent': self.get_random_user_agent()
        })
        
        scraped_images = []
        
        try:
            print(f"Loading Instagram profile: {profile_url}")
            page.goto(profile_url, wait_until="networkidle", timeout=30000)
            self.random_delay()
            
            # Instagram uses dynamic loading, so we'll try to extract from initial page
            # In production, you might need to handle login and more sophisticated scraping
            
            # Try to find post links
            post_links = page.query_selector_all('a[href*="/p/"]')
            
            for i, link in enumerate(post_links[:limit]):
                if len(scraped_images) >= limit:
                    break
                
                try:
                    post_url = link.get_attribute('href')
                    if not post_url or not post_url.startswith('http'):
                        post_url = f"https://www.instagram.com{post_url}"
                    
                    # Navigate to post
                    page.goto(post_url, wait_until="networkidle", timeout=20000)
                    self.random_delay()
                    
                    # Get image
                    img_elem = page.query_selector('img[style*="object-fit"]')
                    if not img_elem:
                        img_elem = page.query_selector('article img')
                    
                    if not img_elem:
                        continue
                    
                    image_url = img_elem.get_attribute('src')
                    if not image_url:
                        continue
                    
                    # Get caption
                    caption_elem = page.query_selector('article span')
                    caption = caption_elem.inner_text() if caption_elem else ''
                    
                    # Extract hashtags
                    hashtags = self.extract_hashtags(caption)
                    
                    # Get engagement (likes and comments)
                    engagement = 0
                    like_elem = page.query_selector('button span')
                    if like_elem:
                        like_text = like_elem.inner_text()
                        engagement = self._parse_engagement(like_text)
                    
                    image_data = {
                        'source': 'instagram',
                        'source_url': post_url,
                        'image_url': image_url,
                        'caption': caption if caption else None,
                        'hashtags': hashtags,
                        'engagement_count': engagement,
                        'username': username,
                        'board_name': None
                    }
                    
                    # Save to database
                    if self.save_scraped_image(**image_data):
                        scraped_images.append(image_data)
                        print(f"Scraped {len(scraped_images)}/{limit} images...")
                    
                    self.random_delay()
                    
                except Exception as e:
                    print(f"Error scraping post: {e}")
                    continue
            
            print(f"Scraped {len(scraped_images)} images from Instagram profile")
            
        except Exception as e:
            print(f"Error scraping Instagram profile: {e}")
            print("Note: Instagram has strict anti-bot measures. Consider using Instagram API.")
        finally:
            page.close()
        
        return scraped_images
    
    def _parse_engagement(self, text: str) -> int:
        """Parse engagement count from text."""
        if not text:
            return 0
        
        text = text.strip().upper().replace(',', '')
        multipliers = {'K': 1000, 'M': 1000000}
        
        for suffix, mult in multipliers.items():
            if suffix in text:
                try:
                    num = float(text.replace(suffix, ''))
                    return int(num * mult)
                except:
                    return 0
        
        try:
            return int(text)
        except:
            return 0
    
    def scrape(self, target: str, limit: int = 50) -> List[Dict]:
        """
        Scrape from Instagram target (username).
        
        Args:
            target: Instagram username (with or without @)
            limit: Maximum number of images to scrape
        """
        username = target.lstrip('@')
        return self.scrape_profile(username, limit)

