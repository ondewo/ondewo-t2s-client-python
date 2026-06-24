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
"""Hermetic unit tests for the headless Keycloak offline-token auth (D18).

No network: the Keycloak token endpoint is replaced by an in-memory fake transport, and time is driven by a
controllable clock.
"""
import asyncio
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Tuple,
    TypeVar,
)

import pytest

from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.utils import keycloak as keycloak_module
from ondewo.t2s.client.utils.async_keycloak import AsyncKeycloakTokenProvider
from ondewo.t2s.client.utils.keycloak import (
    KeycloakAuthenticationError,
    KeycloakTokenProvider,
    build_token_url,
)

KEYCLOAK_URL: str = "https://host/auth"
REALM: str = "ondewo-ccai-platform"
CLIENT_ID: str = "ondewo-nlu-cai-sdk-public"
USERNAME: str = "tech-user@ondewo.com"
PASSWORD: str = "s3cr3t"
TOKEN_URL: str = "https://host/auth/realms/ondewo-ccai-platform/protocol/openid-connect/token"
ACCESS_TTL_S: int = 300

T = TypeVar("T")


def _run(coro_factory: Callable[[], Coroutine[Any, Any, T]]) -> T:
    return asyncio.run(coro_factory())


class FakeClock:
    """A monotonic clock whose value the test advances explicitly."""

    def __init__(self) -> None:
        self.now: float = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class FakeTransport:
    """In-memory replacement for the Keycloak token endpoint.

    Records every posted form body and returns a scripted access/refresh token per call so tests can assert both
    the request shape and that distinct tokens are issued across login/refresh.
    """

    def __init__(self, expires_in: int = ACCESS_TTL_S) -> None:
        self.calls: List[Tuple[str, Dict[str, str]]] = []
        self._counter: int = 0
        self._expires_in: int = expires_in

    def __call__(self, url: str, fields: Dict[str, str]) -> Dict[str, Any]:
        self.calls.append((url, dict(fields)))
        self._counter += 1
        return {
            "access_token": f"access-{self._counter}",
            "refresh_token": f"offline-{self._counter}",
            "expires_in": self._expires_in,
            "token_type": "Bearer",
        }


class AsyncFakeTransport:
    """Awaitable wrapper around :class:`FakeTransport`."""

    def __init__(self, expires_in: int = ACCESS_TTL_S) -> None:
        self.inner: FakeTransport = FakeTransport(expires_in=expires_in)

    async def __call__(self, url: str, fields: Dict[str, str]) -> Dict[str, Any]:
        return self.inner(url, fields)

    @property
    def calls(self) -> List[Tuple[str, Dict[str, str]]]:
        return self.inner.calls


def _make_provider(
    transport: FakeTransport,
    clock: FakeClock,
    token_expiration_in_s: int | None = None,
) -> KeycloakTokenProvider:
    return KeycloakTokenProvider(
        token_url=TOKEN_URL,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
        token_expiration_in_s=token_expiration_in_s,
        transport=transport,
        time_func=clock,
    )


# --------------------------------------------------------------------------- #
# build_token_url
# --------------------------------------------------------------------------- #
def test_build_token_url_composes_oidc_path() -> None:
    assert build_token_url(KEYCLOAK_URL, REALM) == TOKEN_URL


def test_build_token_url_tolerates_trailing_slash() -> None:
    assert build_token_url(KEYCLOAK_URL + "/", REALM) == TOKEN_URL


# --------------------------------------------------------------------------- #
# Sync provider — ROPC login
# --------------------------------------------------------------------------- #
def test_login_uses_ropc_offline_access_public_client() -> None:
    transport: FakeTransport = FakeTransport()
    provider: KeycloakTokenProvider = _make_provider(transport, FakeClock())

    provider.login()

    assert len(transport.calls) == 1
    url, fields = transport.calls[0]
    assert url == TOKEN_URL
    assert fields["grant_type"] == "password"
    assert fields["scope"] == "offline_access"
    assert fields["client_id"] == CLIENT_ID
    assert fields["username"] == USERNAME
    assert fields["password"] == PASSWORD
    # Public client (Q1): no client secret must ever be sent.
    assert "client_secret" not in fields


def test_authorization_metadata_is_bearer() -> None:
    transport: FakeTransport = FakeTransport()
    provider: KeycloakTokenProvider = _make_provider(transport, FakeClock())

    key, value = provider.authorization_metadata()

    assert key == "authorization"
    assert value == "Bearer access-1"


def test_first_access_token_logs_in_lazily() -> None:
    transport: FakeTransport = FakeTransport()
    provider: KeycloakTokenProvider = _make_provider(transport, FakeClock())

    assert provider.access_token() == "access-1"
    assert len(transport.calls) == 1
    assert transport.calls[0][1]["grant_type"] == "password"


def test_access_token_cached_within_validity() -> None:
    transport: FakeTransport = FakeTransport()
    clock: FakeClock = FakeClock()
    provider: KeycloakTokenProvider = _make_provider(transport, clock)

    assert provider.access_token() == "access-1"
    clock.advance(10)
    # Still well inside the 300s TTL minus the 30s leeway → no new call.
    assert provider.access_token() == "access-1"
    assert len(transport.calls) == 1


# --------------------------------------------------------------------------- #
# Sync provider — auto-refresh
# --------------------------------------------------------------------------- #
def test_auto_refresh_uses_refresh_token_grant() -> None:
    transport: FakeTransport = FakeTransport()
    clock: FakeClock = FakeClock()
    provider: KeycloakTokenProvider = _make_provider(transport, clock)

    assert provider.access_token() == "access-1"
    # Cross into the refresh leeway window (300 - 30 = 270s).
    clock.advance(280)
    assert provider.access_token() == "access-2"

    assert len(transport.calls) == 2
    refresh_fields = transport.calls[1][1]
    assert refresh_fields["grant_type"] == "refresh_token"
    assert refresh_fields["client_id"] == CLIENT_ID
    assert refresh_fields["refresh_token"] == "offline-1"
    assert "client_secret" not in refresh_fields


def test_force_refresh_replays_on_unauthenticated() -> None:
    transport: FakeTransport = FakeTransport()
    provider: KeycloakTokenProvider = _make_provider(transport, FakeClock())

    assert provider.access_token() == "access-1"
    # Simulate an UNAUTHENTICATED response triggering a force refresh even though the token is not near expiry.
    assert provider.access_token(force_refresh=True) == "access-2"
    assert transport.calls[1][1]["grant_type"] == "refresh_token"


def test_refresh_rotates_offline_token() -> None:
    transport: FakeTransport = FakeTransport()
    clock: FakeClock = FakeClock()
    provider: KeycloakTokenProvider = _make_provider(transport, clock)

    provider.access_token()
    provider.access_token(force_refresh=True)  # access-2, offline-2
    provider.access_token(force_refresh=True)  # must use the rotated offline-2

    assert transport.calls[2][1]["refresh_token"] == "offline-2"


# --------------------------------------------------------------------------- #
# Sync provider — token_expiration_in_s bounds the refresh loop
# --------------------------------------------------------------------------- #
def test_token_expiration_stops_refresh_loop() -> None:
    transport: FakeTransport = FakeTransport()
    clock: FakeClock = FakeClock()
    provider: KeycloakTokenProvider = _make_provider(transport, clock, token_expiration_in_s=600)

    assert provider.access_token() == "access-1"
    # Advance past the 600s bound AND past the access token's own 300s validity.
    clock.advance(700)
    with pytest.raises(KeycloakAuthenticationError, match="bounded refresh window"):
        provider.access_token()
    # Only the initial login happened; no refresh after the window elapsed.
    assert len(transport.calls) == 1


def test_token_expiration_allows_refresh_before_window_elapses() -> None:
    transport: FakeTransport = FakeTransport()
    clock: FakeClock = FakeClock()
    provider: KeycloakTokenProvider = _make_provider(transport, clock, token_expiration_in_s=600)

    assert provider.access_token() == "access-1"
    # 280s: inside the 600s window but past the refresh leeway → a refresh is allowed.
    clock.advance(280)
    assert provider.access_token() == "access-2"
    assert len(transport.calls) == 2


def test_no_expiration_bound_refreshes_indefinitely() -> None:
    transport: FakeTransport = FakeTransport()
    clock: FakeClock = FakeClock()
    provider: KeycloakTokenProvider = _make_provider(transport, clock, token_expiration_in_s=None)

    provider.access_token()
    for _ in range(3):
        clock.advance(280)
        provider.access_token()

    assert len(transport.calls) == 4  # 1 login + 3 refreshes


# --------------------------------------------------------------------------- #
# Sync provider — error paths
# --------------------------------------------------------------------------- #
def test_missing_access_token_raises() -> None:
    def bad_transport(url: str, fields: Dict[str, str]) -> Dict[str, Any]:
        return {"error": "invalid_grant"}

    provider: KeycloakTokenProvider = KeycloakTokenProvider(
        token_url=TOKEN_URL,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
        transport=bad_transport,
        time_func=FakeClock(),
    )
    with pytest.raises(KeycloakAuthenticationError, match="no access_token"):
        provider.login()


# --------------------------------------------------------------------------- #
# Async provider mirror
# --------------------------------------------------------------------------- #
def test_async_login_uses_ropc_offline_access_public_client() -> None:
    async def _body() -> None:
        transport: AsyncFakeTransport = AsyncFakeTransport()
        provider: AsyncKeycloakTokenProvider = AsyncKeycloakTokenProvider(
            token_url=TOKEN_URL,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
            transport=transport,
            time_func=FakeClock(),
        )
        key, value = await provider.authorization_metadata()
        assert key == "authorization"
        assert value == "Bearer access-1"

        url, fields = transport.calls[0]
        assert url == TOKEN_URL
        assert fields["grant_type"] == "password"
        assert fields["scope"] == "offline_access"
        assert "client_secret" not in fields

    _run(_body)


def test_async_auto_refresh_uses_refresh_token_grant() -> None:
    async def _body() -> None:
        transport: AsyncFakeTransport = AsyncFakeTransport()
        clock: FakeClock = FakeClock()
        provider: AsyncKeycloakTokenProvider = AsyncKeycloakTokenProvider(
            token_url=TOKEN_URL,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
            transport=transport,
            time_func=clock,
        )
        assert await provider.access_token() == "access-1"
        clock.advance(280)
        assert await provider.access_token() == "access-2"
        assert transport.calls[1][1]["grant_type"] == "refresh_token"

    _run(_body)


def test_async_access_token_cached_within_validity() -> None:
    async def _body() -> None:
        transport: AsyncFakeTransport = AsyncFakeTransport()
        clock: FakeClock = FakeClock()
        provider: AsyncKeycloakTokenProvider = AsyncKeycloakTokenProvider(
            token_url=TOKEN_URL,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
            transport=transport,
            time_func=clock,
        )
        assert await provider.access_token() == "access-1"
        clock.advance(10)
        # Still well inside the 300s TTL minus the 30s leeway → cached token, no new call.
        assert await provider.access_token() == "access-1"
        assert len(transport.calls) == 1

    _run(_body)


def test_async_token_expiration_stops_refresh_loop() -> None:
    async def _body() -> None:
        transport: AsyncFakeTransport = AsyncFakeTransport()
        clock: FakeClock = FakeClock()
        provider: AsyncKeycloakTokenProvider = AsyncKeycloakTokenProvider(
            token_url=TOKEN_URL,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
            token_expiration_in_s=600,
            transport=transport,
            time_func=clock,
        )
        assert await provider.access_token() == "access-1"
        clock.advance(700)
        with pytest.raises(KeycloakAuthenticationError, match="bounded refresh window"):
            await provider.access_token()
        assert len(transport.calls) == 1

    _run(_body)


# --------------------------------------------------------------------------- #
# ClientConfig validation (dual-mode + D18)
# --------------------------------------------------------------------------- #
def test_config_legacy_minimal_is_valid() -> None:
    # Backward-compatible: no http_token, no keycloak fields — just host/port (legacy cai-token path).
    config: ClientConfig = ClientConfig(host="localhost", port="50555")
    assert config.use_keycloak is False
    assert config.http_token == ""


def test_config_http_token_no_longer_required() -> None:
    # D5: http_token must not be mandatory anymore.
    config: ClientConfig = ClientConfig(host="localhost", port="50555", user_name="u@x.com", password="pw")
    assert config.http_token == ""


def test_config_keycloak_full_is_valid_and_resolves_username() -> None:
    config: ClientConfig = ClientConfig(
        host="localhost",
        port="50555",
        keycloak_url=KEYCLOAK_URL,
        realm=REALM,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
        token_expiration_in_s=3600,
    )
    assert config.use_keycloak is True
    assert config.resolved_username == USERNAME


def test_config_keycloak_falls_back_to_user_name() -> None:
    config: ClientConfig = ClientConfig(
        host="localhost",
        port="50555",
        keycloak_url=KEYCLOAK_URL,
        realm=REALM,
        client_id=CLIENT_ID,
        user_name=USERNAME,
        password=PASSWORD,
    )
    assert config.resolved_username == USERNAME


def test_config_partial_keycloak_raises() -> None:
    with pytest.raises(ValueError, match="keycloak_url"):
        ClientConfig(
            host="localhost",
            port="50555",
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            # client_id missing
            username=USERNAME,
            password=PASSWORD,
        )


def test_config_keycloak_without_credentials_raises() -> None:
    with pytest.raises(ValueError, match="username"):
        ClientConfig(
            host="localhost",
            port="50555",
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            password=PASSWORD,
        )

    with pytest.raises(ValueError, match="password"):
        ClientConfig(
            host="localhost",
            port="50555",
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            username=USERNAME,
        )


# --------------------------------------------------------------------------- #
# Default requests-backed transport (_requests_transport) — patched, no network
# --------------------------------------------------------------------------- #
class FakeRequestsResponse:
    """Minimal ``requests.Response`` stand-in for the default transport's status/json/text contract."""

    def __init__(self, status_code: int, body: Dict[str, Any]) -> None:
        self.status_code: int = status_code
        self._body: Dict[str, Any] = body

    def json(self) -> Dict[str, Any]:
        return self._body

    @property
    def text(self) -> str:
        return repr(self._body)


def test_default_transport_returns_parsed_body_on_2xx(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: List[Tuple[str, Dict[str, str]]] = []

    def fake_post(url: str, data: Dict[str, str], timeout: float) -> FakeRequestsResponse:
        captured.append((url, dict(data)))
        return FakeRequestsResponse(200, {"access_token": "acc-default"})

    monkeypatch.setattr(keycloak_module.requests, "post", fake_post)

    provider: KeycloakTokenProvider = KeycloakTokenProvider(
        token_url=TOKEN_URL,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
        time_func=FakeClock(),
    )
    # No transport injected → the default _requests_transport is exercised.
    assert provider.access_token() == "acc-default"
    assert captured[0][0] == TOKEN_URL
    assert captured[0][1]["scope"] == "offline_access"
    assert "client_secret" not in captured[0][1]


def test_default_transport_raises_on_non_2xx(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url: str, data: Dict[str, str], timeout: float) -> FakeRequestsResponse:
        return FakeRequestsResponse(401, {"error": "invalid_grant"})

    monkeypatch.setattr(keycloak_module.requests, "post", fake_post)

    provider: KeycloakTokenProvider = KeycloakTokenProvider(
        token_url=TOKEN_URL,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
        time_func=FakeClock(),
    )
    with pytest.raises(KeycloakAuthenticationError, match="status 401"):
        provider.login()


def test_default_transport_wraps_request_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url: str, data: Dict[str, str], timeout: float) -> FakeRequestsResponse:
        raise keycloak_module.requests.RequestException("connection refused")

    monkeypatch.setattr(keycloak_module.requests, "post", fake_post)

    provider: KeycloakTokenProvider = KeycloakTokenProvider(
        token_url=TOKEN_URL,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
        time_func=FakeClock(),
    )
    with pytest.raises(KeycloakAuthenticationError, match="failed"):
        provider.login()


# --------------------------------------------------------------------------- #
# Sync provider — remaining error / stale-token branches
# --------------------------------------------------------------------------- #
def test_refresh_without_login_raises() -> None:
    transport: FakeTransport = FakeTransport()
    provider: KeycloakTokenProvider = _make_provider(transport, FakeClock())

    # White-box: _refresh guards against being called before any offline refresh token exists. The public
    # access_token() funnels the first call through login(), so this guard is only reachable directly.
    with pytest.raises(KeycloakAuthenticationError, match="no offline refresh token"):
        provider._refresh()


def test_bounded_window_serves_still_valid_token_without_refresh() -> None:
    transport: FakeTransport = FakeTransport()
    clock: FakeClock = FakeClock()
    # Window (120s) is shorter than the access-token TTL (300s). At +280s the token is inside the refresh
    # leeway (300 - 30 = 270) so a refresh would normally fire, but the 120s window has elapsed AND the
    # token is still valid → it must be served as-is rather than refreshed or rejected (the 249-250 branch).
    provider: KeycloakTokenProvider = _make_provider(transport, clock, token_expiration_in_s=120)

    assert provider.access_token() == "access-1"
    clock.advance(280)  # inside the refresh leeway, window elapsed, but still before the 300s TTL
    assert provider.access_token() == "access-1"
    assert len(transport.calls) == 1


# --------------------------------------------------------------------------- #
# Async provider — remaining error / stale-token / default-transport branches
# --------------------------------------------------------------------------- #
def test_async_missing_access_token_raises() -> None:
    async def _body() -> None:
        async def bad_transport(url: str, fields: Dict[str, str]) -> Dict[str, Any]:
            return {"error": "invalid_grant"}

        provider: AsyncKeycloakTokenProvider = AsyncKeycloakTokenProvider(
            token_url=TOKEN_URL,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
            transport=bad_transport,
            time_func=FakeClock(),
        )
        with pytest.raises(KeycloakAuthenticationError, match="no access_token"):
            await provider.login()

    _run(_body)


def test_async_refresh_without_login_raises() -> None:
    async def _body() -> None:
        transport: AsyncFakeTransport = AsyncFakeTransport()
        provider: AsyncKeycloakTokenProvider = AsyncKeycloakTokenProvider(
            token_url=TOKEN_URL,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
            transport=transport,
            time_func=FakeClock(),
        )
        # White-box mirror of the sync guard: reachable only by calling _refresh directly.
        with pytest.raises(KeycloakAuthenticationError, match="no offline refresh token"):
            await provider._refresh()

    _run(_body)


def test_async_bounded_window_serves_still_valid_token() -> None:
    async def _body() -> None:
        transport: AsyncFakeTransport = AsyncFakeTransport()
        clock: FakeClock = FakeClock()
        provider: AsyncKeycloakTokenProvider = AsyncKeycloakTokenProvider(
            token_url=TOKEN_URL,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
            token_expiration_in_s=120,
            transport=transport,
            time_func=clock,
        )
        assert await provider.access_token() == "access-1"
        clock.advance(280)  # inside the refresh leeway, window elapsed, but still before the 300s TTL
        assert await provider.access_token() == "access-1"
        assert len(transport.calls) == 1

    _run(_body)


def test_async_default_transport_delegates_to_requests_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    # _default_async_transport runs the sync _requests_transport in a thread; patch that seam so no network.
    captured: List[Tuple[str, Dict[str, str]]] = []

    def fake_requests_transport(url: str, fields: Dict[str, str]) -> Dict[str, Any]:
        captured.append((url, dict(fields)))
        return {"access_token": "acc-async-default", "refresh_token": "off-1", "expires_in": ACCESS_TTL_S}

    # _default_async_transport imports _requests_transport from the sync keycloak module at call time,
    # so patch the symbol there (patching async_keycloak_module would have no effect).
    monkeypatch.setattr(keycloak_module, "_requests_transport", fake_requests_transport)

    async def _body() -> None:
        provider: AsyncKeycloakTokenProvider = AsyncKeycloakTokenProvider(
            token_url=TOKEN_URL,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
            time_func=FakeClock(),
        )
        # No transport injected → _default_async_transport is exercised.
        assert await provider.access_token() == "acc-async-default"
        assert captured[0][0] == TOKEN_URL
        assert captured[0][1]["scope"] == "offline_access"

    _run(_body)
