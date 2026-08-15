"""Main FastAPI application module."""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from backend.harness.orchestrator import run_pipeline

app = FastAPI(title="Voice RAG System API", version="7.4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health endpoint returning a structured response indicating the application is running."""
    return {"status": "ok", "message": "Application process is running", "version": "7.4"}

@app.post("/query")
async def query_endpoint(
    audio_data: UploadFile = File(...),
    language: str = Form(...)
) -> Dict[str, Any]:
    """
    Receives voice query and forwards to the orchestrator.
    """
    try:
        audio_bytes = await audio_data.read()
        result = await run_pipeline(audio_bytes, language)
        return result
    except Exception as e:
        print(f"Error in query_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

