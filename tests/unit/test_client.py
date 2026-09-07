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
    List,
    Set,
    Tuple,
    Type,
)
from unittest.mock import MagicMock, patch

import grpc
import pytest
from google.protobuf.empty_pb2 import Empty
from google.protobuf.message import Message

from ondewo.t2s.client.client import Client
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.services.text_to_speech import Text2Speech
from ondewo.t2s.client.services_container import ServicesContainer
from ondewo.t2s.text_to_speech_pb2 import (
    BatchSynthesizeRequest,
    BatchSynthesizeResponse,
    CreateCustomPhonemizerRequest,
    CustomPhonemizerProto,
    ListCustomPhonemizerRequest,
    ListCustomPhonemizerResponse,
    ListT2sDomainsRequest,
    ListT2sDomainsResponse,
    ListT2sLanguagesRequest,
    ListT2sLanguagesResponse,
    ListT2sNormalizationPipelinesRequest,
    ListT2sNormalizationPipelinesResponse,
    ListT2sPipelinesRequest,
    ListT2sPipelinesResponse,
    NormalizeTextRequest,
    NormalizeTextResponse,
    PhonemizerId,
    StreamingSynthesizeRequest,
    StreamingSynthesizeResponse,
    SynthesizeRequest,
    SynthesizeResponse,
    T2SGetServiceInfoResponse,
    T2sPipelineId,
    Text2SpeechConfig,
    UpdateCustomPhonemizerRequest,
    VoiceCloningRequest,
)

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


# --------------------------------------------------------------------------- #
# Text2Speech service — stub delegation
#
# Every wrapper method in ondewo/t2s/client/services/text_to_speech.py is a one-line
# forward to a gRPC stub RPC. The risk they carry is not logic but wiring: a wrong RPC
# name, a dropped `metadata=` (which is what attaches the Keycloak bearer token) or a
# swallowed return value. Each case below drives one method through a patched
# Text2SpeechStub and asserts exactly that wiring.
# --------------------------------------------------------------------------- #

#: ``(wrapper method, stub RPC attribute, request type, response type)`` for every RPC
#: declared by the Text2Speech service in text-to-speech.proto.
RPC_CASES: List[Tuple[str, str, Type[Message], Type[Message]]] = [
    ("synthesize", "Synthesize", SynthesizeRequest, SynthesizeResponse),
    ("batch_synthesize", "BatchSynthesize", BatchSynthesizeRequest, BatchSynthesizeResponse),
    ("streaming_synthesize", "StreamingSynthesize", StreamingSynthesizeRequest, StreamingSynthesizeResponse),
    ("normalize_text", "NormalizeText", NormalizeTextRequest, NormalizeTextResponse),
    ("get_t2s_pipeline", "GetT2sPipeline", T2sPipelineId, Text2SpeechConfig),
    ("create_t2s_pipeline", "CreateT2sPipeline", Text2SpeechConfig, T2sPipelineId),
    ("delete_t2s_pipeline", "DeleteT2sPipeline", T2sPipelineId, Empty),
    ("update_t2s_pipeline", "UpdateT2sPipeline", Text2SpeechConfig, Empty),
    ("list_t2s_pipelines", "ListT2sPipelines", ListT2sPipelinesRequest, ListT2sPipelinesResponse),
    ("list_t2s_languages", "ListT2sLanguages", ListT2sLanguagesRequest, ListT2sLanguagesResponse),
    ("list_t2s_domains", "ListT2sDomains", ListT2sDomainsRequest, ListT2sDomainsResponse),
    (
        "list_t2s_normalization_pipelines",
        "ListT2sNormalizationPipelines",
        ListT2sNormalizationPipelinesRequest,
        ListT2sNormalizationPipelinesResponse,
    ),
    ("get_service_info", "GetServiceInfo", Empty, T2SGetServiceInfoResponse),
    ("get_custom_phonemizer", "GetCustomPhonemizer", PhonemizerId, CustomPhonemizerProto),
    ("create_custom_phonemizer", "CreateCustomPhonemizer", CreateCustomPhonemizerRequest, PhonemizerId),
    ("delete_custom_phonemizer", "DeleteCustomPhonemizer", PhonemizerId, Empty),
    ("update_custom_phonemizer", "UpdateCustomPhonemizer", UpdateCustomPhonemizerRequest, CustomPhonemizerProto),
    ("list_custom_phonemizer", "ListCustomPhonemizer", ListCustomPhonemizerRequest, ListCustomPhonemizerResponse),
    ("voice_cloning", "VoiceCloning", VoiceCloningRequest, Empty),
]

STUB_PATH: str = "ondewo.t2s.client.services.text_to_speech.Text2SpeechStub"


@pytest.fixture
def mock_stub() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(config: ClientConfig, mock_stub: MagicMock) -> Iterator[Text2Speech]:
    # `Text2Speech.stub` is a non-cached property that builds a new Text2SpeechStub on every
    # call, so the patch has to stay active for the whole test body, not just construction.
    with patch(STUB_PATH, return_value=mock_stub):
        instance: Text2Speech = Text2Speech(config=config, use_secure_channel=False)
        yield instance
        instance.grpc_channel.close()


def test_rpc_cases_cover_every_public_service_method() -> None:
    # Guards the table below: a newly generated wrapper method must be added here, otherwise
    # it ships untested and the coverage gate is the only thing that would notice.
    declared: Set[str] = {name for name, _, _, _ in RPC_CASES}
    public: Set[str] = {
        name
        for name in vars(Text2Speech)
        if not name.startswith("_") and name != "stub" and callable(getattr(Text2Speech, name))
    }
    assert declared == public


@pytest.mark.parametrize("method_name, rpc_name, request_type, response_type", RPC_CASES)
def test_service_method_delegates_to_stub_rpc(
    service: Text2Speech,
    mock_stub: MagicMock,
    method_name: str,
    rpc_name: str,
    request_type: Type[Message],
    response_type: Type[Message],
) -> None:
    request: Any = request_type()
    expected: Any = response_type()
    if method_name == "streaming_synthesize":
        # The only client-streaming RPC: the wrapper takes (and returns) an iterator.
        request = iter([request])
        expected = iter([expected])
    getattr(mock_stub, rpc_name).return_value = expected

    assert getattr(service, method_name)(request) is expected
    getattr(mock_stub, rpc_name).assert_called_once_with(request, metadata=[])


def test_service_forwards_keycloak_bearer_metadata(
    mock_stub: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The `metadata=[]` above only proves metadata is forwarded, not that a configured token
    # reaches the stub. Drive one RPC with a provider in place to close that gap.
    bearer: List[Tuple[str, str]] = [("authorization", "Bearer tok-1")]
    with patch(STUB_PATH, return_value=mock_stub):
        service: Text2Speech = Text2Speech(
            config=ClientConfig(host=GRPC_HOST, port=GRPC_PORT, grpc_cert=None),
            use_secure_channel=False,
        )
        try:
            provider: MagicMock = MagicMock()
            provider.bearer_metadata.return_value = bearer
            monkeypatch.setattr(service, "_keycloak_provider", provider)
            service.synthesize(SynthesizeRequest())
        finally:
            service.grpc_channel.close()
    mock_stub.Synthesize.assert_called_once()
    assert mock_stub.Synthesize.call_args.kwargs["metadata"] == bearer
