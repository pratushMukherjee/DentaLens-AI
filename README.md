# DentaLens AI

An enterprise-grade AI platform for dental insurance, demonstrating RAG pipelines, multi-agent systems, conversational AI, model evaluation, and responsible AI practices.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Streamlit)                     │
│   ┌──────────┐   ┌───────────────────┐   ┌──────────────────┐   │
│   │   Chat   │   │ Claims Dashboard  │   │   Eval Viewer    │   │
│   └────┬─────┘   └────────┬──────────┘   └─────────┬────────┘   │
└────────┼──────────────────┼────────────────────────┼────────────┘
         │                  │                        │
┌────────▼──────────────────▼────────────────────────▼────────────┐
│                      REST API (FastAPI)                         │
│   /chat  /chat/stream  /claims  /benefits  /evaluate  /health   │
└────────┬──────────────────┬────────────────────────┬────────────┘
         │                  │                        │
┌────────▼──────────────────▼────────────────────────▼────────────┐
│                       Service Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Multi-Agent  │  │     RAG      │  │    Evaluation         │  │
│  │   System     │  │   Pipeline   │  │    Pipeline           │  │
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
│                    Infrastructure Layer                         │
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
- **Claims Analytics** — Anomaly detection on 1,200+ claims with 51 flagged anomalies
- **Model Evaluation** — Faithfulness, relevance, and hallucination metrics
- **Responsible AI** — PII detection, medical advice boundaries, bias checks
- **Real Delta Dental Knowledge** — Trained on actual programs: DeltaVision, Special Health Care Needs, Medicare Advantage partners, Healthy Kids Dental, LifeSmile Wellness

## Knowledge Base

| Collection | Documents | Chunks | Content |
|-----------|-----------|--------|---------|
| Benefit Plans | 5 | 20 | PPO Gold, PPO Silver, HMO Basic, PPO Point-of-Service, PPO Standard |
| FAQs | 4 | 17 | Claims, coverage, general dental, Delta Dental programs |
| Procedures | 1 | 27 | CDT procedure codes (D0120-D8090) |
| Claims Data | 1 | — | 1,200 synthetic claims with ~5% seeded anomalies |

## Demo Highlights

```
User: "I got a $1,200 bill for a crown. What should I owe?"
Bot:  Breaks down coverage across PPO Gold (50%), PPO Silver (40%), HMO ($300 copay)

User: "What benefits exist for people with special health care needs?"
Bot:  Up to 4 cleanings/year, anesthesia coverage, extra pre-treatment visits

User: "Are there any billing anomalies?"
Bot:  Lists 51 flagged claims with specific IDs, amounts, and deviation scores

User: "Does Medicare cover dental?"
Bot:  No, but lists 5 Michigan Medicare Advantage partners with dental coverage
```
