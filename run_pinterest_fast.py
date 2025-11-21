"""
Quick script to run Pinterest scraper with progress output.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.pinterest_scraper import PinterestScraper
from scrapers.run_scrapers import PINTEREST_TARGETS

def main():
    print("=" * 60)
    print("Pinterest Scraper with AI Processing")
    print("=" * 60)
    print("\nNote: AI processing takes 2-5 seconds per image")
    print("This includes: YOLO detection, CLIP embedding, quality filtering\n")
    
    limit = 3  # Small limit for testing
    target = PINTEREST_TARGETS[0]  # Just first target
    
    print(f"Scraping: {target}")
    print(f"Limit: {limit} images")
    print(f"AI Processing: ENABLED\n")
    print("Starting...\n")
    
    with PinterestScraper(headless=True, enable_ai_processing=True) as scraper:
        try:
            images = scraper.scrape(target, limit=limit)
            print(f"\n{'='*60}")
            print(f"✓ Completed! Scraped {len(images)} images")
            print(f"{'='*60}\n")
            
            # Show summary
            if images:
                print("Sample results:")
                for i, img in enumerate(images[:3], 1):
                    print(f"\n{i}. {img.get('image_url', 'N/A')[:60]}...")
                    if img.get('detected_class'):
                        print(f"   Class: {img['detected_class']}")
                    if img.get('colors'):
                        print(f"   Colors: {img['colors']}")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

