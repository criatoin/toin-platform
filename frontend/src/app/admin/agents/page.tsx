"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import { AgentConfig } from "@/components/admin/AgentConfig";
import { Bot, Sparkles, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface AgentData {
  id: string;
  name: string;
  directive_key: string;
  llm_provider: string;
  llm_model: string;
  settings: Record<string, unknown>;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const { data } = await supabase.from("agents").select("*");
      setAgents(data ?? []);
      setLoading(false);
    }
    load();
  }, []);

  async function handleSave(agentId: string, updates: Partial<AgentData>) {
    await supabase.from("agents").update(updates).eq("id", agentId);
    setAgents((prev) =>
      prev.map((a) => (a.id === agentId ? { ...a, ...updates } : a))
    );
  }

  return (
    <div className="min-h-screen bg-base-950 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-1">
          <Sparkles size={18} className="text-amber-DEFAULT" />
          <h1
            className="text-2xl font-bold text-text-primary"
            style={{ fontFamily: "var(--font-syne)" }}
          >
            Agentes de IA
          </h1>
        </div>
        <p className="text-sm text-text-muted">
          Configure os agentes de atendimento do seu tenant
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 size={24} className="text-amber-DEFAULT animate-spin" />
        </div>
      ) : agents.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 gap-4 text-center">
          <div className="w-14 h-14 rounded-2xl bg-base-800 border border-border flex items-center justify-center">
            <Bot size={22} className="text-text-muted" />
          </div>
          <div>
            <p className="text-sm font-medium text-text-secondary">
              Nenhum agente configurado
            </p>
            <p className="text-xs text-text-muted mt-1">
              Crie uma instância WhatsApp primeiro para gerar um agente
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <AgentConfig
              key={agent.id}
              agent={agent}
              onSave={(updates) => handleSave(agent.id, updates)}
            />
          ))}
        </div>
      )}

      {/* Stats footer */}
      {!loading && agents.length > 0 && (
        <div className="mt-8 pt-6 border-t border-border flex items-center gap-6">
          <span className="text-xs text-text-muted">
            <span className="font-semibold text-text-secondary">{agents.length}</span>{" "}
            {agents.length === 1 ? "agente" : "agentes"} configurado{agents.length !== 1 ? "s" : ""}
          </span>
          <span className="text-xs font-mono text-text-muted">
            Modelo padrão:{" "}
            <span className="text-amber-DEFAULT">llama-3.3-70b-versatile</span>
          </span>
        </div>
      )}
    </div>
  );
}
