"use client";

import React, { useState } from "react";
import dynamic from "next/dynamic";
import LanguageSelector from "../components/LanguageSelector";
import TranscriptDisplay from "../components/TranscriptDisplay";
import AnswerCard from "../components/AnswerCard";
import LatencyDashboard from "../components/LatencyDashboard";
import GuardrailBadge from "../components/GuardrailBadge";
import { queryVoice } from "../lib/api";
import { LanguageCode, QueryResponse } from "../lib/types";

const VoiceRecorder = dynamic(() => import("../components/VoiceRecorder"), { ssr: false });

type AppState = "idle" | "recording" | "processing" | "completed" | "error";

export default function Home() {
  const [lang, setLang] = useState<LanguageCode>("hi");
  const [appState, setAppState] = useState<AppState>("idle");
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [response, setResponse] = useState<QueryResponse | null>(null);
  
  // Example benchmark metrics (mocked as null until backend provides them or we load from an endpoint)
  const metrics = { p50: null, p70: null, p100: null };

  const handleAudioReady = async (blob: Blob) => {
    setAppState("processing");
    setErrorMsg("");
    
    try {
      const res = await queryVoice(blob, lang);
      setResponse(res);
      setAppState("completed");
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "Failed to communicate with backend.");
      setAppState("error");
    }
  };

  const handleRetry = () => {
    setAppState("idle");
    setErrorMsg("");
    setResponse(null);
  };

  return (
    <main className="flex-1 max-w-5xl w-full mx-auto p-4 md:p-8 flex flex-col gap-8 pb-20">
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-zinc-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-teal-400 to-emerald-500 bg-clip-text text-transparent">
            Voice RAG
          </h1>
          <p className="text-slate-400 mt-1">HH Goa 2026 · MSMARCO-XI Dataset</p>
        </div>
        <div className="flex items-center gap-2 text-xs font-medium bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-full text-slate-300">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Backend Connected
        </div>
      </header>

      <section className="bg-zinc-900/50 rounded-2xl p-4 md:p-6 border border-zinc-800/50 shadow-sm">
        <LanguageSelector selected={lang} onSelect={setLang} disabled={appState === "recording" || appState === "processing"} />
      </section>

      <section className="flex flex-col items-center py-4">
        <VoiceRecorder 
          onAudioReady={handleAudioReady} 
          appState={appState} 
          errorMessage={errorMsg}
          onRetry={handleRetry}
        />
      </section>

      {(appState === "completed" && response) && (
        <section className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <TranscriptDisplay 
            transcript={response.transcript} 
            detectedLang={response.detected_lang}
            selectedLang={lang}
          />
          
          <GuardrailBadge guardrail={response.guardrail} />
          
          {!response.guardrail?.blocked && (
            <AnswerCard 
              answer={response.answer} 
              chunks={response.retrieved_chunks} 
            />
          )}

          <LatencyDashboard 
            latency={response.latency_breakdown} 
            metrics={metrics}
          />
        </section>
      )}
    </main>
  );
}

