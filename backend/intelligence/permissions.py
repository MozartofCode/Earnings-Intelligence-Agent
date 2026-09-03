import os

from rest_framework.permissions import SAFE_METHODS, BasePermission


class HasApiToken(BasePermission):
    """Require `Authorization: Token <API_AUTH_TOKEN>` on unsafe requests.

    A no-op (everything allowed) when API_AUTH_TOKEN is unset, so local dev
    and the bundled frontend work out of the box. Set API_AUTH_TOKEN before
    exposing the API beyond localhost.
    """

    def has_permission(self, request, view):
        token = os.getenv("API_AUTH_TOKEN")
        if not token or request.method in SAFE_METHODS:
            return True
        return request.headers.get("Authorization") == f"Token {token}"
