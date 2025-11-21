"""
Base scraper class with common functionality.
"""

import time
import random
import os
import logging
from typing import Optional, Dict, List, Any
from abc import ABC, abstractmethod
import psycopg2
from psycopg2 import pool

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Fallback user agents (in case fake_useragent fails)
FALLBACK_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]

# Global connection pool
_connection_pool: Optional[pool.SimpleConnectionPool] = None


class BaseScraper(ABC):
    """Base class for scrapers with common functionality."""

    EXPECTED_VECTOR_DIM = int(os.getenv("EMBED_DIM", "512"))

    def __init__(
        self,
        min_delay: float = 2.0,
        max_delay: float = 5.0,
        max_retries: int = 3,
        db_connection: Optional[psycopg2.extensions.connection] = None,
        use_connection_pool: bool = True
    ):
        """
        Initialize base scraper.
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.use_connection_pool = use_connection_pool
        self.db_conn = db_connection
        self._ua = None  # Lazy load UserAgent

    def get_random_user_agent(self) -> str:
        """Get a random user agent with fallback."""
        try:
            if self._ua is None:
                try:
                    from fake_useragent import UserAgent  # optional
                    self._ua = UserAgent()
                except Exception:
                    logger.debug("fake_useragent unavailable; using static fallback")
                    self._ua = None

            if self._ua is not None:
                return self._ua.random
        except Exception:
            pass

        # Fallback to static list
        return random.choice(FALLBACK_USER_AGENTS)

    def random_delay(self):
        """Add random delay between requests."""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)

    def get_db_connection(self):
        """Get database connection from pool or create new one."""
        global _connection_pool

        # If explicit connection provided and open, use it
        try:
            if self.db_conn is not None and not getattr(self.db_conn, "closed", False):
                return self.db_conn
        except Exception:
            pass

        # Use connection pool if enabled
        if self.use_connection_pool:
            if _connection_pool is None:
                try:
                    _connection_pool = pool.SimpleConnectionPool(
                        minconn=1,
                        maxconn=int(os.getenv("DB_POOL_MAX", "10")),
                        host=os.getenv("DB_HOST", "localhost"),
                        port=int(os.getenv("DB_PORT", "5432")),
                        database=os.getenv("DB_NAME", "vibe_search"),
                        user=os.getenv("DB_USER", "postgres"),
                        password=os.getenv("POSTGRES_PASSWORD", "postgres")
                    )
                    logger.info("Database connection pool created")
                except Exception as e:
                    logger.error(f"Failed to create connection pool: {e}")
                    self.use_connection_pool = False

            if _connection_pool is not None:
                try:
                    conn = _connection_pool.getconn()
                    return conn
                except Exception as e:
                    logger.warning(f"Failed to get connection from pool: {e}")
                    self.use_connection_pool = False

        # Fallback to direct connection
        try:
            return psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                database=os.getenv("DB_NAME", "vibe_search"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres")
            )
        except Exception as e:
            logger.error(f"Failed to open DB connection: {e}")
            raise

    def return_db_connection(self, conn: Optional[psycopg2.extensions.connection]):
        """Return connection to pool if using pooling, otherwise close if created here."""
        global _connection_pool

        if conn is None:
            return

        try:
            if self.use_connection_pool and _connection_pool is not None:
                try:
                    # put conn back to pool (if it's still open)
                    _connection_pool.putconn(conn)
                except Exception as e:
                    logger.warning(f"Error returning connection to pool: {e}")
                    try:
                        conn.close()
                    except Exception:
                        pass
            else:
                # if this connection was not the global persistent db_conn, close it
                if conn != self.db_conn:
                    try:
                        conn.close()
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"Error while returning DB connection: {e}")

    def _validate_embedding(self, embedding: Optional[List[float]]) -> Optional[List[float]]:
        """Validate embedding length and numeric types."""
        if embedding is None:
            return None
        try:
            emb = [float(x) for x in embedding]
            if len(emb) != self.EXPECTED_VECTOR_DIM:
                logger.warning(f"Embedding dim mismatch: {len(emb)} != {self.EXPECTED_VECTOR_DIM}")
                return None
            return emb
        except Exception:
            logger.exception("Invalid embedding format")
            return None

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
        Uses UNIQUE (source, image_url) for dedupe.
        """
        conn = None
        cursor = None
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO scraped_images (
                    source, source_url, image_url, caption, hashtags,
                    engagement_count, username, board_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source, image_url) DO UPDATE SET
                    caption = EXCLUDED.caption,
                    hashtags = EXCLUDED.hashtags,
                    engagement_count = EXCLUDED.engagement_count,
                    source_url = EXCLUDED.source_url,
                    scraped_at = CURRENT_TIMESTAMP
            """, (
                source, source_url, image_url, caption,
                hashtags, engagement_count, username, board_name
            ))
            conn.commit()
            logger.debug(f"Saved image: {image_url}")
            return True
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception(f"Error saving image: {e}")
            return False
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            self.return_db_connection(conn)

    def save_scraped_image_enhanced(self, **kwargs) -> bool:
        """
        Save scraped image with enhanced AI-processed data.
        Expects kwargs keys:
          source, source_url, image_url, caption, hashtags, engagement_count,
          username, board_name, embedding, detected_class, bbox, colors, styles,
          brands, local_path, quality_score
        """
        # Provide defaults and validation
        data = {
            "source": None,
            "source_url": None,
            "image_url": None,
            "caption": None,
            "hashtags": None,
            "engagement_count": 0,
            "username": None,
            "board_name": None,
            "embedding": None,
            "detected_class": None,
            "bbox": None,
            "colors": None,
            "styles": None,
            "brands": None,
            "local_path": None,
            "quality_score": None
        }
        data.update(kwargs)

        # Validate embedding
        embedding = self._validate_embedding(data.get("embedding"))
        embedding_str = None
        if embedding is not None:
            # convert to Postgres vector literal (pgvector accepts like '[0.1, 0.2, ...]')
            embedding_str = '[' + ', '.join(str(float(x)) for x in embedding) + ']'

        # JSON for quality_score
        import json
        quality_score_json = json.dumps(data["quality_score"]) if data["quality_score"] is not None else None

        conn = None
        cursor = None
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Prepare values tuple - ensure all 16 values are present
            values = (
                data["source"], 
                data["source_url"], 
                data["image_url"], 
                data["caption"],
                data["hashtags"] if data["hashtags"] else None, 
                data["engagement_count"], 
                data["username"], 
                data["board_name"],
                embedding_str, 
                data["detected_class"], 
                data["bbox"] if data["bbox"] else None, 
                data["colors"] if data["colors"] else None,
                data["styles"] if data["styles"] else None, 
                data["brands"] if data["brands"] else None, 
                data["local_path"], 
                quality_score_json
            )
            
            # Debug: verify we have 16 values
            if len(values) != 16:
                logger.error(f"Value count mismatch: expected 16, got {len(values)}")
                logger.error(f"Values: {values}")
            
            cursor.execute("""
                INSERT INTO scraped_images (
                    source, source_url, image_url, caption, hashtags,
                    engagement_count, username, board_name, image_embedding,
                    detected_class, bbox, extracted_colors, extracted_styles,
                    extracted_brands, local_path, quality_score
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::vector, %s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (source, image_url) DO UPDATE SET
                    caption = EXCLUDED.caption,
                    hashtags = EXCLUDED.hashtags,
                    engagement_count = EXCLUDED.engagement_count,
                    source_url = EXCLUDED.source_url,
                    image_embedding = EXCLUDED.image_embedding,
                    detected_class = EXCLUDED.detected_class,
                    bbox = EXCLUDED.bbox,
                    extracted_colors = EXCLUDED.extracted_colors,
                    extracted_styles = EXCLUDED.extracted_styles,
                    extracted_brands = EXCLUDED.extracted_brands,
                    local_path = EXCLUDED.local_path,
                    quality_score = EXCLUDED.quality_score,
                    scraped_at = CURRENT_TIMESTAMP
            """, values)
            conn.commit()
            logger.debug(f"Saved enhanced image: {data['image_url']} (class: {data['detected_class']})")
            return True
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception(f"Error saving enhanced image: {e}")
            print(f"    DB Error: {str(e)[:100]}")  # Show error for debugging
            return False
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            self.return_db_connection(conn)

    @abstractmethod
    def scrape(self, target: str, limit: int = 50) -> List[Dict]:
        """
        Scrape images from target.
        """
        pass
