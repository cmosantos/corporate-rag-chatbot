# Deployment Notes

## Recommended Topology

Run the FastAPI service behind an internal gateway or API management layer that terminates TLS, authenticates employees with the corporate identity provider, and injects trusted identity headers such as `X-User-Id`, `X-User-Roles`, and `X-Department`.

Do not expose this service directly to the public internet. Keep source documents, vector store IDs, and internal API tokens server-side only.

## Environment Variables

- `OPENAI_API_KEY`: loaded from a secret store or workload identity flow
- `OPENAI_MODEL`: default `gpt-5.5`; override per deployment if needed
- `OPENAI_VECTOR_STORE_ID`: vector store created by the ingestion job
- `INTERNAL_API_BASE_URL`: placeholder internal API root
- `INTERNAL_API_TOKEN`: service credential for approved internal APIs
- `AUTH_SHARED_SECRET`: local development placeholder; production should use gateway identity
- `AUDIT_LOG_PATH`: JSONL audit destination
- `ALLOWED_SENSITIVITY_LEVELS`: sensitivity allowlist for ingestion

## Container

Example Dockerfile:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .
COPY app ./app
COPY scripts ./scripts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Gateway Controls

- Enforce employee authentication before requests reach the service.
- Strip inbound identity headers from clients and re-add trusted values after auth.
- Apply rate limits per user and department.
- Restrict egress so the backend can reach OpenAI and approved internal APIs only.
- Send audit logs to a centralized SIEM or immutable log store.
- Add request size limits for `/chat` and ingestion paths.

## Operational Metrics

Track answer latency, OpenAI error rate, retrieval source count, tool call count, tool failure rate, refusals, unknown-answer rate, and cost per department or tenant.

