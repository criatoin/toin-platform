"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";
import { Bot, Loader2, Eye, EyeOff, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const { error } = await supabase.auth.signInWithPassword({ email, password });

    if (error) {
      setError("E-mail ou senha incorretos.");
      setLoading(false);
    } else {
      window.location.href = "/inbox";
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-950 relative overflow-hidden">
      {/* Grid background */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(245,158,11,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(245,158,11,0.5) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      {/* Glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-amber-DEFAULT/5 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 w-full max-w-sm px-4">
        <div className="bg-base-900 border border-border rounded-2xl p-8 shadow-2xl animate-fade-up">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-amber-DEFAULT/10 border border-amber-dim/50 flex items-center justify-center">
              <Bot size={18} className="text-amber-DEFAULT" />
            </div>
            <div>
              <h1
                className="text-lg font-bold text-text-primary leading-none"
                style={{ fontFamily: "var(--font-syne)" }}
              >
                TOIN
              </h1>
              <p className="text-xs text-text-muted">Atendimento Inteligente</p>
            </div>
          </div>

          <h2
            className="text-base font-semibold text-text-primary mb-6"
            style={{ fontFamily: "var(--font-syne)" }}
          >
            Entrar na plataforma
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1.5">
                E-mail
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="voce@empresa.com.br"
                className="w-full bg-base-800 border border-border rounded-lg px-3.5 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-amber-dim focus:bg-base-700 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1.5">
                Senha
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full bg-base-800 border border-border rounded-lg px-3.5 py-2.5 pr-10 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-amber-dim focus:bg-base-700 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary transition-colors"
                >
                  {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2 bg-crimson/10 border border-crimson/30 rounded-lg px-3 py-2.5 text-xs text-crimson animate-fade-up">
                <AlertTriangle size={12} />
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className={cn(
                "w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all",
                "bg-amber-DEFAULT text-base-950 hover:bg-amber-DEFAULT/90 active:scale-[0.98]",
                loading && "opacity-60 cursor-not-allowed"
              )}
            >
              {loading ? (
                <Loader2 size={15} className="animate-spin" />
              ) : null}
              {loading ? "Entrando..." : "Entrar"}
            </button>
          </form>
        </div>

        <p className="text-center text-[11px] text-text-muted mt-4">
          TOIN Plataforma © {new Date().getFullYear()}
        </p>
      </div>
    </div>
  );
}
