import pytest

from app.core.auth import Principal
from app.core.errors import AppError
from app.tools.internal_api import InternalApiClient
from app.tools.registry import ToolRegistry


def test_ticket_status_validates_ticket_id() -> None:
    registry = ToolRegistry(InternalApiClient())
    principal = Principal(user_id="u1", roles={"employee", "it_support"})

    result = registry.execute("get_ticket_status", '{"ticket_id":"TCK-12345"}', principal)

    assert result["ticket_id"] == "TCK-12345"
    assert result["status"] == "open"


def test_ticket_status_rejects_unapproved_id_shape() -> None:
    registry = ToolRegistry(InternalApiClient())
    principal = Principal(user_id="u1", roles={"employee", "it_support"})

    with pytest.raises(AppError):
        registry.execute("get_ticket_status", '{"ticket_id":"../../etc/passwd"}', principal)


def test_directory_lookup_requires_role() -> None:
    registry = ToolRegistry(InternalApiClient())
    principal = Principal(user_id="u1", roles={"employee"})

    with pytest.raises(AppError) as exc:
        registry.execute("lookup_directory_person", '{"email":"person@example.com"}', principal)

    assert exc.value.status_code == 403

