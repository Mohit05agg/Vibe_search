# Vibe Search Frontend

Next.js 14+ frontend for Vibe Search multimodal fashion search engine.

## Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

Create `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Features

- **Text Search**: Natural language product search
- **Image Search**: Upload images to find similar products
- **Explore Feed**: Browse scraped fashion images from Pinterest/Instagram
- **Click-to-Search**: Click on scraped images to find similar products
- **Product Details**: View detailed product information in modals
- **Match Scores**: See similarity scores for search results

## Development

The frontend runs on `http://localhost:3000` by default.

Make sure the FastAPI backend is running on `http://localhost:8000`.

