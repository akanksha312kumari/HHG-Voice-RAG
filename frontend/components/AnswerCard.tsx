import React, { useState } from "react";
import { Sparkles, ChevronDown, ChevronUp, Database } from "lucide-react";
import { RetrievedChunk } from "../lib/types";

interface AnswerCardProps {
  answer: string | null;
  chunks: RetrievedChunk[];
}

export default function AnswerCard({ answer, chunks }: AnswerCardProps) {
  const [showContext, setShowContext] = useState(false);

  if (!answer) return null;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex flex-col gap-4 shadow-lg">
      <div className="flex items-center gap-2 border-b border-zinc-800 pb-3">
        <Sparkles size={18} className="text-amber-400" />
        <h2 className="text-lg font-bold text-slate-100">Answer</h2>
      </div>
      
      <div className="text-slate-200 leading-relaxed text-lg whitespace-pre-wrap">
        {answer}
      </div>

      {chunks.length > 0 && (
        <div className="mt-4 pt-4 border-t border-zinc-800">
          <button 
            onClick={() => setShowContext(!showContext)}
            className="flex items-center justify-between w-full text-sm font-medium text-slate-400 hover:text-slate-300 transition-colors"
          >
            <span className="flex items-center gap-2">
              <Database size={14} /> Retrieved Context ({chunks.length} chunks)
            </span>
            {showContext ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          
          {showContext && (
            <div className="mt-3 flex flex-col gap-3">
              <div className="text-xs text-slate-500 mb-1">
                Strategies used: <span className="font-mono bg-zinc-800 px-1 py-0.5 rounded text-slate-400">P · S · W · SM · H</span>
              </div>
              {chunks.map((chunk, idx) => (
                <div key={idx} className="bg-zinc-950 p-3 rounded-lg border border-zinc-800/50">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-400">
                      Strategy: {chunk.strategy}
                    </span>
                    {chunk.language && (
                      <span className="text-xs text-slate-500">Lang: {chunk.language}</span>
                    )}
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed">
                    {chunk.text}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

