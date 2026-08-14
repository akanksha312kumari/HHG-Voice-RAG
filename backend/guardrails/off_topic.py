"""Off-topic guardrail module."""
from typing import List

def check_off_topic(query_embedding: List[float], corpus_centroid: List[float]) -> bool:
    """
    Cosine similarity check against corpus centroid.
    """
    # TODO: Implement off-topic check
    raise NotImplementedError("Off-topic check not implemented yet.")
