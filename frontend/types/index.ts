export interface Product {
  id: number;
  product_id: string;
  title: string;
  category?: string;
  sub_category?: string;
  brand_name?: string;
  featured_image?: string;
  lowest_price?: number;
  pdp_url?: string;
  similarity_score?: number;
}

export interface SearchResponse {
  products: Product[];
  total: number;
  query_time_ms: number;
}

export interface ScrapedImage {
  id: number;
  source: string;
  source_url: string;
  image_url: string;
  caption?: string;
  hashtags?: string[];
  engagement_count: number;
  username?: string;
  board_name?: string;
}

