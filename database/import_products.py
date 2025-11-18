"""
Import products from CSV into PostgreSQL database.
Handles data type conversion and ensures data integrity.
"""

import csv
import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql


def parse_bool(value: str) -> Optional[bool]:
    """Convert string boolean to Python boolean."""
    if not value or value.strip() == '':
        return None
    return value.strip().lower() in ('true', '1', 'yes', 't')


def parse_decimal(value: str) -> Optional[Decimal]:
    """Convert string to Decimal, handling empty strings."""
    if not value or value.strip() == '':
        return None
    try:
        return Decimal(value.strip())
    except (ValueError, TypeError):
        return None


def parse_int(value: str) -> Optional[int]:
    """Convert string to integer, handling empty strings."""
    if not value or value.strip() == '':
        return None
    try:
        return int(value.strip())
    except (ValueError, TypeError):
        return None


def parse_date(value: str) -> Optional[datetime]:
    """Parse date string to datetime."""
    if not value or value.strip() == '':
        return None
    try:
        # Try common date formats
        for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y']:
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
        return None
    except (ValueError, TypeError):
        return None


def get_db_connection():
    """Create database connection to WSL PostgreSQL."""
    # Connect to PostgreSQL running in WSL
    # From Windows, localhost:5432 should work
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="vibe_search",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD", "postgres")  # Change if you set a different password
    )


def import_products_from_csv(csv_path: Path, batch_size: int = 100):
    """
    Import products from CSV file into PostgreSQL.
    
    Args:
        csv_path: Path to the CSV file
        batch_size: Number of records to insert per batch
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Read CSV and prepare data
        products = []
        with csv_path.open('r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Map CSV columns to database columns
                product_data = {
                    'product_id': row.get('id', '').strip(),
                    'sku_id': row.get('sku_id', '').strip() or None,
                    'title': row.get('title', '').strip(),
                    'slug': row.get('slug', '').strip() or None,
                    'category': row.get('category', '').strip() or None,
                    'sub_category': row.get('sub_category', '').strip() or None,
                    'brand_name': row.get('brand_name', '').strip() or None,
                    'product_type': row.get('product_type', '').strip() or None,
                    'gender': row.get('gender', '').strip() or None,
                    'colorways': row.get('colorways', '').strip() or None,
                    'brand_sku': row.get('brand_sku', '').strip() or None,
                    'model': row.get('model', '').strip() or None,
                    'lowest_price': parse_decimal(row.get('lowest_price', '0')),
                    'description': row.get('description', '').strip() or None,
                    'is_d2c': parse_bool(row.get('is_d2c', 'False')),
                    'is_active': parse_bool(row.get('is_active', 'True')),
                    'is_certificate_required': parse_bool(row.get('is_certificate_required', 'False')),
                    'featured_image': row.get('featured_image', '').strip() or None,
                    'quantity_left': parse_int(row.get('quantity_left', '0')),
                    'wishlist_num': parse_int(row.get('wishlist_num', '0')),
                    'stock_claimed_percent': parse_int(row.get('stock_claimed_percent', '0')),
                    'discount_percentage': parse_decimal(row.get('discount_percentage', '0')),
                    'note': row.get('note', '').strip() or None,
                    'tags': row.get('tags', '').strip() or None,
                    'release_date': parse_date(row.get('release_date', '')),
                    'pdp_url': row.get('pdp_url', '').strip() or None,
                    'created_at': parse_date(row.get('created_at', '')) or datetime.now(),
                    'updated_at': parse_date(row.get('updated_at', '')) or datetime.now(),
                }
                
                # Skip if no product_id or title
                if not product_data['product_id'] or not product_data['title']:
                    continue
                
                products.append(product_data)
        
        print(f"Loaded {len(products)} products from CSV")
        
        # Insert in batches
        insert_query = """
        INSERT INTO products (
            product_id, sku_id, title, slug, category, sub_category,
            brand_name, product_type, gender, colorways, brand_sku, model,
            lowest_price, description, is_d2c, is_active, is_certificate_required,
            featured_image, quantity_left, wishlist_num, stock_claimed_percent,
            discount_percentage, note, tags, release_date, pdp_url, created_at, updated_at
        ) VALUES %s
        ON CONFLICT (product_id) DO UPDATE SET
            title = EXCLUDED.title,
            category = EXCLUDED.category,
            sub_category = EXCLUDED.sub_category,
            brand_name = EXCLUDED.brand_name,
            featured_image = EXCLUDED.featured_image,
            lowest_price = EXCLUDED.lowest_price,
            updated_at = EXCLUDED.updated_at
        """
        
        batch_count = 0
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            values = [
                (
                    p['product_id'], p['sku_id'], p['title'], p['slug'],
                    p['category'], p['sub_category'], p['brand_name'],
                    p['product_type'], p['gender'], p['colorways'],
                    p['brand_sku'], p['model'], p['lowest_price'],
                    p['description'], p['is_d2c'], p['is_active'],
                    p['is_certificate_required'], p['featured_image'],
                    p['quantity_left'], p['wishlist_num'],
                    p['stock_claimed_percent'], p['discount_percentage'],
                    p['note'], p['tags'], p['release_date'], p['pdp_url'],
                    p['created_at'], p['updated_at']
                )
                for p in batch
            ]
            
            execute_values(cursor, insert_query, values)
            batch_count += 1
            print(f"Inserted batch {batch_count} ({len(batch)} products)")
        
        conn.commit()
        print(f"\nSuccessfully imported {len(products)} products!")
        
        # Print summary statistics
        cursor.execute("SELECT COUNT(*) FROM products")
        total = cursor.fetchone()[0]
        print(f"Total products in database: {total}")
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE featured_image IS NOT NULL")
        with_images = cursor.fetchone()[0]
        print(f"Products with images: {with_images}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error importing products: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    csv_path = Path("products_export_20250916_071707.csv")
    
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        exit(1)
    
    print("Starting product import...")
    print(f"CSV file: {csv_path}")
    print("Database: vibe_search (PostgreSQL)")
    print("-" * 50)
    
    import_products_from_csv(csv_path)
    print("\nImport completed!")

