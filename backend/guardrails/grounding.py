"""Grounding guardrail module."""
from typing import List, Dict, Any
import re

def check_grounding(answer: str, retrieved_chunks: List[Dict[str, Any]]) -> bool:
    """
    Check if the generated answer is grounded in the retrieved chunks.
    Lightweight N-gram or keyword overlap.
    """
    if not retrieved_chunks:
        # If no chunks, answer cannot be grounded unless it says "I don't know"
        return "I don't know" in answer or "sorry" in answer
        
    combined_context = " ".join([c.get("text", "") for c in retrieved_chunks]).lower()
    
    # Extract significant nouns/numbers from answer
    words = re.findall(r'\b[a-zA-Z0-9]{4,}\b', answer.lower())
    if not words:
        return True
        
    # Check if a sufficient ratio of words in the answer exist in the context
    matches = sum(1 for w in words if w in combined_context)
    
    # If less than 20% of significant words match context, flag as hallucination
    if len(words) > 5 and (matches / len(words)) < 0.2:
        return False
        
    return True
