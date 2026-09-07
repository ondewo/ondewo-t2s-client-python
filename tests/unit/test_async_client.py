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
    List,
    Set,
    Tuple,
    Type,
    TypeVar,
)
from unittest.mock import AsyncMock, MagicMock, patch

import grpc
import pytest
from google.protobuf.empty_pb2 import Empty
from google.protobuf.message import Message

from ondewo.t2s.client.async_client import AsyncClient
from ondewo.t2s.client.async_services_container import AsyncServicesContainer
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.services.async_text_to_speech import Text2Speech as AsyncText2Speech
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
                client.services.text_to_speech.grpc_channel,
                grpc.aio.Channel,
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
            config=config,
            use_secure_channel=False,
            options=options,
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
    config: ClientConfig,
    method_name: str,
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


# --------------------------------------------------------------------------- #
# Async Text2Speech service — stub delegation
#
# Same wiring risk as the synchronous wrappers (RPC name, `metadata=`, return value),
# plus one the sync side cannot have: `create_async_services` rewrites the generated
# file with perl, and a missed `await self.stub...` would return a coroutine instead of
# the response. Awaiting each method through an AsyncMock stub catches that.
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

STUB_PATH: str = "ondewo.t2s.client.services.async_text_to_speech.Text2SpeechStub"


def _async_stub() -> MagicMock:
    # Every wrapper does `await self.stub.<Rpc>(...)`; plain MagicMock attributes are not
    # awaitable, so each RPC attribute is replaced with an AsyncMock.
    stub: MagicMock = MagicMock()
    for _, rpc_name, _, _ in RPC_CASES:
        setattr(stub, rpc_name, AsyncMock())
    return stub


def test_async_rpc_cases_cover_every_public_service_method() -> None:
    # Guards the table above: a newly generated wrapper method must be added here, otherwise
    # it ships untested and the coverage gate is the only thing that would notice.
    declared: Set[str] = {name for name, _, _, _ in RPC_CASES}
    public: Set[str] = {
        name
        for name in vars(AsyncText2Speech)
        if not name.startswith("_") and name != "stub" and callable(getattr(AsyncText2Speech, name))
    }
    assert declared == public


@pytest.mark.parametrize("method_name, rpc_name, request_type, response_type", RPC_CASES)
def test_async_service_method_delegates_to_stub_rpc(
    config: ClientConfig,
    method_name: str,
    rpc_name: str,
    request_type: Type[Message],
    response_type: Type[Message],
) -> None:
    async def _body() -> None:
        stub: MagicMock = _async_stub()
        request: Any = request_type()
        expected: Any = response_type()
        if method_name == "streaming_synthesize":
            # The only client-streaming RPC: the wrapper takes (and returns) an iterator.
            request = iter([request])
            expected = iter([expected])
        getattr(stub, rpc_name).return_value = expected

        # `stub` is a non-cached property that builds a new Text2SpeechStub on every call, so
        # the patch has to stay active for the whole call, not just construction.
        with patch(STUB_PATH, return_value=stub):
            service: AsyncText2Speech = AsyncText2Speech(config=config, use_secure_channel=False)
            try:
                assert await getattr(service, method_name)(request) is expected
            finally:
                await service.grpc_channel.close(grace=None)
        getattr(stub, rpc_name).assert_awaited_once_with(request, metadata=[])

    _run(_body)


def test_async_service_forwards_keycloak_bearer_metadata(
    config: ClientConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The `metadata=[]` above only proves metadata is forwarded, not that a configured token
    # reaches the stub. Drive one RPC with a provider in place to close that gap.
    bearer: List[Tuple[str, str]] = [("authorization", "Bearer tok-1")]

    async def _body() -> None:
        stub: MagicMock = _async_stub()
        with patch(STUB_PATH, return_value=stub):
            service: AsyncText2Speech = AsyncText2Speech(config=config, use_secure_channel=False)
            try:
                provider: MagicMock = MagicMock()
                provider.bearer_metadata.return_value = bearer
                monkeypatch.setattr(service, "_keycloak_provider", provider)
                await service.synthesize(SynthesizeRequest())
            finally:
                await service.grpc_channel.close(grace=None)
        assert stub.Synthesize.await_args.kwargs["metadata"] == bearer

    _run(_body)
