"use client";

import { useState } from "react";
import { Bot, User, Loader2, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface HandoffButtonProps {
  botActive: boolean;
  conversationId: string;
  onToggle: (botActive: boolean) => Promise<void>;
}

export function HandoffButton({
  botActive,
  conversationId,
  onToggle,
}: HandoffButtonProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setLoading(true);
    setError(null);
    try {
      await onToggle(!botActive);
    } catch {
      setError("Falha ao alternar modo");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center gap-3">
      {/* Status indicator */}
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "w-1.5 h-1.5 rounded-full animate-pulse-dot",
            botActive ? "bg-amber-DEFAULT" : "bg-emerald-DEFAULT"
          )}
        />
        <span className="text-xs text-text-secondary">
          {botActive ? "Bot ativo" : "Atendimento humano"}
        </span>
      </div>

      {error && (
        <span className="flex items-center gap-1 text-xs text-crimson">
          <AlertTriangle size={11} />
          {error}
        </span>
      )}

      <button
        onClick={handleClick}
        disabled={loading}
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all border",
          botActive
            ? "bg-emerald-glow border-emerald-dim text-emerald-DEFAULT hover:bg-emerald-900/30 hover:border-emerald-DEFAULT"
            : "bg-amber-glow border-amber-dim text-amber-DEFAULT hover:bg-amber-900/30 hover:border-amber-DEFAULT",
          loading && "opacity-50 cursor-not-allowed"
        )}
      >
        {loading ? (
          <Loader2 size={13} className="animate-spin" />
        ) : botActive ? (
          <User size={13} />
        ) : (
          <Bot size={13} />
        )}
        {loading
          ? "Aguarde..."
          : botActive
          ? "Assumir conversa"
          : "Devolver ao bot"}
      </button>
    </div>
  );
}
