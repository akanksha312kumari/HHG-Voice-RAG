"""Generator pipeline module.
Primary model: openai/gpt-oss-20b via Groq.
Maximum generation target: 80 tokens.
"""
from typing import Optional, List, Dict, Any

async def generate_answer(query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Generate an answer using Groq.
    
    If generation fails or exceeds its deadline, return the best retrieved grounded chunk.
    No second LLM fallback.
    """
    # TODO: Implement generator call
    raise NotImplementedError("Generator not implemented yet.")
