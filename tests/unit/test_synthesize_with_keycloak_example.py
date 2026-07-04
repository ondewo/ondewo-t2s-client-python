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
"""Hermetic mock tests for the ``examples/synthesize_with_keycloak.py`` example.

No live server and no network are touched: the gRPC stub and the Keycloak token provider are
replaced with ``unittest.mock`` fakes, so the tests assert that the example builds the right
protobuf requests, forwards the bearer metadata on every call, and handles the response.
"""
from typing import (
    List,
    Tuple,
    cast,
)
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest

from examples.synthesize_with_keycloak import (
    build_keycloak_config,
    build_synthesize_request,
    list_pipeline_ids,
    main,
    run,
    synthesize,
)
from ondewo.t2s.client.client import Client
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.services.text_to_speech import Text2Speech
from ondewo.t2s.client.utils.keycloak import KeycloakTokenProvider
from ondewo.t2s.text_to_speech_pb2 import (
    ListT2sPipelinesRequest,
    ListT2sPipelinesResponse,
    SynthesizeRequest,
    SynthesizeResponse,
    Text2SpeechConfig,
)

# Bound exactly once so a refactor that changes only an input or an expectation cannot silently
# make a test tautological.
KEYCLOAK_URL: str = "https://kc.example.com/auth"
REALM: str = "ondewo-ccai-platform"
CLIENT_ID: str = "ondewo-nlu-cai-sdk-public"
USERNAME: str = "tech-user@example.com"
PASSWORD: str = "s3cr3t"
PIPELINE_ID: str = "pipeline-en-1"
TEXT: str = "Hello, this is ONDEWO Text-to-Speech."
BEARER_METADATA: List[Tuple[str, str]] = [("authorization", "Bearer acc-1")]


def _pipelines_response(*pipeline_ids: str) -> ListT2sPipelinesResponse:
    """Build a ``ListT2sPipelinesResponse`` carrying the given pipeline ids.

    Args:
        pipeline_ids (str):
            The ids to expose as available pipelines.

    Returns:
        ListT2sPipelinesResponse:
            A response whose ``pipelines`` carry exactly ``pipeline_ids``.
    """
    return ListT2sPipelinesResponse(
        pipelines=[Text2SpeechConfig(id=pipeline_id) for pipeline_id in pipeline_ids],
    )


def _synthesize_response() -> SynthesizeResponse:
    """Build a representative ``SynthesizeResponse``.

    Returns:
        SynthesizeResponse:
            A response carrying non-empty audio plus its length/generation-time metadata.
    """
    return SynthesizeResponse(
        audio=b"RIFF\x00\x00\x00\x00WAVE",
        audio_length=1.5,
        generation_time=0.25,
        audio_uuid="uuid-1",
    )


def _service_mock(
    pipelines: ListT2sPipelinesResponse,
    synthesis: SynthesizeResponse,
) -> MagicMock:
    """Build a ``Text2Speech`` stand-in whose stub returns canned responses.

    Args:
        pipelines (ListT2sPipelinesResponse):
            The response returned by ``stub.ListT2sPipelines``.
        synthesis (SynthesizeResponse):
            The response returned by ``stub.Synthesize``.

    Returns:
        MagicMock:
            A mock service with a ``stub`` exposing ``ListT2sPipelines`` / ``Synthesize``.
    """
    service: MagicMock = MagicMock()
    service.stub.ListT2sPipelines.return_value = pipelines
    service.stub.Synthesize.return_value = synthesis
    return service


class TestBuildKeycloakConfig:
    """The ``build_keycloak_config`` helper produces a valid D18 Keycloak config."""

    def test_reports_use_keycloak_and_resolves_username(self) -> None:
        """A fully specified config reports ``use_keycloak`` and resolves the username."""
        config: ClientConfig = build_keycloak_config(
            host="localhost",
            port="50555",
            keycloak_url=KEYCLOAK_URL,
            realm=REALM,
            client_id=CLIENT_ID,
            username=USERNAME,
            password=PASSWORD,
        )

        assert config.use_keycloak is True
        assert config.resolved_username == USERNAME
        # No certificate supplied -> an insecure channel is expected downstream.
        assert config.grpc_cert is None

    def test_partial_keycloak_config_raises(self) -> None:
        """Omitting a mandatory Keycloak credential fails config validation."""
        with pytest.raises(ValueError, match="password"):
            build_keycloak_config(
                host="localhost",
                port="50555",
                keycloak_url=KEYCLOAK_URL,
                realm=REALM,
                client_id=CLIENT_ID,
                username=USERNAME,
                password="",
            )


class TestBuildSynthesizeRequest:
    """The ``build_synthesize_request`` helper maps its args onto the current proto shape."""

    def test_pipeline_id_and_length_scale_live_on_nested_config(self) -> None:
        """The pipeline id and length scale are set on the nested ``RequestConfig``."""
        length_scale: float = 0.7
        request: SynthesizeRequest = build_synthesize_request(
            pipeline_id=PIPELINE_ID,
            text=TEXT,
            length_scale=length_scale,
        )

        assert request.text == TEXT
        assert request.config.t2s_pipeline_id == PIPELINE_ID
        assert request.config.length_scale == pytest.approx(length_scale)

    def test_length_scale_defaults_to_natural_speed(self) -> None:
        """Omitting ``length_scale`` yields the natural-speed default of ``1.0``."""
        request: SynthesizeRequest = build_synthesize_request(pipeline_id=PIPELINE_ID, text=TEXT)

        assert request.config.length_scale == pytest.approx(1.0)


class TestListPipelineIds:
    """``list_pipeline_ids`` forwards the bearer metadata and extracts the ids."""

    def test_calls_stub_with_metadata_and_returns_ids(self) -> None:
        """The stub is called with an empty list request + metadata; ids are returned."""
        service: MagicMock = _service_mock(
            pipelines=_pipelines_response(PIPELINE_ID, "pipeline-de-1"),
            synthesis=_synthesize_response(),
        )

        ids: List[str] = list_pipeline_ids(
            service=cast(Text2Speech, service),
            metadata=BEARER_METADATA,
        )

        assert ids == [PIPELINE_ID, "pipeline-de-1"]
        service.stub.ListT2sPipelines.assert_called_once()
        call = service.stub.ListT2sPipelines.call_args
        assert isinstance(call.args[0], ListT2sPipelinesRequest)
        assert call.kwargs["metadata"] == BEARER_METADATA


class TestSynthesize:
    """``synthesize`` builds the right request, forwards metadata, and returns the response."""

    def test_sends_expected_request_with_metadata(self) -> None:
        """The Synthesize stub receives the built request + metadata and its response is returned."""
        expected_response: SynthesizeResponse = _synthesize_response()
        service: MagicMock = _service_mock(
            pipelines=_pipelines_response(PIPELINE_ID),
            synthesis=expected_response,
        )

        response: SynthesizeResponse = synthesize(
            service=cast(Text2Speech, service),
            metadata=BEARER_METADATA,
            pipeline_id=PIPELINE_ID,
            text=TEXT,
            length_scale=0.5,
        )

        assert response is expected_response
        service.stub.Synthesize.assert_called_once()
        call = service.stub.Synthesize.call_args
        sent_request = call.args[0]
        assert isinstance(sent_request, SynthesizeRequest)
        assert sent_request.text == TEXT
        assert sent_request.config.t2s_pipeline_id == PIPELINE_ID
        assert sent_request.config.length_scale == pytest.approx(0.5)
        assert call.kwargs["metadata"] == BEARER_METADATA


class TestRun:
    """``run`` drives one authenticated round-trip end to end against mocks."""

    def test_returns_synthesis_for_first_pipeline(self) -> None:
        """It reads the bearer metadata, synthesizes on the first pipeline, and returns the response."""
        expected_response: SynthesizeResponse = _synthesize_response()
        service: MagicMock = _service_mock(
            pipelines=_pipelines_response(PIPELINE_ID, "pipeline-de-1"),
            synthesis=expected_response,
        )
        client: MagicMock = MagicMock()
        client.services.text_to_speech = service
        provider: MagicMock = MagicMock()
        provider.bearer_metadata.return_value = BEARER_METADATA

        response: SynthesizeResponse = run(
            client=cast(Client, client),
            provider=cast(KeycloakTokenProvider, provider),
            text=TEXT,
        )

        assert response is expected_response
        provider.bearer_metadata.assert_called_once()
        # The first listed pipeline is the one that synthesizes.
        sent_request = service.stub.Synthesize.call_args.args[0]
        assert sent_request.config.t2s_pipeline_id == PIPELINE_ID
        assert service.stub.Synthesize.call_args.kwargs["metadata"] == BEARER_METADATA

    def test_raises_when_no_pipelines_available(self) -> None:
        """With no pipelines on the server, ``run`` raises ``RuntimeError`` and never synthesizes."""
        service: MagicMock = _service_mock(
            pipelines=_pipelines_response(),
            synthesis=_synthesize_response(),
        )
        client: MagicMock = MagicMock()
        client.services.text_to_speech = service
        provider: MagicMock = MagicMock()
        provider.bearer_metadata.return_value = BEARER_METADATA

        with pytest.raises(RuntimeError, match="No T2S pipelines"):
            run(
                client=cast(Client, client),
                provider=cast(KeycloakTokenProvider, provider),
                text=TEXT,
            )

        service.stub.Synthesize.assert_not_called()


class TestMain:
    """``main`` wires the real Client + token-provider factory and runs without a live server."""

    def test_wires_provider_and_client_and_tears_down(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """It builds a Keycloak client, synthesizes with bearer metadata, then tears down.

        Args:
            monkeypatch (pytest.MonkeyPatch):
                Fixture used to supply the Keycloak password via the environment.
        """
        # build_keycloak_config requires a non-empty password for the Keycloak flow.
        monkeypatch.setenv("ONDEWO_KEYCLOAK_PASSWORD", PASSWORD)

        service: MagicMock = _service_mock(
            pipelines=_pipelines_response(PIPELINE_ID),
            synthesis=_synthesize_response(),
        )
        client: MagicMock = MagicMock()
        client.services.text_to_speech = service
        provider: MagicMock = MagicMock()
        provider.bearer_metadata.return_value = BEARER_METADATA

        with patch(
            "examples.synthesize_with_keycloak.Client",
            return_value=client,
        ) as client_cls, patch(
            "examples.synthesize_with_keycloak.get_keycloak_token_provider",
            return_value=provider,
        ) as get_provider:
            main()

        # The factory + client were constructed from the same validated config.
        get_provider.assert_called_once()
        config_arg = get_provider.call_args.args[0]
        assert isinstance(config_arg, ClientConfig)
        assert config_arg.use_keycloak is True
        client_cls.assert_called_once()

        # A single authenticated Synthesize round-trip happened.
        service.stub.Synthesize.assert_called_once()
        assert service.stub.Synthesize.call_args.kwargs["metadata"] == BEARER_METADATA

        # Deterministic teardown of both the provider thread and the gRPC channel.
        provider.stop.assert_called_once()
        client.disconnect.assert_called_once()
