import { NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET() {
  try {
    // This is a placeholder - you'll need to create this endpoint in FastAPI
    // For now, return empty array
    return NextResponse.json({ images: [] });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to fetch scraped images" },
      { status: 500 }
    );
  }
}

