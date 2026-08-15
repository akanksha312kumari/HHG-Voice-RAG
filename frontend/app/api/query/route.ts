import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    
    // In production, the backend might take exactly the multipart form or we might
    // need to format it depending on FastAPI backend's precise expectation.
    // Assuming backend takes multipart/form-data.
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    
    const backendRes = await fetch(`${backendUrl}/query`, {
      method: "POST",
      body: formData,
    });

    if (!backendRes.ok) {
      console.error("Backend Error", backendRes.status, backendRes.statusText);
      return NextResponse.json(
        { error: `Backend API error: ${backendRes.statusText}` },
        { status: backendRes.status }
      );
    }

    const data = await backendRes.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Proxy Error:", error);
    return NextResponse.json(
      { error: "Internal Server Error in Next.js Proxy" },
      { status: 500 }
    );
  }
}

