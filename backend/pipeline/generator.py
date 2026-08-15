"""Generator pipeline module.
Primary model: openai/gpt-oss-20b via Groq.
Maximum generation target: 80 tokens.
"""
import os
import asyncio
from typing import List, Dict, Any, Tuple
from groq import AsyncGroq

async def generate_answer(query: str, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[str, str]:
    """
    Generate an answer using Groq. Returns (answer_text, source)
    Fallback to best retrieved chunk on error/timeout.
    """
    if not retrieved_chunks:
        return "I am sorry, I do not have enough information to answer this.", "fallback"

    best_chunk_text = retrieved_chunks[0].get("text", "")
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("WARNING: GROQ_API_KEY not set. Using retrieved chunk fallback.")
        return best_chunk_text, "fallback"

    client = AsyncGroq(api_key=groq_key)
    
    context = "\n".join([c.get("text", "") for c in retrieved_chunks])
    prompt = f"Answer the user's question using ONLY the provided context. If the context doesn't contain the answer, say you don't know. Keep it under 80 words.\n\nContext:\n{context}\n\nQuestion: {query}"

    try:
        # 80 tokens max to meet tight latency targets
        chat_completion = await asyncio.wait_for(
            client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                model="openai/gpt-oss-20b",
                max_tokens=80,
                temperature=0.1
            ),
            timeout=2.0 # Strict deadline to avoid violating <200ms
        )
        return chat_completion.choices[0].message.content, "llm"
    except Exception as e:
        print(f"Generator Exception or Timeout: {e}. Falling back to chunk.")
        return best_chunk_text, "fallback"

