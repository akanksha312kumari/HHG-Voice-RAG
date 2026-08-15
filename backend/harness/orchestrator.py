"""Orchestrator module for managing the pipeline flow."""
import time
import asyncio
from typing import Any, Dict

from backend.pipeline import stt, embedder, retriever, generator
from backend.guardrails import safety, off_topic, grounding
from backend.harness.schemas import PipelineResult, GuardrailResult, LatencyBreakdown

async def run_pipeline(audio_data: bytes, lang: str) -> Dict[str, Any]:
    """
    Main orchestration logic enforcing this dependency order:
    STT -> embedding -> concurrent retrieval -> merge/dedupe -> rerank -> off-topic -> LLM -> grounding
    """
    latencies = LatencyBreakdown()
    request_id = f"req-{int(time.time() * 1000)}"
    start_total = time.perf_counter()

    # 1. STT
    t0 = time.perf_counter()
    stt_res = await stt.transcribe_audio(audio_data, lang)
    latencies.stt_ms = round((time.perf_counter() - t0) * 1000, 2)
    transcript = stt_res.transcript
    detected_lang = stt_res.detected_lang

    # 2. Safety Check (STT output)
    if safety.check_unsafe_input(transcript):
        return _build_blocked_response(request_id, lang, transcript, detected_lang, latencies, "unsafe_input")

    # 3. Embedding
    t0 = time.perf_counter()
    query_embed = embedder.embed_text(transcript)
    latencies.embedding_ms = round((time.perf_counter() - t0) * 1000, 2)

    # 4. Off-Topic Check
    t0 = time.perf_counter()
    is_off_topic = off_topic.check_off_topic(query_embed)
    latencies.off_topic_ms = round((time.perf_counter() - t0) * 1000, 2)
    if is_off_topic:
        return _build_blocked_response(request_id, lang, transcript, detected_lang, latencies, "off_topic")

    # 5. Concurrent Retrieval
    t0 = time.perf_counter()
    results = await asyncio.gather(
        retriever.retrieve_by_embed(query_embed, lang, "P", 5),
        retriever.retrieve_by_embed(query_embed, lang, "S", 5),
        retriever.retrieve_by_embed(query_embed, lang, "W", 5),
        retriever.retrieve_by_embed(query_embed, lang, "SM", 5),
        retriever.retrieve_by_embed(query_embed, lang, "H", 5),
    )
    latencies.retrieval_ms = round((time.perf_counter() - t0) * 1000, 2)

    # Flatten chunks
    all_chunks = []
    for strat_chunks in results:
        all_chunks.extend(strat_chunks)

    # 6. Rerank & Deduplicate
    t0 = time.perf_counter()
    top_chunks = retriever.rerank_and_dedupe(query_embed, all_chunks, top_k=3)
    latencies.rerank_ms = round((time.perf_counter() - t0) * 1000, 2)

    # 7. LLM Generation
    t0 = time.perf_counter()
    answer_text, source = await generator.generate_answer(transcript, top_chunks)
    latencies.generation_ms = round((time.perf_counter() - t0) * 1000, 2)

    # 8. Grounding Check
    t0 = time.perf_counter()
    is_grounded = grounding.check_grounding(answer_text, top_chunks)
    latencies.grounding_ms = round((time.perf_counter() - t0) * 1000, 2)

    latencies.total_ms = round((time.perf_counter() - start_total) * 1000, 2)

    if not is_grounded:
        return _build_blocked_response(request_id, lang, transcript, detected_lang, latencies, "hallucination_detected")

    # Success Response
    res = PipelineResult(
        request_id=request_id,
        language=lang,
        transcript=transcript,
        detected_lang=detected_lang,
        answer=answer_text,
        retrieved_chunks=top_chunks,
        guardrail=GuardrailResult(blocked=False, grounded=True),
        latency_breakdown=latencies,
        model="openai/gpt-oss-20b",
        answer_source=source
    )
    return res.model_dump()


def _build_blocked_response(req_id, lang, transcript, detected, latencies, reason):
    res = PipelineResult(
        request_id=req_id,
        language=lang,
        transcript=transcript,
        detected_lang=detected,
        answer="",
        retrieved_chunks=[],
        guardrail=GuardrailResult(blocked=True, reason=reason, grounded=False),
        latency_breakdown=latencies,
        model="openai/gpt-oss-20b",
        answer_source="guardrail"
    )
    return res.model_dump()

