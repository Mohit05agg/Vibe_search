"use client";

import { useState } from "react";
import SearchInterface from "@/components/SearchInterface";
import ResultsGrid from "@/components/ResultsGrid";
import ExploreFeed from "@/components/ExploreFeed";
import ProductModal from "@/components/ProductModal";
import { Product } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [activeTab, setActiveTab] = useState<"search" | "explore">("explore");

  const handleSearchResults = (results: Product[]) => {
    setSearchResults(results);
    setActiveTab("search");
  };

  const handleImageClick = async (imageUrl: string) => {
    setIsSearching(true);
    try {
      const response = await fetch(`${API_URL}/api/search/image`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_url: imageUrl,
          limit: 20,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.products || []);
        setActiveTab("search");
      }
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-900 mb-2">Vibe Search</h1>
          <p className="text-gray-600 text-lg">
            Discover fashion products with visual and text search
          </p>
        </header>

        <div className="mb-6 flex gap-4 justify-center">
          <button
            onClick={() => setActiveTab("explore")}
            className={`px-6 py-2 rounded-lg font-medium transition ${
              activeTab === "explore"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 hover:bg-gray-50"
            }`}
          >
            Explore Feed
          </button>
          <button
            onClick={() => setActiveTab("search")}
            className={`px-6 py-2 rounded-lg font-medium transition ${
              activeTab === "search"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 hover:bg-gray-50"
            }`}
          >
            Search Results
          </button>
        </div>

        <SearchInterface
          onSearchResults={handleSearchResults}
          isSearching={isSearching}
          setIsSearching={setIsSearching}
        />

        {activeTab === "explore" && (
          <ExploreFeed onImageClick={handleImageClick} />
        )}

        {activeTab === "search" && (
          <ResultsGrid
            products={searchResults}
            onProductClick={setSelectedProduct}
          />
        )}

        {selectedProduct && (
          <ProductModal
            product={selectedProduct}
            onClose={() => setSelectedProduct(null)}
          />
        )}
      </div>
    </main>
  );
}

