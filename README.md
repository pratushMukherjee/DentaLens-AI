# DentaLens AI

An enterprise-grade AI platform for dental insurance, demonstrating RAG pipelines, multi-agent systems, conversational AI, model evaluation, and responsible AI practices.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Streamlit)                     │
│   ┌──────────┐   ┌───────────────────┐   ┌──────────────────┐  │
│   │   Chat   │   │ Claims Dashboard  │   │   Eval Viewer    │  │
│   └────┬─────┘   └────────┬──────────┘   └────────┬─────────┘  │
└────────┼──────────────────┼────────────────────────┼────────────┘
         │                  │                        │
┌────────▼──────────────────▼────────────────────────▼────────────┐
│                      REST API (FastAPI)                          │
│   /chat  /chat/stream  /claims  /benefits  /evaluate  /health   │
└────────┬──────────────────┬────────────────────────┬────────────┘
         │                  │                        │
┌────────▼──────────────────▼────────────────────────▼────────────┐
│                       Service Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Multi-Agent   │  │     RAG      │  │    Evaluation         │  │
│  │   System      │  │   Pipeline   │  │    Pipeline           │  │
│  │              │  │              │  │                       │  │
│  │ ┌──────────┐ │  │ Ingestion    │  │ Faithfulness          │  │
│  │ │  Router  │ │  │ Retrieval    │  │ Relevance             │  │
│  │ │  Agent   │ │  │ Generation   │  │ Hallucination         │  │
│  │ └────┬─────┘ │  └──────────────┘  │ Responsible AI        │  │
│  │      │       │                    └───────────────────────┘  │
│  │ ┌────▼─────┐ │                                               │
│  │ │ Benefits │ │  ┌──────────────┐                             │
│  │ │  Agent   │ │  │ Conversation │                             │
│  │ ├──────────┤ │  │   Manager    │                             │
│  │ │  Claims  │ │  │   + Memory   │                             │
│  │ │  Agent   │ │  └──────────────┘                             │
│  │ └──────────┘ │                                               │
│  └──────────────┘                                               │
└────────┬──────────────────┬─────────────────────────────────────┘
         │                  │
┌────────▼──────────────────▼─────────────────────────────────────┐
│                    Infrastructure Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │   ChromaDB   │  │   OpenAI     │  │   Claims Data         │  │
│  │ Vector Store │  │  LLM + Emb   │  │   Repository          │  │
│  └──────────────┘  └──────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Language:** Python 3.11+
- **LLM:** OpenAI GPT-4o-mini
- **Embeddings:** OpenAI text-embedding-3-small
- **Vector Store:** ChromaDB
- **Orchestration:** LangChain
- **API:** FastAPI with Pydantic v2
- **Frontend:** Streamlit
- **Testing:** pytest with async support

## Design Patterns

| Pattern | Where Used |
|---------|-----------|
| **Repository** | Claims data access (`ClaimsRepository`) |
| **Factory** | Agent creation (`AgentFactory`), LLM/Embedding providers |
| **Strategy** | Agent processing (`BaseAgent`), Memory strategies |
| **Dependency Injection** | FastAPI `Depends()` wiring |
| **Chain of Responsibility** | Router Agent → Specialist Agent delegation |

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your OpenAI API key

# Seed vector store
make seed

# Start API
make api

# Start Frontend (separate terminal)
make frontend
```

## Project Structure

```
src/dentalens/
├── config/          # Settings, logging, constants
├── domain/          # Models, enums, exceptions
├── infrastructure/  # ChromaDB, OpenAI, data access
├── services/        # Agents, RAG, conversation, evaluation
├── api/             # FastAPI routes, schemas, middleware
└── frontend/        # Streamlit pages and components
```

## Key Features

- **RAG-Powered Q&A** — Ask about dental benefit plans with cited sources
- **Multi-Agent Routing** — Queries automatically routed to the right specialist
- **Claims Analytics** — Anomaly detection and trend analysis on dental claims
- **Model Evaluation** — Faithfulness, relevance, and hallucination metrics
- **Responsible AI** — PII detection, medical advice boundaries, bias checks
- **Streaming Chat** — Real-time token streaming via Server-Sent Events
