# Corporate RAG Chatbot

Deployment-ready Python backend for an internal employee assistant using OpenAI Responses API, file search, and approved internal API tools.

## What is included

- FastAPI backend with `/chat`, `/healthz`, and `/readyz`
- OpenAI Responses API integration with `file_search`
- Document ingestion job for OpenAI vector stores
- Strict tool schemas and server-side validation
- Placeholder internal API clients for policy metadata, ticket status, and directory lookup
- Authentication and authorization hooks for an internal gateway or identity provider
- JSONL audit logging with minimal metadata
- Safe error handling that avoids leaking secrets or backend traces
- Minimal tests for retrieval request construction and tool validation

## Folder Structure

```text
app/
  api/                 FastAPI routes and request lifecycle
  core/                config, auth, errors, audit logging
  schemas/             public request/response models
  services/            OpenAI RAG workflow and ingestion
  tools/               approved tool schemas, validators, dispatch
scripts/
  ingest_documents.py  batch document ingestion CLI
tests/
  test_rag_service.py
  test_tools.py
docs/
  agents-sdk-adaptation.md
  deployment.md
  security.md
```

## Quick Start

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
uvicorn app.main:app --reload
```

For local requests, send identity headers that your internal gateway would normally set:

```bash
curl -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -H "X-User-Id: employee-123" `
  -H "X-User-Roles: employee,it_support" `
  -H "X-Department: operations" `
  -d "{\"question\":\"What is the status of ticket TCK-12345?\",\"conversation_id\":\"demo\"}"
```

## Ingest Documents

Prepare a registry JSON file:

```json
[
  {
    "path": "docs/internal-faq.pdf",
    "title": "Internal FAQ",
    "owner": "Knowledge Team",
    "source_url": "https://intranet.example.invalid/faq",
    "sensitivity": "internal",
    "freshness_date": "2026-06-01"
  }
]
```

Run ingestion:

```bash
python scripts/ingest_documents.py --registry registry.json --vector-store-name internal-knowledge
```

The script prints the vector store ID. Set `OPENAI_VECTOR_STORE_ID` before starting the API.

## OpenAI Notes

This project follows current OpenAI file search patterns: create a vector store, upload files with `purpose="assistants"`, attach files to the vector store, then pass a `file_search` tool with `vector_store_ids` to `client.responses.create`. The chat service also requests `include=["file_search_call.results"]` so retrieved sources can be surfaced when available.

## Tests

```bash
pytest
```

Tests mock OpenAI and internal APIs, so they do not require network access.

## Agents SDK Adaptation

The OpenAI integration is isolated in `app/services/rag.py`, and internal tools are isolated in `app/tools/registry.py`. See `docs/agents-sdk-adaptation.md` for the migration path to an Agents SDK runner.
