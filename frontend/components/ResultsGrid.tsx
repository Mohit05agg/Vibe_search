"use client";

import { Product } from "@/types";
import Image from "next/image";

interface ResultsGridProps {
  products: Product[];
  onProductClick: (product: Product) => void;
}

export default function ResultsGrid({
  products,
  onProductClick,
}: ResultsGridProps) {
  if (products.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">
          No results found. Try a different search query or upload an image.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {products.map((product) => (
        <div
          key={product.id}
          onClick={() => onProductClick(product)}
          className="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-xl transition-shadow"
        >
          {product.featured_image && (
            <div className="relative w-full h-64 bg-gray-200">
              <Image
                src={product.featured_image}
                alt={product.title}
                fill
                className="object-cover"
                unoptimized
              />
              {product.similarity_score !== undefined && (
                <div className="absolute top-2 right-2 bg-blue-600 text-white px-2 py-1 rounded text-sm font-medium">
                  {Math.round(product.similarity_score * 100)}% match
                </div>
              )}
            </div>
          )}
          <div className="p-4">
            <h3 className="font-semibold text-gray-900 mb-1 line-clamp-2">
              {product.title}
            </h3>
            {product.brand_name && (
              <p className="text-sm text-gray-600 mb-2">{product.brand_name}</p>
            )}
            {product.lowest_price !== undefined && product.lowest_price > 0 && (
              <p className="text-lg font-bold text-blue-600">
                ${product.lowest_price.toFixed(2)}
              </p>
            )}
            {product.category && (
              <span className="inline-block mt-2 px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                {product.category}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

