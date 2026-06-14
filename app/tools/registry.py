import json
from typing import Any, Callable

from fastapi import Depends
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.core.auth import Principal
from app.core.errors import AppError
from app.tools.internal_api import InternalApiClient


class PolicyMetadataArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    policy_key: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{1,63}$")


class TicketStatusArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    ticket_id: str = Field(pattern=r"^TCK-[0-9]{3,12}$")


class DirectoryLookupArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ToolRegistry:
    def __init__(self, internal_api: InternalApiClient) -> None:
        self.internal_api = internal_api

    def openai_tool_definitions(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "name": "get_policy_metadata",
                "description": "Look up metadata for an internal policy by approved policy key.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "policy_key": {
                            "type": "string",
                            "description": "Stable policy key, not a free-form policy title.",
                        }
                    },
                    "required": ["policy_key"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "get_ticket_status",
                "description": "Look up the status of an internal support ticket the user can access.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {"ticket_id": {"type": "string", "pattern": "^TCK-[0-9]{3,12}$"}},
                    "required": ["ticket_id"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "lookup_directory_person",
                "description": "Look up minimal directory information for a person by corporate email.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {"email": {"type": "string", "format": "email"}},
                    "required": ["email"],
                    "additionalProperties": False,
                },
            },
        ]

    def execute(self, name: str, raw_arguments: str, principal: Principal) -> dict[str, Any]:
        if name not in self._handlers:
            raise AppError("Requested tool is not approved.", status_code=400)
        try:
            arguments = json.loads(raw_arguments or "{}")
        except json.JSONDecodeError as exc:
            raise AppError("Tool arguments were not valid JSON.", status_code=400) from exc

        schema, handler = self._handlers[name]
        try:
            parsed = schema.model_validate(arguments)
        except ValidationError as exc:
            raise AppError("Tool arguments failed validation.", status_code=400) from exc
        return handler(parsed, principal)

    @property
    def _handlers(
        self,
    ) -> dict[str, tuple[type[BaseModel], Callable[[BaseModel, Principal], dict[str, Any]]]]:
        return {
            "get_policy_metadata": (
                PolicyMetadataArgs,
                lambda args, principal: self.internal_api.get_policy_metadata(
                    args.policy_key, principal
                ),
            ),
            "get_ticket_status": (
                TicketStatusArgs,
                lambda args, principal: self.internal_api.get_ticket_status(args.ticket_id, principal),
            ),
            "lookup_directory_person": (
                DirectoryLookupArgs,
                lambda args, principal: self.internal_api.lookup_directory_person(
                    args.email, principal
                ),
            ),
        }


def get_internal_api_client() -> InternalApiClient:
    return InternalApiClient()


def get_tool_registry(
    internal_api: InternalApiClient = Depends(get_internal_api_client),
) -> ToolRegistry:
    return ToolRegistry(internal_api)

