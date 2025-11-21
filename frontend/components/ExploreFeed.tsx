"use client";

import { useState, useEffect } from "react";
import { ScrapedImage } from "@/types";
import Image from "next/image";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ExploreFeedProps {
  onImageClick: (imageUrl: string) => void;
}

export default function ExploreFeed({ onImageClick }: ExploreFeedProps) {
  const [images, setImages] = useState<ScrapedImage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScrapedImages();
  }, []);

  const fetchScrapedImages = async () => {
    try {
      // Note: You'll need to create an API endpoint to fetch scraped images
      // For now, this is a placeholder
      const response = await fetch(`${API_URL}/api/scraped-images`);
      if (response.ok) {
        const data = await response.json();
        setImages(data.images || []);
      }
    } catch (error) {
      console.error("Error fetching scraped images:", error);
      // Fallback: show message
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Loading explore feed...</p>
      </div>
    );
  }

  if (images.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg shadow-md">
        <p className="text-gray-500 mb-4">
          No scraped images available. Run the scrapers to populate the feed.
        </p>
        <p className="text-sm text-gray-400">
          Run: <code className="bg-gray-100 px-2 py-1 rounded">python scrapers/run_scrapers.py</code>
        </p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Explore Feed</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {images.map((image) => (
          <div
            key={image.id}
            onClick={() => onImageClick(image.image_url)}
            className="relative aspect-square rounded-lg overflow-hidden cursor-pointer hover:opacity-90 transition group"
          >
            <Image
              src={image.image_url}
              alt={image.caption || "Fashion image"}
              fill
              className="object-cover"
              unoptimized
            />
            {/* AI metadata badges */}
            {(image.detected_class || image.extracted_colors?.length) && (
              <div className="absolute top-2 left-2 flex flex-wrap gap-1">
                {image.detected_class && (
                  <span className="bg-blue-600 text-white px-2 py-1 rounded text-xs font-medium">
                    {image.detected_class}
                  </span>
                )}
                {image.extracted_colors?.slice(0, 2).map((color, idx) => (
                  <span
                    key={idx}
                    className="bg-purple-600 text-white px-2 py-1 rounded text-xs font-medium"
                  >
                    {color}
                  </span>
                ))}
              </div>
            )}
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition">
              <div className="absolute bottom-0 left-0 right-0 p-2 text-white text-sm opacity-0 group-hover:opacity-100 transition">
                {image.caption && (
                  <p className="line-clamp-2">{image.caption}</p>
                )}
                {image.extracted_brands?.length > 0 && (
                  <p className="text-xs mt-1 text-yellow-300">
                    Brand: {image.extracted_brands.join(", ")}
                  </p>
                )}
                {image.extracted_styles?.length > 0 && (
                  <p className="text-xs text-gray-300">
                    Style: {image.extracted_styles.slice(0, 2).join(", ")}
                  </p>
                )}
                <p className="text-xs mt-1">Click to search similar</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

