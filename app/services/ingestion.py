from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import Settings
from app.core.errors import AppError


SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md", ".doc", ".docx", ".pptx", ".html", ".json"}


class DocumentMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    path: Path
    title: str = Field(min_length=1, max_length=256)
    owner: str = Field(min_length=1, max_length=256)
    source_url: str | None = None
    sensitivity: str = "internal"
    freshness_date: str | None = None


class IngestedDocument(BaseModel):
    title: str
    file_id: str
    vector_store_file_id: str | None = None


class IngestionService:
    def __init__(self, client: OpenAI, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    def ensure_vector_store(self, vector_store_id: str | None, name: str) -> str:
        if vector_store_id:
            return vector_store_id
        vector_store = self.client.vector_stores.create(name=name)
        return vector_store.id

    def ingest(self, documents: list[DocumentMetadata], vector_store_id: str) -> list[IngestedDocument]:
        results: list[IngestedDocument] = []
        for document in documents:
            self._validate_document(document)
            with document.path.open("rb") as handle:
                uploaded = self.client.files.create(file=handle, purpose="assistants")
            attached = self.client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=uploaded.id,
                attributes={
                    "title": document.title,
                    "owner": document.owner,
                    "source_url": document.source_url or "",
                    "sensitivity": document.sensitivity,
                    "freshness_date": document.freshness_date or "",
                },
            )
            results.append(
                IngestedDocument(
                    title=document.title,
                    file_id=uploaded.id,
                    vector_store_file_id=getattr(attached, "id", None),
                )
            )
        return results

    def _validate_document(self, document: DocumentMetadata) -> None:
        if not document.path.exists() or not document.path.is_file():
            raise AppError(f"Document not found: {document.path}", status_code=400)
        if document.path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise AppError(f"Unsupported document type: {document.path.suffix}", status_code=400)
        if document.sensitivity.lower() not in self.settings.allowed_sensitivity_set:
            raise AppError(
                f"Document sensitivity is not approved for ingestion: {document.sensitivity}",
                status_code=400,
            )

