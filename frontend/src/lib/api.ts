import { supabase } from "./supabase";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch(path: string, options?: RequestInit) {
  const token = (await supabase.auth.getSession()).data.session?.access_token;
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options?.headers,
    },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const api = {
  conversations: {
    list: () => apiFetch("/conversations/"),
    get: (id: string) => apiFetch(`/conversations/${id}`),
    toggleBot: (id: string, botActive: boolean) =>
      apiFetch(`/conversations/${id}/bot`, {
        method: "PATCH",
        body: JSON.stringify({ bot_active: botActive }),
      }),
  },
  contacts: {
    list: () => apiFetch("/contacts/"),
    get: (id: string) => apiFetch(`/contacts/${id}`),
  },
  whatsapp: {
    instances: {
      list: () => apiFetch("/whatsapp/instances"),
      qrcode: (id: string) => apiFetch(`/whatsapp/instances/${id}/qrcode`),
      reconnect: (id: string) =>
        apiFetch(`/whatsapp/instances/${id}/reconnect`, { method: "POST" }),
    },
  },
};
