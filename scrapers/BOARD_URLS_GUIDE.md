# Pinterest Board URLs Guide

## Current Status

The scraper is currently configured to use **Pinterest search queries** instead of specific board URLs. This works, but if you have the actual board URLs, using them directly is more efficient.

## Board Names You Provided

1. Minimal Streetwear
2. Men's Streetwear Outfit Ideas
3. Streetwear Outfit Ideas
4. Streetwear Fashion Instagram
5. Luxury Fashion (Roxx Inspire)
6. Luxury Classy Outfits
7. Luxury Streetwear Brands

## How to Get Board URLs

### Method 1: Find Board URLs on Pinterest

1. Go to Pinterest.com
2. Search for the board name
3. Click on a board that matches
4. Copy the URL from your browser
5. Format: `https://www.pinterest.com/username/board-name/`

### Method 2: Use Search URLs (Current Method)

The current configuration uses search URLs which work well:
- `https://www.pinterest.com/search/pins/?q=minimal%20streetwear`

This scrapes pins from search results, which includes pins from multiple boards.

## Updating the Scraper

### To Use Specific Board URLs:

1. Find the actual board URLs on Pinterest
2. Edit `scrapers/run_scrapers.py`
3. Replace the search URLs with board URLs:

```python
PINTEREST_TARGETS = [
    "https://www.pinterest.com/username/minimal-streetwear/",
    "https://www.pinterest.com/username/mens-streetwear-outfit-ideas/",
    # ... etc
]
```

### Current Configuration (Search URLs)

The current setup uses search URLs which:
- ✅ Work immediately without finding specific boards
- ✅ Scrape pins from multiple boards matching the search
- ✅ More flexible and comprehensive
- ⚠️ May include some irrelevant results

### Using Board URLs

If you use specific board URLs:
- ✅ More targeted scraping
- ✅ Only pins from that specific board
- ✅ Better organization
- ⚠️ Requires finding the exact board URLs first

## Running the Scraper

The scraper works with both formats:

```bash
# Using current search URLs
python scrapers/run_scrapers.py --source pinterest --limit 25

# Or specify custom board URLs
python scrapers/run_scrapers.py --source pinterest \
    --pinterest-target "https://www.pinterest.com/username/board-name/" \
    --limit 25
```

## Recommendation

**For now:** Keep using search URLs (current setup) - they work well and don't require finding specific board URLs.

**If you want specific boards:** Find the board URLs on Pinterest and update `PINTEREST_TARGETS` in `scrapers/run_scrapers.py`.

