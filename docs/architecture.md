# DentaLens AI — System Architecture

## Overview

DentaLens AI is a layered enterprise application following clean architecture principles.
Each layer has a specific responsibility and depends only on layers below it.

## Layer Diagram

```
┌─────────────────────────────────────────────┐
│              Presentation Layer              │
│     Streamlit Frontend  •  FastAPI REST      │
├─────────────────────────────────────────────┤
│               Service Layer                  │
│  Agents • RAG • Conversation • Evaluation    │
├─────────────────────────────────────────────┤
│            Infrastructure Layer              │
│  ChromaDB • OpenAI LLM • Claims Repository  │
├─────────────────────────────────────────────┤
│               Domain Layer                   │
│   Models • Enums • Exceptions • Constants    │
└─────────────────────────────────────────────┘
```

## Design Patterns

### Repository Pattern (`ClaimsRepository`)
Abstracts data access behind a clean interface. Consumers call `get_claims_by_status()`
without knowing whether data comes from CSV, SQL, or an API.

### Factory Pattern (`AgentFactory`, `LLMProviderFactory`, `EmbeddingProviderFactory`)
Encapsulates object creation complexity. The `AgentFactory.create(AgentType.BENEFITS)`
call constructs a fully-configured agent with all dependencies injected.

### Strategy Pattern (`BaseAgent`, `MemoryStrategy`)
Agents share a common `process(query, context) -> AgentResponse` interface.
The router selects the appropriate strategy at runtime. Memory strategies
(BufferWindow vs Summary) are also interchangeable.

### Dependency Injection (`FastAPI Depends()`)
All services are wired via `api/dependencies.py`. Route handlers receive
pre-configured service instances, making them thin and testable.

### Chain of Responsibility (`RouterAgent`)
User queries flow through the router, which classifies intent and delegates
to the appropriate specialist agent. If confidence is low, it asks for clarification.

## Data Flow

### Chat Request Flow
```
User Message
    → POST /api/v1/chat
    → ConversationManager.chat()
    → RouterAgent.classify() — keyword heuristic or LLM classification
    → Specialist Agent (Benefits or Claims)
        → Benefits: RetrievalService.retrieve_and_generate()
            → ChromaDB similarity search
            → LLM generation with context
        → Claims: ClaimsRepository data + LLM analysis
    → Response with sources and metadata
```

### RAG Pipeline
```
Seed Documents (Markdown, JSON)
    → DentalDocumentLoader (chunking with metadata)
    → EmbeddingProviderFactory (text-embedding-3-small)
    → ChromaVectorStore (persistence)

User Query
    → Embedding
    → ChromaDB similarity search (top-k)
    → Context injection into system prompt
    → LLM generation with grounding
```

## Configuration

All configuration via environment variables / `.env` file,
managed by Pydantic `BaseSettings`. Sensitive values use `SecretStr`.
