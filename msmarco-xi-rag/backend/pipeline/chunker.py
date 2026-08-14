"""Chunker module for offline indexing only.
Do NOT allow this module to be imported by runtime query orchestration.
"""
from typing import List, Dict, Any

def chunk_document(text: str, strategy: str) -> List[Dict[str, Any]]:
    """
    Offline indexing chunker.
    
    Strategies to implement later:
    P: passage-level
    S: sentence-level with minimum 10-word handling and merge-up guard
    W: 128-token window / 32-token overlap
    SM: semantic split using consecutive-sentence cosine threshold 0.75
    H: hierarchical dual: full passage + one-line summary
    """
    # TODO: Implement chunking logic for offline indexing
    raise NotImplementedError("Offline chunker not implemented yet.")
