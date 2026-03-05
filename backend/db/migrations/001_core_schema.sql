-- ============================================================
-- TOIN Platform — Core Schema (Migration 001)
-- ============================================================

-- Habilitar extensão UUID
create extension if not exists "uuid-ossp";

-- ============================================================
-- PLANS
-- ============================================================
create table if not exists plans (
  id           uuid primary key default uuid_generate_v4(),
  name         text not null unique,
  features     jsonb not null default '{}',
  created_at   timestamptz not null default now()
);

-- ============================================================
-- TENANTS
-- ============================================================
create table if not exists tenants (
  id           uuid primary key default uuid_generate_v4(),
  name         text not null,
  slug         text not null unique,
  plan_id      uuid references plans(id),
  settings     jsonb not null default '{}',
  created_at   timestamptz not null default now()
);

-- ============================================================
-- USERS (atendentes/admins por tenant)
-- Referencia auth.users do Supabase Auth
-- ============================================================
create table if not exists users (
  id           uuid primary key references auth.users(id) on delete cascade,
  tenant_id    uuid not null references tenants(id) on delete cascade,
  email        text not null,
  role         text not null default 'agent',   -- 'admin' | 'agent'
  created_at   timestamptz not null default now()
);

-- ============================================================
-- WHATSAPP INSTANCES
-- ============================================================
create table if not exists whatsapp_instances (
  id              uuid primary key default uuid_generate_v4(),
  tenant_id       uuid not null references tenants(id) on delete cascade,
  instance_name   text not null unique,          -- nome no Evolution API
  phone_number    text,
  status          text not null default 'disconnected',  -- 'connected' | 'disconnected' | 'qr_pending'
  provider        text not null default 'evolution',
  settings        jsonb not null default '{}',
  created_at      timestamptz not null default now()
);

-- ============================================================
-- AGENTS (configuração de agente por tenant)
-- ============================================================
create table if not exists agents (
  id              uuid primary key default uuid_generate_v4(),
  tenant_id       uuid not null references tenants(id) on delete cascade,
  name            text not null,
  directive_key   text not null default 'toin',  -- chave do arquivo em directives/
  llm_provider    text not null default 'groq',
  llm_model       text not null default 'llama-3.3-70b-versatile',
  settings        jsonb not null default '{}',
  created_at      timestamptz not null default now()
);

-- ============================================================
-- CONTACTS
-- ============================================================
create table if not exists contacts (
  id           uuid primary key default uuid_generate_v4(),
  tenant_id    uuid not null references tenants(id) on delete cascade,
  phone        text not null,                    -- formato internacional: +5511...
  name         text,
  email        text,
  metadata     jsonb not null default '{}',      -- empresa, cargo, objetivo, etc.
  created_at   timestamptz not null default now(),
  unique (tenant_id, phone)
);

-- ============================================================
-- CONVERSATIONS
-- ============================================================
create table if not exists conversations (
  id                      uuid primary key default uuid_generate_v4(),
  tenant_id               uuid not null references tenants(id) on delete cascade,
  contact_id              uuid not null references contacts(id) on delete cascade,
  whatsapp_instance_id    uuid references whatsapp_instances(id),
  agent_id                uuid references agents(id),
  status                  text not null default 'open',   -- 'open' | 'closed'
  bot_active              boolean not null default true,
  assigned_to             uuid references users(id),
  agent_state             jsonb not null default '{}',    -- estado persistido do LangGraph
  created_at              timestamptz not null default now(),
  updated_at              timestamptz not null default now()
);

-- ============================================================
-- MESSAGES
-- ============================================================
create table if not exists messages (
  id                   uuid primary key default uuid_generate_v4(),
  conversation_id      uuid not null references conversations(id) on delete cascade,
  tenant_id            uuid not null references tenants(id) on delete cascade,
  sender_type          text not null,             -- 'user' | 'bot' | 'human_agent'
  content              text not null default '',
  media_url            text,
  media_type           text,                      -- 'image' | 'audio' | 'document'
  whatsapp_message_id  text,                      -- ID retornado pelo provider
  metadata             jsonb not null default '{}',
  created_at           timestamptz not null default now()
);

-- ============================================================
-- ÍNDICES
-- ============================================================
create index if not exists idx_tenants_slug             on tenants(slug);
create index if not exists idx_users_tenant             on users(tenant_id);
create index if not exists idx_whatsapp_tenant          on whatsapp_instances(tenant_id);
create index if not exists idx_whatsapp_instance_name   on whatsapp_instances(instance_name);
create index if not exists idx_agents_tenant            on agents(tenant_id);
create index if not exists idx_contacts_tenant_phone    on contacts(tenant_id, phone);
create index if not exists idx_conversations_tenant     on conversations(tenant_id, status);
create index if not exists idx_conversations_contact    on conversations(contact_id);
create index if not exists idx_messages_conversation    on messages(conversation_id);
create index if not exists idx_messages_tenant          on messages(tenant_id);
create index if not exists idx_messages_created         on messages(conversation_id, created_at);

-- ============================================================
-- ROW LEVEL SECURITY
-- O backend usa service_role_key (bypassa RLS).
-- RLS protege acesso direto pelo frontend via anon key + JWT.
-- ============================================================
alter table tenants           enable row level security;
alter table users             enable row level security;
alter table whatsapp_instances enable row level security;
alter table agents            enable row level security;
alter table contacts          enable row level security;
alter table conversations     enable row level security;
alter table messages          enable row level security;

-- Política helper: retorna tenant_id do usuário autenticado
create or replace function current_tenant_id()
returns uuid
language sql
stable
as $$
  select tenant_id from users where id = auth.uid()
$$;

-- Políticas de leitura por tenant
create policy "tenant_isolation_conversations"
  on conversations for all
  using (tenant_id = current_tenant_id());

create policy "tenant_isolation_messages"
  on messages for all
  using (tenant_id = current_tenant_id());

create policy "tenant_isolation_contacts"
  on contacts for all
  using (tenant_id = current_tenant_id());

create policy "tenant_isolation_whatsapp_instances"
  on whatsapp_instances for all
  using (tenant_id = current_tenant_id());

create policy "tenant_isolation_agents"
  on agents for all
  using (tenant_id = current_tenant_id());

create policy "users_own_tenant"
  on users for select
  using (tenant_id = current_tenant_id());

-- ============================================================
-- DADOS INICIAIS — Planos
-- ============================================================
insert into plans (name, features) values
  ('basic',   '{"calendar": false, "kb": false, "stt": false, "vision": false, "crm": false}'),
  ('pro',     '{"calendar": true,  "kb": true,  "stt": true,  "vision": true,  "crm": false}'),
  ('segment', '{"calendar": true,  "kb": true,  "stt": true,  "vision": true,  "crm": true}')
on conflict (name) do nothing;

-- ============================================================
-- TRIGGER: atualiza updated_at em conversations
-- ============================================================
create or replace function update_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger conversations_updated_at
  before update on conversations
  for each row execute function update_updated_at();
