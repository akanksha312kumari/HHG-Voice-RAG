"""Off-topic guardrail module."""
from typing import List
from scipy.spatial.distance import cosine

# Pre-computed anchor for "HH Goa rules, history, competition, AI" etc.
# Using a zero vector placeholder. Real system would load the 384d anchor vector.
GOA_ANCHOR = [0.1] * 384

def check_off_topic(embedding: List[float]) -> bool:
    """
    Check if the query embedding is off-topic compared to the Goa dataset anchors.
    """
    if not embedding or sum(embedding) == 0:
        return False
        
    try:
        # Distance is 1 - cosine_similarity. If distance > threshold, it's off-topic.
        distance = cosine(embedding, GOA_ANCHOR)
        if distance > 0.8: # Threshold placeholder
            return True
        return False
    except:
        return False
