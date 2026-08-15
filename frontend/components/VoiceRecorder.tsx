"use client";

import React, { useEffect } from "react";
import { useReactMediaRecorder } from "react-media-recorder";
import { Mic, Square, Loader2, AlertCircle } from "lucide-react";

type RecorderState = "idle" | "recording" | "processing" | "completed" | "error";

interface VoiceRecorderProps {
  onAudioReady: (blob: Blob) => void;
  appState: RecorderState;
  errorMessage?: string;
  onRetry: () => void;
}

export default function VoiceRecorder({ onAudioReady, appState, errorMessage, onRetry }: VoiceRecorderProps) {
  const { status, startRecording, stopRecording, mediaBlobUrl, error } = useReactMediaRecorder({
    audio: true,
    video: false,
    mediaRecorderOptions: {
      mimeType: "audio/webm", // Standard fallback, we instruct backend to expect WebM/WAV handling via API if strictly required
    },
  });

  useEffect(() => {
    const fetchBlob = async () => {
      if (mediaBlobUrl && status === "stopped") {
        const response = await fetch(mediaBlobUrl);
        const blob = await response.blob();
        onAudioReady(blob);
      }
    };
    fetchBlob();
  }, [mediaBlobUrl, status, onAudioReady]);

  if (appState === "error" || error) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-rose-950/20 rounded-2xl border border-rose-900/30 gap-4">
        <AlertCircle size={40} className="text-rose-500" />
        <div className="text-center">
          <h3 className="font-semibold text-rose-400">Error Recording</h3>
          <p className="text-sm text-rose-300/80 mt-1">
            {errorMessage || error || "Microphone access is required to ask a voice question."}
          </p>
        </div>
        <button 
          onClick={onRetry}
          className="px-4 py-2 bg-rose-500/20 text-rose-400 font-medium rounded-lg hover:bg-rose-500/30 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center p-12 bg-zinc-900 rounded-3xl border border-zinc-800 shadow-xl relative overflow-hidden">
      {appState === "recording" && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-32 h-32 bg-rose-500/10 rounded-full animate-ping" />
        </div>
      )}
      
      <div className="relative z-10 flex flex-col items-center gap-6">
        {appState === "idle" || appState === "completed" ? (
          <button
            onClick={startRecording}
            className="w-24 h-24 bg-teal-500 hover:bg-teal-400 text-zinc-950 rounded-full flex items-center justify-center shadow-lg shadow-teal-500/20 transition-transform hover:scale-105"
            aria-label="Start recording"
          >
            <Mic size={40} />
          </button>
        ) : appState === "recording" ? (
          <button
            onClick={stopRecording}
            className="w-24 h-24 bg-rose-500 hover:bg-rose-400 text-zinc-950 rounded-full flex items-center justify-center shadow-lg shadow-rose-500/20 transition-transform hover:scale-105"
            aria-label="Stop recording"
          >
            <Square size={32} className="fill-current" />
          </button>
        ) : (
          <div className="w-24 h-24 bg-zinc-800 text-teal-500 rounded-full flex items-center justify-center shadow-lg">
            <Loader2 size={40} className="animate-spin" />
          </div>
        )}

        <div className="text-center">
          <h2 className="text-xl font-semibold text-slate-100">
            {appState === "idle" || appState === "completed" 
              ? "Ask a question" 
              : appState === "recording" 
                ? "Listening..." 
                : "Processing..."}
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            {appState === "idle" || appState === "completed" 
              ? "Press the microphone to speak" 
              : appState === "recording"
                ? "Tap to stop"
                : "Analyzing and retrieving context"}
          </p>
        </div>
      </div>
    </div>
  );
}

