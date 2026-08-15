# System Data-Flow Document (USER_FLOW.md)

This document describes the actual user experience and active data-flow architecture of the HH Goa Voice RAG system, reflecting the current implemented state.

---

## FLOW 1 — OPEN APPLICATION

```text
User opens frontend
↓
Frontend loads
↓
Backend health state is checked
↓
User sees application ready state
```

**Actual UI Experience:** The Next.js frontend mounts the `VoiceRecorder` component dynamically (avoiding SSR issues with `window` objects). The application defaults to an "Idle" state, displaying the Language Selector and the microphone button.

---

## FLOW 2 — SELECT LANGUAGE

```text
User opens language selector
↓
Selects one of 14 supported languages
↓
Selected language is displayed
```

**Supported Languages (14):**
- Assamese (`as`)
- Bengali (`bn`)
- Gujarati (`gu`)
- Hindi (`hi`)
- Kannada (`kn`)
- Malayalam (`ml`)
- Marathi (`mr`)
- Nepali (`ne`)
- Odia (`or` — mapped to `od-IN` internally for Sarvam)
- Punjabi (`pa`)
- Sanskrit (`sa`)
- Tamil (`ta`)
- Telugu (`te`)
- Urdu (`ur`)

---

## FLOW 3 — ASK A VOICE QUESTION

```text
User selects language
↓
User presses microphone
↓
Browser requests microphone permission
↓
User speaks
↓
Recording state is displayed
↓
User finishes speaking
↓
Audio is submitted
```

**Implementation Detail:** The `VoiceRecorder` component uses the `react-media-recorder` hook to capture a `WAV` blob at `16 kHz mono`. When the user stops recording, the WAV blob and language code are dispatched to the Next.js API proxy route, which forwards it as a `multipart/form-data` request to the FastAPI backend.

---

## FLOW 4 — PROCESSING

The backend orchestrates the request exactly in this required order:

```text
End of speech
↓
Sarvam STT
↓
Safety guardrail
↓
Query embedding
↓
Five concurrent retrieval strategies
    P
    S
    W
    SM
    H
↓
Merge + dedupe
↓
Cosine rerank
↓
Off-topic guardrail
↓
Groq openai/gpt-oss-20b
↓
Grounding check
↓
Response
```

**Implementation Detail:** 
- Embedding occurs *before* retrieval.
- Retrieval executes across all five Pinecone strategies *concurrently* using `asyncio.gather`.
- There is no second LLM in the loop; `openai/gpt-oss-20b` is the exclusive generator.

---

## SUCCESSFUL ANSWER FLOW

```text
Backend response
↓
Transcript shown
↓
Detected language shown
↓
Answer shown
↓
Top-3 retrieved context available
↓
Guardrail status shown
↓
Latency breakdown shown
↓
P50/P70/P100 shown when benchmark data exists
```

**UI Distinction:** The application strictly separates the *Per-request latency* (rendered dynamically in the Latency Dashboard) from the *Benchmark distribution* (P50/P70/P100), ensuring users don't confuse individual speeds with the overall deployed target metrics.

---

## GUARDRAIL USER FLOWS

### Unsafe input
```text
User speaks unsafe query
↓
Safety guardrail blocks
↓
No normal answer displayed
↓
UI shows unsafe_input
```

### Off-topic
```text
User asks unrelated question
↓
Off-topic guardrail blocks
↓
UI shows off_topic
↓
No normal answer displayed
```

### Grounding failure
```text
Generation occurs
↓
Grounding check fails
↓
Ungrounded answer is not presented as valid
↓
UI shows hallucination_detected
```

---

## ERROR FLOWS

The frontend handles failures gracefully without crashing:

- **Microphone permission denied:** Browser blocks access; UI remains idle and displays a prompt to allow permissions.
- **Backend unavailable:** Next.js proxy returns a 500/504; UI renders an "Error" state notifying the user the server is unreachable.
- **STT failure:** Backend returns an empty transcript; pipeline returns a graceful error to the UI.
- **Retrieval unavailable:** Returns an empty candidate array. The LLM will fall back to "I don't know" or the request is safely aborted.
- **LLM timeout (2.0s):** The generator falls back immediately to the best retrieved grounded chunk.
- **Request timeout:** Frontend network catch block displays a generic error message.
- **Malformed response:** The strict TypeScript schema parsing will reject invalid formats and display an error to avoid corrupt UI rendering.

---

## LATENCY MEASUREMENT FLOW

```text
Clock starts:
END OF SPEECH

Clock ends:
FIRST TOKEN ON SCREEN
```

**Telemetry Lifecycle:**
```text
Per-step telemetry
↓
Total request latency
↓
Rolling last-10 average
↓
Benchmark P50/P70/P100
```

> [!IMPORTANT]
> The P50/P70/P100 metrics represent **benchmark results**, not individual request projections. Only actual deployed benchmark results are labelled as measured. Currently, these are labeled as:
> `P50: pending deployed benchmark`
> `P70: pending deployed benchmark`
> `P100: pending deployed benchmark`

---

## DEMO FLOW

The designated demonstration sequence executes as follows:

```text
Hindi
↓
Tamil
↓
Sanskrit
↓
Assamese
↓
Nepali
↓
Guardrail rejection
↓
Latency metrics
```

### Sanskrit-Specific Drill Down
```text
Sanskrit selected
↓
User speaks Sanskrit
↓
Transcript visible
↓
Answer visible
↓
LatencyDashboard remains visible
↓
Measured latency can be captured
```
*(Note: No projected latency numbers are shown during the live demo; only actual measurements are displayed).*
