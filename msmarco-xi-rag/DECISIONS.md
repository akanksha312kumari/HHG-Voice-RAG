# Engineering Decisions Log (DECISIONS.md)

This document is the authoritative engineering decision log for the Voice RAG System. It records all architectural, technological, API, and implementation choices made during development.

---

## DECISION REGISTRY

| Decision ID | Date | Decision Topic | Status |
|---|---|---|---|
| [DEC-001](#dec-001-speech-to-text-stt-integration) | 2026-08-14 | Speech-to-Text (STT) Integration | **APPROVED** |
| [DEC-002](#dec-002-text-embedding-model-and-execution) | 2026-08-14 | Text Embedding Model and Execution | **APPROVED** |
| [DEC-003](#dec-003-pinecone-index-and-metadata-strategy) | 2026-08-14 | Pinecone Single Index & Metadata Strategy | **APPROVED** |
| [DEC-004](#dec-004-concurrent-multi-strategy-retrieval) | 2026-08-14 | Concurrent Multi-Strategy Retrieval | **APPROVED** |
| [DEC-005](#dec-005-primary-generation-via-groq-with-hard-fallback) | 2026-08-14 | Primary Generation via Groq with Hard Fallback | **APPROVED** |
| [DEC-006](#dec-006-lightweight-local-guardrails) | 2026-08-14 | Lightweight Local Guardrails | **APPROVED** |
| [DEC-007](#dec-007-architecture-and-deployment-environment) | 2026-08-14 | Architecture and Deployment Environment | **APPROVED** |

---

### DEC-001: Speech-to-Text (STT) Integration

* **Decision ID**: DEC-001
* **Date**: 2026-08-14
* **Decision**: Integrate Sarvam Saaras v3 via a real-time WebSocket client connection for voice transcription.
* **Context**: The frontend sends captured raw audio bytes, which need to be transcribed quickly and accurately across multiple Indian languages.
* **Reason**: WebSockets prevent connection overhead (handshake latency) for every chunk of audio streamed from the user, facilitating sub-second real-time transcription.
* **Alternatives considered**: 
  * HTTP REST endpoints for audio upload (rejected due to high connection overhead per chunk).
  * Hosting a local Whisper model on Render Native CPU (rejected due to severe resource/memory constraints and slow execution times on CPU).
* **Why the selected option was chosen**: Sarvam Saaras v3 provides highly optimized model endpoints for Indian vernacular languages with low-latency WebSocket streaming support.
* **Master Plan reference**: Section 3.1 (STT Pipeline Orchestration)
* **Files/components affected**: 
  * `backend/pipeline/stt.py` ([stt.py](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/backend/pipeline/stt.py))
  * `backend/main.py` ([main.py](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/backend/main.py))
* **Risks**: Network connectivity, dependency on external API, rate limits.
* **Follow-up action**: Implement robust connection retry logic and a fallback error payload.
* **Status**: APPROVED

---

### DEC-002: Text Embedding Model and Execution

* **Decision ID**: DEC-002
* **Date**: 2026-08-14
* **Decision**: Implement `paraphrase-multilingual-MiniLM-L12-v2` locally using ONNX Runtime with quantized CPU weights.
* **Context**: System must generate text embeddings of query strings during the runtime flow to find matching documents.
* **Reason**: Running embeddings locally avoids network requests, bringing query embedding generation time down to <15ms.
* **Alternatives considered**:
  * OpenAI `/v1/embeddings` API (rejected because it adds 60–120ms network latency).
  * HuggingFace Hosted API (rejected due to network latency and potential cold starts).
  * Local PyTorch/sentence-transformers (rejected because PyTorch adds massive startup overhead and has slower CPU inference times).
* **Why the selected option was chosen**: ONNX Runtime provides highly optimized CPU execution for transformer models, allowing fast and cost-free local vectorization.
* **Master Plan reference**: Section 3.2 (Runtime Embedding Layer)
* **Files/components affected**:
  * `backend/pipeline/embedder.py` ([embedder.py](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/backend/pipeline/embedder.py))
* **Risks**: Lower semantic recall compared to much larger commercial APIs (e.g. OpenAI/Cohere).
* **Follow-up action**: Profile embedding execution speed on Render environment CPU.
* **Status**: APPROVED

---

### DEC-003: Pinecone Index and Metadata Strategy

* **Decision ID**: DEC-003
* **Date**: 2026-08-14
* **Decision**: Use a single Pinecone index named `msmarco-xi` to store all five chunking strategies (P, S, W, SM, H) differentiated through metadata attributes (`strategy` and `language`).
* **Context**: We need to manage and query five distinct text splitting methods without blowing up index costs and infrastructure complexity.
* **Reason**: Differentiating strategies inside metadata keeps the code simple and enables query-time isolation using metadata filtering filters without needing multiple physical indices.
* **Alternatives considered**:
  * Five separate Pinecone indexes (rejected due to cost, configuration overhead, and multi-index connection latencies).
  * Namespace partitioning (rejected as namespace querying doesn't allow cross-namespace aggregation if desired, and metadata query filtering is more standard for filtering).
* **Why the selected option was chosen**: Satisfies the system requirement of using exactly **one Pinecone index** and leverages Pinecone's efficient metadata filtering capabilities.
* **Master Plan reference**: Section 4.1 (Pinecone Indexing Setup)
* **Files/components affected**:
  * `backend/pipeline/retriever.py` ([retriever.py](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/backend/pipeline/retriever.py))
  * `indexing/kaggle_indexer.ipynb` ([kaggle_indexer.ipynb](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/indexing/kaggle_indexer.ipynb))
  * `indexing/verify_index.py` ([verify_index.py](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/indexing/verify_index.py))
* **Risks**: Pinecone metadata index storage limits (solved by indexing only search-relevant tags like `strategy` and `language`).
* **Follow-up action**: Ensure indexing notebook correctly writes these metadata properties.
* **Status**: APPROVED

---

### DEC-004: Concurrent Multi-Strategy Retrieval

* **Decision ID**: DEC-004
* **Date**: 2026-08-14
* **Decision**: Run query searches across the 5 chunking strategies concurrently in parallel using Python's `asyncio.gather` on the single index.
* **Context**: The RAG pipeline needs to fetch documents from all five strategies concurrently to construct the candidate set.
* **Reason**: Sequential requests would scale retrieval latency to ~500ms. Concurrent execution completes retrieval in the time of the slowest single request (~100ms).
* **Alternatives considered**:
  * Sequential API calls.
  * Querying all strategies in a single query without filtering (not possible, as we need top-k distinct documents *per strategy* to compare them fairly).
* **Why the selected option was chosen**: Crucial optimization step to stay within the strict 190ms latency budget.
* **Master Plan reference**: Section 4.2 (Concurrent Multi-Strategy Retrieval)
* **Files/components affected**:
  * `backend/pipeline/retriever.py` ([retriever.py](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/backend/pipeline/retriever.py))
* **Risks**: Rate limits/concurrency limits on the free/developer tier Pinecone API.
* **Follow-up action**: Stress test Pinecone with multiple concurrent sessions.
* **Status**: APPROVED

---

### DEC-005: Primary Generation via Groq with Hard Fallback

* **Decision ID**: DEC-005
* **Date**: 2026-08-14
* **Decision**: Use `openai/gpt-oss-20b` via the Groq API with a maximum generation budget of 80 tokens. If the API fails or times out, immediately fall back to the best retrieved grounded chunk (no second LLM fallback).
* **Context**: LLM answer synthesis must be extremely fast and robust to failures.
* **Reason**: Groq is chosen for its high token-per-second performance. If it fails, contacting another model (e.g. OpenAI/Anthropic) would double the latency, causing a timeout. Falling back directly to the best retrieved chunk keeps responses immediate and factual.
* **Alternatives considered**:
  * Fallback to a secondary cloud LLM service (rejected due to additional latency).
  * Returning a generic error message (rejected; retrieving a grounded chunk is much more helpful to the user).
* **Why the selected option was chosen**: Provides the lowest possible latency path on failure and satisfies the critical constraint: *no second LLM fallback*.
* **Master Plan reference**: Section 5.1 (LLM Integration and Fallback Path)
* **Files/components affected**:
  * `backend/pipeline/generator.py` ([generator.py](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/backend/pipeline/generator.py))
* **Risks**: Raw grounded chunk might look unformatted compared to a synthesized answer.
* **Follow-up action**: Implement a strict timeout on the Groq client.
* **Status**: APPROVED

---

### DEC-006: Lightweight Local Guardrails

* **Decision ID**: DEC-006
* **Date**: 2026-08-14
* **Decision**: Implement guardrails locally (regex safety check, centroid cosine similarity off-topic check, and ROUGE-1 grounding check). Do not call external LLMs for guardrails.
* **Context**: Inputs and outputs must be checked for safety, topic relevance, and hallucination.
* **Reason**: Calling an LLM or safety API for guardrail evaluation would add 200–500ms of latency. Local algorithms execute in <1ms.
* **Alternatives considered**:
  * LlamaGuard / NeMo Guardrails (rejected because they require a separate heavy runtime or external model calls).
  * Guardrails AI cloud services (rejected due to network latency).
* **Why the selected option was chosen**: Local execution guarantees that guardrails do not bottleneck the 190ms latency budget.
* **Master Plan reference**: Section 6.0 (Guardrail Implementations)
* **Files/components affected**:
  * `backend/guardrails/safety.py` ([safety.py](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/backend/guardrails/safety.py))
  * `backend/guardrails/off_topic.py` ([off_topic.py](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/backend/guardrails/off_topic.py))
  * `backend/guardrails/grounding.py` ([grounding.py](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/backend/guardrails/grounding.py))
* **Risks**: Lower safety sensitivity compared to deep learning guardrail models.
* **Follow-up action**: Tune the grounding and off-topic thresholds using sample datasets.
* **Status**: APPROVED

---

### DEC-007: Architecture and Deployment Environment

* **Decision ID**: DEC-007
* **Date**: 2026-08-14
* **Decision**: Deploy FastAPI backend and Next.js frontend to Render using the Native Python environment. Do NOT use Docker.
* **Context**: Target cloud platform configuration.
* **Reason**: Strict contest requirements forbid containerization via Docker.
* **Alternatives considered**:
  * Docker deployment (rejected - explicitly forbidden).
* **Why the selected option was chosen**: Compliance with project deployment rules.
* **Master Plan reference**: Section 2.1 (Deployment Architecture)
* **Files/components affected**:
  * `backend/render.yaml` ([render.yaml](file:///d:/HACKATHONS/HHGOA/TASK2/hhg-voice-RAG-model/msmarco-xi-rag/backend/render.yaml))
* **Risks**: Operating system library discrepancies (Windows dev vs Linux deploy) with ONNX or sound libraries.
* **Follow-up action**: Ensure all packages in `requirements.txt` are cross-platform.
* **Status**: APPROVED
