"""
Base scraper class with common functionality.
"""

import time
import random
import os
from typing import Optional, Dict, List
from abc import ABC, abstractmethod
from fake_useragent import UserAgent
import psycopg2


class BaseScraper(ABC):
    """Base class for scrapers with common functionality."""
    
    def __init__(
        self,
        min_delay: float = 2.0,
        max_delay: float = 5.0,
        max_retries: int = 3,
        db_connection: Optional[psycopg2.extensions.connection] = None
    ):
        """
        Initialize base scraper.
        
        Args:
            min_delay: Minimum delay between requests (seconds)
            max_delay: Maximum delay between requests (seconds)
            max_retries: Maximum number of retries for failed requests
            db_connection: Database connection (optional)
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.ua = UserAgent()
        self.db_conn = db_connection
        
    def get_random_user_agent(self) -> str:
        """Get a random user agent."""
        return self.ua.random
    
    def random_delay(self):
        """Add random delay between requests."""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
    
    def get_db_connection(self):
        """Get or create database connection."""
        if self.db_conn is None or self.db_conn.closed:
            self.db_conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                database=os.getenv("DB_NAME", "vibe_search"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres")
            )
        return self.db_conn
    
    def save_scraped_image(
        self,
        source: str,
        source_url: str,
        image_url: str,
        caption: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        engagement_count: int = 0,
        username: Optional[str] = None,
        board_name: Optional[str] = None
    ) -> bool:
        """
        Save scraped image to database.
        
        Returns:
            True if saved successfully, False otherwise
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO scraped_images (
                    source, source_url, image_url, caption, hashtags,
                    engagement_count, username, board_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_url) DO UPDATE SET
                    caption = EXCLUDED.caption,
                    hashtags = EXCLUDED.hashtags,
                    engagement_count = EXCLUDED.engagement_count,
                    scraped_at = CURRENT_TIMESTAMP
            """, (
                source, source_url, image_url, caption,
                hashtags, engagement_count, username, board_name
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving image: {e}")
            return False
        finally:
            cursor.close()
    
    @abstractmethod
    def scrape(self, target: str, limit: int = 50) -> List[Dict]:
        """
        Scrape images from target.
        
        Args:
            target: Target URL or username/board name
            limit: Maximum number of images to scrape
            
        Returns:
            List of scraped image data dictionaries
        """
        pass

