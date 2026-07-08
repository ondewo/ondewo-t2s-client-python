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
from typing import (
    Any,
    Iterator,
)

import grpc
import pytest

from ondewo.t2s.client.client import Client
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.services.text_to_speech import Text2Speech
from ondewo.t2s.client.services_container import ServicesContainer

GRPC_HOST: str = "localhost"
GRPC_PORT: str = "50555"


@pytest.fixture
def config() -> ClientConfig:
    return ClientConfig(host=GRPC_HOST, port=GRPC_PORT, grpc_cert=None)


@pytest.fixture
def client(config: ClientConfig) -> Iterator[Client]:
    instance: Client = Client(config=config, use_secure_channel=False)
    yield instance
    if instance.services is not None:
        instance.disconnect()


def test_client_initializes_services_container(client: Client) -> None:
    assert client.services is not None
    assert isinstance(client.services, ServicesContainer)


def test_client_exposes_text_to_speech_service(client: Client) -> None:
    assert isinstance(client.services.text_to_speech, Text2Speech)


def test_client_text_to_speech_has_grpc_channel(client: Client) -> None:
    channel: Any = client.services.text_to_speech.grpc_channel
    assert isinstance(channel, grpc.Channel)


def test_client_rejects_non_base_client_config() -> None:
    class NotAConfig:
        host = GRPC_HOST
        port = GRPC_PORT

    with pytest.raises(ValueError, match="BaseClientConfig"):
        Client(config=NotAConfig(), use_secure_channel=False)  # type: ignore[arg-type]


def test_client_secure_channel_without_cert_raises(config: ClientConfig) -> None:
    with pytest.raises(ValueError, match="grpc certificate"):
        Client(config=config, use_secure_channel=True)


def test_client_accepts_custom_grpc_options(config: ClientConfig) -> None:
    options = {
        ("grpc.max_send_message_length", 1024 * 1024),
        ("grpc.max_receive_message_length", 1024 * 1024),
    }
    instance: Client = Client(config=config, use_secure_channel=False, options=options)
    try:
        assert instance.services is not None
    finally:
        instance.disconnect()


def test_client_disconnect_clears_services(client: Client) -> None:
    client.disconnect()
    assert client.services is None


def test_client_disconnect_without_services_raises(client: Client) -> None:
    client.disconnect()
    with pytest.raises(AttributeError):
        client.disconnect()


def test_client_connect_when_already_connected_raises(
    client: Client,
    config: ClientConfig,
) -> None:
    with pytest.raises(ConnectionError):
        client.connect(config=config, use_secure_channel=False)


def test_client_can_reconnect_after_disconnect(
    client: Client,
    config: ClientConfig,
) -> None:
    client.disconnect()
    client.connect(config=config, use_secure_channel=False)
    assert client.services is not None
    assert isinstance(client.services.text_to_speech, Text2Speech)


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
def test_client_text_to_speech_exposes_method(client: Client, method_name: str) -> None:
    assert callable(getattr(client.services.text_to_speech, method_name))
