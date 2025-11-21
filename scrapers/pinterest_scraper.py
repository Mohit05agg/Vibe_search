"""
Pinterest scraper using Playwright.
Enhanced with AI processing pipeline (object detection, embeddings, quality filtering).
"""

import re
import time
import logging
from typing import List, Dict, Optional
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper

# Add parent directory to path for AI modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

try:
    from ai.processing_pipeline import ImageProcessingPipeline
    AI_AVAILABLE = True
except Exception:
    AI_AVAILABLE = False
    logger.warning("AI processing modules not available. Install dependencies: pip install ultralytics opencv-python nudenet transformers")

class PinterestScraper(BaseScraper):
    """Scraper for Pinterest boards and pins."""

    def __init__(
        self,
        headless: bool = True,
        enable_ai_processing: bool = True,
        download_dir: Optional[str] = None,
        **kwargs
    ):
        # Set default delays if not provided (faster for AI processing)
        if 'min_delay' not in kwargs:
            kwargs['min_delay'] = 1.0
        if 'max_delay' not in kwargs:
            kwargs['max_delay'] = 2.0
        super().__init__(**kwargs)
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.enable_ai_processing = enable_ai_processing and AI_AVAILABLE
        self.processing_pipeline = None

        if self.enable_ai_processing:
            try:
                self.processing_pipeline = ImageProcessingPipeline(
                    download_dir=download_dir,
                    max_workers=1,  # Single worker for faster per-image processing (less overhead)
                    save_local=False  # Disable local saving for speed (images still processed)
                )
            except Exception as e:
                logger.warning(f"Could not initialize AI processing pipeline: {e}")
                self.enable_ai_processing = False

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
            try:
                self.browser.close()
            except Exception:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass

    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        if not text:
            return []
        hashtags = re.findall(r'#(\w+)', text)
        return [tag.lower() for tag in hashtags]

    def _safe_process(self, image_url: str, alt_text: str, pin_url: str):
        """Wrap pipeline processing with retries and defensive returns."""
        if not self.processing_pipeline:
            return None
        for attempt in range(3):
            try:
                result = self.processing_pipeline.process_image(
                    image_url=image_url,
                    caption=alt_text,
                    source='pinterest',
                    source_url=pin_url
                )
                return result
            except Exception as e:
                logger.warning(f"AI pipeline attempt {attempt+1}/3 failed for {image_url}: {e}")
                time.sleep(1.5 * (attempt + 1))
        return None

    def scrape_board(self, board_url: str, limit: int = 50) -> List[Dict]:
        """
        Scrape images from a Pinterest board.
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use context manager.")

        page = self.browser.new_page()
        page.set_extra_http_headers({
            'User-Agent': self.get_random_user_agent(),
            'Accept-Language': 'en-US,en;q=0.9'
        })

        scraped_images = []
        seen_urls = set()

        try:
            logger.info(f"Loading Pinterest board: {board_url}")
            print(f"Loading page: {board_url[:60]}...")
            page.goto(board_url, wait_until="domcontentloaded", timeout=15000)  # Faster timeout
            print("Page loaded, extracting images...")
            self.random_delay()

            scroll_count = 0
            max_scrolls = 20

            while len(scraped_images) < limit and scroll_count < max_scrolls:
                # Robust selector: find images with pinterest domains
                img_elems = page.query_selector_all('img')
                for img_elem in img_elems:
                    if len(scraped_images) >= limit:
                        break
                    try:
                        src = img_elem.get_attribute('src') or img_elem.get_attribute('data-src') or img_elem.get_attribute('srcset')
                        if not src:
                            continue
                        # Prefer full URLs (if srcset present, pick first absolute)
                        if isinstance(src, str) and ' ' in src and 'http' in src:
                            # srcset format, pick first url
                            src = src.split(',')[0].strip().split(' ')[0]

                        image_url = src
                        if not image_url or 'pinimg' not in image_url and 'pinterest' not in image_url:
                            # still allow some non-pinimg sources but skip likely irrelevant ones
                            pass

                        # find ancestor pin link (if possible)
                        ancestor = img_elem
                        pin_url = None
                        for _ in range(3):
                            try:
                                parent = ancestor.evaluate_handle("node => node.parentElement")
                                if not parent:
                                    break
                                href = parent.get_attribute('href') if hasattr(parent, 'get_attribute') else None
                                if href and '/pin/' in href:
                                    pin_url = href if href.startswith('http') else f"https://www.pinterest.com{href}"
                                    break
                                ancestor = parent
                            except Exception:
                                break

                        # fallback pin url
                        pin_url = pin_url or page.url

                        # avoid duplicates
                        if image_url in seen_urls:
                            continue
                        seen_urls.add(image_url)

                        # get alt text
                        alt_text = img_elem.get_attribute('alt') or ''

                        hashtags = self.extract_hashtags(alt_text)

                        # engagement extraction best-effort
                        engagement = 0
                        try:
                            like_elem = img_elem.evaluate_handle("node => node.closest('div').querySelector('[data-test-id=\"pinrep-like-count\"]')")
                            if like_elem:
                                like_text = like_elem.inner_text()
                                engagement = self._parse_engagement(like_text)
                        except Exception:
                            engagement = 0

                        image_data = {
                            'source': 'pinterest',
                            'source_url': pin_url,
                            'image_url': image_url,
                            'caption': alt_text if alt_text else None,
                            'hashtags': hashtags,
                            'engagement_count': engagement,
                            'username': None,
                            'board_name': self._extract_board_name(board_url)
                        }

                        # AI processing
                        current_count = len(scraped_images)
                        if current_count >= limit:
                            break
                            
                        if self.enable_ai_processing:
                            print(f"  Processing image {current_count + 1}/{limit} with AI...", end=" ", flush=True)
                            processed = self._safe_process(image_url, alt_text, pin_url)
                            if processed:
                                print("✓", end=" ", flush=True)
                                # processed is always a dict with well-defined keys
                                # defend against missing keys
                                detections = processed.get('detections') or {}
                                primary = detections.get('primary') if detections else None
                                # Safely extract primary detection fields
                                primary_dict = primary if isinstance(primary, dict) else {}
                                image_data.update({
                                    'detected_class': primary_dict.get('detected_class') if primary_dict else None,
                                    'bbox': primary_dict.get('bbox') if primary_dict else None,
                                    'embedding': processed.get('embedding'),
                                    'colors': processed.get('colors', []),
                                    'styles': processed.get('styles', []),
                                    'brands': processed.get('brands', []),
                                    'local_path': processed.get('local_path'),
                                    'quality_score': processed.get('quality', {})
                                })
                                saved = self.save_scraped_image_enhanced(**image_data)
                                if saved:
                                    scraped_images.append(image_data)
                                    print(f"Saved ({len(scraped_images)}/{limit})")
                                else:
                                    print("✗ Save failed")
                                    # fallback save basic
                                    if self.save_scraped_image(**image_data):
                                        scraped_images.append(image_data)
                                        print(f"Saved basic ({len(scraped_images)}/{limit})")
                            else:
                                print("✗ (processing failed, saving basic)", end=" ", flush=True)
                                # pipeline returned None
                                if self.save_scraped_image(**image_data):
                                    scraped_images.append(image_data)
                                    print(f"Saved ({len(scraped_images)}/{limit})")
                                else:
                                    print("✗ Save failed")
                        else:
                            if self.save_scraped_image(**image_data):
                                scraped_images.append(image_data)

                        self.random_delay()

                    except Exception as e:
                        logger.exception(f"Error scraping img element: {e}")
                        continue

                # scroll more
                if len(scraped_images) < limit:
                    try:
                        page.evaluate("window.scrollBy(0, window.innerHeight)")
                        time.sleep(0.5)
                        self.random_delay()
                    except Exception:
                        # fallback: try full page height
                        try:
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            time.sleep(0.5)
                            self.random_delay()
                        except Exception:
                            pass
                    scroll_count += 1

            logger.info(f"Scraped {len(scraped_images)} images from Pinterest board")
        except Exception as e:
            logger.exception(f"Error scraping Pinterest board: {e}")
        finally:
            try:
                page.close()
            except Exception:
                pass

        return scraped_images

    def _parse_engagement(self, text: str) -> int:
        """Parse engagement count from text (e.g., '1.2K' -> 1200)."""
        if not text:
            return 0
        text = text.strip().upper()
        multipliers = {'K': 1000, 'M': 1000000}
        try:
            for suffix, mult in multipliers.items():
                if suffix in text:
                    num = float(text.replace(suffix, ''))
                    return int(num * mult)
            return int(text.replace(',', ''))
        except Exception:
            return 0

    def _extract_board_name(self, url: str) -> Optional[str]:
        """Extract board name from URL."""
        try:
            match = re.search(r'/board/([^/]+)', url)
            if match:
                return match.group(1).replace('-', ' ').title()
        except Exception:
            pass
        return None

    def scrape(self, target: str, limit: int = 50) -> List[Dict]:
        """
        Scrape from Pinterest target (board URL or username).
        """
        if 'pinterest.com' in target or target.startswith('http'):
            return self.scrape_board(target, limit)
        else:
            board_url = f"https://www.pinterest.com/{target}"
            return self.scrape_board(board_url, limit)
