# Frontend Integration

The planned Lovable frontend should remain a separate presentation layer and communicate with the FastAPI backend through HTTPS.

## Required API configuration

Configure the frontend with a public environment variable named `VITE_API_BASE_URL`. Its value must point to the deployed FastAPI service without a trailing slash.

Example:

```text
VITE_API_BASE_URL=https://api.example.com
```

The backend must include the Lovable deployment domain in the `ALLOWED_ORIGINS` environment variable.

## Chat request

The interface sends a `POST` request to `/chat` using JSON.

```json
{
  "question": "Where can I find the remote work policy?",
  "conversation_id": "browser-generated-id"
}
```

For a portfolio demonstration, the frontend can send fixed demo identity headers:

```text
X-User-Id: portfolio-demo
X-User-Roles: employee
X-Department: operations
```

These headers are only suitable for a controlled demonstration. In production, a trusted gateway or identity provider must authenticate the employee, remove client-provided identity headers and inject verified identity context.

## Response presentation

The interface should display:

- the assistant answer as the primary content;
- source citations below the answer;
- approved tool calls as a compact activity summary;
- clear loading, empty and error states;
- a visible label indicating when the interface is operating in demo mode.

## Security boundary

The browser must never contain the OpenAI API key, vector store ID or internal API credentials. All model and tool calls remain inside the FastAPI backend.

## Recommended user experience

Use a professional corporate design with a left navigation panel, a focused conversation area and a source panel. The first screen should include suggested questions related to IT support, onboarding, policies and internal procedures. Avoid decorative AI imagery that makes the application look like a generic chatbot.
