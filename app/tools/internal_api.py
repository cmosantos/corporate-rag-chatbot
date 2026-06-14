from app.core.auth import Principal, require_role


class InternalApiClient:
    """Placeholder for organization-approved internal APIs."""

    def get_policy_metadata(self, policy_key: str, principal: Principal) -> dict[str, str]:
        return {
            "policy_key": policy_key,
            "title": "Generic policy metadata",
            "owner": "Policy Office",
            "freshness_date": "2026-01-01",
        }

    def get_ticket_status(self, ticket_id: str, principal: Principal) -> dict[str, str]:
        require_role(principal, "it_support")
        return {
            "ticket_id": ticket_id,
            "status": "open",
            "owner_team": "Support",
        }

    def lookup_directory_person(self, email: str, principal: Principal) -> dict[str, str]:
        require_role(principal, "directory_reader")
        return {
            "email": email,
            "display_name": "Example Employee",
            "department": "Example Department",
        }

