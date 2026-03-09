# DentaLens AI — API Reference

Base URL: `http://localhost:8000`
OpenAPI Docs: `http://localhost:8000/docs`

## Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Basic health check |
| GET | `/api/v1/health/ready` | Readiness check with component status |

## Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Send a message with auto agent routing |
| GET | `/api/v1/chat/history/{id}` | Get conversation history |

### POST /api/v1/chat
```json
// Request
{
  "conversation_id": "optional-existing-id",
  "message": "Does the PPO Gold plan cover root canals?"
}

// Response
{
  "conversation_id": "uuid",
  "response": "Yes, the PPO Gold plan covers...",
  "agent_used": "benefits",
  "sources": [{"document": "delta_ppo_gold.md", "relevance_score": 0.23}],
  "confidence": 0.92
}
```

## Benefits

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/benefits/plans` | List all benefit plans |
| GET | `/api/v1/benefits/plans/{id}` | Get plan details |
| POST | `/api/v1/benefits/query` | Direct RAG query for benefits |

## Claims

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/claims` | List claims (filters: status, limit, offset) |
| GET | `/api/v1/claims/{id}` | Get claim by ID |
| GET | `/api/v1/claims/analysis/summary` | Aggregate statistics |
| GET | `/api/v1/claims/analysis/anomalies` | Detected billing anomalies |

## Evaluation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/evaluate` | Evaluate a single response |
| POST | `/api/v1/evaluate/batch` | Evaluate a batch of responses |
