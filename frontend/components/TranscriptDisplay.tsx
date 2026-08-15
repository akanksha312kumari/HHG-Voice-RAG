import React from "react";
import { MessageSquareText } from "lucide-react";

interface TranscriptDisplayProps {
  transcript: string | null;
  detectedLang?: string | null;
  selectedLang: string;
}

export default function TranscriptDisplay({ transcript, detectedLang, selectedLang }: TranscriptDisplayProps) {
  if (!transcript) return null;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
        <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
          <MessageSquareText size={16} className="text-teal-400" />
          You asked
        </h3>
        {detectedLang && (
          <span className="text-xs bg-zinc-800 text-slate-400 px-2 py-1 rounded-md">
            Detected: <span className="font-medium text-slate-300">{detectedLang}</span>
          </span>
        )}
      </div>
      <p className="text-lg text-slate-100">{transcript}</p>
    </div>
  );
}

