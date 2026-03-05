"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { QrCode, Loader2, RefreshCw, CheckCircle2, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface QRCodePanelProps {
  instanceId: string;
  instanceName: string;
  onClose: () => void;
  onConnected?: () => void;
}

export function QRCodePanel({
  instanceId,
  instanceName,
  onClose,
  onConnected,
}: QRCodePanelProps) {
  const [qrBase64, setQrBase64] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attempts, setAttempts] = useState(0);

  const fetchQR = useCallback(async () => {
    setError(null);
    try {
      const data = await api.whatsapp.instances.qrcode(instanceId);
      if (data.qrcode_base64) {
        setQrBase64(data.qrcode_base64);
        setAttempts((n) => n + 1);
      }
    } catch {
      setError("Falha ao carregar QR code. Tente reconectar.");
    } finally {
      setLoading(false);
    }
  }, [instanceId]);

  // Poll every 3s for QR refresh
  useEffect(() => {
    fetchQR();
    const interval = setInterval(fetchQR, 3000);
    return () => clearInterval(interval);
  }, [fetchQR]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm animate-fade-up">
      <div className="bg-base-900 border border-border rounded-2xl p-6 w-full max-w-sm shadow-2xl relative">
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-7 h-7 rounded-lg bg-base-700 hover:bg-base-600 flex items-center justify-center transition-colors"
        >
          <X size={13} className="text-text-muted" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-5">
          <div className="w-9 h-9 rounded-lg bg-amber-glow border border-amber-dim/50 flex items-center justify-center">
            <QrCode size={16} className="text-amber-DEFAULT" />
          </div>
          <div>
            <h3
              className="text-sm font-bold text-text-primary leading-none"
              style={{ fontFamily: "var(--font-syne)" }}
            >
              Conectar WhatsApp
            </h3>
            <p className="text-xs text-text-muted mt-0.5 font-mono">
              {instanceName}
            </p>
          </div>
        </div>

        {/* QR Area */}
        <div className="relative flex items-center justify-center bg-base-800 border border-border rounded-xl p-4 mb-4 min-h-[220px]">
          {loading && !qrBase64 ? (
            <div className="flex flex-col items-center gap-3">
              <Loader2 size={24} className="text-amber-DEFAULT animate-spin" />
              <p className="text-xs text-text-muted">Gerando QR code…</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center gap-3 text-center">
              <p className="text-xs text-crimson">{error}</p>
              <button
                onClick={() => { setLoading(true); fetchQR(); }}
                className="flex items-center gap-1.5 text-xs text-amber-DEFAULT hover:text-amber-DEFAULT/80 transition-colors"
              >
                <RefreshCw size={12} />
                Tentar novamente
              </button>
            </div>
          ) : qrBase64 ? (
            <>
              <img
                src={qrBase64.startsWith("data:") ? qrBase64 : `data:image/png;base64,${qrBase64}`}
                alt="QR Code WhatsApp"
                className="w-48 h-48 object-contain rounded-lg"
              />
              {/* Refresh shimmer overlay */}
              {loading && (
                <div className="absolute inset-0 rounded-xl bg-base-800/60 flex items-center justify-center">
                  <RefreshCw size={18} className="text-amber-DEFAULT animate-spin" />
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Instructions */}
        <ol className="space-y-1.5 mb-4">
          {[
            "Abra o WhatsApp no celular",
            "Toque em Menu > Dispositivos Vinculados",
            "Escaneie o QR code acima",
          ].map((step, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-text-secondary">
              <span className="w-4 h-4 rounded-full bg-base-600 border border-border flex items-center justify-center text-[9px] font-bold text-text-muted shrink-0 mt-0.5">
                {i + 1}
              </span>
              {step}
            </li>
          ))}
        </ol>

        {/* Polling indicator */}
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-1.5 text-[10px] text-text-muted font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-DEFAULT animate-pulse-dot" />
            Atualizando a cada 3s
          </span>
          <span className="text-[10px] font-mono text-text-muted">
            #{attempts}
          </span>
        </div>
      </div>
    </div>
  );
}
