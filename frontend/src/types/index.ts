export interface Contact {
  id: string;
  tenant_id: string;
  phone: string;
  name?: string;
  email?: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  tenant_id: string;
  sender_type: "user" | "bot" | "human_agent";
  content: string;
  media_url?: string;
  media_type?: "image" | "audio" | "document";
  whatsapp_message_id?: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface Conversation {
  id: string;
  tenant_id: string;
  contact_id: string;
  contacts?: Contact;
  whatsapp_instance_id?: string;
  agent_id?: string;
  status: "open" | "closed";
  bot_active: boolean;
  assigned_to?: string;
  agent_state: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}
