"use client";

import { useEffect, useState, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import { api } from "@/lib/api";
import { ConversationList } from "@/components/inbox/ConversationList";
import { ChatView } from "@/components/inbox/ChatView";
import { Bot, Wifi, WifiOff, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Conversation, Message } from "@/types";

export default function InboxPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selected, setSelected] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [realtimeConnected, setRealtimeConnected] = useState(false);

  // Load conversations
  useEffect(() => {
    async function load() {
      try {
        const data = await api.conversations.list();
        setConversations(data);
      } catch (err) {
        console.error("Failed to load conversations:", err);
      } finally {
        setLoadingList(false);
      }
    }
    load();
  }, []);

  // Load messages when conversation selected
  useEffect(() => {
    if (!selected) return;

    async function loadMessages() {
      setLoadingMessages(true);
      try {
        const data = await api.conversations.get(selected!.id);
        setMessages(data.messages ?? []);
      } catch (err) {
        console.error("Failed to load messages:", err);
      } finally {
        setLoadingMessages(false);
      }
    }

    loadMessages();
  }, [selected?.id]);

  // Supabase Realtime — subscribe to new messages
  useEffect(() => {
    const channel = supabase
      .channel("inbox-realtime")
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "messages",
        },
        (payload) => {
          const newMsg = payload.new as Message;

          // If message belongs to selected conversation, append it
          if (selected && newMsg.conversation_id === selected.id) {
            setMessages((prev) => {
              if (prev.find((m) => m.id === newMsg.id)) return prev;
              return [...prev, newMsg];
            });
          }

          // Update conversation list preview
          setConversations((prev) =>
            prev.map((c) =>
              c.id === newMsg.conversation_id
                ? { ...c, messages: [...(c.messages ?? []), newMsg] }
                : c
            )
          );
        }
      )
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "conversations",
        },
        (payload) => {
          const updated = payload.new as Conversation;
          setConversations((prev) =>
            prev.map((c) => (c.id === updated.id ? { ...c, ...updated } : c))
          );
          if (selected?.id === updated.id) {
            setSelected((prev) => (prev ? { ...prev, ...updated } : prev));
          }
        }
      )
      .subscribe((status) => {
        setRealtimeConnected(status === "SUBSCRIBED");
      });

    return () => {
      supabase.removeChannel(channel);
    };
  }, [selected?.id]);

  const handleSelectConversation = useCallback((conv: Conversation) => {
    setSelected(conv);
    setMessages([]);
  }, []);

  const handleToggleBot = useCallback(
    async (botActive: boolean) => {
      if (!selected) return;
      const updated = await api.conversations.toggleBot(selected.id, botActive);
      setSelected((prev) => (prev ? { ...prev, ...updated } : prev));
      setConversations((prev) =>
        prev.map((c) => (c.id === updated.id ? { ...c, ...updated } : c))
      );
    },
    [selected]
  );

  async function handleSignOut() {
    await supabase.auth.signOut();
    window.location.href = "/login";
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-base-950">
      {/* Sidebar nav (narrow) */}
      <nav className="flex flex-col items-center w-14 bg-base-900 border-r border-border py-4 gap-3 shrink-0">
        {/* Logo */}
        <div className="w-8 h-8 rounded-lg bg-amber-DEFAULT/10 border border-amber-dim/50 flex items-center justify-center mb-2">
          <Bot size={15} className="text-amber-DEFAULT" />
        </div>

        <div className="flex-1" />

        {/* Realtime indicator */}
        <div
          className="group relative"
          title={realtimeConnected ? "Tempo real ativo" : "Desconectado"}
        >
          {realtimeConnected ? (
            <Wifi size={16} className="text-emerald-DEFAULT animate-pulse-dot" />
          ) : (
            <WifiOff size={16} className="text-crimson" />
          )}
        </div>

        {/* Sign out */}
        <button
          onClick={handleSignOut}
          className="w-8 h-8 rounded-lg hover:bg-base-700 flex items-center justify-center transition-colors group"
          title="Sair"
        >
          <LogOut
            size={14}
            className="text-text-muted group-hover:text-text-secondary"
          />
        </button>
      </nav>

      {/* Conversation list */}
      <aside className="w-72 bg-base-900 border-r border-border shrink-0 flex flex-col overflow-hidden">
        <ConversationList
          conversations={conversations}
          selectedId={selected?.id ?? null}
          onSelect={handleSelectConversation}
          loading={loadingList}
        />
      </aside>

      {/* Main chat area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {selected ? (
          loadingMessages ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="flex flex-col items-center gap-3">
                <div className="w-8 h-8 rounded-full border-2 border-amber-DEFAULT border-t-transparent animate-spin" />
                <p className="text-xs text-text-muted">Carregando mensagens…</p>
              </div>
            </div>
          ) : (
            <ChatView
              conversation={selected}
              messages={messages}
              onToggleBot={handleToggleBot}
            />
          )
        ) : (
          <EmptyState />
        )}
      </main>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="relative flex-1 flex flex-col items-center justify-center gap-6 select-none">
      {/* Abstract grid bg */}
      <div
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(rgba(245,158,11,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(245,158,11,0.5) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      <div className="relative z-10 flex flex-col items-center gap-4 text-center">
        <div className="w-16 h-16 rounded-2xl bg-base-800 border border-border flex items-center justify-center">
          <Bot size={28} className="text-amber-DEFAULT" />
        </div>
        <div>
          <h2
            className="text-lg font-bold text-text-primary"
            style={{ fontFamily: "var(--font-syne)" }}
          >
            TOIN Inbox
          </h2>
          <p className="text-sm text-text-muted mt-1 max-w-xs">
            Selecione uma conversa para visualizar o atendimento em tempo real
          </p>
        </div>
      </div>
    </div>
  );
}
