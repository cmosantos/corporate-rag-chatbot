from dataclasses import dataclass

from fastapi import Header

from app.core.errors import AppError


@dataclass(frozen=True)
class Principal:
    user_id: str
    roles: set[str]
    department: str | None = None

    def has_role(self, role: str) -> bool:
        return role in self.roles


def get_principal(
    x_user_id: str | None = Header(default=None),
    x_user_roles: str | None = Header(default="employee"),
    x_department: str | None = Header(default=None),
) -> Principal:
    """Trust identity headers only when set by an internal gateway."""
    if not x_user_id:
        raise AppError("Missing authenticated user context.", status_code=401)
    roles = {role.strip() for role in (x_user_roles or "").split(",") if role.strip()}
    if "employee" not in roles:
        roles.add("employee")
    return Principal(user_id=x_user_id, roles=roles, department=x_department)


def require_role(principal: Principal, role: str) -> None:
    if not principal.has_role(role):
        raise AppError("You are not authorized to perform that action.", status_code=403)

