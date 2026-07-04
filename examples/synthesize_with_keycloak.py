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
"""
Minimal end-to-end example: authenticate against Keycloak, then synthesize speech.

This mirrors the current ONDEWO CCAI auth model (D18): the SDK performs a headless
Resource-Owner-Password-Credentials (ROPC) login with ``scope=offline_access`` against the
*public* Keycloak client and auto-refreshes a short-lived access token, which is attached to
each gRPC call as ``Authorization: Bearer`` metadata. There is no ``cai-token`` / HTTP-Basic
credential anymore.

The high-level ``Client`` owns the gRPC channel and stub; the ``KeycloakTokenProvider`` owns
the bearer token. The generated service wrappers now forward this metadata automatically when
the client is built from a Keycloak config, but this example issues requests directly through
the stub with ``metadata=provider.bearer_metadata()`` to show the explicit low-level transport.

Run it against a real server by exporting the ``ONDEWO_*`` environment variables below, then::

    python examples/synthesize_with_keycloak.py
"""
import os
from typing import (
    List,
    Optional,
    Tuple,
)

from ondewo.t2s.client.client import Client
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.services.text_to_speech import Text2Speech
from ondewo.t2s.client.utils.keycloak import (
    KeycloakTokenProvider,
    get_keycloak_token_provider,
)
from ondewo.t2s.text_to_speech_pb2 import (
    ListT2sPipelinesRequest,
    ListT2sPipelinesResponse,
    RequestConfig,
    SynthesizeRequest,
    SynthesizeResponse,
)

# gRPC metadata is a flat sequence of (key, value) string tuples.
Metadata = List[Tuple[str, str]]


def build_keycloak_config(
    host: str,
    port: str,
    keycloak_url: str,
    realm: str,
    client_id: str,
    username: str,
    password: str,
    grpc_cert: Optional[str] = None,
    token_expiration_in_s: Optional[int] = None,
) -> ClientConfig:
    """Build a ``ClientConfig`` wired for the D18 Keycloak offline-token flow.

    Args:
        host (str):
            Hostname/IP of the ONDEWO T2S gRPC server.
        port (str):
            Port of the ONDEWO T2S gRPC server.
        keycloak_url (str):
            Base URL of the Keycloak server (the part before ``/realms/<realm>``).
        realm (str):
            Keycloak realm name.
        client_id (str):
            Public SDK client id used for the ROPC grant (no client secret is sent).
        username (str):
            Technical-user email/username for the ROPC grant.
        password (str):
            Technical-user password for the ROPC grant.
        grpc_cert (Optional[str]):
            PEM certificate for a secure channel; ``None`` uses an insecure channel.
        token_expiration_in_s (Optional[int]):
            Optional upper bound (seconds since login) on how long auto-refresh runs.

    Returns:
        ClientConfig:
            A validated config reporting ``use_keycloak is True``.
    """
    return ClientConfig(
        host=host,
        port=port,
        grpc_cert=grpc_cert,
        keycloak_url=keycloak_url,
        realm=realm,
        client_id=client_id,
        username=username,
        password=password,
        token_expiration_in_s=token_expiration_in_s,
    )


def build_synthesize_request(
    pipeline_id: str,
    text: str,
    length_scale: float = 1.0,
) -> SynthesizeRequest:
    """Build a ``SynthesizeRequest`` for the given pipeline and text.

    The pipeline id and modulation parameters live on the nested ``RequestConfig`` in the
    current API; ``SynthesizeRequest`` itself only carries ``text`` and ``config``.

    Args:
        pipeline_id (str):
            Id of the T2S pipeline that should synthesize the text.
        text (str):
            The text to convert to speech.
        length_scale (float):
            Time-stretch factor (``1.0`` is the natural speed; lower is faster).

    Returns:
        SynthesizeRequest:
            The request message ready to send to the ``Synthesize`` RPC.
    """
    return SynthesizeRequest(
        text=text,
        config=RequestConfig(t2s_pipeline_id=pipeline_id, length_scale=length_scale),
    )


def list_pipeline_ids(service: Text2Speech, metadata: Metadata) -> List[str]:
    """List the ids of every T2S pipeline available on the server.

    Args:
        service (Text2Speech):
            The T2S service exposing the gRPC stub bound to the client's channel.
        metadata (Metadata):
            Per-call gRPC metadata carrying the ``Authorization: Bearer`` token.

    Returns:
        List[str]:
            The pipeline ids returned by ``ListT2sPipelines``.
    """
    response: ListT2sPipelinesResponse = service.stub.ListT2sPipelines(
        ListT2sPipelinesRequest(),
        metadata=metadata,
    )
    return [pipeline.id for pipeline in response.pipelines]


def synthesize(
    service: Text2Speech,
    metadata: Metadata,
    pipeline_id: str,
    text: str,
    length_scale: float = 1.0,
) -> SynthesizeResponse:
    """Synthesize ``text`` on ``pipeline_id`` and return the response.

    Args:
        service (Text2Speech):
            The T2S service exposing the gRPC stub bound to the client's channel.
        metadata (Metadata):
            Per-call gRPC metadata carrying the ``Authorization: Bearer`` token.
        pipeline_id (str):
            Id of the T2S pipeline that should synthesize the text.
        text (str):
            The text to convert to speech.
        length_scale (float):
            Time-stretch factor (``1.0`` is the natural speed; lower is faster).

    Returns:
        SynthesizeResponse:
            The generated audio plus its metadata (length, generation time, uuid).
    """
    request: SynthesizeRequest = build_synthesize_request(
        pipeline_id=pipeline_id,
        text=text,
        length_scale=length_scale,
    )
    response: SynthesizeResponse = service.stub.Synthesize(request, metadata=metadata)
    return response


def run(client: Client, provider: KeycloakTokenProvider, text: str) -> SynthesizeResponse:
    """Drive one authenticated synthesis round-trip and report the result.

    Args:
        client (Client):
            A connected ONDEWO T2S client owning the gRPC channel/stub.
        provider (KeycloakTokenProvider):
            The shared token provider supplying the bearer metadata for each call.
        text (str):
            The text to synthesize on the first available pipeline.

    Returns:
        SynthesizeResponse:
            The synthesis result for ``text`` on the first available pipeline.

    Raises:
        RuntimeError:
            If the server reports no available T2S pipelines.
    """
    service: Text2Speech = client.services.text_to_speech
    metadata: Metadata = provider.bearer_metadata()

    pipeline_ids: List[str] = list_pipeline_ids(service=service, metadata=metadata)
    if not pipeline_ids:
        raise RuntimeError("No T2S pipelines are available on the server.")

    response: SynthesizeResponse = synthesize(
        service=service,
        metadata=metadata,
        pipeline_id=pipeline_ids[0],
        text=text,
    )
    print(
        f"Synthesized {response.audio_length:.2f}s of audio "
        f"({len(response.audio)} bytes) in {response.generation_time:.2f}s "
        f"[uuid={response.audio_uuid}]."
    )
    return response


def main() -> None:
    """Authenticate against Keycloak and synthesize a short greeting on the first pipeline."""
    config: ClientConfig = build_keycloak_config(
        host=os.getenv("ONDEWO_T2S_HOST", "localhost"),
        port=os.getenv("ONDEWO_T2S_PORT", "50555"),
        keycloak_url=os.getenv("ONDEWO_KEYCLOAK_URL", "https://keycloak.example.com/auth"),
        realm=os.getenv("ONDEWO_KEYCLOAK_REALM", "ondewo-ccai-platform"),
        client_id=os.getenv("ONDEWO_KEYCLOAK_CLIENT_ID", "ondewo-nlu-cai-sdk-public"),
        username=os.getenv("ONDEWO_KEYCLOAK_USERNAME", "technical-user@ondewo.com"),
        password=os.getenv("ONDEWO_KEYCLOAK_PASSWORD", ""),
        grpc_cert=os.getenv("ONDEWO_T2S_GRPC_CERT") or None,
    )

    # One shared provider performs the ROPC offline-token login once and auto-refreshes it.
    provider: KeycloakTokenProvider = get_keycloak_token_provider(config)
    client: Client = Client(config=config, use_secure_channel=bool(config.grpc_cert))
    try:
        run(client=client, provider=provider, text="Hello, this is ONDEWO Text-to-Speech.")
    finally:
        provider.stop()
        client.disconnect()


if __name__ == "__main__":
    main()
