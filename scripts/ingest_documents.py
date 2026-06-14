import argparse
import json
from pathlib import Path

from app.core.config import get_settings
from app.services.ingestion import DocumentMetadata, IngestionService
from app.services.openai_client import get_openai_client


def load_registry(path: Path) -> list[DocumentMetadata]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    base_dir = path.parent
    documents = []
    for item in data:
        document = DocumentMetadata.model_validate(item)
        if not document.path.is_absolute():
            document.path = base_dir / document.path
        documents.append(document)
    return documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest approved internal documents.")
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--vector-store-id", default=None)
    parser.add_argument("--vector-store-name", default="internal-knowledge")
    args = parser.parse_args()

    settings = get_settings()
    service = IngestionService(client=get_openai_client(), settings=settings)
    vector_store_id = service.ensure_vector_store(args.vector_store_id, args.vector_store_name)
    results = service.ingest(load_registry(args.registry), vector_store_id)

    print(json.dumps({"vector_store_id": vector_store_id, "documents": [r.model_dump() for r in results]}, indent=2))


if __name__ == "__main__":
    main()

