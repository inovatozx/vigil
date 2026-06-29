# Vigil AI Workspace

**Vigil** é um clone self-hosted do Odysseus AI — um workspace de IA completo que roda 100% localmente em sua máquina. Oferece chat com streaming, gerenciamento de modelos LLM, memória vetorial com ChromaDB, busca web com SearXNG, e muito mais.

## Stack Tecnológico

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| **Backend** | FastAPI + Uvicorn | Async nativo, WebSocket fácil, tipagem forte com Pydantic |
| **Frontend** | Vanilla JavaScript + HTML + CSS | Zero build step, carregamento rápido, sem dependências de framework |
| **Banco de Dados** | SQLite | Self-contained, zero config, backup = copiar arquivo |
| **Vector Store** | ChromaDB | Embeddings locais, busca semântica para RAG e memória |
| **Busca Web** | SearXNG (self-hosted) | Privacidade, sem API keys, meta-search engine |
| **Embeddings** | FastEmbed (ONNX) | Roda em CPU, sem GPU necessária, modelo ~50MB |
| **Containerização** | Docker Compose | Orquestra todos os serviços com um comando |
| **Autenticação** | bcrypt + TOTP (2FA) | Segurança robusta sem dependência externa |

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (PWA)                            │
│   Vanilla JS Modules + HTML + CSS (tema escuro, responsivo) │
│        Service Worker para offline + WebSocket              │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP/WS
┌──────────────────────────────▼──────────────────────────────┐
│                   BACKEND (FastAPI/Uvicorn)                 │
│                                                              │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────────────┐  │
│  │ Routes  │ │Services │ │ Agent    │ │ MCP Servers     │  │
│  │ (API)   │ │(Business│ │ Loop     │ │ (email, img,    │  │
│  │         │ │ Logic)  │ │ +Tools   │ │ memory, rag)    │  │
│  └────┬─────┘ └────┬────┘ └────┬─────┘ └────────┬────────┘  │
│       │            │           │                │            │
│  ┌────▼────────────▼───────────▼────────────────▼─────────┐  │
│  │           Core Layer                                   │  │
│  │  Database │ Auth │ Config │ LLM Core │ Embeddings    │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────┬──────────┬──────────┬──────────┬─────────────────┘
           │          │          │          │
    ┌──────▼───┐ ┌────▼────┐ ┌──▼───┐ ┌───▼────┐
    │ SQLite   │ │ChromaDB │ │SearX │ │ ntfy   │
    │ (data)   │ │(vectors)│ │NG    │ │(notify)│
    └──────────┘ └─────────┘ └──────┘ └────────┘
           │
    ┌──────▼──────────────────────────────────┐
    │      LLM Providers                       │
    │ Ollama │ OpenAI │ Groq │ Anthropic │    │
    │ Gemini │ Mistral│ DeepSeek │ xAI │ ... │
    └─────────────────────────────────────────┘
```

## Estrutura de Diretórios

```
vigil/
├── app.py                          # Entry point FastAPI
├── docker-compose.yml              # Orquestração de serviços
├── Dockerfile                      # Build da aplicação
├── .env.example                    # Template de configuração
├── requirements.txt                # Dependências Python
├── pyproject.toml                  # Metadata do projeto
│
├── core/                           # Camada core
│   ├── __init__.py
│   ├── config.py                   # Configurações (pydantic-settings)
│   ├── constants.py                # Constantes globais
│   ├── database.py                 # SQLAlchemy models + engine
│   ├── auth.py                     # AuthManager (bcrypt, TOTP, JWT)
│   ├── middleware.py               # CORS, Rate Limit, Security Headers
│   └── exceptions.py               # Exceções customizadas
│
├── src/                            # Lógica de negócio
│   ├── __init__.py
│   ├── llm_core.py                 # Abstração universal de LLM
│   ├── chat_handler.py             # Processamento de chat
│   ├── chat_processor.py           # Pipeline de processamento
│   ├── memory.py                   # Sistema de memória
│   ├── memory_vector.py            # Memória vetorial (ChromaDB)
│   ├── embeddings.py               # FastEmbed ONNX
│   ├── model_discovery.py          # Descoberta automática de modelos
│   └── prompt_security.py          # Proteção contra prompt injection
│
├── routes/                         # Endpoints da API
│   ├── __init__.py
│   ├── chat_routes.py              # /api/chat/*
│   ├── auth_routes.py              # /api/auth/*
│   ├── model_routes.py             # /api/models/*
│   └── session_routes.py           # /api/sessions/*
│
├── static/                         # Frontend
│   ├── index.html                  # Página principal (SPA)
│   ├── style.css                   # Estilos globais (tema escuro)
│   ├── app.js                      # Entry point JS
│   ├── manifest.json               # PWA manifest
│   └── js/
│       ├── init.js                 # Inicialização
│       ├── chat.js                 # Interface de chat
│       ├── sessions.js             # Gerenciamento de sessões
│       ├── models.js               # Seleção de modelos
│       └── settings.js             # Configurações
│
├── config/                         # Configurações de serviços
│   └── searxng/
│       └── settings.yml            # Config do SearXNG
│
└── data/                           # Dados persistentes (gitignored)
    ├── app.db                      # SQLite database
    ├── chroma_db/                  # ChromaDB vectors
    ├── sessions/                   # Arquivos de sessão
    ├── uploads/                    # Uploads do usuário
    └── models/                     # Modelos baixados
```

## Instalação e Uso

### Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.11+ (se rodar sem Docker)
- 4GB+ RAM disponível

### Com Docker Compose (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/manus-ai/vigil.git
cd vigil

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API (OpenAI, Anthropic, etc.)

# 3. Inicie os serviços
docker-compose up -d

# 4. Acesse a aplicação
# Abra http://localhost:8000 no seu navegador
```

### Sem Docker (Desenvolvimento Local)

```bash
# 1. Clone o repositório
git clone https://github.com/manus-ai/vigil.git
cd vigil

# 2. Crie um ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env

# 5. Inicie o servidor FastAPI
uvicorn app:app --reload

# 6. Acesse a aplicação
# Abra http://localhost:8000 no seu navegador
```

## Modelos de Dados

### Usuários e Autenticação

- **users**: Armazena informações de usuário, hash de senha, TOTP secret
- **api_tokens**: Tokens de API para acesso programático

### Chat e Sessões

- **sessions**: Sessões de chat (UUID, título, modelo usado)
- **messages**: Mensagens individuais (role, content, tokens, attachments)

### Memória

- **memories**: Fatos, preferências e contexto extraído do chat
- ChromaDB: Armazena embeddings vetoriais para busca semântica

### Documentos e Conteúdo

- **documents**: Documentos markdown/html/csv/txt
- **gallery_images**: Imagens geradas ou enviadas
- **notes**: Notas rápidas
- **tasks**: Tarefas com status e recorrência

### Email e Calendário

- **email_accounts**: Contas IMAP/SMTP configuradas
- **emails**: Emails sincronizados
- **calendar_events**: Eventos de calendário com suporte a CalDAV

### Configuração

- **provider_configs**: Configurações de provedores LLM (OpenAI, Anthropic, etc.)
- **user_preferences**: Preferências de usuário (tema, idioma, etc.)

## Endpoints da API

### Autenticação

- `POST /api/auth/register` — Registrar novo usuário
- `POST /api/auth/login` — Fazer login
- `POST /api/auth/logout` — Fazer logout
- `GET /api/auth/me` — Dados do usuário atual
- `POST /api/auth/totp/setup` — Configurar 2FA
- `POST /api/auth/totp/verify` — Verificar código 2FA

### Chat

- `POST /api/chat` — Enviar mensagem (streaming via SSE)
- `GET /api/chat/sessions` — Listar sessões
- `POST /api/chat/sessions` — Criar sessão
- `GET /api/chat/sessions/:id` — Obter sessão com mensagens
- `PATCH /api/chat/sessions/:id` — Atualizar sessão
- `DELETE /api/chat/sessions/:id` — Deletar sessão

### Modelos

- `GET /api/models` — Listar modelos disponíveis
- `GET /api/models/providers` — Listar provedores configurados
- `POST /api/models/providers` — Adicionar/atualizar provedor
- `DELETE /api/models/providers/:id` — Remover provedor

### Sessões

- `GET /api/sessions` — Listar sessões
- `POST /api/sessions` — Criar sessão
- `GET /api/sessions/:id` — Obter sessão
- `PATCH /api/sessions/:id` — Atualizar sessão
- `DELETE /api/sessions/:id` — Deletar sessão

## Streaming de Chat

O Vigil utiliza **Server-Sent Events (SSE)** para streaming de respostas em tempo real. Quando você envia uma mensagem, a resposta do LLM é transmitida incrementalmente, permitindo que você veja a resposta sendo gerada em tempo real.

### Fluxo

1. Frontend envia mensagem via `POST /api/chat`
2. Backend carrega contexto da sessão
3. Backend injeta memórias relevantes (RAG)
4. Backend faz streaming da resposta do LLM
5. Frontend renderiza incrementalmente
6. Backend salva mensagem e extrai memórias (background)

## Configuração de Provedores LLM

O Vigil suporta múltiplos provedores de LLM:

- **Ollama** (local) — Gratuito, privado, sem API key
- **OpenAI** — GPT-4, GPT-3.5, etc.
- **Anthropic** — Claude
- **Google Gemini** — Gemini Pro
- **Groq** — Llama 2, Mixtral (rápido)
- **DeepSeek** — DeepSeek-V2
- **Mistral** — Mistral 7B, Large
- **xAI** — Grok

Configure suas chaves de API no arquivo `.env`:

```bash
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
OLLAMA_BASE_URL="http://localhost:11434"
```

## Segurança

- **Autenticação**: JWT com refresh tokens
- **2FA**: TOTP (Google Authenticator, Authy, etc.)
- **Criptografia**: Senhas com bcrypt, API keys criptografadas
- **Headers de Segurança**: HSTS, CSP, X-Frame-Options, etc.
- **Rate Limiting**: Proteção contra abuso
- **Proteção contra Prompt Injection**: Detecção de padrões suspeitos

## Desenvolvimento

### Estrutura de Código

- **core/**: Configurações, autenticação, banco de dados
- **src/**: Lógica de negócio (LLM, chat, memória)
- **routes/**: Endpoints da API
- **static/**: Frontend (HTML, CSS, JS)

### Adicionar um Novo Endpoint

1. Crie uma rota em `routes/new_routes.py`
2. Importe em `app.py` e adicione com `app.include_router()`
3. Teste com `curl` ou Postman

### Adicionar um Novo Provedor LLM

1. Crie uma classe herdando de `LLMProvider` em `src/llm_core.py`
2. Implemente `stream_chat_completion()`
3. Registre em `LLMCore._initialize_providers()`

## Troubleshooting

### Erro: "Connection refused" ao conectar com Ollama

Certifique-se de que Ollama está rodando:

```bash
ollama serve
```

Ou configure a URL correta em `.env`:

```bash
OLLAMA_BASE_URL="http://localhost:11434"
```

### Erro: "Database locked"

SQLite pode ter problemas com múltiplas conexões simultâneas. Se ocorrer, considere migrar para PostgreSQL.

### Erro: "Out of memory"

Reduza o tamanho do modelo LLM ou aumente a RAM disponível.

## Roadmap

- [ ] Agentes autônomos com loop de pensamento
- [ ] Integração com MCP (Model Context Protocol)
- [ ] Suporte a plugins
- [ ] Interface de pesquisa profunda
- [ ] Editor de documentos colaborativo
- [ ] Sincronização de calendário (CalDAV)
- [ ] Gerenciamento de email
- [ ] Geração e edição de imagens
- [ ] Text-to-Speech e Speech-to-Text
- [ ] Suporte a PostgreSQL e outros bancos
- [ ] Autoscaling e clustering

## Licença

MIT License — Veja [LICENSE](LICENSE) para detalhes.

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Suporte

Para dúvidas ou problemas, abra uma issue no GitHub ou entre em contato com a equipe Manus AI.

---

**Vigil** — Seu workspace de IA privado, self-hosted e poderoso. 🚀
