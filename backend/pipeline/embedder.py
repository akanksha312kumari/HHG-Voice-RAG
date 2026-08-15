"""Embedder pipeline module.
Model: paraphrase-multilingual-MiniLM-L12-v2 (384 dimensions).
Uses ONNX Runtime / quantized CPU path.
"""
import os
from typing import List

class Embedder:
    """Singleton embedder class."""
    
    def __init__(self) -> None:
        self.session = None
        self.tokenizer = None
        self._initialized = False

    def _initialize(self):
        # We lazy-load the heavy ONNX session to keep fastapi fast at startup if it's not strictly needed
        if self._initialized: return
        try:
            import onnxruntime as ort
            from tokenizers import Tokenizer
            # In a real environment, you'd specify the paths to the downloaded model.onnx and tokenizer.json
            model_path = os.getenv("ONNX_MODEL_PATH", "model.onnx")
            tok_path = os.getenv("ONNX_TOKENIZER_PATH", "tokenizer.json")
            if os.path.exists(model_path) and os.path.exists(tok_path):
                self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
                self.tokenizer = Tokenizer.from_file(tok_path)
        except Exception as e:
            print(f"ONNX Initialization Error: {e}")
        self._initialized = True

    def embed_text(self, text: str) -> List[float]:
        self._initialize()
        if not self.session or not self.tokenizer:
            # Fallback mock if weights are not present
            return [0.0] * 384
            
        try:
            import numpy as np
            output = self.tokenizer.encode(text)
            input_ids = np.array([output.ids], dtype=np.int64)
            attention_mask = np.array([output.attention_mask], dtype=np.int64)
            
            ort_inputs = {
                self.session.get_inputs()[0].name: input_ids,
                self.session.get_inputs()[1].name: attention_mask
            }
            
            # Simple ONNX pass (assuming paraphrase-multilingual-MiniLM-L12-v2 takes input_ids and attention_mask)
            ort_outs = self.session.run(None, ort_inputs)
            
            # Mean pooling
            token_embeddings = ort_outs[0]
            input_mask_expanded = np.expand_dims(attention_mask, -1).astype(float)
            sum_embeddings = np.sum(token_embeddings * input_mask_expanded, 1)
            sum_mask = np.clip(np.sum(input_mask_expanded, 1), a_min=1e-9, a_max=None)
            sentence_embeddings = sum_embeddings / sum_mask
            
            return sentence_embeddings[0].tolist()
            
        except Exception as e:
            print(f"Embedding error: {e}")
            return [0.0] * 384

embedder_instance = Embedder()

def embed_text(text: str) -> List[float]:
    return embedder_instance.embed_text(text)

