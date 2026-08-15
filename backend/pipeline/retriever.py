"""Retriever pipeline module."""
import os
import asyncio
from typing import List, Tuple
import numpy as np
from pinecone import AsyncPinecone
from backend.harness.schemas import RetrievedChunk

class RetrievalUnavailableError(Exception):
    """Domain-specific error raised when Pinecone infrastructure is completely unreachable."""
    pass

# Global pinecone client to avoid reconnect overhead
pc = None
index = None

def _get_pinecone_index():
    global pc, index
    if pc is None:
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            return None
        pc = AsyncPinecone(api_key=api_key)
        # STRICT REQUIREMENT: Index must be exactly msmarco-xi
        index = pc.IndexAsync("msmarco-xi")
    return index

async def retrieve_by_embed(embed: np.ndarray, lang: str, strategy: str, top_k: int = 5) -> List[Tuple[RetrievedChunk, float]]:
    """
    Retrieve documents from the existing Pinecone index using the provided embedding.
    Returns a list of tuples containing (RetrievedChunk, score) to allow for later global score sorting.
    """
    # 1. Validate vector shape matching exactly 384 dimensions
    if embed.shape != (384,):
        raise ValueError(f"Vector dimension mismatch: expected (384,), got {embed.shape}")
        
    idx = _get_pinecone_index()
    if not idx:
        raise RetrievalUnavailableError("Pinecone credentials missing. Infrastructure unreachable.")
    
    # Convert np.ndarray to list of floats for Pinecone API
    vector = embed.tolist()
    
    response = await idx.query(
        vector=vector,
        filter={"strategy": {"$eq": strategy}, "lang": {"$eq": lang}},
        top_k=top_k,
        include_metadata=True,
        include_values=False
    )
    
    results = []
    for match in response.matches:
        chunk = RetrievedChunk(
            text=match.metadata.get("text", ""),
            strategy=strategy,
            language=lang,
            passage_id=match.metadata.get("passage_id", "")
        )
        # We store Pinecone's returned similarity score (since metric="cosine") to use in the Global Score Sort
        results.append((chunk, match.score))
    return results

async def retrieve_ensemble(embed: np.ndarray, lang: str) -> List[RetrievedChunk]:
    """
    Executes the 5 strategy queries concurrently.
    If all 5 fail due to infrastructure issues, raises RetrievalUnavailableError.
    Otherwise merges successful candidates, deduplicates, and performs Global Score Sort.
    """
    # 1. Execute five concurrent queries. return_exceptions=True isolates individual strategy failures
    # without crashing the entire ensemble immediately.
    results = await asyncio.gather(
        retrieve_by_embed(embed, lang, "P", 5),
        retrieve_by_embed(embed, lang, "S", 5),
        retrieve_by_embed(embed, lang, "W", 5),
        retrieve_by_embed(embed, lang, "SM", 5),
        retrieve_by_embed(embed, lang, "H", 5),
        return_exceptions=True
    )
    
    # 2. Extract successful strategy results and trap complete outages
    all_candidates: List[Tuple[RetrievedChunk, float]] = []
    success_count = 0
    for strat_results in results:
        if isinstance(strat_results, Exception):
            if isinstance(strat_results, RetrievalUnavailableError):
                continue
            print(f"Strategy retrieval encountered error: {strat_results}")
        else:
            success_count += 1
            all_candidates.extend(strat_results)
            
    if success_count == 0:
        raise RetrievalUnavailableError("All 5 retrieval strategies failed. Pinecone infrastructure is unreachable.")
        
    # 3. Deduplicate strictly by passage_id
    unique_candidates = {}
    for chunk, score in all_candidates:
        pid = chunk.passage_id
        # Fallback to text hash if passage_id is missing to avoid dropping valid distinct chunks
        key = pid if pid else hash(chunk.text)
        
        if key not in unique_candidates:
            unique_candidates[key] = (chunk, score)
        else:
            # If we've seen this passage before, retain the one with the highest similarity score
            existing_chunk, existing_score = unique_candidates[key]
            if score > existing_score:
                unique_candidates[key] = (chunk, score)

    deduped_candidates = list(unique_candidates.values())
    
    # 4. Global Score Sort
    # Because include_values=False, we intentionally do NOT have the raw candidate vectors 
    # to run an in-process cosine computation. We rely strictly on Pinecone's returned metric score.
    # We do NOT invent a second embedding path here to fake cosine reranking.
    deduped_candidates.sort(key=lambda x: x[1], reverse=True)
    
    # 5. Extract top 3 and strip the score tuple
    top_3 = [chunk for chunk, score in deduped_candidates[:3]]
    return top_3
