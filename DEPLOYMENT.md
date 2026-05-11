# Deploy do AI Court

Plano recomendado: frontend na Vercel e backend na Render.

Se a Render travar no plano free, use Koyeb para o backend. Para este projeto, Koyeb costuma ser o caminho mais direto porque aceita Dockerfile, WebSocket e Postgres com `pgvector`.

## 1. Backend na Render

1. No Render, crie um **Blueprint** apontando para este repositorio.
2. Use o `render.yaml` da raiz. Ele cria:
   - `ai-court-backend` como Web Service Docker;
   - `ai-court-db` como Render Postgres 16;
   - `ai-court-redis` como Render Key Value;
   - `alembic upgrade head` no boot do container para criar `vector`, `pgcrypto` e as tabelas, mantendo compatibilidade com o plano free.
3. Quando o Render pedir variaveis com `sync: false`, preencha:
   - `FRONTEND_ORIGIN`: URL final da Vercel, por exemplo `https://ai-court.vercel.app`.
   - `PDF_BASE_URL`: URL publica do backend, por exemplo `https://ai-court-backend.onrender.com`.
4. Depois do deploy, valide:

```txt
https://ai-court-backend.onrender.com/health
```

## 2. Frontend na Vercel

1. Importe o repositorio na Vercel.
2. Configure **Root Directory** como `frontend`.
3. O `frontend/vercel.json` define Vite, `npm ci`, `npm run build`, `dist` e fallback para SPA.
4. Configure a variavel de ambiente:

```txt
VITE_API_BASE_URL=https://ai-court-backend.onrender.com
```

`VITE_WS_BASE_URL` e opcional. Se ficar vazio, o frontend converte automaticamente `https://` em `wss://` usando a mesma origem da API.

## 3. Ajuste final de CORS

Depois que a Vercel gerar a URL definitiva, volte no Render e confirme que `FRONTEND_ORIGIN` contem essa origem exata. Para mais de uma origem, separe por virgula:

```txt
https://ai-court.vercel.app,https://www.seu-dominio.com
```

## Alternativa: backend na Koyeb

1. Na Koyeb, crie um **Database Service** PostgreSQL 16.
2. Crie um **Web Service** conectado ao GitHub.
3. Configure:
   - Repository: `guilhermemichael/AI-Court`
   - Branch: `main`
   - Builder: `Dockerfile`
   - Work directory: `backend`
   - Dockerfile location: `Dockerfile`
   - Exposed port: `8000`
4. Variaveis do backend:

```txt
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=<connection string do Postgres da Koyeb>
REDIS_URL=redis://localhost:6379/0
FRONTEND_ORIGIN=https://sua-url-da-vercel.vercel.app
PDF_BASE_URL=https://sua-url-da-koyeb.koyeb.app
PDF_STORAGE_PATH=/tmp/ai-court/pdfs
LLM_MODE=mock
EMBEDDING_DIMENSIONS=1536
RATE_LIMIT_PER_MINUTE=60
TRIAL_STEP_DELAY_MS=450
```

O comando do container ja roda `alembic upgrade head` antes de iniciar a API, entao as extensoes `vector` e `pgcrypto` e as tabelas sao criadas no primeiro boot.

Depois que a Koyeb gerar a URL publica do backend, volte na Vercel e atualize:

```txt
VITE_API_BASE_URL=https://sua-url-da-koyeb.koyeb.app
```

Em seguida faca redeploy do frontend na Vercel.

## Observacoes de portfolio

O plano `free` deixa o projeto barato para demonstracao, mas pode dormir e atrasar o primeiro acesso. Para uma demo mais fluida em entrevista, suba o Web Service para `starter` e o Postgres para um plano pago pequeno.
