# DentaLens AI — Multi-Agent System Design

## Overview

DentaLens uses a **three-agent architecture** with a router/triage pattern.
This design mirrors enterprise AI systems where different domains require
specialized knowledge and tools.

## Agent Architecture

```
                    User Query
                        │
                        ▼
              ┌─────────────────┐
              │   Router Agent  │
              │                 │
              │ 1. Keyword scan │
              │ 2. LLM classify │
              └────────┬────────┘
                       │
            ┌──────────┼──────────┐
            ▼                     ▼
   ┌────────────────┐   ┌────────────────┐
   │ Benefits Agent │   │  Claims Agent  │
   │                │   │                │
   │ RAG retrieval  │   │ Data analysis  │
   │ + LLM answer   │   │ + LLM summary  │
   └────────────────┘   └────────────────┘
```

## Router Agent

**Two-tier classification approach:**

1. **Fast path (keyword heuristic):** Scans for domain keywords
   (e.g., "covered", "deductible" → benefits; "claim", "denied" → claims).
   If confidence > 0.6, routes immediately without calling the LLM.

2. **LLM classification:** For ambiguous queries, calls the LLM with
   a structured JSON output format to classify intent and confidence.

This saves LLM calls on 70-80% of queries while maintaining accuracy
on edge cases.

## Benefits Q&A Agent

Uses the full RAG pipeline:
1. Retrieves relevant chunks from ChromaDB (benefit plans, FAQs, CDT codes)
2. Injects context into the system prompt with grounding instructions
3. Generates a response with source citations
4. Returns confidence based on retrieval scores

**Key prompt engineering decisions:**
- Explicit instruction to answer ONLY from context
- Instruction to say "I don't have information" when context is insufficient
- Citation format guidance for plan names and CDT codes

## Claims Analysis Agent

Uses structured data analysis:
1. Queries ClaimsRepository for summary statistics and anomalies
2. Formats data as context for the LLM
3. LLM generates natural language analysis with specific data points
4. Returns analysis with metadata (total claims, anomalies detected)

**Key design decisions:**
- Pre-computes aggregates rather than sending raw data to the LLM
- Anomaly detection uses statistical deviation (>2 std from mean)
- Limits data context to top 10 anomalies to stay within token limits

## Design Pattern Rationale

**Why Strategy pattern (not inheritance hierarchy)?**
All agents implement `BaseAgent.process()`, making them interchangeable.
The router can delegate to any agent without knowing its implementation.
This also enables easy testing with mock agents.

**Why Factory pattern for agent creation?**
Agents have different constructor dependencies (BenefitsAgent needs RetrievalService,
ClaimsAgent needs ClaimsRepository). The factory encapsulates this complexity.

**Why keyword + LLM routing (not LLM-only)?**
- Keyword routing is ~100x faster (no API call)
- Reduces API costs significantly
- LLM fallback catches ambiguous queries the keywords miss
- Production systems need this kind of optimization
