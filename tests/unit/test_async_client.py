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
import asyncio
from typing import (
    Any,
    Callable,
    Coroutine,
    TypeVar,
)

import grpc
import pytest

from ondewo.t2s.client.async_client import AsyncClient
from ondewo.t2s.client.async_services_container import AsyncServicesContainer
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.services.async_text_to_speech import Text2Speech as AsyncText2Speech

GRPC_HOST: str = "localhost"
GRPC_PORT: str = "50555"

T = TypeVar("T")


def _run(coro_factory: Callable[[], Coroutine[Any, Any, T]]) -> T:
    return asyncio.run(coro_factory())


@pytest.fixture
def config() -> ClientConfig:
    return ClientConfig(host=GRPC_HOST, port=GRPC_PORT, grpc_cert=None)


def test_async_client_initializes_services_container(config: ClientConfig) -> None:
    async def _body() -> None:
        client: AsyncClient = AsyncClient(config=config, use_secure_channel=False)
        try:
            assert client.services is not None
            assert isinstance(client.services, AsyncServicesContainer)
        finally:
            await client.disconnect()

    _run(_body)


def test_async_client_exposes_text_to_speech_service(config: ClientConfig) -> None:
    async def _body() -> None:
        client: AsyncClient = AsyncClient(config=config, use_secure_channel=False)
        try:
            assert isinstance(client.services.text_to_speech, AsyncText2Speech)
        finally:
            await client.disconnect()

    _run(_body)


def test_async_client_text_to_speech_has_aio_grpc_channel(config: ClientConfig) -> None:
    async def _body() -> None:
        client: AsyncClient = AsyncClient(config=config, use_secure_channel=False)
        try:
            assert isinstance(
                client.services.text_to_speech.grpc_channel, grpc.aio.Channel,
            )
        finally:
            await client.disconnect()

    _run(_body)


def test_async_client_rejects_non_base_client_config() -> None:
    class NotAConfig:
        host = GRPC_HOST
        port = GRPC_PORT

    with pytest.raises(ValueError, match="BaseClientConfig"):
        AsyncClient(config=NotAConfig(), use_secure_channel=False)  # type: ignore[arg-type]


def test_async_client_secure_channel_without_cert_raises(config: ClientConfig) -> None:
    with pytest.raises(ValueError, match="grpc certificate"):
        AsyncClient(config=config, use_secure_channel=True)


def test_async_client_accepts_custom_grpc_options(config: ClientConfig) -> None:
    options = {
        ("grpc.max_send_message_length", 1024 * 1024),
        ("grpc.max_receive_message_length", 1024 * 1024),
    }

    async def _body() -> None:
        client: AsyncClient = AsyncClient(
            config=config, use_secure_channel=False, options=options,
        )
        try:
            assert client.services is not None
        finally:
            await client.disconnect()

    _run(_body)


def test_async_client_disconnect_clears_services(config: ClientConfig) -> None:
    async def _body() -> None:
        client: AsyncClient = AsyncClient(config=config, use_secure_channel=False)
        await client.disconnect()
        assert client.services is None

    _run(_body)


def test_async_client_disconnect_without_services_raises(config: ClientConfig) -> None:
    async def _body() -> None:
        client: AsyncClient = AsyncClient(config=config, use_secure_channel=False)
        await client.disconnect()
        with pytest.raises(AttributeError):
            await client.disconnect()

    _run(_body)


def test_async_client_connect_when_already_connected_raises(
    config: ClientConfig,
) -> None:
    async def _body() -> None:
        client: AsyncClient = AsyncClient(config=config, use_secure_channel=False)
        try:
            with pytest.raises(ConnectionError):
                await client.connect(config=config, use_secure_channel=False)
        finally:
            await client.disconnect()

    _run(_body)


def test_async_client_can_reconnect_after_disconnect(config: ClientConfig) -> None:
    async def _body() -> None:
        client: AsyncClient = AsyncClient(config=config, use_secure_channel=False)
        await client.disconnect()
        await client.connect(config=config, use_secure_channel=False)
        try:
            assert client.services is not None
            assert isinstance(client.services.text_to_speech, AsyncText2Speech)
        finally:
            await client.disconnect()

    _run(_body)


@pytest.mark.parametrize(
    "method_name",
    [
        "synthesize",
        "batch_synthesize",
        "streaming_synthesize",
        "normalize_text",
        "get_t2s_pipeline",
        "create_t2s_pipeline",
        "delete_t2s_pipeline",
        "update_t2s_pipeline",
        "list_t2s_pipelines",
        "list_t2s_languages",
        "list_t2s_domains",
        "list_t2s_normalization_pipelines",
        "get_service_info",
        "get_custom_phonemizer",
        "create_custom_phonemizer",
        "delete_custom_phonemizer",
        "update_custom_phonemizer",
        "list_custom_phonemizer",
    ],
)
def test_async_client_text_to_speech_exposes_coroutine_method(
    config: ClientConfig, method_name: str,
) -> None:
    async def _body() -> None:
        client: AsyncClient = AsyncClient(config=config, use_secure_channel=False)
        try:
            method = getattr(client.services.text_to_speech, method_name)
            assert callable(method)
            assert asyncio.iscoroutinefunction(method)
        finally:
            await client.disconnect()

    _run(_body)
