"use client";

import { Product } from "@/types";
import Image from "next/image";

interface ProductModalProps {
  product: Product;
  onClose: () => void;
}

export default function ProductModal({ product, onClose }: ProductModalProps) {
  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-2xl font-bold text-gray-900">{product.title}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>

          {product.featured_image && (
            <div className="relative w-full h-96 mb-4 rounded-lg overflow-hidden bg-gray-200">
              <Image
                src={product.featured_image}
                alt={product.title}
                fill
                className="object-cover"
                unoptimized
              />
            </div>
          )}

          <div className="space-y-4">
            {product.brand_name && (
              <div>
                <span className="font-semibold text-gray-700">Brand: </span>
                <span className="text-gray-900">{product.brand_name}</span>
              </div>
            )}

            {product.category && (
              <div>
                <span className="font-semibold text-gray-700">Category: </span>
                <span className="text-gray-900">{product.category}</span>
                {product.sub_category && (
                  <span className="text-gray-600"> / {product.sub_category}</span>
                )}
              </div>
            )}

            {product.lowest_price !== undefined && product.lowest_price > 0 && (
              <div>
                <span className="font-semibold text-gray-700">Price: </span>
                <span className="text-2xl font-bold text-blue-600">
                  ${product.lowest_price.toFixed(2)}
                </span>
              </div>
            )}

            {product.similarity_score !== undefined && (
              <div>
                <span className="font-semibold text-gray-700">Match Score: </span>
                <span className="text-gray-900">
                  {Math.round(product.similarity_score * 100)}%
                </span>
              </div>
            )}

            {product.pdp_url && (
              <a
                href={product.pdp_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
              >
                View Product
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

