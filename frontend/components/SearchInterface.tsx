"use client";

import { useState } from "react";
import { Product, SearchResponse } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface SearchInterfaceProps {
  onSearchResults: (results: Product[]) => void;
  isSearching: boolean;
  setIsSearching: (value: boolean) => void;
}

export default function SearchInterface({
  onSearchResults,
  isSearching,
  setIsSearching,
}: SearchInterfaceProps) {
  const [query, setQuery] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [searchType, setSearchType] = useState<"text" | "image">("text");

  const handleTextSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    try {
      const response = await fetch(`${API_URL}/api/search/text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          limit: 20,
        }),
      });

      if (response.ok) {
        const data: SearchResponse = await response.json();
        onSearchResults(data.products || []);
      } else {
        console.error("Search failed");
      }
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleImageUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!imageFile) return;

    setIsSearching(true);
    try {
      const formData = new FormData();
      formData.append("image_file", imageFile);
      formData.append("limit", "20");

      const response = await fetch(`${API_URL}/api/search/image/upload`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data: SearchResponse = await response.json();
        onSearchResults(data.products || []);
      } else {
        console.error("Image search failed");
      }
    } catch (error) {
      console.error("Image search error:", error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
      <div className="flex gap-4 mb-4">
        <button
          onClick={() => setSearchType("text")}
          className={`px-4 py-2 rounded-lg font-medium transition ${searchType === "text"
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-700"
            }`}
        >
          Text Search
        </button>
        <button
          onClick={() => setSearchType("image")}
          className={`px-4 py-2 rounded-lg font-medium transition ${searchType === "image"
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-700"
            }`}
        >
          Image Search
        </button>
      </div>

      {searchType === "text" ? (
        <form onSubmit={handleTextSearch} className="flex gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for products... (e.g., 'black sneakers', 'summer dress')"
            className="flex-1 px-5 py-3 rounded-xl border border-gray-200 bg-gray-50 text-black
             placeholder:text-gray-400 shadow-sm focus:outline-none focus:ring-2 
             focus:ring-blue-500 transition-all"
            disabled={isSearching}
          />

          <button
            type="submit"
            disabled={isSearching || !query.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {isSearching ? "Searching..." : "Search"}
          </button>
        </form>
      ) : (
        <form onSubmit={handleImageUpload} className="space-y-4">
          <div>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              disabled={isSearching}
            />
            {imagePreview && (
              <div className="mt-4">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="max-w-xs rounded-lg border border-gray-300"
                />
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={isSearching || !imageFile}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {isSearching ? "Searching..." : "Search Similar Products"}
          </button>
        </form>
      )}
    </div>
  );
}

