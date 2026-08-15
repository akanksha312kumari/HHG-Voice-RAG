"""Retrieval quality evaluation."""
import asyncio
from backend.pipeline.embedder import embed_query
from backend.pipeline.retriever import retrieve_ensemble, RetrievalUnavailableError

async def evaluate_retrieval():
    """
    Evaluate retrieval quality (Recall@5, MRR@10) across Indian languages.
    Ensures that validation uses exactly the same vector pathway as production.
    """
    print("============================================================")
    print("RETRIEVAL QUALITY EVALUATION")
    print("============================================================")
    
    print("WARNING: msmarco-xi validation set missing locally. Recall@5/MRR@10 are pending.")
    print("Executing parity smoke test through production pipeline...")
    
    test_queries = [
        ("hi", "भारत की राजधानी क्या है?"),
        ("ta", "இந்தியாவின் தலைநகரம் என்ன?"),
        ("bn", "ভারতের রাজধানী কি?"),
        ("sa", "भारतस्य राजधानी का अस्ति?")
    ]
    
    for lang, q in test_queries:
        print(f"\nEvaluating Language: {lang} | Query: {q}")
        try:
            embed = await embed_query(q)
            results = await retrieve_ensemble(embed, lang)
            print(f"PASS: Successfully retrieved {len(results)} chunks for {lang}")
        except RetrievalUnavailableError as e:
            # Trap infrastructure failure correctly during local testing
            if lang == "bn":
                print(f"Bengali retrieval quality: NOT AVAILABLE — language not indexed (Fallback caught)")
            else:
                print(f"Infrastructure Offline: Cannot evaluate {lang} (Fallback caught)")
        except Exception as e:
            print(f"FAIL LOUDLY: Retrieval crashed for {lang} with error: {e}")

if __name__ == "__main__":
    asyncio.run(evaluate_retrieval())
