import React from "react";
import { ShieldAlert, ShieldCheck } from "lucide-react";
import { GuardrailResult } from "../lib/types";

interface GuardrailBadgeProps {
  guardrail: GuardrailResult | null;
}

export default function GuardrailBadge({ guardrail }: GuardrailBadgeProps) {
  if (!guardrail) return null;

  if (guardrail.blocked) {
    let title = "Request Blocked";
    let desc = "The question could not be answered.";
    
    if (guardrail.reason === "unsafe_input") {
      desc = "Unsafe input detected.";
    } else if (guardrail.reason === "off_topic") {
      desc = "Off-topic query. The question could not be answered from the indexed knowledge base.";
    } else if (guardrail.reason === "hallucination_detected") {
      title = "Answer Blocked";
      desc = "Insufficient grounding. Hallucination detected.";
    }

    return (
      <div className="bg-rose-950/40 border border-rose-900/50 rounded-xl p-4 flex items-start gap-3 text-rose-400">
        <ShieldAlert className="shrink-0 mt-0.5" size={20} />
        <div>
          <h3 className="font-bold text-base">{title}</h3>
          <p className="text-sm opacity-90 mt-1">{desc}</p>
        </div>
      </div>
    );
  }

  // Not blocked
  return (
    <div className="inline-flex items-center gap-1.5 text-xs text-teal-500 bg-teal-500/10 px-2 py-1 rounded-full font-medium border border-teal-500/20">
      <ShieldCheck size={14} />
      Guardrails Passed
    </div>
  );
}

