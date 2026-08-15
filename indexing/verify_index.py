"""Verify offline index module."""
import os
from pinecone import Pinecone

def verify_pinecone_index() -> None:
    """Verify that the msmarco-xi Pinecone index exists, has expected dimensions, and meets the metadata contract."""
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("PINECONE_API_KEY not found. Skipping live verification.")
        return
        
    pc = Pinecone(api_key=api_key)
    
    print("Connecting to Pinecone index 'msmarco-xi'...")
    try:
        # 1. Index Configuration
        idx_info = pc.describe_index("msmarco-xi")
        dim = getattr(idx_info, 'dimension', 0)
        metric = getattr(idx_info, 'metric', '')
        
        assert dim == 384, f"FAIL LOUDLY: Expected dimension 384, got {dim}. You must recreate the index."
        assert metric == "cosine", f"FAIL LOUDLY: Expected metric cosine, got {metric}. Reranking depends on this."
        print(f"PASS: Index msmarco-xi configuration verified: dimension={dim}, metric={metric}")
        
        # 2. Index Statistics
        idx = pc.Index("msmarco-xi")
        stats = idx.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        print(f"Index statistics: Total vectors indexed = {total_vectors}")
        
        # 3. Metadata Contract
        response = idx.query(
            vector=[0.0] * 384,
            top_k=1,
            include_metadata=True,
            include_values=False
        )
        
        if response.matches:
            meta = response.matches[0].metadata
            assert "lang" in meta, "FAIL LOUDLY: Metadata missing 'lang'"
            assert "passage_id" in meta, "FAIL LOUDLY: Metadata missing 'passage_id'"
            assert "strategy" in meta, "FAIL LOUDLY: Metadata missing 'strategy'"
            assert "chunk_id" in meta, "FAIL LOUDLY: Metadata missing 'chunk_id'"
            assert "text" in meta, "INDEX METADATA CONTRACT INCOMPLETE: Missing 'text'"
            
            # Runtime constraint verification
            assert isinstance(meta.get("text"), str) and len(meta.get("text")) > 0, "INDEX METADATA CONTRACT INCOMPLETE: 'text' is empty"
            
            print("PASS: Metadata schema (lang, passage_id, strategy, chunk_id, text) verified.")
        else:
            print("WARNING: Index is completely empty. Cannot verify metadata schema.")
            
    except Exception as e:
        print(f"FAIL LOUDLY: Index verification failed: {e}")
        raise e

if __name__ == "__main__":
    verify_pinecone_index()
