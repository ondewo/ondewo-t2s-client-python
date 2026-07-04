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
"""Hermetic unit tests for the D18 Keycloak-aware service interfaces (core auth wiring).

No live server and no network are touched: the keycloak token endpoint is replaced with a fake
``requests.post`` so the offline-token login is exercised without any network. The tests assert
that the generated service wrappers inherit these interfaces and expose the ``metadata`` the
wrapper methods forward as ``Authorization: Bearer`` on every gRPC call.
"""
import asyncio
from typing import (
    Any,
    Dict,
    List,
    Tuple,
)

import pytest

import ondewo.t2s.client.utils.keycloak as keycloak_module
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.core.async_services_interface import AsyncServicesInterface
from ondewo.t2s.client.core.services_interface import ServicesInterface
from ondewo.t2s.client.services.async_text_to_speech import Text2Speech as AsyncText2Speech
from ondewo.t2s.client.services.text_to_speech import Text2Speech

# Bound exactly once so a refactor that changes only an input or an expectation cannot silently
# make a test tautological.
GRPC_HOST: str = "localhost"
GRPC_PORT: str = "50555"
KEYCLOAK_URL: str = "https://kc.example.com/auth"
REALM: str = "ondewo-ccai-platform"
CLIENT_ID: str = "ondewo-nlu-cai-sdk-public"
USERNAME: str = "tech-user@example.com"
PASSWORD: str = "s3cr3t"
ACCESS_TOKEN: str = "acc-1"
EXPECTED_BEARER_METADATA: List[Tuple[str, str]] = [("authorization", f"Bearer {ACCESS_TOKEN}")]


class _FakeResponse:
    """Minimal ``requests.Response`` stand-in returning a canned Keycloak token body."""

    status_code: int = 200

    def json(self) -> Dict[str, Any]:
        """Return a canned token-endpoint body carrying the access/refresh tokens.

        Returns:
            Dict[str, Any]:
                A Keycloak-shaped token response.
        """
        return {
            "access_token": ACCESS_TOKEN,
            "refresh_token": "off-1",
            "expires_in": 300,
            "token_type": "Bearer",
        }

    @property
    def text(self) -> str:
        """Return a placeholder raw body used only in error messages.

        Returns:
            str:
                A constant body representation.
        """
        return "ok"


def _legacy_config() -> ClientConfig:
    """Build a non-Keycloak (legacy) config that reports ``use_keycloak is False``.

    Returns:
        ClientConfig:
            A host/port-only config with no Keycloak fields.
    """
    return ClientConfig(host=GRPC_HOST, port=GRPC_PORT, grpc_cert=None)


def _keycloak_config() -> ClientConfig:
    """Build a fully-specified Keycloak (D18) config that reports ``use_keycloak is True``.

    Returns:
        ClientConfig:
            A config carrying the ROPC offline-token credentials.
    """
    return ClientConfig(
        host=GRPC_HOST,
        port=GRPC_PORT,
        grpc_cert=None,
        keycloak_url=KEYCLOAK_URL,
        realm=REALM,
        client_id=CLIENT_ID,
        username=USERNAME,
        password=PASSWORD,
    )


class TestSyncServicesInterface:
    """The sync ``ServicesInterface`` metadata wiring, exercised through the generated wrapper."""

    def test_wrapper_subclasses_the_interface(self) -> None:
        """The generated ``Text2Speech`` wrapper inherits the Keycloak-aware interface."""
        service: Text2Speech = Text2Speech(config=_legacy_config(), use_secure_channel=False)
        try:
            assert isinstance(service, ServicesInterface)
        finally:
            service.grpc_channel.close()

    def test_no_keycloak_yields_empty_metadata(self) -> None:
        """Without Keycloak configured, no provider is built and the metadata is empty."""
        service: Text2Speech = Text2Speech(config=_legacy_config(), use_secure_channel=False)
        try:
            assert service._keycloak_provider is None
            assert service.metadata == []
        finally:
            service.grpc_channel.close()

    def test_keycloak_yields_bearer_metadata(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With Keycloak configured, the provider supplies the ``Authorization: Bearer`` metadata.

        Args:
            monkeypatch (pytest.MonkeyPatch):
                Fixture used to replace ``requests.post`` so the ROPC login hits no network.
        """
        monkeypatch.setattr(keycloak_module.requests, "post", lambda url, data, timeout: _FakeResponse())

        service: Text2Speech = Text2Speech(config=_keycloak_config(), use_secure_channel=False)
        try:
            assert service._keycloak_provider is not None
            assert service.metadata == EXPECTED_BEARER_METADATA
        finally:
            provider = service._keycloak_provider
            if provider is not None:
                provider.stop()
            service.grpc_channel.close()


class TestAsyncServicesInterface:
    """The async ``AsyncServicesInterface`` metadata wiring, via the generated async wrapper."""

    def test_wrapper_subclasses_the_interface(self) -> None:
        """The generated async ``Text2Speech`` wrapper inherits the async Keycloak-aware interface."""
        async def _body() -> None:
            service: AsyncText2Speech = AsyncText2Speech(config=_legacy_config(), use_secure_channel=False)
            try:
                assert isinstance(service, AsyncServicesInterface)
            finally:
                await service.grpc_channel.close(grace=None)

        asyncio.run(_body())

    def test_no_keycloak_yields_empty_metadata(self) -> None:
        """Without Keycloak configured, no provider is built and the metadata is empty."""
        async def _body() -> None:
            service: AsyncText2Speech = AsyncText2Speech(config=_legacy_config(), use_secure_channel=False)
            try:
                assert service._keycloak_provider is None
                assert service.metadata == []
            finally:
                await service.grpc_channel.close(grace=None)

        asyncio.run(_body())

    def test_keycloak_yields_bearer_metadata(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With Keycloak configured, the async provider supplies the bearer metadata.

        Args:
            monkeypatch (pytest.MonkeyPatch):
                Fixture used to replace ``requests.post`` so the ROPC login hits no network.
        """
        monkeypatch.setattr(keycloak_module.requests, "post", lambda url, data, timeout: _FakeResponse())

        async def _body() -> None:
            service: AsyncText2Speech = AsyncText2Speech(config=_keycloak_config(), use_secure_channel=False)
            try:
                assert service._keycloak_provider is not None
                assert service.metadata == EXPECTED_BEARER_METADATA
            finally:
                provider = service._keycloak_provider
                if provider is not None:
                    provider.stop()
                await service.grpc_channel.close(grace=None)

        asyncio.run(_body())
