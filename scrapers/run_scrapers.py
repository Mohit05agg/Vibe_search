"""
Main script to run scrapers for Pinterest and Instagram.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import re
from scrapers.pinterest_scraper import PinterestScraper
from scrapers.instagram_scraper import InstagramScraper


# Target boards/pages from project requirements
# Note: These are board names. To use specific boards, replace with full board URLs:
# Format: https://www.pinterest.com/username/board-name/
# Or use search URLs (current format) which work with the scraper

PINTEREST_TARGETS = [
    # Option 1: Use search URLs (works without specific board URLs)
    "https://www.pinterest.com/search/pins/?q=minimal%20streetwear",
    "https://www.pinterest.com/search/pins/?q=men%27s%20streetwear%20outfit%20ideas",
    "https://www.pinterest.com/search/pins/?q=streetwear%20outfit%20ideas",
    "https://www.pinterest.com/search/pins/?q=streetwear%20fashion%20instagram",
    "https://www.pinterest.com/search/pins/?q=luxury%20fashion",
    "https://www.pinterest.com/search/pins/?q=luxury%20classy%20outfits",
    "https://www.pinterest.com/search/pins/?q=luxury%20streetwear%20brands",
    
    # Option 2: Use specific board URLs (replace with actual URLs when available)
    # Example format (uncomment and replace with actual URLs):
    # "https://www.pinterest.com/username/minimal-streetwear/",
    # "https://www.pinterest.com/username/mens-streetwear-outfit-ideas/",
    # "https://www.pinterest.com/username/streetwear-outfit-ideas/",
    # "https://www.pinterest.com/username/streetwear-fashion-instagram/",
    # "https://www.pinterest.com/username/luxury-fashion/",
    # "https://www.pinterest.com/username/luxury-classy-outfits/",
    # "https://www.pinterest.com/username/luxury-streetwear-brands/",
]

INSTAGRAM_TARGETS = [
    # Instagram profile URLs
    "https://www.instagram.com/minimalstreetstyle/",
    "https://www.instagram.com/outfitgrid/",
    "https://www.instagram.com/outfitpage/",
    "https://www.instagram.com/mensfashionpost/",
    "https://www.instagram.com/hodinkee/",
    "https://www.instagram.com/wristcheck/",
    "https://www.instagram.com/purseblog/",
    "https://www.instagram.com/rayban/",
    "https://www.instagram.com/prada/",
    "https://www.instagram.com/thesolesupplier/",
    
    # Note: You can also use just usernames (without URL) - the scraper handles both
    # "stadiumgoods",
    # "flightclub",
    # "sunglasshut",
    # "cartier",
]


def scrape_pinterest(targets: list, limit_per_target: int = 25):
    """Scrape Pinterest boards."""
    print("=" * 60)
    print("Starting Pinterest Scraping")
    print("=" * 60)
    
    total_scraped = 0
    
    with PinterestScraper(headless=True) as scraper:
        for target in targets:
            print(f"\nScraping Pinterest: {target}")
            try:
                images = scraper.scrape(target, limit=limit_per_target)
                total_scraped += len(images)
                print(f"✓ Scraped {len(images)} images from {target}")
            except Exception as e:
                print(f"✗ Error scraping {target}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Pinterest scraping complete: {total_scraped} total images")
    print(f"{'='*60}\n")
    
    return total_scraped


def scrape_instagram(targets: list, limit_per_target: int = 25):
    """Scrape Instagram profiles."""
    print("=" * 60)
    print("Starting Instagram Scraping")
    print("=" * 60)
    
    total_scraped = 0
    
    with InstagramScraper(headless=True) as scraper:
        for target in targets:
            # Extract username for display
            if 'instagram.com' in target:
                match = re.search(r'instagram\.com/([^/]+)', target)
                display_name = f"@{match.group(1)}" if match else target
            else:
                display_name = f"@{target.lstrip('@')}"
            
            print(f"\nScraping Instagram: {display_name} ({target})")
            try:
                images = scraper.scrape(target, limit=limit_per_target)
                total_scraped += len(images)
                print(f"✓ Scraped {len(images)} images from {display_name}")
            except Exception as e:
                print(f"✗ Error scraping {display_name}: {e}")
                print("Note: Instagram has strict anti-bot measures.")
    
    print(f"\n{'='*60}")
    print(f"Instagram scraping complete: {total_scraped} total images")
    print(f"{'='*60}\n")
    
    return total_scraped


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Scrape Pinterest and Instagram")
    parser.add_argument(
        '--source',
        choices=['pinterest', 'instagram', 'all'],
        default='all',
        help='Source to scrape'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=25,
        help='Number of images per target (default: 25)'
    )
    parser.add_argument(
        '--pinterest-target',
        action='append',
        help='Pinterest board URL or username'
    )
    parser.add_argument(
        '--instagram-target',
        action='append',
        help='Instagram username'
    )
    
    args = parser.parse_args()
    
    pinterest_targets = args.pinterest_target or PINTEREST_TARGETS
    instagram_targets = args.instagram_target or INSTAGRAM_TARGETS
    
    total = 0
    
    if args.source in ['pinterest', 'all']:
        total += scrape_pinterest(pinterest_targets, args.limit)
    
    if args.source in ['instagram', 'all']:
        total += scrape_instagram(instagram_targets, args.limit)
    
    print(f"\n{'='*60}")
    print(f"Total images scraped: {total}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

