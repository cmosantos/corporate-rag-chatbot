# Security Notes

- Treat retrieval as confidential server-side context. Never send source documents to browser clients.
- Validate tool calls twice: schema validation before the model sees the tool, and server-side validation before execution.
- Check authorization in every internal API handler, even when the model selected the tool correctly.
- Return minimal tool data to the model. Avoid dumping full tickets, directory records, or policy documents.
- Keep audit logs metadata-focused. Do not log full prompts, retrieved chunks, or secrets by default.
- Ingest only approved sensitivity levels. Reject unsupported formats and documents without ownership metadata.
- Use evals and red-team prompts for prompt injection, stale policy answers, and unauthorized tool attempts.
- Rotate API keys and internal service tokens through a secret manager.

