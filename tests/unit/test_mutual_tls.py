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
TLS and mutual TLS, end to end through the SDK's own ``Client`` / ``AsyncClient`` and ``ClientConfig``.

Every handshake test starts a real in-process gRPC server with certificates minted per module (one deployment
CA and one unrelated "foreign" CA), builds the real client from a ``ClientConfig`` and makes one real
``Synthesize`` call. A call that reaches the server proves the handshake; a refused handshake surfaces as
``UNAVAILABLE`` (an ``RpcError``, never a crash of the process). ``Synthesize`` is not idempotent, so the
SDK's retry policy never re-sends it and a refusal is reported at once.
"""

import asyncio
import datetime
from concurrent import futures
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
)

import grpc
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import (
    hashes,
    serialization,
)
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import (
    ExtendedKeyUsageOID,
    NameOID,
)

import ondewo.t2s.client.core.async_services_interface as async_services_interface_module
import ondewo.t2s.client.core.services_interface as services_interface_module
from ondewo.t2s.client.async_client import AsyncClient
from ondewo.t2s.client.client import Client
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.text_to_speech_pb2 import (
    SynthesizeRequest,
    SynthesizeResponse,
)

SERVER_NAME: str = "localhost"
SERVICE: str = "ondewo.t2s.Text2Speech"
PASSWORD: str = "planted-password-never-printed"
BEARER: List[Tuple[str, str]] = [("authorization", "Bearer planted-token")]


class Pki:
    """One throwaway CA with a server leaf (SAN ``localhost``) and a client leaf, all PEM bytes."""

    def __init__(self, name: str) -> None:
        self._ca_key: ec.EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP256R1())
        self.ca_cert: bytes = self._issue(f"{name}-ca", self._ca_key.public_key(), ca=True, issuer=None)
        server_key: ec.EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP256R1())
        self.server_key: bytes = _pem_key(server_key)
        self.server_cert: bytes = self._issue(
            f"{name}-server",
            server_key.public_key(),
            ca=False,
            issuer=x509.load_pem_x509_certificate(self.ca_cert),
            usage=ExtendedKeyUsageOID.SERVER_AUTH,
            san=SERVER_NAME,
        )
        client_key: ec.EllipticCurvePrivateKey = ec.generate_private_key(ec.SECP256R1())
        self.client_key: bytes = _pem_key(client_key)
        self.client_cert: bytes = self._issue(
            f"{name}-client",
            client_key.public_key(),
            ca=False,
            issuer=x509.load_pem_x509_certificate(self.ca_cert),
            usage=ExtendedKeyUsageOID.CLIENT_AUTH,
        )

    def _issue(
        self,
        subject: str,
        public_key: ec.EllipticCurvePublicKey,
        ca: bool,
        issuer: Optional[x509.Certificate],
        usage: Optional[x509.ObjectIdentifier] = None,
        san: Optional[str] = None,
    ) -> bytes:
        now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        name: x509.Name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject)])
        builder: x509.CertificateBuilder = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name if issuer is None else issuer.subject)
            .public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=30))
            .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
        )
        if usage is not None:
            builder = builder.add_extension(x509.ExtendedKeyUsage([usage]), critical=False)
        if san is not None:
            builder = builder.add_extension(x509.SubjectAlternativeName([x509.DNSName(san)]), critical=False)
        return builder.sign(self._ca_key, hashes.SHA256()).public_bytes(serialization.Encoding.PEM)


def _pem_key(key: ec.EllipticCurvePrivateKey) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


@pytest.fixture(scope="module")
def pki() -> Pki:
    return Pki("deployment")


@pytest.fixture(scope="module")
def foreign() -> Pki:
    return Pki("foreign")


class _Server:
    """A real TLS gRPC server answering ``Synthesize`` and recording the metadata of each call."""

    def __init__(self, pki: Pki, require_client_auth: bool) -> None:
        self.metadata: List[Tuple[str, str]] = []
        self._server: grpc.Server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        handler: grpc.GenericRpcHandler = grpc.method_handlers_generic_handler(
            SERVICE,
            {
                "Synthesize": grpc.unary_unary_rpc_method_handler(
                    self._synthesize,
                    request_deserializer=SynthesizeRequest.FromString,
                    response_serializer=SynthesizeResponse.SerializeToString,
                )
            },
        )
        self._server.add_generic_rpc_handlers((handler,))
        credentials: grpc.ServerCredentials = grpc.ssl_server_credentials(
            [(pki.server_key, pki.server_cert)],
            root_certificates=pki.ca_cert if require_client_auth else None,
            require_client_auth=require_client_auth,
        )
        self.port: int = self._server.add_secure_port(f"{SERVER_NAME}:0", credentials)
        self._server.start()

    def _synthesize(self, request: SynthesizeRequest, context: grpc.ServicerContext) -> SynthesizeResponse:
        self.metadata.extend((key, value) for key, value in context.invocation_metadata())
        return SynthesizeResponse(audio_uuid="served")

    def stop(self) -> None:
        self._server.stop(grace=None)


@pytest.fixture
def server() -> Iterator[Callable[[Pki, bool], _Server]]:
    """Start TLS servers on ephemeral ports; ``(pki, require_client_auth) -> _Server``."""
    servers: List[_Server] = []

    def start(pki: Pki, require_client_auth: bool) -> _Server:
        started: _Server = _Server(pki, require_client_auth)
        servers.append(started)
        return started

    yield start
    for started in servers:
        started.stop()


def _config(port: int, trust: Pki, client: Optional[Pki] = None, **extra: Any) -> ClientConfig:
    """A config trusting ``trust``'s CA, presenting ``client``'s leaf when given (mutual TLS)."""
    return ClientConfig(
        host=SERVER_NAME,
        port=str(port),
        grpc_cert=trust.ca_cert.decode(),
        grpc_client_cert=None if client is None else client.client_cert.decode(),
        grpc_client_key=None if client is None else client.client_key.decode(),
        **extra,
    )


def _synthesize(config: ClientConfig) -> SynthesizeResponse:
    client: Client = Client(config=config, use_secure_channel=True)
    try:
        response: SynthesizeResponse = client.services.text_to_speech.synthesize(SynthesizeRequest(text="hi"))
        return response
    finally:
        client.disconnect()


def _async_synthesize(config: ClientConfig) -> SynthesizeResponse:
    async def call() -> SynthesizeResponse:
        client: AsyncClient = AsyncClient(config=config, use_secure_channel=True)
        try:
            response: SynthesizeResponse = await client.services.text_to_speech.synthesize(SynthesizeRequest(text="hi"))
            return response
        finally:
            await client.disconnect()

    return asyncio.run(call())


CALLS: List[Callable[[ClientConfig], SynthesizeResponse]] = [_synthesize, _async_synthesize]
CALL_IDS: List[str] = ["Client", "AsyncClient"]


def _crlf(pem: bytes) -> str:
    return pem.decode().replace("\n", "\r\n")


@pytest.mark.parametrize("call", CALLS, ids=CALL_IDS)
class TestHandshakes:
    """Real handshakes of the SDK clients against TLS-only and client-auth servers."""

    def test_plain_tls_is_served(self, call: Any, server: Any, pki: Pki) -> None:
        started: _Server = server(pki, False)
        assert call(_config(started.port, pki)).audio_uuid == "served"

    def test_mutual_tls_is_served(self, call: Any, server: Any, pki: Pki) -> None:
        started: _Server = server(pki, True)
        assert call(_config(started.port, pki, client=pki)).audio_uuid == "served"

    def test_mutual_tls_with_crlf_pems_is_served(self, call: Any, server: Any, pki: Pki) -> None:
        started: _Server = server(pki, True)
        config: ClientConfig = ClientConfig(
            host=SERVER_NAME,
            port=str(started.port),
            grpc_cert=_crlf(pki.ca_cert),
            grpc_client_cert=_crlf(pki.client_cert),
            grpc_client_key=_crlf(pki.client_key),
        )
        assert call(config).audio_uuid == "served"

    def test_empty_identity_on_both_is_plain_tls(self, call: Any, server: Any, pki: Pki) -> None:
        started: _Server = server(pki, False)
        config: ClientConfig = ClientConfig(
            host=SERVER_NAME,
            port=str(started.port),
            grpc_cert=pki.ca_cert.decode(),
            grpc_client_cert="",
            grpc_client_key="",
        )
        assert call(config).audio_uuid == "served"

    def test_no_identity_against_a_client_auth_server_is_unavailable(self, call: Any, server: Any, pki: Pki) -> None:
        started: _Server = server(pki, True)
        with pytest.raises(grpc.RpcError) as refusal:
            call(_config(started.port, pki))
        assert refusal.value.code() is grpc.StatusCode.UNAVAILABLE  # type: ignore[attr-defined]
        assert started.metadata == []

    def test_identity_from_an_unrelated_ca_is_refused(self, call: Any, server: Any, pki: Pki, foreign: Pki) -> None:
        started: _Server = server(pki, True)
        with pytest.raises(grpc.RpcError) as refusal:
            call(_config(started.port, pki, client=foreign))
        assert refusal.value.code() is grpc.StatusCode.UNAVAILABLE  # type: ignore[attr-defined]
        assert started.metadata == []

    def test_a_server_from_an_unrelated_ca_is_refused(self, call: Any, server: Any, pki: Pki, foreign: Pki) -> None:
        started: _Server = server(foreign, False)
        with pytest.raises(grpc.RpcError) as refusal:
            call(_config(started.port, pki, client=pki))
        assert refusal.value.code() is grpc.StatusCode.UNAVAILABLE  # type: ignore[attr-defined]

    def test_keycloak_bearer_travels_over_mutual_tls(
        self, call: Any, server: Any, pki: Pki, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A Keycloak config (fake token provider, no network) keeps its bearer header on an mTLS channel."""

        class _FakeProvider:
            def bearer_metadata(self) -> List[Tuple[str, str]]:
                return BEARER

        for module in (services_interface_module, async_services_interface_module):
            monkeypatch.setattr(module, "get_keycloak_token_provider", lambda config: _FakeProvider())
        started: _Server = server(pki, True)
        config: ClientConfig = _config(
            started.port,
            pki,
            client=pki,
            keycloak_url="https://kc.example.com/auth",
            realm="realm",
            client_id="client",
            username="user",
            password=PASSWORD,
        )
        assert call(config).audio_uuid == "served"
        assert BEARER[0] in started.metadata


class TestRefusedBeforeGrpc:
    """Misconfigurations are refused by the SDK with a ``ValueError`` before any channel exists."""

    @pytest.mark.parametrize("dropped", ["grpc_client_cert", "grpc_client_key"])
    def test_half_a_client_identity_is_refused_by_the_config(self, pki: Pki, dropped: str) -> None:
        identity: Dict[str, Any] = {
            "grpc_client_cert": pki.client_cert.decode(),
            "grpc_client_key": pki.client_key.decode(),
        }
        identity[dropped] = ""
        with pytest.raises(ValueError, match="set both to use mutual TLS, or neither") as refusal:
            ClientConfig(host=SERVER_NAME, port="1", grpc_cert=pki.ca_cert.decode(), **identity)
        assert "PRIVATE KEY" not in str(refusal.value)
        assert "CERTIFICATE" not in str(refusal.value)

    def test_insecure_channel_with_an_identity_is_refused(self, pki: Pki) -> None:
        config: ClientConfig = _config(1, pki, client=pki, password=PASSWORD)
        with pytest.raises(ValueError, match="use a secure channel") as refusal:
            Client(config=config, use_secure_channel=False)
        assert "PRIVATE KEY" not in str(refusal.value)
        assert PASSWORD not in str(refusal.value)

    def test_async_insecure_channel_with_an_identity_is_refused(self, pki: Pki) -> None:
        config: ClientConfig = _config(1, pki, client=pki, password=PASSWORD)

        async def build() -> None:
            AsyncClient(config=config, use_secure_channel=False)

        with pytest.raises(ValueError, match="use a secure channel"):
            asyncio.run(build())

    def test_repr_and_str_never_render_the_key_or_password(self, pki: Pki) -> None:
        config: ClientConfig = _config(1, pki, client=pki, password=PASSWORD)
        assert config.grpc_client_key == pki.client_key
        assert config.password == PASSWORD
        for rendered in (repr(config), str(config)):
            assert "PRIVATE KEY" not in rendered
            assert PASSWORD not in rendered
            assert "grpc_client_key='***REDACTED***'" in rendered
