"""Pydantic schemas for the RAG pipeline."""
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class QueryRequest(BaseModel):
    request_id: str
    language: str
    audio_data: Optional[bytes] = None

class STTResult(BaseModel):
    transcript: str
    detected_lang: Optional[str] = None

class RetrievedChunk(BaseModel):
    text: str
    strategy: str
    language: Optional[str] = None
    passage_id: Optional[str] = None

class GuardrailResult(BaseModel):
    blocked: bool
    reason: Optional[str] = None
    grounded: Optional[bool] = None

class LatencyBreakdown(BaseModel):
    stt_ms: Optional[float] = None
    embedding_ms: Optional[float] = None
    retrieval_ms: Optional[float] = None
    rerank_ms: Optional[float] = None
    off_topic_ms: Optional[float] = None
    generation_ms: Optional[float] = None
    grounding_ms: Optional[float] = None
    total_ms: Optional[float] = None

class PipelineResult(BaseModel):
    request_id: str
    language: str
    transcript: str
    detected_lang: Optional[str] = None
    answer: str
    retrieved_chunks: List[RetrievedChunk]
    guardrail: GuardrailResult
    latency_breakdown: LatencyBreakdown
    model: str
    answer_source: str

