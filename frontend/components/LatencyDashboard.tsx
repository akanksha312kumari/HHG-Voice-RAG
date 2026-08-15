import React, { useEffect, useState } from "react";
import { Activity, Clock } from "lucide-react";
import { LatencyBreakdown, BenchmarkMetrics } from "../lib/types";

interface LatencyDashboardProps {
  latency: LatencyBreakdown | null;
  metrics: BenchmarkMetrics | null;
}

export default function LatencyDashboard({ latency, metrics }: LatencyDashboardProps) {
  const [rollingAvg, setRollingAvg] = useState<number | null>(null);

  useEffect(() => {
    if (latency?.total_ms) {
      // Basic rolling average of last 10 queries
      const stored = localStorage.getItem("rollingLatency");
      let history: number[] = stored ? JSON.parse(stored) : [];
      history.push(latency.total_ms);
      if (history.length > 10) history = history.slice(-10);
      
      localStorage.setItem("rollingLatency", JSON.stringify(history));
      const avg = history.reduce((a, b) => a + b, 0) / history.length;
      setRollingAvg(Math.round(avg));
    }
  }, [latency]);

  const Item = ({ label, value }: { label: string; value?: number }) => (
    <div className="flex justify-between items-center text-sm py-1 border-b border-zinc-800/50 last:border-0">
      <span className="text-slate-400">{label}</span>
      <span className="font-mono text-slate-200">{value !== undefined ? `${value} ms` : "-"}</span>
    </div>
  );

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex flex-col gap-5">
      <div className="flex items-center gap-2 border-b border-zinc-800 pb-3">
        <Activity size={18} className="text-teal-400" />
        <h2 className="text-lg font-bold text-slate-100">Telemetry</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Live Latency</h3>
          <div className="bg-zinc-950 p-3 rounded-lg border border-zinc-800/50">
            {latency ? (
              <>
                <Item label="STT" value={latency.stt_ms} />
                <Item label="Embedding" value={latency.embedding_ms} />
                <Item label="Retrieval" value={latency.retrieval_ms} />
                <Item label="Rerank" value={latency.rerank_ms} />
                <Item label="Guardrail" value={latency.off_topic_ms} />
                <Item label="Generation" value={latency.generation_ms} />
                <Item label="Grounding" value={latency.grounding_ms} />
                <div className="flex justify-between items-center text-sm py-2 mt-1 border-t border-zinc-800">
                  <span className="font-bold text-slate-300">Total</span>
                  <span className="font-mono font-bold text-teal-400">{latency.total_ms} ms</span>
                </div>
              </>
            ) : (
              <div className="text-sm text-slate-500 py-4 text-center">Awaiting query...</div>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-4">
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Benchmarks (Measured)</h3>
            <div className="bg-zinc-950 p-3 rounded-lg border border-zinc-800/50 flex flex-col gap-2">
              <Item label="P50" value={metrics?.p50 ?? undefined} />
              <Item label="P70" value={metrics?.p70 ?? undefined} />
              <Item label="P100" value={metrics?.p100 ?? undefined} />
              {!metrics?.p50 && (
                <div className="text-xs text-amber-500/80 mt-1 flex justify-center">Benchmark pending</div>
              )}
            </div>
          </div>
          
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-2">
              <Clock size={12} /> Rolling Average
            </h3>
            <div className="bg-zinc-950 px-4 py-3 rounded-lg border border-zinc-800/50 flex items-center justify-between">
              <span className="text-sm text-slate-400">Last 10 queries</span>
              <span className="font-mono text-lg font-semibold text-slate-200">
                {rollingAvg !== null ? `${rollingAvg} ms` : "-"}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

