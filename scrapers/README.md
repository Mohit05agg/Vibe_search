# Scrapers Module

Scrapers for collecting fashion images from Pinterest and Instagram.

## Features

- **Pinterest Scraper**: Scrapes images from Pinterest boards
- **Instagram Scraper**: Scrapes images from Instagram profiles (note: Instagram has strict anti-bot measures)
- **Error Handling**: Retry logic and error recovery
- **Rate Limiting**: Configurable delays between requests
- **User Agent Rotation**: Random user agents to avoid detection
- **Database Integration**: Automatically saves scraped data to PostgreSQL

## Usage

### Basic Usage

```bash
# Scrape all targets (Pinterest and Instagram)
python scrapers/run_scrapers.py

# Scrape only Pinterest
python scrapers/run_scrapers.py --source pinterest

# Scrape only Instagram
python scrapers/run_scrapers.py --source instagram

# Custom targets
python scrapers/run_scrapers.py --pinterest-target "https://www.pinterest.com/board/url" --limit 50
```

### Programmatic Usage

```python
from scrapers.pinterest_scraper import PinterestScraper

# Scrape Pinterest board
with PinterestScraper(headless=True) as scraper:
    images = scraper.scrape("https://www.pinterest.com/minimalstreetstyle/", limit=50)
    print(f"Scraped {len(images)} images")
```

## Important Notes

### Instagram Limitations

Instagram has very strict anti-bot measures:
- May require login for some profiles
- Rate limiting is aggressive
- May block requests from automated browsers
- Consider using Instagram API for production use

### Pinterest

- Generally more permissive than Instagram
- Public boards can be scraped without login
- Rate limiting is still recommended

## Configuration

Set environment variables for database connection:
- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME` (default: vibe_search)
- `DB_USER` (default: postgres)
- `POSTGRES_PASSWORD` (default: postgres)

## Target Boards/Pages

Default targets from project requirements:
- Pinterest: minimalstreetstyle, outfitgrid
- Instagram: @minimalstreetstyle, @outfitgrid

## Output

Scraped images are saved to the `scraped_images` table with:
- Source (pinterest/instagram)
- Image URL
- Caption/description
- Hashtags
- Engagement metrics
- Username/board name
- Timestamp

