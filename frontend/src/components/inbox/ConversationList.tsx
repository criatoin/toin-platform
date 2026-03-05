"use client";

import { useState } from "react";
import { formatDistanceToNowStrict } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Search, Bot, User, SlidersHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Conversation } from "@/types";

interface ConversationListProps {
  conversations: Conversation[];
  selectedId: string | null;
  onSelect: (conv: Conversation) => void;
  loading?: boolean;
}

function getInitials(name?: string, phone?: string): string {
  if (name) {
    const parts = name.trim().split(" ");
    return parts.length > 1
      ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
      : parts[0].slice(0, 2).toUpperCase();
  }
  return phone?.slice(-2) ?? "??";
}

function getAvatarColor(id: string): string {
  const colors = [
    "bg-violet-900/60 text-violet-300",
    "bg-cyan-900/60 text-cyan-300",
    "bg-rose-900/60 text-rose-300",
    "bg-amber-900/60 text-amber-300",
    "bg-emerald-900/60 text-emerald-300",
    "bg-sky-900/60 text-sky-300",
    "bg-orange-900/60 text-orange-300",
  ];
  const idx = id.charCodeAt(0) % colors.length;
  return colors[idx];
}

function SkeletonRow() {
  return (
    <div className="flex items-center gap-3 px-4 py-3">
      <div className="w-10 h-10 rounded-full bg-base-600 animate-pulse shrink-0" />
      <div className="flex-1 space-y-2">
        <div className="h-3 bg-base-600 rounded animate-pulse w-2/3" />
        <div className="h-2.5 bg-base-700 rounded animate-pulse w-4/5" />
      </div>
      <div className="h-2 bg-base-600 rounded animate-pulse w-8" />
    </div>
  );
}

export function ConversationList({
  conversations,
  selectedId,
  onSelect,
  loading,
}: ConversationListProps) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "bot" | "human">("all");

  const filtered = conversations.filter((c) => {
    const name = c.contacts?.name ?? c.contacts?.phone ?? "";
    const matchesSearch = name.toLowerCase().includes(search.toLowerCase());
    const matchesFilter =
      filter === "all"
        ? true
        : filter === "bot"
        ? c.bot_active
        : !c.bot_active;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 pt-5 pb-3 border-b border-border">
        <div className="flex items-center justify-between mb-3">
          <h1
            className="text-base font-bold tracking-tight text-text-primary"
            style={{ fontFamily: "var(--font-syne)" }}
          >
            Conversas
          </h1>
          <span className="text-xs font-mono text-text-muted tabular-nums">
            {filtered.length}
          </span>
        </div>

        {/* Search */}
        <div className="relative">
          <Search
            className="absolute left-2.5 top-1/2 -translate-y-1/2 text-text-muted"
            size={13}
          />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar contato..."
            className="w-full bg-base-700 border border-border rounded-lg pl-8 pr-3 py-2 text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:border-amber-dim focus:bg-base-600 transition-colors"
          />
        </div>

        {/* Filter tabs */}
        <div className="flex gap-1 mt-2.5">
          {(["all", "bot", "human"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md text-xs font-medium transition-all",
                filter === f
                  ? f === "bot"
                    ? "bg-amber-glow text-amber border border-amber-dim"
                    : f === "human"
                    ? "bg-emerald-glow text-emerald-DEFAULT border border-emerald-dim"
                    : "bg-base-600 text-text-primary border border-border"
                  : "text-text-muted hover:text-text-secondary hover:bg-base-700"
              )}
            >
              {f === "bot" && <Bot size={10} />}
              {f === "human" && <User size={10} />}
              {f === "all" ? "Todos" : f === "bot" ? "Bot" : "Humano"}
            </button>
          ))}
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <>
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonRow key={i} />
            ))}
          </>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-40 gap-2">
            <SlidersHorizontal size={20} className="text-text-muted" />
            <p className="text-xs text-text-muted">Nenhuma conversa</p>
          </div>
        ) : (
          filtered.map((conv, i) => {
            const isSelected = conv.id === selectedId;
            const contact = conv.contacts;
            const initials = getInitials(contact?.name, contact?.phone);
            const avatarColor = getAvatarColor(conv.id);
            const lastMsg =
              conv.messages?.[conv.messages.length - 1];
            const timeAgo = lastMsg
              ? formatDistanceToNowStrict(new Date(lastMsg.created_at), {
                  locale: ptBR,
                  addSuffix: false,
                })
              : formatDistanceToNowStrict(new Date(conv.updated_at), {
                  locale: ptBR,
                  addSuffix: false,
                });

            return (
              <button
                key={conv.id}
                onClick={() => onSelect(conv)}
                style={{ animationDelay: `${i * 30}ms` }}
                className={cn(
                  "w-full flex items-start gap-3 px-4 py-3 border-b border-border/50 text-left transition-all animate-fade-up",
                  isSelected
                    ? "bg-base-700 border-l-2 border-l-amber-DEFAULT"
                    : "hover:bg-base-800/80 border-l-2 border-l-transparent"
                )}
              >
                {/* Avatar */}
                <div
                  className={cn(
                    "w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5",
                    avatarColor
                  )}
                >
                  {initials}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-0.5">
                    <span
                      className={cn(
                        "text-sm font-semibold truncate",
                        isSelected ? "text-text-primary" : "text-text-secondary"
                      )}
                    >
                      {contact?.name ?? contact?.phone ?? "Desconhecido"}
                    </span>
                    <span className="text-[10px] font-mono text-text-muted shrink-0 tabular-nums">
                      {timeAgo}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    {/* Bot/Human indicator */}
                    <span
                      className={cn(
                        "inline-flex items-center gap-1 text-[9px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded",
                        conv.bot_active
                          ? "bg-amber-glow text-amber-DEFAULT"
                          : "bg-emerald-glow text-emerald-DEFAULT"
                      )}
                    >
                      {conv.bot_active ? (
                        <Bot size={8} />
                      ) : (
                        <User size={8} />
                      )}
                      {conv.bot_active ? "Bot" : "Humano"}
                    </span>

                    {lastMsg && (
                      <span className="text-xs text-text-muted truncate">
                        {lastMsg.content.length > 35
                          ? lastMsg.content.slice(0, 35) + "…"
                          : lastMsg.content}
                      </span>
                    )}
                  </div>
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
