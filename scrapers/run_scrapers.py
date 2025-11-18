"""
Main script to run scrapers for Pinterest and Instagram.
"""

import argparse
from scrapers.pinterest_scraper import PinterestScraper
from scrapers.instagram_scraper import InstagramScraper


# Target boards/pages from project requirements
PINTEREST_TARGETS = [
    "https://www.pinterest.com/search/pins/?q=minimal%20streetwear",
    "https://www.pinterest.com/search/pins/?q=men%27s%20streetwear%20outfit%20ideas",
    "https://www.pinterest.com/search/pins/?q=streetwear%20outfit%20ideas",
    "https://www.pinterest.com/search/pins/?q=streetwear%20fashion%20instagram",
    "https://www.pinterest.com/search/pins/?q=luxury%20fashion",
    "https://www.pinterest.com/search/pins/?q=luxury%20classy%20outfits",
    "https://www.pinterest.com/search/pins/?q=luxury%20streetwear%20brands",
]

INSTAGRAM_TARGETS = [
    "minimalstreetstyle",
    "outfitgrid",
    "outfitpage",
    "mensfashionpost",
    "stadiumgoods",
    "flightclub",
    "hodinkee",
    "wristcheck",
    "purseblog",
    "sunglasshut",
    "rayban",
    "prada",
    "cartier",
    "thesolesupplier",
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
            print(f"\nScraping Instagram: @{target}")
            try:
                images = scraper.scrape(target, limit=limit_per_target)
                total_scraped += len(images)
                print(f"✓ Scraped {len(images)} images from @{target}")
            except Exception as e:
                print(f"✗ Error scraping @{target}: {e}")
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

