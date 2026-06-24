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
"""Async mirror of the headless Keycloak offline-token authentication for the ONDEWO T2S client (D18).

Identical contract to :mod:`ondewo.t2s.client.utils.keycloak` but with an awaitable HTTP transport and async
``login`` / ``access_token`` / ``authorization_metadata`` coroutines. The token endpoint call is injectable so
unit tests stay fully hermetic.
"""
import asyncio
import time
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
    Tuple,
)

from ondewo.t2s.client.utils.keycloak import (
    _REFRESH_LEEWAY_S,
    KeycloakAuthenticationError,
    build_token_url,
)

__all__ = ["AsyncKeycloakTokenProvider", "AsyncHttpTransport", "build_token_url"]

# An async transport posts the (url, form fields) to the Keycloak token endpoint and returns the parsed JSON body.
AsyncHttpTransport = Callable[[str, Dict[str, str]], Awaitable[Dict[str, Any]]]


async def _default_async_transport(url: str, fields: Dict[str, str]) -> Dict[str, Any]:
    """Default async transport that runs the synchronous :mod:`requests` transport in a thread.

    Avoids adding an async HTTP dependency (``httpx``/``aiohttp``) while keeping the call off the event loop.

    Args:
        url (str):
            The Keycloak token endpoint URL.
        fields (Dict[str, str]):
            The form body fields.

    Returns:
        Dict[str, Any]:
            The parsed JSON response body.
    """
    from ondewo.t2s.client.utils.keycloak import _requests_transport

    return await asyncio.to_thread(_requests_transport, url, fields)


class AsyncKeycloakTokenProvider:
    """Async variant of :class:`~ondewo.t2s.client.utils.keycloak.KeycloakTokenProvider` (D18).

    Performs the ROPC offline-token login, auto-refreshes the access token, and exposes the
    ``Authorization: Bearer`` metadata tuple. Concurrency-safe: an :class:`asyncio.Lock` created in ``__init__``
    serializes login/refresh so concurrent calls do not race the token endpoint.
    """

    def __init__(
        self,
        token_url: str,
        client_id: str,
        username: str,
        password: str,
        token_expiration_in_s: Optional[int] = None,
        transport: Optional[AsyncHttpTransport] = None,
        time_func: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialize the async provider.

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
            transport (Optional[AsyncHttpTransport]):
                Awaitable HTTP transport. Defaults to running the sync ``requests`` transport in a thread.
            time_func (Callable[[], float]):
                Monotonic clock used for expiry bookkeeping. Injectable for tests.
        """
        self._token_url: str = token_url
        self._client_id: str = client_id
        self._username: str = username
        self._password: str = password
        self._token_expiration_in_s: Optional[int] = token_expiration_in_s
        self._transport: AsyncHttpTransport = transport if transport is not None else _default_async_transport
        self._time: Callable[[], float] = time_func

        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._access_token_expires_at: float = 0.0
        self._login_time: Optional[float] = None
        # Created here (not at module/class scope) to avoid the "Lock bound to a different event loop" trap.
        self._lock: asyncio.Lock = asyncio.Lock()

    async def login(self) -> None:
        """Perform the one-time ROPC offline-token login.

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
        self._store_token_response(await self._transport(self._token_url, fields))

    async def _refresh(self) -> None:
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
        self._store_token_response(await self._transport(self._token_url, fields))

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

    async def access_token(self, force_refresh: bool = False) -> str:
        """Return a currently-valid access token, refreshing it if needed.

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
        async with self._lock:
            if self._access_token is None:
                await self.login()
                assert self._access_token is not None  # noqa: S101 - login() guarantees a token or raises
                return self._access_token

            needs_refresh: bool = (
                force_refresh or self._time() >= (self._access_token_expires_at - _REFRESH_LEEWAY_S)
            )
            if not needs_refresh:
                return self._access_token

            if self._refresh_window_elapsed():
                if not force_refresh and self._time() < self._access_token_expires_at:
                    return self._access_token
                raise KeycloakAuthenticationError(
                    "Keycloak token expired and the bounded refresh window "
                    f"(token_expiration_in_s={self._token_expiration_in_s}) has elapsed; re-login required."
                )

            await self._refresh()
            assert self._access_token is not None  # noqa: S101 - _refresh() guarantees a token or raises
            return self._access_token

    async def authorization_metadata(self, force_refresh: bool = False) -> Tuple[str, str]:
        """Return the gRPC ``Authorization: Bearer`` metadata tuple for the current access token.

        Args:
            force_refresh (bool):
                Force a token refresh before building the metadata.

        Returns:
            Tuple[str, str]:
                ``("authorization", "Bearer <access_token>")``.
        """
        token: str = await self.access_token(force_refresh=force_refresh)
        return ("authorization", f"Bearer {token}")
