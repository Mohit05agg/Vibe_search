"""Quick script to check AI-processed data in database."""
import psycopg2
import os

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='vibe_search',
    user='postgres',
    password=os.getenv('POSTGRES_PASSWORD', 'postgres')
)
cur = conn.cursor()

# Get statistics
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(detected_class) as with_class,
        COUNT(extracted_colors) as with_colors,
        COUNT(image_embedding) as with_embedding
    FROM scraped_images
""")
row = cur.fetchone()
print(f"Total scraped images: {row[0]}")
print(f"With detected_class: {row[1]}")
print(f"With extracted_colors: {row[2]}")
print(f"With image_embedding: {row[3]}")
print()

# Get sample AI-processed data
cur.execute("""
    SELECT detected_class, extracted_colors, extracted_styles, extracted_brands
    FROM scraped_images 
    WHERE detected_class IS NOT NULL 
    LIMIT 5
""")
print("Sample AI-processed data:")
print("-" * 60)
for r in cur.fetchall():
    print(f"Class: {r[0]}")
    print(f"Colors: {r[1]}")
    print(f"Styles: {r[2]}")
    print(f"Brands: {r[3]}")
    print()

cur.close()
conn.close()

