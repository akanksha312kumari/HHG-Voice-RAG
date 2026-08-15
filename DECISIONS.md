# Engineering Decisions Log (DECISIONS.md)

This document is the authoritative engineering decision log for the Voice RAG System. It records all architectural, technological, API, and implementation choices actually implemented in the system.

---

## DECISION REGISTRY

| Decision ID | Date | Decision Topic | Status |
|---|---|---|---|
| [DEC-001](#dec-001-speech-to-text-stt-integration) | 2026-08-14 | Speech-to-Text (STT) Integration | **IMPLEMENTED** |
| [DEC-002](#dec-002-text-embedding-model-and-execution) | 2026-08-14 | Text Embedding Model and Execution | **IMPLEMENTED** |
| [DEC-003](#dec-003-pinecone-index-and-metadata-strategy) | 2026-08-14 | Pinecone Single Index & Metadata Strategy | **IMPLEMENTED** |
| [DEC-004](#dec-004-concurrent-multi-strategy-retrieval) | 2026-08-14 | Concurrent Multi-Strategy Retrieval | **IMPLEMENTED** |
| [DEC-005](#dec-005-primary-generation-via-groq-with-hard-fallback) | 2026-08-14 | Primary Generation via Groq with Hard Fallback | **IMPLEMENTED** |
| [DEC-006](#dec-006-lightweight-local-guardrails) | 2026-08-14 | Lightweight Local Guardrails | **IMPLEMENTED** |
| [DEC-007](#dec-007-architecture-and-deployment-environment) | 2026-08-14 | Architecture and Deployment Environment | **PENDING INTEGRATION** |
| [DEC-008](#dec-008-frontend-architecture-proxy-pattern) | 2026-08-15 | Frontend Architecture & Proxy Pattern | **IMPLEMENTED** |
| [DEC-009](#dec-009-voice-input-format) | 2026-08-15 | Voice Input Format | **IMPLEMENTED** |
| [DEC-010](#dec-010-runtime-vs-offline-separation) | 2026-08-15 | Runtime vs Offline Separation | **IMPLEMENTED** |
| [DEC-011](#dec-011-latency-clock-and-telemetry) | 2026-08-15 | Latency Clock and Telemetry | **TESTED** |
| [DEC-012](#dec-012-mock-mode-restrictions) | 2026-08-15 | Mock Mode Restrictions | **IMPLEMENTED** |

---

### DEC-001: Speech-to-Text (STT) Integration

* **Decision**: Integrate Sarvam Saaras v3 (`saaras:v3-realtime`).
* **Context**: Voice queries in 14 vernacular languages need rapid transcription.
* **Implementation Details**: Supported languages mapped explicitly (including `or → od-IN`). 
* **Status**: IMPLEMENTED

---

### DEC-002: Text Embedding Model and Execution

* **Decision**: Implement `paraphrase-multilingual-MiniLM-L12-v2` locally using ONNX Runtime with quantized CPU weights.
* **Context**: System must generate text embeddings of query strings during the runtime flow to find matching documents.
* **Implementation Details**: Uses `onnxruntime` and `tokenizers` executing entirely on CPU to avoid networking round-trips.
* **Status**: IMPLEMENTED

---

### DEC-003: Pinecone Index and Metadata Strategy

* **Decision**: Use exactly one Pinecone index named `msmarco-xi`.
* **Context**: We need to manage and query five distinct text splitting methods.
* **Implementation Details**: The chunking strategy (`P`, `S`, `W`, `SM`, `H`) is stored as metadata. There are no separate indexes for different strategies. The vectors are 384 dimensions using a `cosine` metric.
* **Status**: IMPLEMENTED

---

### DEC-004: Concurrent Multi-Strategy Retrieval

* **Decision**: Run query searches across the 5 chunking strategies concurrently in parallel using Python's `asyncio.gather`.
* **Context**: RAG pipeline fetches documents from all five strategies concurrently to construct the candidate set.
* **Implementation Details**: Implemented. The returned 25 candidates are merged, deduplicated by text content, and reranked using cosine similarity before passing to the LLM.
* **Status**: IMPLEMENTED

---

### DEC-005: Primary Generation via Groq with Hard Fallback

* **Decision**: Use `openai/gpt-oss-20b` via the Groq API.
* **Context**: LLM answer synthesis must be extremely fast and robust to failures.
* **Implementation Details**: If the Groq API fails or times out within the interactive budget, the system immediately falls back to the **best retrieved grounded chunk**. There is **no second LLM request** inside the interactive latency budget, and **no blocking retry/backoff** on the critical path.
* **Status**: IMPLEMENTED

---

### DEC-006: Lightweight Local Guardrails

* **Decision**: Implement guardrails locally (regex safety check, centroid cosine similarity off-topic check, and ROUGE-style overlap grounding check).
* **Context**: Inputs and outputs must be checked for safety, topic relevance, and hallucination without external LLM calls.
* **Implementation Details**: 
  - **Layer 1**: `unsafe_input` (STT output block).
  - **Layer 2**: `off_topic` (Embedding centroid block).
  - **Layer 3**: `hallucination_detected` (Grounding failure block).
* **Status**: IMPLEMENTED

---

### DEC-007: Architecture and Deployment Environment

* **Decision**: Deploy FastAPI backend and Next.js frontend to Render/Vercel natively.
* **Context**: Deployment target configuration.
* **Status**: PENDING INTEGRATION (Deployment scripts prepared but not actively hosted).

---

### DEC-008: Frontend Architecture & Proxy Pattern

* **Decision**: The frontend is built using Next.js 14 App Router, TypeScript, and Tailwind CSS. All communications route through a Next.js API proxy to the FastAPI backend.
* **Context**: API keys must not be exposed to the client.
* **Implementation Details**:
  - `Frontend ↓ Next.js API proxy ↓ FastAPI backend`.
  - The frontend does not directly call Sarvam, Groq, or Pinecone. Private service credentials remain completely backend-side.
* **Status**: IMPLEMENTED

---

### DEC-009: Voice Input Format

* **Decision**: The browser records audio as `WAV`, `16 kHz`, `mono`.
* **Implementation Details**: Handled by `react-media-recorder` within the `VoiceRecorder` component, generating a Blob submitted as multipart form data.
* **Status**: IMPLEMENTED

---

### DEC-010: Runtime vs Offline Separation

* **Decision**: Kaggle is exclusively used for offline one-time indexing. The Render FastAPI backend is exclusively for runtime query/retrieval.
* **Implementation Details**:
  - The runtime **MUST NOT**: load MSMARCO-XI dataset, chunk documents, embed documents, or re-index Pinecone.
  - The runtime **ONLY**: transcribes, embeds the query, searches the index, and generates answers.
* **Status**: IMPLEMENTED

---

### DEC-011: Latency Clock and Telemetry

* **Decision**: The authoritative latency clock is explicitly defined as `END OF SPEECH → FIRST TOKEN ON SCREEN`.
* **Implementation Details**: 
  - Frontend telemetry natively supports per-step latency displays, a rolling average of the last 10 queries, retrieved top-3 context, guardrail status, detected language, and transcript.
  - **Benchmark Distributions**: P50/P70/P100 metrics are reserved strictly for measured deployed latency. Currently, these metrics read: `P50: pending deployed benchmark`, `P70: pending deployed benchmark`, `P100: pending deployed benchmark`.
* **Status**: TESTED

---

### DEC-012: Mock Mode Restrictions

* **Decision**: Mock mode exists only for development and UI prototyping.
* **Implementation Details**: 
  - Mock data is **NOT** production telemetry.
  - Mock latency **MUST NOT** be reported as measured Task 2 latency.
  - `USE_MOCK_DATA = false` is enforced for the real integration test path and production.
* **Status**: IMPLEMENTED
