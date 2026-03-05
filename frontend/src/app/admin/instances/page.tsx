"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { QRCodePanel } from "@/components/admin/QRCodePanel";
import {
  Wifi,
  WifiOff,
  QrCode,
  RefreshCw,
  Plus,
  Phone,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface WhatsAppInstance {
  id: string;
  tenant_id: string;
  instance_name: string;
  phone_number?: string;
  status: "connected" | "disconnected" | "qr_pending";
  provider: string;
  created_at: string;
}

const STATUS_CONFIG = {
  connected: {
    label: "Conectado",
    icon: Wifi,
    color: "text-emerald-DEFAULT",
    bg: "bg-emerald-glow border-emerald-dim/50",
    dot: "bg-emerald-DEFAULT",
  },
  disconnected: {
    label: "Desconectado",
    icon: WifiOff,
    color: "text-crimson",
    bg: "bg-crimson/10 border-crimson/30",
    dot: "bg-crimson",
  },
  qr_pending: {
    label: "Aguardando QR",
    icon: QrCode,
    color: "text-amber-DEFAULT",
    bg: "bg-amber-glow border-amber-dim/50",
    dot: "bg-amber-DEFAULT animate-pulse-dot",
  },
};

export default function InstancesPage() {
  const [instances, setInstances] = useState<WhatsAppInstance[]>([]);
  const [loading, setLoading] = useState(true);
  const [reconnecting, setReconnecting] = useState<string | null>(null);
  const [qrPanel, setQrPanel] = useState<WhatsAppInstance | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.whatsapp.instances.list();
        setInstances(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleReconnect(inst: WhatsAppInstance) {
    setReconnecting(inst.id);
    try {
      await api.whatsapp.instances.reconnect(inst.id);
      setInstances((prev) =>
        prev.map((i) =>
          i.id === inst.id ? { ...i, status: "qr_pending" } : i
        )
      );
    } catch (e) {
      console.error(e);
    } finally {
      setReconnecting(null);
    }
  }

  return (
    <div className="min-h-screen bg-base-950 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1
              className="text-2xl font-bold text-text-primary"
              style={{ fontFamily: "var(--font-syne)" }}
            >
              Instâncias WhatsApp
            </h1>
            <p className="text-sm text-text-muted mt-1">
              Gerencie as conexões WhatsApp do seu tenant
            </p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-amber-DEFAULT text-base-950 rounded-lg text-sm font-semibold hover:bg-amber-DEFAULT/90 transition-colors">
            <Plus size={15} />
            Nova instância
          </button>
        </div>

        {/* Stats bar */}
        {!loading && (
          <div className="flex items-center gap-6 mt-4">
            {(["connected", "qr_pending", "disconnected"] as const).map((s) => {
              const count = instances.filter((i) => i.status === s).length;
              const cfg = STATUS_CONFIG[s];
              return (
                <div key={s} className="flex items-center gap-2">
                  <span className={cn("w-2 h-2 rounded-full", cfg.dot)} />
                  <span className="text-xs text-text-muted">
                    <span className={cn("font-semibold", cfg.color)}>
                      {count}
                    </span>{" "}
                    {cfg.label}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="bg-base-900 border border-border rounded-xl p-5 h-32 animate-pulse"
            />
          ))}
        </div>
      ) : instances.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 gap-4 text-center">
          <div className="w-14 h-14 rounded-2xl bg-base-800 border border-border flex items-center justify-center">
            <Phone size={22} className="text-text-muted" />
          </div>
          <div>
            <p className="text-sm font-medium text-text-secondary">
              Nenhuma instância configurada
            </p>
            <p className="text-xs text-text-muted mt-1">
              Crie sua primeira instância WhatsApp
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {instances.map((inst, i) => {
            const cfg = STATUS_CONFIG[inst.status];
            const Icon = cfg.icon;

            return (
              <div
                key={inst.id}
                className="bg-base-900 border border-border rounded-xl p-5 hover:border-base-500 transition-colors animate-fade-up"
                style={{ animationDelay: `${i * 60}ms` }}
              >
                {/* Instance header */}
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3
                      className="text-sm font-bold text-text-primary"
                      style={{ fontFamily: "var(--font-syne)" }}
                    >
                      {inst.instance_name}
                    </h3>
                    {inst.phone_number && (
                      <p className="text-xs font-mono text-text-muted mt-0.5">
                        {inst.phone_number}
                      </p>
                    )}
                  </div>
                  <span
                    className={cn(
                      "flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider px-2 py-1 rounded-md border",
                      cfg.bg,
                      cfg.color
                    )}
                  >
                    <Icon size={10} />
                    {cfg.label}
                  </span>
                </div>

                <p className="text-[10px] font-mono text-text-muted mb-4 uppercase">
                  {inst.provider}
                </p>

                {/* Actions */}
                <div className="flex gap-2">
                  {inst.status !== "connected" && (
                    <button
                      onClick={() => setQrPanel(inst)}
                      className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-amber-glow border border-amber-dim/50 text-xs text-amber-DEFAULT font-semibold hover:bg-amber-900/30 transition-colors"
                    >
                      <QrCode size={12} />
                      Ver QR Code
                    </button>
                  )}
                  <button
                    onClick={() => handleReconnect(inst)}
                    disabled={reconnecting === inst.id}
                    className={cn(
                      "flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-base-700 border border-border text-xs text-text-secondary font-medium hover:text-text-primary hover:border-base-500 transition-colors",
                      reconnecting === inst.id && "opacity-50 cursor-not-allowed"
                    )}
                  >
                    {reconnecting === inst.id ? (
                      <Loader2 size={12} className="animate-spin" />
                    ) : (
                      <RefreshCw size={12} />
                    )}
                    Reconectar
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* QR Panel modal */}
      {qrPanel && (
        <QRCodePanel
          instanceId={qrPanel.id}
          instanceName={qrPanel.instance_name}
          onClose={() => setQrPanel(null)}
          onConnected={() => {
            setInstances((prev) =>
              prev.map((i) =>
                i.id === qrPanel.id ? { ...i, status: "connected" } : i
              )
            );
            setQrPanel(null);
          }}
        />
      )}
    </div>
  );
}
