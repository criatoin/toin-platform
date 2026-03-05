"use client";

import { useState } from "react";
import { Bot, Save, Loader2, ChevronDown, Cpu } from "lucide-react";
import { cn } from "@/lib/utils";

interface AgentData {
  id: string;
  name: string;
  directive_key: string;
  llm_provider: string;
  llm_model: string;
  settings: Record<string, unknown>;
}

interface AgentConfigProps {
  agent: AgentData;
  onSave: (updates: Partial<AgentData>) => Promise<void>;
}

const LLM_MODELS = [
  { provider: "groq", model: "llama-3.3-70b-versatile", label: "LLaMA 3.3 70B (Groq)" },
  { provider: "groq", model: "llama-3.1-8b-instant", label: "LLaMA 3.1 8B Instant (Groq)" },
  { provider: "groq", model: "mixtral-8x7b-32768", label: "Mixtral 8x7B (Groq)" },
];

export function AgentConfig({ agent, onSave }: AgentConfigProps) {
  const [name, setName] = useState(agent.name);
  const [model, setModel] = useState(agent.llm_model);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  async function handleSave() {
    setSaving(true);
    setSaved(false);
    try {
      await onSave({ name, llm_model: model });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } finally {
      setSaving(false);
    }
  }

  const selectedModel = LLM_MODELS.find((m) => m.model === model);
  const isDirty = name !== agent.name || model !== agent.llm_model;

  return (
    <div className="bg-base-900 border border-border rounded-xl p-5 space-y-5 animate-fade-up">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-amber-glow border border-amber-dim/50 flex items-center justify-center">
          <Bot size={16} className="text-amber-DEFAULT" />
        </div>
        <div>
          <h3
            className="text-sm font-bold text-text-primary leading-none"
            style={{ fontFamily: "var(--font-syne)" }}
          >
            {agent.name}
          </h3>
          <p className="text-xs font-mono text-text-muted mt-0.5">
            {agent.id.slice(0, 8)}
          </p>
        </div>
      </div>

      <div className="h-px bg-border" />

      {/* Name */}
      <div>
        <label className="block text-xs font-medium text-text-secondary mb-1.5">
          Nome do agente
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full bg-base-800 border border-border rounded-lg px-3.5 py-2.5 text-sm text-text-primary focus:outline-none focus:border-amber-dim transition-colors"
        />
      </div>

      {/* Directive */}
      <div>
        <label className="block text-xs font-medium text-text-secondary mb-1.5">
          Diretiva ativa
        </label>
        <div className="flex items-center gap-2 px-3.5 py-2.5 bg-base-800 border border-border rounded-lg">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-DEFAULT" />
          <span className="text-sm font-mono text-text-secondary">
            {agent.directive_key}
          </span>
          <span className="ml-auto text-[10px] font-mono text-text-muted uppercase">
            Ativo
          </span>
        </div>
      </div>

      {/* LLM Model */}
      <div>
        <label className="block text-xs font-medium text-text-secondary mb-1.5">
          Modelo LLM
        </label>
        <div className="relative">
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full appearance-none bg-base-800 border border-border rounded-lg px-3.5 py-2.5 text-sm text-text-primary focus:outline-none focus:border-amber-dim transition-colors pr-9"
          >
            {LLM_MODELS.map((m) => (
              <option key={m.model} value={m.model}>
                {m.label}
              </option>
            ))}
          </select>
          <ChevronDown
            size={14}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none"
          />
        </div>

        {/* Model info chip */}
        <div className="flex items-center gap-2 mt-2">
          <Cpu size={11} className="text-text-muted" />
          <span className="text-[11px] text-text-muted font-mono">
            {selectedModel?.provider ?? "groq"} ·{" "}
            {model}
          </span>
        </div>
      </div>

      {/* Save */}
      <button
        onClick={handleSave}
        disabled={!isDirty || saving}
        className={cn(
          "w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all border",
          isDirty && !saving
            ? "bg-amber-DEFAULT text-base-950 border-transparent hover:bg-amber-DEFAULT/90"
            : saved
            ? "bg-emerald-glow border-emerald-dim text-emerald-DEFAULT"
            : "bg-base-700 border-border text-text-muted cursor-not-allowed"
        )}
      >
        {saving ? (
          <Loader2 size={14} className="animate-spin" />
        ) : (
          <Save size={14} />
        )}
        {saving ? "Salvando…" : saved ? "Salvo!" : "Salvar alterações"}
      </button>
    </div>
  );
}
