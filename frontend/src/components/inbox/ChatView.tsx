"use client";

import { useEffect, useRef } from "react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Bot, User, UserCircle2, Image, FileText, Mic } from "lucide-react";
import { cn } from "@/lib/utils";
import { HandoffButton } from "./HandoffButton";
import type { Conversation, Message } from "@/types";

interface ChatViewProps {
  conversation: Conversation;
  messages: Message[];
  onToggleBot: (botActive: boolean) => Promise<void>;
}

function SenderBadge({ type }: { type: Message["sender_type"] }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-[9px] font-semibold uppercase tracking-widest px-1.5 py-0.5 rounded",
        type === "bot"
          ? "bg-amber-glow text-amber-DEFAULT border border-amber-dim/40"
          : type === "human_agent"
          ? "bg-emerald-glow text-emerald-DEFAULT border border-emerald-dim/40"
          : "bg-base-500 text-text-muted border border-border"
      )}
    >
      {type === "bot" ? (
        <Bot size={8} />
      ) : type === "human_agent" ? (
        <User size={8} />
      ) : (
        <UserCircle2 size={8} />
      )}
      {type === "bot" ? "Bot" : type === "human_agent" ? "Agente" : "Lead"}
    </span>
  );
}

function MediaPreview({ type }: { type?: string }) {
  if (!type) return null;
  const icons = {
    image: <Image size={14} className="text-text-secondary" />,
    audio: <Mic size={14} className="text-text-secondary" />,
    document: <FileText size={14} className="text-text-secondary" />,
  };
  return (
    <span className="flex items-center gap-1 text-xs italic text-text-muted">
      {icons[type as keyof typeof icons]}
      {type === "image" ? "Imagem" : type === "audio" ? "Áudio" : "Documento"}
    </span>
  );
}

function MessageBubble({ msg, index }: { msg: Message; index: number }) {
  const isUser = msg.sender_type === "user";
  const isBot = msg.sender_type === "bot";

  return (
    <div
      className={cn(
        "flex gap-2.5 max-w-[80%] animate-fade-up",
        isUser ? "self-start" : "self-end flex-row-reverse"
      )}
      style={{ animationDelay: `${index * 20}ms` }}
    >
      {/* Avatar dot */}
      <div
        className={cn(
          "w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-1",
          isUser
            ? "bg-base-500"
            : isBot
            ? "bg-amber-900/50 border border-amber-dim/50"
            : "bg-emerald-900/50 border border-emerald-dim/50"
        )}
      >
        {isUser ? (
          <UserCircle2 size={12} className="text-text-muted" />
        ) : isBot ? (
          <Bot size={12} className="text-amber-DEFAULT" />
        ) : (
          <User size={12} className="text-emerald-DEFAULT" />
        )}
      </div>

      {/* Bubble */}
      <div className="flex flex-col gap-1">
        <div
          className={cn(
            "px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed relative",
            isUser
              ? "bg-base-700 border border-border text-text-secondary rounded-tl-sm"
              : isBot
              ? "bg-base-600 border border-amber-dim/20 text-text-primary rounded-tr-sm"
              : "bg-emerald-900/25 border border-emerald-dim/30 text-text-primary rounded-tr-sm"
          )}
        >
          {msg.content ? (
            msg.content
          ) : (
            <MediaPreview type={msg.media_type} />
          )}
        </div>

        {/* Footer */}
        <div
          className={cn(
            "flex items-center gap-2",
            isUser ? "flex-row" : "flex-row-reverse"
          )}
        >
          <SenderBadge type={msg.sender_type} />
          <span className="text-[10px] font-mono text-text-muted tabular-nums">
            {format(new Date(msg.created_at), "HH:mm", { locale: ptBR })}
          </span>
        </div>
      </div>
    </div>
  );
}

function DateDivider({ date }: { date: string }) {
  return (
    <div className="flex items-center gap-3 my-4">
      <div className="flex-1 h-px bg-border" />
      <span className="text-[10px] font-mono text-text-muted uppercase tracking-widest shrink-0">
        {format(new Date(date), "dd 'de' MMMM", { locale: ptBR })}
      </span>
      <div className="flex-1 h-px bg-border" />
    </div>
  );
}

export function ChatView({ conversation, messages, onToggleBot }: ChatViewProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const contact = conversation.contacts;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Group messages by date
  const grouped: { date: string; msgs: Message[] }[] = [];
  for (const msg of messages) {
    const date = msg.created_at.slice(0, 10);
    const last = grouped[grouped.length - 1];
    if (last && last.date === date) {
      last.msgs.push(msg);
    } else {
      grouped.push({ date, msgs: [msg] });
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-border bg-base-900/80 backdrop-blur-sm shrink-0">
        <div className="flex items-center gap-3">
          <div>
            <p
              className="text-sm font-bold text-text-primary leading-none"
              style={{ fontFamily: "var(--font-syne)" }}
            >
              {contact?.name ?? contact?.phone ?? "Contato desconhecido"}
            </p>
            {contact?.name && (
              <p className="text-xs font-mono text-text-muted mt-0.5">
                {contact.phone}
              </p>
            )}
          </div>

          {/* Lead info chips */}
          {(conversation.agent_state as Record<string, string>)
            ?.lead_company && (
            <span className="px-2 py-0.5 rounded-md bg-base-600 border border-border text-xs text-text-secondary">
              {(conversation.agent_state as Record<string, string>).lead_company}
            </span>
          )}

          {/* Stage badge */}
          {(conversation.agent_state as Record<string, string>)
            ?.current_stage && (
            <span className="px-2 py-0.5 rounded-md bg-base-700 border border-border text-[10px] font-mono text-text-muted uppercase">
              {(conversation.agent_state as Record<string, string>).current_stage}
            </span>
          )}
        </div>

        <HandoffButton
          botActive={conversation.bot_active}
          conversationId={conversation.id}
          onToggle={onToggleBot}
        />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
            <div className="w-12 h-12 rounded-full bg-base-700 border border-border flex items-center justify-center">
              <Bot size={20} className="text-amber-DEFAULT" />
            </div>
            <div>
              <p className="text-sm font-medium text-text-secondary">
                Aguardando mensagens
              </p>
              <p className="text-xs text-text-muted mt-1">
                As mensagens aparecerão aqui em tempo real
              </p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {grouped.map(({ date, msgs }) => (
              <div key={date}>
                <DateDivider date={date} />
                {msgs.map((msg, i) => (
                  <MessageBubble key={msg.id} msg={msg} index={i} />
                ))}
              </div>
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Footer bar */}
      <div className="px-5 py-2.5 border-t border-border bg-base-900/60 shrink-0">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-mono text-text-muted">
            ID: {conversation.id.slice(0, 8)}…
          </span>
          <div className="flex items-center gap-4">
            <span className="text-[10px] text-text-muted">
              {messages.length} mensagen{messages.length !== 1 ? "s" : ""}
            </span>
            <span
              className={cn(
                "flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider",
                conversation.status === "open"
                  ? "text-emerald-DEFAULT"
                  : "text-text-muted"
              )}
            >
              <span
                className={cn(
                  "w-1.5 h-1.5 rounded-full",
                  conversation.status === "open"
                    ? "bg-emerald-DEFAULT animate-pulse-dot"
                    : "bg-text-muted"
                )}
              />
              {conversation.status === "open" ? "Aberta" : "Fechada"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
