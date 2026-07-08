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
each gRPC call as ``Authorization: Bearer`` metadata. The bearer JWT is the only credential.

The high-level ``Client`` owns the gRPC channel and stub; the ``KeycloakTokenProvider`` owns
the bearer token. The generated service wrappers now forward this metadata automatically when
the client is built from a Keycloak config, but this example issues requests directly through
the stub with ``metadata=provider.bearer_metadata()`` to show the explicit low-level transport.

Configure it by filling in ``examples/environment.env`` (loaded automatically), then::

    python examples/synthesize_with_keycloak.py
"""

import os
import sys
from pathlib import Path
from typing import (
    List,
    Optional,
    Tuple,
)

import grpc
from dotenv import load_dotenv
from loguru import logger as log

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

# Load the example configuration (connection + Keycloak credentials) from environment.env sitting
# next to this script, so the example works regardless of the current working directory.
load_dotenv(Path(__file__).with_name("environment.env"))

# gRPC metadata is a flat sequence of (key, value) string tuples.
Metadata = List[Tuple[str, str]]


def _env(name: str, default: str = "") -> str:
    """Read an environment variable, treating a blank value as unset.

    Args:
        name (str):
            The environment variable name.
        default (str):
            The value to fall back to when the variable is unset or blank.

    Returns:
        str:
            The variable's value, or ``default`` when it is unset/blank.
    """
    return os.getenv(name) or default


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
    keycloak_verify_ssl: bool = True,
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
        keycloak_verify_ssl (bool):
            Whether to verify the Keycloak server's TLS certificate on the token-endpoint call.

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
        keycloak_verify_ssl=keycloak_verify_ssl,
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

    Raises:
        grpc.RpcError:
            If the ``ListT2sPipelines`` RPC fails.
    """
    log.info("START: list_pipeline_ids")
    try:
        response: ListT2sPipelinesResponse = service.stub.ListT2sPipelines(
            ListT2sPipelinesRequest(),
            metadata=metadata,
        )
    except grpc.RpcError as rpc_error:
        log.error(f"ListT2sPipelines RPC failed: code={rpc_error.code()} details={rpc_error.details()}")
        raise
    pipeline_ids: List[str] = [pipeline.id for pipeline in response.pipelines]
    log.info(f"DONE: list_pipeline_ids: found {len(pipeline_ids)} pipeline(s)")
    return pipeline_ids


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

    Raises:
        grpc.RpcError:
            If the ``Synthesize`` RPC fails.
    """
    log.info(f"START: synthesize: pipeline_id={pipeline_id} length_scale={length_scale}")
    request: SynthesizeRequest = build_synthesize_request(
        pipeline_id=pipeline_id,
        text=text,
        length_scale=length_scale,
    )
    try:
        response: SynthesizeResponse = service.stub.Synthesize(request, metadata=metadata)
    except grpc.RpcError as rpc_error:
        log.error(
            f"Synthesize RPC failed for pipeline {pipeline_id}: code={rpc_error.code()} details={rpc_error.details()}"
        )
        raise
    log.info("DONE: synthesize")
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
    log.info(
        f"Synthesized {response.audio_length:.2f}s of audio "
        f"({len(response.audio)} bytes) in {response.generation_time:.2f}s "
        f"[uuid={response.audio_uuid}]."
    )
    return response


def main() -> None:
    """Authenticate against Keycloak and synthesize a short greeting on the first pipeline."""
    log.info("START: synthesize_with_keycloak: main")

    use_secure_channel: bool = _env("ONDEWO_USE_SECURE_CHANNEL", "false").strip().lower() == "true"
    grpc_cert: Optional[str] = None
    cert_path: str = _env("ONDEWO_GRPC_CERT").strip()
    if use_secure_channel and cert_path:
        grpc_cert = Path(cert_path).read_text()

    config: ClientConfig = build_keycloak_config(
        host=_env("ONDEWO_HOST", "localhost"),
        port=_env("ONDEWO_PORT", "50555"),
        keycloak_url=_env("KEYCLOAK_URL", "https://keycloak.example.com/auth"),
        realm=_env("KEYCLOAK_REALM", "ondewo-ccai-platform"),
        client_id=_env("KEYCLOAK_CLIENT_ID", "ondewo-nlu-cai-sdk-public"),
        username=_env("KEYCLOAK_USER_NAME", "technical-user@ondewo.com"),
        password=_env("KEYCLOAK_PASSWORD"),
        grpc_cert=grpc_cert,
        keycloak_verify_ssl=_env("KEYCLOAK_VERIFY_SSL", "true").strip().lower() == "true",
    )
    log.info(f"Connecting to ONDEWO T2S at {config.host}:{config.port} (secure={use_secure_channel})")

    # One shared provider performs the ROPC offline-token login once and auto-refreshes it.
    provider: KeycloakTokenProvider = get_keycloak_token_provider(config)
    client: Client = Client(config=config, use_secure_channel=use_secure_channel)
    try:
        run(client=client, provider=provider, text="Hello, this is ONDEWO Text-to-Speech.")
    finally:
        provider.stop()
        client.disconnect()
    log.info("DONE: synthesize_with_keycloak: main")


if __name__ == "__main__":
    try:
        main()
    except grpc.RpcError as rpc_error:
        log.exception(
            f"Keycloak T2S example failed with a gRPC error: code={rpc_error.code()} details={rpc_error.details()}"
        )
        sys.exit(1)
    except Exception:
        log.exception("Keycloak T2S example failed with an unexpected error.")
        sys.exit(1)
