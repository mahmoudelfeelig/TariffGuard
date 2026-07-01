from __future__ import annotations

import secrets
import string
from typing import Any

import boto3


def _temporary_password() -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        value = "".join(secrets.choice(alphabet) for _ in range(18))
        if (
            any(char.islower() for char in value)
            and any(char.isupper() for char in value)
            and any(char.isdigit() for char in value)
            and any(char in "!@#$%^&*" for char in value)
        ):
            return value


class CognitoRepository:
    def __init__(self, user_pool_id: str, client: Any | None = None) -> None:
        self.user_pool_id = user_pool_id
        self.client = client or boto3.client("cognito-idp")

    def list_users(self) -> list[dict[str, Any]]:
        users: list[dict[str, Any]] = []
        pagination_token: str | None = None
        while True:
            kwargs: dict[str, Any] = {"UserPoolId": self.user_pool_id, "Limit": 60}
            if pagination_token:
                kwargs["PaginationToken"] = pagination_token
            response = self.client.list_users(**kwargs)
            for user in response.get("Users", []):
                attributes = {
                    item["Name"]: item["Value"] for item in user.get("Attributes", [])
                }
                groups = self.client.admin_list_groups_for_user(
                    UserPoolId=self.user_pool_id, Username=user["Username"]
                ).get("Groups", [])
                users.append(
                    {
                        "username": user["Username"],
                        "email": attributes.get("email", user["Username"]),
                        "enabled": user.get("Enabled", False),
                        "status": user.get("UserStatus", "UNKNOWN"),
                        "role": (
                            "admin"
                            if any(group["GroupName"] == "admins" for group in groups)
                            else "operator"
                        ),
                        "createdAt": (
                            user["UserCreateDate"].isoformat()
                            if user.get("UserCreateDate")
                            else None
                        ),
                    }
                )
            pagination_token = response.get("PaginationToken")
            if not pagination_token:
                break
        return users

    def create_user(self, email: str, role: str) -> dict[str, str]:
        password = _temporary_password()
        response = self.client.admin_create_user(
            UserPoolId=self.user_pool_id,
            Username=email,
            TemporaryPassword=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
            ],
            MessageAction="SUPPRESS",
        )
        username = response["User"]["Username"]
        if role == "admin":
            self.client.admin_add_user_to_group(
                UserPoolId=self.user_pool_id, Username=username, GroupName="admins"
            )
        return {
            "username": username,
            "email": email,
            "role": role,
            "temporaryPassword": password,
        }

    def set_enabled(self, username: str, enabled: bool) -> None:
        method = self.client.admin_enable_user if enabled else self.client.admin_disable_user
        method(UserPoolId=self.user_pool_id, Username=username)
