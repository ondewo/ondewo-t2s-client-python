# Copyright 2021-2026 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Headless Keycloak offline-token authentication for the ONDEWO T2S client (D18).

The provider performs a Resource-Owner-Password-Credentials (ROPC) grant with ``scope=offline_access`` against a
**public** Keycloak client (no ``client_secret`` — Q1) to obtain a long-lived *offline* refresh token, then
auto-refreshes the short-lived access token (``grant_type=refresh_token``) and exposes it as the
``Authorization: Bearer`` gRPC metadata tuple. The refresh loop stops once ``token_expiration_in_s`` has elapsed
since login.

The HTTP call to the Keycloak token endpoint is injectable (``transport``) so unit tests can run fully hermetic
without any network.
"""
import time
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Tuple,
)

import requests

# A transport posts the (url, form-encoded fields) to the Keycloak token endpoint and returns the parsed JSON body.
HttpTransport = Callable[[str, Dict[str, str]], Dict[str, Any]]

# Refresh the access token once it is within this many seconds of its expiry, so a call never races ``exp``.
_REFRESH_LEEWAY_S: int = 30


class KeycloakAuthenticationError(Exception):
    """Raised when the Keycloak token endpoint rejects a grant or returns an unusable response."""


def _requests_transport(url: str, fields: Dict[str, str]) -> Dict[str, Any]:
    """Default transport backed by :mod:`requests`.

    Args:
        url (str):
            The Keycloak token endpoint URL.
        fields (Dict[str, str]):
            The ``application/x-www-form-urlencoded`` body fields.

    Returns:
        Dict[str, Any]:
            The parsed JSON response body.

    Raises:
        KeycloakAuthenticationError:
            If the request fails or the endpoint returns a non-2xx status.
    """
    try:
        response: requests.Response = requests.post(url, data=fields, timeout=30)
    except requests.RequestException as exc:
        raise KeycloakAuthenticationError(f"Keycloak token request to {url!r} failed: {exc}") from exc

    if response.status_code >= 400:
        raise KeycloakAuthenticationError(
            f"Keycloak token endpoint {url!r} returned status {response.status_code}: {response.text}"
        )

    body: Dict[str, Any] = response.json()
    return body


def build_token_url(keycloak_url: str, realm: str) -> str:
    """Build the OIDC token endpoint URL for a realm.

    Args:
        keycloak_url (str):
            Base Keycloak URL (e.g. ``"https://host/auth"``); a trailing slash is tolerated.
        realm (str):
            Realm name (e.g. ``"ondewo-ccai-platform"``).

    Returns:
        str:
            The full ``.../realms/<realm>/protocol/openid-connect/token`` URL.
    """
    base: str = keycloak_url.rstrip("/")
    return f"{base}/realms/{realm}/protocol/openid-connect/token"


class KeycloakTokenProvider:
    """Acquires and auto-refreshes a Keycloak access token via the ROPC offline-token flow (D18).

    The provider logs in once with ``grant_type=password`` + ``scope=offline_access`` against a public client,
    keeps the resulting offline refresh token, and exchanges it for a fresh access token whenever the current one
    is about to expire. After ``token_expiration_in_s`` seconds (measured from login) the refresh loop stops and
    further calls to :meth:`access_token` raise :class:`KeycloakAuthenticationError`.
    """

    def __init__(
        self,
        token_url: str,
        client_id: str,
        username: str,
        password: str,
        token_expiration_in_s: Optional[int] = None,
        transport: Optional[HttpTransport] = None,
        time_func: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialize the provider.

        Args:
            token_url (str):
                The Keycloak OIDC token endpoint URL.
            client_id (str):
                Public client id used for the ROPC grant (no secret).
            username (str):
                Keycloak user name for the ROPC grant.
            password (str):
                Password for the ROPC grant.
            token_expiration_in_s (Optional[int]):
                Upper bound on how long auto-refresh runs, measured from login. ``None`` means run until the
                offline session expires.
            transport (Optional[HttpTransport]):
                HTTP transport to call the token endpoint. Defaults to a :mod:`requests`-backed transport.
            time_func (Callable[[], float]):
                Monotonic clock used for expiry bookkeeping. Injectable for tests.
        """
        self._token_url: str = token_url
        self._client_id: str = client_id
        self._username: str = username
        self._password: str = password
        self._token_expiration_in_s: Optional[int] = token_expiration_in_s
        self._transport: HttpTransport = transport if transport is not None else _requests_transport
        self._time: Callable[[], float] = time_func

        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._access_token_expires_at: float = 0.0
        self._login_time: Optional[float] = None

    def login(self) -> None:
        """Perform the one-time ROPC offline-token login.

        Calls the token endpoint with ``grant_type=password``, the public ``client_id``, ``username``,
        ``password`` and ``scope=offline_access``, then stores the access + offline refresh tokens.

        Raises:
            KeycloakAuthenticationError:
                If the grant is rejected or the response lacks an access/refresh token.
        """
        fields: Dict[str, str] = {
            "grant_type": "password",
            "client_id": self._client_id,
            "username": self._username,
            "password": self._password,
            "scope": "offline_access",
        }
        self._login_time = self._time()
        self._store_token_response(self._transport(self._token_url, fields))

    def _refresh(self) -> None:
        """Exchange the offline refresh token for a fresh access token.

        Raises:
            KeycloakAuthenticationError:
                If no offline refresh token is available or the refresh grant is rejected.
        """
        if not self._refresh_token:
            raise KeycloakAuthenticationError("Cannot refresh: no offline refresh token; call login() first.")

        fields: Dict[str, str] = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "refresh_token": self._refresh_token,
        }
        self._store_token_response(self._transport(self._token_url, fields))

    def _store_token_response(self, body: Dict[str, Any]) -> None:
        """Persist tokens + expiry from a token-endpoint response body.

        Args:
            body (Dict[str, Any]):
                Parsed JSON body containing at least ``access_token``.

        Raises:
            KeycloakAuthenticationError:
                If the body carries no ``access_token``.
        """
        access_token: Optional[str] = body.get("access_token")
        if not access_token:
            raise KeycloakAuthenticationError(f"Keycloak response has no access_token: {body}")

        self._access_token = access_token
        # Keycloak rotates the refresh token; keep the previous one if the response omits it.
        refresh_token: Optional[str] = body.get("refresh_token")
        if refresh_token:
            self._refresh_token = refresh_token

        expires_in: int = int(body.get("expires_in", 0))
        self._access_token_expires_at = self._time() + expires_in

    def _refresh_window_elapsed(self) -> bool:
        """Whether ``token_expiration_in_s`` has elapsed since login.

        Returns:
            bool:
                ``True`` if the bounded refresh window has passed (no further refresh allowed).
        """
        if self._token_expiration_in_s is None or self._login_time is None:
            return False
        return (self._time() - self._login_time) >= self._token_expiration_in_s

    def access_token(self, force_refresh: bool = False) -> str:
        """Return a currently-valid access token, refreshing it if needed.

        Logs in on first use, refreshes when the access token is within the leeway of its expiry, and refreshes
        unconditionally when ``force_refresh`` is set (used to recover from ``UNAUTHENTICATED``). Once the bounded
        refresh window has elapsed the current token is returned only while still valid; otherwise an error is
        raised.

        Args:
            force_refresh (bool):
                Force a refresh regardless of the current token's remaining lifetime.

        Returns:
            str:
                A valid access token.

        Raises:
            KeycloakAuthenticationError:
                If no valid token can be produced (e.g. the bounded refresh window elapsed and the token expired).
        """
        if self._access_token is None:
            self.login()
            assert self._access_token is not None  # noqa: S101 - login() guarantees a token or raises
            return self._access_token

        needs_refresh: bool = force_refresh or self._time() >= (self._access_token_expires_at - _REFRESH_LEEWAY_S)
        if not needs_refresh:
            return self._access_token

        if self._refresh_window_elapsed():
            # Refresh is no longer permitted; only the still-valid current token may be served.
            if not force_refresh and self._time() < self._access_token_expires_at:
                return self._access_token
            raise KeycloakAuthenticationError(
                "Keycloak token expired and the bounded refresh window "
                f"(token_expiration_in_s={self._token_expiration_in_s}) has elapsed; re-login required."
            )

        self._refresh()
        assert self._access_token is not None  # noqa: S101 - _refresh() guarantees a token or raises
        return self._access_token

    def authorization_metadata(self, force_refresh: bool = False) -> Tuple[str, str]:
        """Return the gRPC ``Authorization: Bearer`` metadata tuple for the current access token.

        Args:
            force_refresh (bool):
                Force a token refresh before building the metadata.

        Returns:
            Tuple[str, str]:
                ``("authorization", "Bearer <access_token>")``.
        """
        return ("authorization", f"Bearer {self.access_token(force_refresh=force_refresh)}")
