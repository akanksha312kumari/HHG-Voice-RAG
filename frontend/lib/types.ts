export type LanguageCode =
  | "as"
  | "bn"
  | "gu"
  | "hi"
  | "kn"
  | "ml"
  | "mr"
  | "ne"
  | "or"
  | "pa"
  | "sa"
  | "ta"
  | "te"
  | "ur";

export interface RetrievedChunk {
  text: string;
  strategy: string;
  // Additional fields returned by backend
  language?: string;
  passage_id?: string;
}

export interface GuardrailResult {
  blocked: boolean;
  reason: string | null;
  grounded?: boolean;
}

export interface LatencyBreakdown {
  stt_ms?: number;
  embedding_ms?: number;
  retrieval_ms?: number;
  rerank_ms?: number;
  off_topic_ms?: number;
  generation_ms?: number;
  grounding_ms?: number;
  total_ms?: number;
}

export interface QueryResponse {
  request_id: string;
  language: string;
  transcript: string;
  answer: string;
  retrieved_chunks: RetrievedChunk[];
  guardrail: GuardrailResult;
  latency_breakdown: LatencyBreakdown;
  model: string;
  answer_source: string;
  detected_lang?: string;
}

// Internal metric type for the frontend
export interface BenchmarkMetrics {
  p50: number | null;
  p70: number | null;
  p100: number | null;
}
