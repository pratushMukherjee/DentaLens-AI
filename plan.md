# DentaLens AI - Delta Dental Applied AI Internship Portfolio Project

## Context

This project targets the **Delta Dental Applied AI Internship (JR101158)**. The goal is to build an enterprise-grade AI platform for dental insurance that demonstrates every technical skill listed in the job posting — RAG, multi-agent systems, conversational AI, prompt engineering, embeddings, model evaluation, responsible AI, API integration, and clean software architecture with design patterns. The project is directly relevant to Delta Dental's business domain, using synthetic dental benefit plans, claims data, and CDT procedure codes.

## Project: DentaLens AI

An enterprise AI platform for dental insurance featuring:
1. **RAG Pipeline** — Ingest dental benefit docs into ChromaDB, retrieve context for LLM answers
2. **Multi-Agent System** — Router Agent, Benefits Q&A Agent, Claims Analysis Agent
3. **Conversational AI** — Streaming chat with conversation memory
4. **Model Evaluation** — Faithfulness, relevance, hallucination detection, responsible AI checks
5. **REST API** — FastAPI with layered architecture and dependency injection
6. **Frontend** — Streamlit dashboard with chat + claims analytics + eval viewer

**Tech Stack:** Python 3.11+, FastAPI, LangChain, OpenAI SDK, ChromaDB, Streamlit, Pydantic, pytest

---

## Implementation Phases (each committed to GitHub)

### Phase 1: Foundation & Data
**Files to create:**
- `pyproject.toml` — Dependencies and project metadata
- `.env.example`, `.gitignore`, `Makefile`
- `README.md` — Project overview with architecture diagram
- `src/dentalens/__init__.py`
- `src/dentalens/config/settings.py` — Pydantic BaseSettings (API keys, model names, paths)
- `src/dentalens/config/logging_config.py` — Structured JSON logging
- `src/dentalens/config/constants.py` — Chunk sizes, collection names, defaults
- `src/dentalens/domain/models/claim.py` — Claim model (claim_id, procedure_code, amounts, status)
- `src/dentalens/domain/models/benefit_plan.py` — BenefitPlan model (coverage percentages, deductibles)
- `src/dentalens/domain/models/conversation.py` — Message and Conversation models
- `src/dentalens/domain/models/evaluation.py` — EvaluationResult model
- `src/dentalens/domain/enums.py` — ClaimStatus, ProcedureCategory, AgentType, IntentType
- `src/dentalens/domain/exceptions.py` — DentaLensError hierarchy
- `data/seed/benefit_plans/` — 3 synthetic plan docs (PPO Gold, PPO Silver, HMO Basic)
- `data/seed/faqs/` — 3 FAQ markdown files
- `data/seed/procedures/cdt_codes.json` — CDT procedure code reference
- `data/seed/claims/synthetic_claims.csv` — 1000+ synthetic claims with ~5% anomalies
- `data/seed/claims/providers.json` — Synthetic provider directory
- `src/dentalens/infrastructure/data/seed_data_generator.py` — Script to generate all synthetic data
- `src/dentalens/infrastructure/data/claims_repository.py` — Repository pattern for claims access

**Design patterns:** Repository Pattern (ClaimsRepository)

### Phase 2: RAG & LLM Infrastructure
**Files to create:**
- `src/dentalens/infrastructure/vectorstore/embedding_provider.py` — Factory for embedding models
- `src/dentalens/infrastructure/vectorstore/chroma_client.py` — ChromaDB wrapper (add, search, delete)
- `src/dentalens/infrastructure/vectorstore/document_loader.py` — Load + chunk markdown/JSON docs
- `src/dentalens/infrastructure/llm/llm_provider.py` — LLM provider factory (OpenAI models)
- `src/dentalens/infrastructure/llm/prompt_templates.py` — All prompt templates (router, benefits, claims, eval)
- `src/dentalens/services/rag/ingestion_service.py` — Document ingestion pipeline
- `src/dentalens/services/rag/retrieval_service.py` — Retrieve context + generate RAG responses
- `scripts/seed_vectorstore.py` — CLI to ingest docs into ChromaDB

**Design patterns:** Factory Pattern (EmbeddingProviderFactory, LLMProviderFactory)

### Phase 3: Multi-Agent System & Conversation
**Files to create:**
- `src/dentalens/services/agents/base_agent.py` — Abstract base agent (Strategy pattern)
- `src/dentalens/services/agents/router_agent.py` — Classifies intent, delegates to specialists
- `src/dentalens/services/agents/benefits_agent.py` — RAG-powered benefits Q&A
- `src/dentalens/services/agents/claims_agent.py` — Claims analysis with data access
- `src/dentalens/services/agents/agent_factory.py` — Creates configured agent instances
- `src/dentalens/services/agents/agent_registry.py` — Maps AgentType to agent instances
- `src/dentalens/services/conversation/conversation_manager.py` — Conversation state, streaming chat
- `src/dentalens/services/conversation/memory_strategy.py` — BufferWindow and Summary strategies

**Design patterns:** Strategy (BaseAgent), Factory (AgentFactory), Chain of Responsibility (RouterAgent), Registry

### Phase 4: Evaluation Pipeline
**Files to create:**
- `src/dentalens/services/evaluation/evaluator.py` — Orchestrates all metrics
- `src/dentalens/services/evaluation/metrics/faithfulness.py` — LLM-as-judge grounding check
- `src/dentalens/services/evaluation/metrics/relevance.py` — Semantic relevance scoring
- `src/dentalens/services/evaluation/metrics/hallucination.py` — Hallucination detection
- `src/dentalens/services/evaluation/metrics/responsible_ai.py` — PII, bias, medical advice checks
- `src/dentalens/services/evaluation/eval_dataset.py` — Golden Q&A dataset loader
- `scripts/run_evaluation.py` — CLI to run evaluation suite
- `tests/evaluation/golden_qa_pairs.json` — 20-30 ground truth Q&A pairs

### Phase 5: REST API
**Files to create:**
- `src/dentalens/api/app.py` — FastAPI application factory with lifespan events
- `src/dentalens/api/dependencies.py` — Dependency injection (settings, services, agents)
- `src/dentalens/api/routers/chat.py` — POST /chat, POST /chat/stream (SSE), GET /chat/history
- `src/dentalens/api/routers/claims.py` — GET /claims, GET /claims/analysis/anomalies
- `src/dentalens/api/routers/benefits.py` — GET /benefits/plans, POST /benefits/query
- `src/dentalens/api/routers/evaluation.py` — POST /evaluate, POST /evaluate/batch
- `src/dentalens/api/routers/health.py` — GET /health, GET /health/ready
- `src/dentalens/api/schemas/requests.py` — Pydantic request models
- `src/dentalens/api/schemas/responses.py` — Pydantic response models
- `src/dentalens/api/middleware/error_handler.py` — Global exception handler
- `src/dentalens/api/middleware/request_logging.py` — Request/response logging

**Design patterns:** Dependency Injection (FastAPI Depends), Application Factory

### Phase 6: Frontend
**Files to create:**
- `src/dentalens/frontend/app.py` — Streamlit entry point
- `src/dentalens/frontend/pages/01_chat.py` — Conversational AI chat interface
- `src/dentalens/frontend/pages/02_claims_dashboard.py` — Claims analytics with charts
- `src/dentalens/frontend/pages/03_evaluation.py` — Evaluation results viewer
- `src/dentalens/frontend/components/chat_widget.py` — Reusable chat UI component
- `src/dentalens/frontend/components/metrics_cards.py` — Metric display cards
- `src/dentalens/frontend/components/charts.py` — Chart helpers

### Phase 7: Testing & Documentation
**Files to create:**
- `tests/conftest.py` — Shared fixtures (mock LLM, mock vector store, sample data)
- `tests/unit/test_claim_model.py`, `test_retrieval_service.py`, `test_router_agent.py`, `test_conversation_manager.py`, `test_evaluation_metrics.py`, `test_prompt_templates.py`
- `tests/integration/test_rag_pipeline.py`, `test_agent_routing.py`, `test_api_endpoints.py`
- `tests/evaluation/test_eval_suite.py`
- `docs/architecture.md`, `docs/api_reference.md`, `docs/agent_design.md`

---

## Job Requirements Coverage

| Requirement | Demonstrated By |
|---|---|
| Enterprise-scale AI solutions | Layered architecture, config management, structured logging, typed models |
| AI proof-of-concepts | Multi-agent system, RAG pipeline, evaluation framework |
| Conversational AI, intelligent agents | Chat with streaming, conversation memory, multi-agent routing |
| LLMs, prompt engineering, embeddings | Crafted prompts, OpenAI embeddings, LangChain orchestration |
| Backend services, APIs, data sources | FastAPI REST API, ChromaDB, claims data repository, DI |
| Agent-based systems, RAG, model eval, responsible AI | 3-agent system, full RAG, faithfulness/hallucination metrics, PII detection |
| Python programming | Python 3.11+ with type hints, async/await, pattern matching |
| APIs, data processing, cloud-based | FastAPI + OpenAPI docs, pandas, Pydantic, env-based config |
| OpenAI, LLMs, LangChain | OpenAI GPT-4o-mini, embeddings, LangChain chains/retrievers |
| Software architecture, OOP, design patterns | Factory, Strategy, Repository, DI, Chain of Responsibility, ABC |

---

## Verification Strategy

1. **Unit tests:** `pytest tests/unit/ -v` — all domain models, agents, metrics (mocked externals)
2. **Integration tests:** `pytest tests/integration/ -v` — RAG pipeline, agent routing, API endpoints
3. **Evaluation suite:** `python scripts/run_evaluation.py` — faithfulness > 0.8, hallucination < 10%
4. **Manual demo:** Start API (`uvicorn`) + Streamlit, test chat flow, claims dashboard, eval page
5. **Linting:** `ruff check src/ tests/` + `ruff format src/ tests/`

---

## Git Strategy

- Initialize repo, create GitHub remote
- Commit after each phase with descriptive message
- Each phase is a self-contained, buildable increment
