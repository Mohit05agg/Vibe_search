"""
Instagram scraper using Playwright.
Note: Instagram has strict anti-bot measures. This scraper uses basic techniques.
For production, consider using Instagram API or specialized tools.
"""

import re
import time
import json
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
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu'
            ]
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
        Optimized to extract from profile grid view first, then individual posts if needed.
        
        Args:
            username: Instagram username (without @)
            limit: Maximum number of images to scrape
            
        Returns:
            List of scraped image data
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use context manager.")
        
        profile_url = f"https://www.instagram.com/{username}/"
        
        # Check if browser is still open
        if not self.browser or not self.browser.is_connected():
            raise RuntimeError("Browser connection lost. Please restart scraper.")
        
        page = None
        scraped_images = []
        
        try:
            page = self.browser.new_page()
            
            # Set realistic viewport and user agent
            page.set_viewport_size({"width": 1920, "height": 1080})
            user_agent = self.get_random_user_agent()
            page.set_extra_http_headers({
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            print(f"Loading Instagram profile: {profile_url}")
            
            # Navigate with longer timeout and wait for content
            try:
                page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"⚠ Navigation error for @{username}: {e}")
                return scraped_images
            
            # Wait for page to load
            self.random_delay()
            
            # Check for login prompt or blocked access
            try:
                login_prompt = page.query_selector('input[name="username"]')
                page_text = page.inner_text('body').lower()
                blocked = 'sorry' in page_text or 'blocked' in page_text or 'log in' in page_text
                
                if login_prompt or blocked:
                    print(f"⚠ Access restricted for @{username} (login required or blocked). Skipping...")
                    return scraped_images
            except:
                pass  # Continue even if check fails
            
            # Method 1: Try to extract from profile grid view (faster, less navigation)
            print("Attempting to extract from profile grid...")
            grid_images = self._extract_from_grid(page, username, limit)
            scraped_images.extend(grid_images)
            
            # Method 2: If we need more images, try extracting from individual posts
            if len(scraped_images) < limit:
                print(f"Extracted {len(scraped_images)} from grid, trying individual posts...")
                post_images = self._extract_from_posts(page, username, limit - len(scraped_images))
                scraped_images.extend(post_images)
            
            # Method 3: Try extracting from embedded JSON data
            if len(scraped_images) < limit:
                print("Trying to extract from embedded JSON data...")
                json_images = self._extract_from_json(page, username, limit - len(scraped_images))
                scraped_images.extend(json_images)
            
            print(f"Scraped {len(scraped_images)} images from Instagram profile @{username}")
            
        except Exception as e:
            print(f"Error scraping Instagram profile @{username}: {e}")
            print("Note: Instagram has strict anti-bot measures.")
        finally:
            if page:
                try:
                    page.close()
                except:
                    pass  # Ignore errors when closing page
        
        return scraped_images
    
    def _extract_from_grid(self, page: Page, username: str, limit: int) -> List[Dict]:
        """Extract images from profile grid view."""
        images = []
        
        try:
            # Scroll to load more posts
            for _ in range(3):
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                self.random_delay()
            
            # Try multiple selectors for Instagram's grid
            selectors = [
                'article img',
                'img[style*="object-fit"]',
                'img[alt*="photo"]',
                'a[href*="/p/"] img',
                'div[role="button"] img'
            ]
            
            img_elements = []
            for selector in selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    img_elements = elements
                    break
            
            seen_urls = set()
            for img_elem in img_elements[:limit * 2]:  # Get more to account for duplicates
                if len(images) >= limit:
                    break
                
                try:
                    image_url = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                    if not image_url or image_url in seen_urls:
                        continue
                    
                    # Filter out small/icon images
                    if 's150x150' in image_url or 's50x50' in image_url:
                        continue
                    
                    seen_urls.add(image_url)
                    
                    # Try to get post link
                    post_link = None
                    parent = img_elem.evaluate_handle("el => el.closest('a[href*=\"/p/\"]')")
                    if parent:
                        href = parent.get_attribute('href') if hasattr(parent, 'get_attribute') else None
                        if href:
                            post_link = f"https://www.instagram.com{href}" if not href.startswith('http') else href
                    
                    # Get alt text for caption
                    alt_text = img_elem.get_attribute('alt') or ''
                    
                    image_data = {
                        'source': 'instagram',
                        'source_url': post_link or f"https://www.instagram.com/{username}/",
                        'image_url': image_url,
                        'caption': alt_text if alt_text else None,
                        'hashtags': self.extract_hashtags(alt_text),
                        'engagement_count': 0,
                        'username': username,
                        'board_name': None
                    }
                    
                    if self.save_scraped_image(**image_data):
                        images.append(image_data)
                        print(f"Scraped {len(images)}/{limit} images from grid...")
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"Error extracting from grid: {e}")
        
        return images
    
    def _extract_from_posts(self, page: Page, username: str, limit: int) -> List[Dict]:
        """Extract images by visiting individual posts."""
        images = []
        
        try:
            # Find post links
            post_links = page.query_selector_all('a[href*="/p/"]')
            post_urls = []
            
            for link in post_links[:limit]:
                href = link.get_attribute('href')
                if href:
                    if not href.startswith('http'):
                        href = f"https://www.instagram.com{href}"
                    post_urls.append(href)
            
            for post_url in post_urls[:limit]:
                if len(images) >= limit:
                    break
                
                try:
                    page.goto(post_url, wait_until="domcontentloaded", timeout=30000)
                    self.random_delay()
                    
                    # Get main image
                    img_selectors = [
                        'article img[style*="object-fit"]',
                        'article img',
                        'img[alt*="photo"]'
                    ]
                    
                    image_url = None
                    for selector in img_selectors:
                        img_elem = page.query_selector(selector)
                        if img_elem:
                            image_url = img_elem.get_attribute('src')
                            if image_url and 's150x150' not in image_url:
                                break
                    
                    if not image_url:
                        continue
                    
                    # Get caption
                    caption = ''
                    caption_selectors = [
                        'article span',
                        'h1 + span',
                        '[data-testid="post-caption"]'
                    ]
                    
                    for selector in caption_selectors:
                        elem = page.query_selector(selector)
                        if elem:
                            caption = elem.inner_text()
                            if caption:
                                break
                    
                    image_data = {
                        'source': 'instagram',
                        'source_url': post_url,
                        'image_url': image_url,
                        'caption': caption if caption else None,
                        'hashtags': self.extract_hashtags(caption),
                        'engagement_count': 0,
                        'username': username,
                        'board_name': None
                    }
                    
                    if self.save_scraped_image(**image_data):
                        images.append(image_data)
                        print(f"Scraped {len(images)}/{limit} images from posts...")
                    
                    self.random_delay()
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error extracting from posts: {e}")
        
        return images
    
    def _extract_from_json(self, page: Page, username: str, limit: int) -> List[Dict]:
        """Extract images from embedded JSON data in page source."""
        images = []
        
        try:
            # Get page content
            content = page.content()
            
            # Look for JSON data embedded in script tags
            
            # Try to find window._sharedData or similar
            json_match = re.search(r'window\._sharedData\s*=\s*({.+?});', content)
            if not json_match:
                json_match = re.search(r'<script type="application/json"[^>]*>(.+?)</script>', content, re.DOTALL)
            
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    # Navigate through JSON structure to find posts
                    # This structure varies, so we'll try common paths
                    posts = []
                    if 'entry_data' in data:
                        profile_data = data.get('entry_data', {}).get('ProfilePage', [])
                        if profile_data:
                            user = profile_data[0].get('graphql', {}).get('user', {})
                            posts = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
                    
                    for post in posts[:limit]:
                        if len(images) >= limit:
                            break
                        
                        node = post.get('node', {})
                        image_url = node.get('display_url') or node.get('thumbnail_src')
                        if not image_url:
                            continue
                        
                        shortcode = node.get('shortcode', '')
                        post_url = f"https://www.instagram.com/p/{shortcode}/" if shortcode else f"https://www.instagram.com/{username}/"
                        
                        caption = ''
                        caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
                        if caption_edges:
                            caption = caption_edges[0].get('node', {}).get('text', '')
                        
                        image_data = {
                            'source': 'instagram',
                            'source_url': post_url,
                            'image_url': image_url,
                            'caption': caption if caption else None,
                            'hashtags': self.extract_hashtags(caption),
                            'engagement_count': node.get('edge_liked_by', {}).get('count', 0),
                            'username': username,
                            'board_name': None
                        }
                        
                        if self.save_scraped_image(**image_data):
                            images.append(image_data)
                            print(f"Scraped {len(images)}/{limit} images from JSON...")
                            
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"Error extracting from JSON: {e}")
        
        return images
    
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
        Scrape from Instagram target (username or URL).
        
        Args:
            target: Instagram username (with or without @) or full URL
            limit: Maximum number of images to scrape
        """
        # Extract username from URL if full URL is provided
        if 'instagram.com' in target:
            # Extract username from URL like https://www.instagram.com/username/
            match = re.search(r'instagram\.com/([^/]+)', target)
            if match:
                username = match.group(1).rstrip('/')
            else:
                username = target.lstrip('@')
        else:
            username = target.lstrip('@')
        
        return self.scrape_profile(username, limit)

