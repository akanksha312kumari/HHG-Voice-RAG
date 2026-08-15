"""Safety guardrail module."""

import re

UNSAFE_KEYWORDS = ["hack", "bypass", "exploit", "ignore previous instructions", "violence", "illegal"]

def check_unsafe_input(text: str) -> bool:
    """
    Lightweight regex safety layer.
    """
    text_lower = text.lower()
    for kw in UNSAFE_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", text_lower):
            return True
    return False
