from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, max_length=128)
    department: str | None = Field(default=None, max_length=128)


class SourceCitation(BaseModel):
    title: str | None = None
    file_id: str | None = None
    source_url: str | None = None
    snippet: str | None = None


class ToolCallSummary(BaseModel):
    name: str
    status: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceCitation] = []
    tool_calls: list[ToolCallSummary] = []

