"""Embedder pipeline module.
Model: paraphrase-multilingual-MiniLM-L12-v2 (384 dimensions).
Uses ONNX Runtime / quantized CPU path.
"""
import os
import asyncio
from typing import List
from collections import OrderedDict
import numpy as np

class Embedder:
    """Singleton embedder class."""
    
    def __init__(self) -> None:
        self.session = None
        self.tokenizer = None
        self._initialized = False

    def _initialize(self):
        # Lazy-load the heavy ONNX session to keep fastapi fast at startup
        if self._initialized: return
        try:
            import onnxruntime as ort
            from tokenizers import Tokenizer
            model_path = os.getenv("ONNX_MODEL_PATH", "model.onnx")
            tok_path = os.getenv("ONNX_TOKENIZER_PATH", "tokenizer.json")
            if os.path.exists(model_path) and os.path.exists(tok_path):
                self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
                self.tokenizer = Tokenizer.from_file(tok_path)
        except Exception as e:
            print(f"ONNX Initialization Error: {e}")
        self._initialized = True

    def encode(self, text: str, normalize_embeddings: bool = True) -> np.ndarray:
        self._initialize()
        if not self.session or not self.tokenizer:
            # Fallback mock if weights are not present
            return np.zeros(384, dtype=np.float32)
            
        try:
            output = self.tokenizer.encode(text)
            input_ids = np.array([output.ids], dtype=np.int64)
            attention_mask = np.array([output.attention_mask], dtype=np.int64)
            
            ort_inputs = {
                self.session.get_inputs()[0].name: input_ids,
                self.session.get_inputs()[1].name: attention_mask
            }
            
            # Simple ONNX pass
            ort_outs = self.session.run(None, ort_inputs)
            
            # Mean pooling
            token_embeddings = ort_outs[0]
            input_mask_expanded = np.expand_dims(attention_mask, -1).astype(float)
            sum_embeddings = np.sum(token_embeddings * input_mask_expanded, 1)
            sum_mask = np.clip(np.sum(input_mask_expanded, 1), a_min=1e-9, a_max=None)
            sentence_embeddings = sum_embeddings / sum_mask
            
            # Extract first batch item
            vec = sentence_embeddings[0]
            
            # L2 Normalization (CRITICAL for parity with offline indexer)
            if normalize_embeddings:
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
                
            return vec.astype(np.float32)
            
        except Exception as e:
            print(f"Embedding error: {e}")
            return np.zeros(384, dtype=np.float32)

embedder = Embedder()

_embedding_cache: OrderedDict[str, np.ndarray] = OrderedDict()
CACHE_MAX = 256
_cache_lock = asyncio.Lock()

async def embed_query(text: str) -> np.ndarray:
    key = " ".join(text.strip().lower().split())

    async with _cache_lock:
        cached = _embedding_cache.get(key)
        if cached is not None:
            _embedding_cache.move_to_end(key)
            return cached

    # Run heavy computation outside the lock to prevent blocking the event loop
    vector = await asyncio.to_thread(
        embedder.encode,
        text,
        normalize_embeddings=True,
    )

    vector = np.asarray(vector, dtype=np.float32)

    # Strictly enforce 384 dimensions matching paraphrase-multilingual-MiniLM-L12-v2 parity
    if vector.shape != (384,):
        raise ValueError(f"Invalid embedding shape: {vector.shape}; expected (384,)")

    async with _cache_lock:
        if key not in _embedding_cache:
            _embedding_cache[key] = vector
        _embedding_cache.move_to_end(key)

        if len(_embedding_cache) > CACHE_MAX:
            _embedding_cache.popitem(last=False)

    return _embedding_cache[key]
