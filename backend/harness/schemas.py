"""Pydantic schemas for the RAG pipeline."""
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class QueryRequest(BaseModel):
    """Placeholder for query request schema."""
    request_id: str
    language: str
    audio_data: Optional[bytes] = None
    # TODO: Add further fields as necessary

class STTResult(BaseModel):
    """Placeholder for STT result schema."""
    transcript: str
    # TODO: Add further fields

class RetrievedChunk(BaseModel):
    """Placeholder for a retrieved chunk schema."""
    text: str
    strategy: str
    # TODO: Add metadata and score fields

class GuardrailResult(BaseModel):
    """Placeholder for guardrail result schema."""
    blocked: bool
    reason: Optional[str] = None
    grounded: Optional[bool] = None

class LatencyBreakdown(BaseModel):
    """Placeholder for latency breakdown schema."""
    stt_ms: Optional[float] = None
    embedding_ms: Optional[float] = None
    retrieval_ms: Optional[float] = None
    rerank_ms: Optional[float] = None
    off_topic_ms: Optional[float] = None
    generation_ms: Optional[float] = None
    grounding_ms: Optional[float] = None
    total_ms: Optional[float] = None

class PipelineResult(BaseModel):
    """Placeholder for the final pipeline result schema."""
    request_id: str
    language: str
    transcript: str
    answer: str
    retrieved_chunks: List[RetrievedChunk]
    guardrail: GuardrailResult
    latency_breakdown: LatencyBreakdown
    model: str
    answer_source: str
