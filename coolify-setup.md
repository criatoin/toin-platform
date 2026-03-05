# Deploy no Coolify — TOIN Platform

## Pré-requisitos

- Servidor com Coolify instalado (self-hosted)
- Repositório Git acessível pelo Coolify
- Conta Supabase com projeto criado e schema aplicado
- Evolution API rodando e acessível
- Chave de API do Groq
- Credenciais do Google Calendar (service account JSON)
- Conta Langfuse (ou instância self-hosted)

---

## 1. Backend (FastAPI)

### Criar serviço no Coolify

1. **New Resource → Application → Dockerfile**
2. Apontar para a pasta `/backend` no repositório
3. Porta: `8000`
4. Health check: `GET /health` → esperado `{"status":"ok"}`

### Variáveis de ambiente

```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

EVOLUTION_API_URL=https://evolution.seuserver.com
EVOLUTION_API_KEY=sua-chave

GROQ_API_KEY=gsk_...

GOOGLE_CALENDAR_CREDENTIALS_JSON={"type":"service_account",...}
GOOGLE_CALENDAR_ID=primary

LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

SECRET_KEY=<random-32-chars>
WEBHOOK_SECRET=<random-secret>
```

---

## 2. Frontend (Next.js)

### Criar serviço no Coolify

1. **New Resource → Application → Dockerfile**
2. Apontar para a pasta `/frontend`
3. Porta: `3000`

### Variáveis de ambiente

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_API_URL=https://api.seudominio.com
```

---

## 3. Domínios e SSL

O Coolify provisiona SSL automático via Let's Encrypt.

- Backend: `api.seudominio.com` → porta 8000
- Frontend: `app.seudominio.com` → porta 3000

---

## 4. Configurar webhook no Evolution API

Após o deploy, configure o webhook no painel do Evolution API:

- **URL:** `https://api.seudominio.com/whatsapp/webhook/{nome-da-instancia}`
- **Eventos:** `messages.upsert`, `connection.update`

---

## 5. Smoke test

```bash
# Backend health
curl https://api.seudominio.com/health
# Esperado: {"status":"ok","service":"toin-backend"}

# Enviar mensagem de teste pelo WhatsApp para a instância conectada
# → Verificar que a mensagem aparece no inbox em tempo real
# → Verificar que o bot responde automaticamente
```

---

## 6. Monitoramento

- **Langfuse:** acessar dashboard de traces em `https://cloud.langfuse.com`
- **Supabase:** monitorar queries lentas e uso de storage
- **Coolify:** logs dos containers em tempo real no painel
