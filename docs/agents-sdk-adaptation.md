# Agents SDK Adaptation

The project keeps model orchestration behind `app/services/rag.py` and tool execution behind `app/tools/registry.py` so it can move to the OpenAI Agents SDK without changing API routes or internal API clients.

Suggested migration shape:

1. Convert each entry from `ToolRegistry.openai_tool_definitions()` into an Agents SDK tool wrapper.
2. Keep the same Pydantic argument models for server-side validation.
3. Preserve `Principal` authorization checks inside tool handlers.
4. Replace `RagChatService.answer()` with an agent runner that has the file search tool and internal tools registered.
5. Keep `/chat` request/response schemas stable so frontend and gateway integrations do not change.

This split also makes it easier to introduce specialist agents later, such as a policy agent, support-ticket agent, and directory agent, while keeping audit logging and authorization centralized.

