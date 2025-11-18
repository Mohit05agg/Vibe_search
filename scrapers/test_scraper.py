"""
Test script for scrapers.
Tests with a small limit to verify functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.pinterest_scraper import PinterestScraper
from scrapers.instagram_scraper import InstagramScraper


def test_pinterest():
    """Test Pinterest scraper with a small limit."""
    print("=" * 60)
    print("Testing Pinterest Scraper")
    print("=" * 60)
    
    # Test with a public Pinterest board
    test_url = "https://www.pinterest.com/minimalstreetstyle/"
    
    try:
        with PinterestScraper(headless=True) as scraper:
            print(f"Scraping: {test_url}")
            print("Limit: 5 images (for testing)")
            images = scraper.scrape(test_url, limit=5)
            
            print(f"\n✓ Successfully scraped {len(images)} images")
            
            if images:
                print("\nSample scraped data:")
                for i, img in enumerate(images[:2], 1):
                    print(f"\n  Image {i}:")
                    print(f"    URL: {img['image_url'][:80]}...")
                    print(f"    Caption: {img['caption'][:60] if img['caption'] else 'None'}...")
                    print(f"    Hashtags: {img['hashtags']}")
                    print(f"    Engagement: {img['engagement_count']}")
            
            return len(images) > 0
            
    except Exception as e:
        print(f"\n✗ Error testing Pinterest scraper: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_instagram():
    """Test Instagram scraper with a small limit."""
    print("\n" + "=" * 60)
    print("Testing Instagram Scraper")
    print("=" * 60)
    print("Note: Instagram has strict anti-bot measures.")
    print("This test may fail if Instagram blocks the request.")
    print("=" * 60)
    
    test_username = "minimalstreetstyle"
    
    try:
        with InstagramScraper(headless=True) as scraper:
            print(f"Scraping: @{test_username}")
            print("Limit: 3 images (for testing)")
            images = scraper.scrape(test_username, limit=3)
            
            print(f"\n✓ Successfully scraped {len(images)} images")
            
            if images:
                print("\nSample scraped data:")
                for i, img in enumerate(images[:2], 1):
                    print(f"\n  Image {i}:")
                    print(f"    URL: {img['image_url'][:80]}...")
                    print(f"    Caption: {img['caption'][:60] if img['caption'] else 'None'}...")
                    print(f"    Hashtags: {img['hashtags']}")
                    print(f"    Engagement: {img['engagement_count']}")
            
            return len(images) > 0
            
    except Exception as e:
        print(f"\n✗ Error testing Instagram scraper: {e}")
        print("This is expected - Instagram often blocks automated access.")
        return False


def check_database():
    """Check if scraped images are in database."""
    import os
    import psycopg2
    
    print("\n" + "=" * 60)
    print("Checking Database")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "vibe_search"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres")
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                source,
                COUNT(*) as count
            FROM scraped_images
            GROUP BY source
        """)
        
        results = cursor.fetchall()
        
        if results:
            print("\nScraped images in database:")
            for source, count in results:
                print(f"  {source}: {count} images")
        else:
            print("\nNo scraped images found in database yet.")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error checking database: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Scraper Test Suite")
    print("=" * 60)
    
    # Test Pinterest (more reliable)
    pinterest_success = test_pinterest()
    
    # Test Instagram (may fail due to anti-bot measures)
    instagram_success = test_instagram()
    
    # Check database
    check_database()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Pinterest: {'✓ PASS' if pinterest_success else '✗ FAIL'}")
    print(f"Instagram: {'✓ PASS' if instagram_success else '✗ FAIL (expected)'}")
    print("=" * 60)

