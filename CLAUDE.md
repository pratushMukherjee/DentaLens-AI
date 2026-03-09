# DentaLens AI — Project Context for Claude Code

## What This Is
Enterprise AI platform for dental insurance built as a portfolio project targeting the **Delta Dental Applied AI Internship (JR101158, Okemos MI)**. Demonstrates RAG, multi-agent systems, conversational AI, model evaluation, responsible AI, and clean architecture.

## GitHub
https://github.com/pratushMukherjee/DentaLens-AI

## How to Run
```bash
# Requires Python 3.11 (ChromaDB incompatible with 3.14)
# Venv already exists at .venv/ using py -3.11
source .venv/Scripts/activate

# OpenAI key is in .env (gitignored). NEVER commit .env
# .env.example has placeholder only

# Seed vector store (64 chunks: 20 plans, 17 FAQs, 27 procedures)
python scripts/seed_vectorstore.py

# Start API (port 8000)
python -m uvicorn src.dentalens.api.app:create_app --factory --host 0.0.0.0 --port 8000

# Start frontend (port 8501, separate terminal)
streamlit run src/dentalens/frontend/app.py --server.port 8501

# Run tests (57 tests, all passing)
python -m pytest tests/ -v
```

## Architecture
- **Frontend:** Streamlit (app.py + 3 pages) at `src/dentalens/frontend/`
- **API:** FastAPI at `src/dentalens/api/` — routes: /chat, /claims, /benefits, /evaluate, /health
- **Agents:** Router (keyword + LLM), Benefits (RAG), Claims (data analysis) at `src/dentalens/services/agents/`
- **RAG:** ChromaDB vector store, 1024-char chunks, 200 overlap, top-8 retrieval, source-labeled context
- **Evaluation:** Faithfulness, relevance, hallucination, responsible AI at `src/dentalens/services/evaluation/`
- **Data:** Synthetic claims CSV (1,200 rows), benefit plan MDs, FAQ MDs, CDT codes JSON

## Key Design Decisions
- Chunk size 1024 / overlap 200 (was 512/50, broke specific questions)
- Source file labels prepended to each context chunk (LLM couldn't attribute plans without them)
- Prompt says "show all plans" when user says "my plan" without specifying
- Router uses keyword heuristics first (free, fast) then LLM fallback for ambiguous queries
- Brand color is #41A928 (Delta Dental green), configured in `styles.py` and `.streamlit/config.toml`

## Knowledge Base (RAG seed documents)
- `data/seed/benefit_plans/` — 5 plans: PPO Gold, PPO Silver, HMO Basic, PPO Point-of-Service, PPO Standard
- `data/seed/faqs/` — 4 files: claims FAQ, coverage FAQ, general dental FAQ, programs FAQ (DeltaVision, Special Health Care Needs, Medicare, LifeSmile, etc.)
- `data/seed/procedures/cdt_codes.json` — 27 CDT procedure codes
- `data/seed/claims/synthetic_claims.csv` — 1,200 claims with ~5% seeded anomalies

## Important Files
- `src/dentalens/config/constants.py` — CHUNK_SIZE, RETRIEVAL_K, thresholds
- `src/dentalens/infrastructure/llm/prompt_templates.py` — All LLM prompts
- `src/dentalens/services/rag/retrieval_service.py` — RAG pipeline (retrieve + generate)
- `src/dentalens/services/agents/router_agent.py` — Intent classification + routing keywords
- `src/dentalens/frontend/components/styles.py` — Brand colors, CSS, reusable UI components
- `docs/interview_prep.md` — 20+ interview questions with answers

## Known Constraints
- ChromaDB requires Python 3.11 (breaks on 3.14 due to Pydantic v1 internals)
- Some integration tests have `skipif` guards for when ChromaDB can't import
- Vector store must be re-seeded after changing CHUNK_SIZE/OVERLAP or adding new docs
- Kill uvicorn before re-seeding (ChromaDB files get locked)
