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
from dataclasses import dataclass, fields
from typing import Any, ClassVar, FrozenSet, List, Optional

from dataclasses_json import dataclass_json
from ondewo.utils.base_client_config import BaseClientConfig


@dataclass_json
@dataclass(frozen=True)
class ClientConfig(BaseClientConfig):
    """Config for the ONDEWO T2S client.

    In addition to the host/port/cert inherited from ``BaseClientConfig`` this config carries the
    credentials for the headless Keycloak offline-token auth flow (D18) used by the ONDEWO CCAI platform.

    The SDK authenticates against a **public** Keycloak client (no ``client_secret`` — Q1/D18) using the
    Resource-Owner-Password-Credentials (ROPC) grant with ``scope=offline_access``: set ``keycloak_url``,
    ``realm``, ``client_id``, ``username`` and ``password``. The SDK then auto-refreshes the short-lived
    access token in the background and attaches it to every gRPC call as the ``Authorization: Bearer``
    metadata header. ``token_expiration_in_s`` optionally bounds how long the refresh loop runs.

    Backward compatibility: every field defaults to empty/``None`` so a bare ``ClientConfig(host=..., port=...)``
    (e.g. against a plaintext server or an Envoy ingress that injects auth) stays valid. When any Keycloak
    field is set, the full ROPC set (``keycloak_url``, ``realm``, ``client_id``, a username and ``password``)
    is required.

    Attributes:
        user_name (str):
            Backward-compatible alias for ``username``; used as the Keycloak ROPC user name when
            ``username`` is empty (e.g. ``"testuser@ondewo.com"``).
        password (str):
            Password of the (2FA-exempt) technical user used for the Keycloak ROPC grant.
        keycloak_url (Optional[str]):
            Base URL of the Keycloak server (e.g. ``"https://host/auth"``). When set together with ``realm``,
            ``client_id``, ``username`` and ``password``, the SDK uses the D18 offline-token flow.
        realm (Optional[str]):
            Keycloak realm name (e.g. ``"ondewo-ccai-platform"``).
        client_id (Optional[str]):
            Public Keycloak client id for the ROPC grant (e.g. ``"ondewo-nlu-cai-sdk-public"``). No client secret
            is used — this is a public client (Q1).
        username (Optional[str]):
            Keycloak user name for the ROPC grant. Falls back to ``user_name`` when omitted.
        token_expiration_in_s (Optional[int]):
            Upper bound (in seconds, since login) on how long the background access-token refresh runs. ``None``
            means refresh until the offline session itself expires.
        keycloak_verify_ssl (bool):
            Whether to verify the Keycloak server's TLS certificate on the token-endpoint
            call. Defaults to ``True`` (secure). Set ``False`` only for a self-signed/local
            Envoy at ``https://localhost:12001/auth``.
    """

    user_name: str = ""
    password: str = ""
    keycloak_url: Optional[str] = None
    realm: Optional[str] = None
    client_id: Optional[str] = None
    username: Optional[str] = None
    token_expiration_in_s: Optional[int] = None
    keycloak_verify_ssl: bool = True

    #: Fields whose value must never be rendered. ``grpc_cert`` is PEM material and ``password`` is
    #: the ROPC login secret; both are printed verbatim by the ``__repr__`` ``@dataclass`` generates.
    SECRET_FIELD_NAMES: ClassVar[FrozenSet[str]] = frozenset({"password", "grpc_cert"})

    def __repr__(self) -> str:
        """
        Render the config without its credential material.

        ``@dataclass`` generates a ``__repr__`` that prints every field, so any caller doing
        ``log.debug(f"...{config}")`` -- or a bare traceback carrying locals -- writes the ROPC
        password and the gRPC certificate to its logs in clear text. Downstream services do exactly
        that: a repository-wide sweep in ondewo-vtsi found this class among its leaking dataclasses.

        An EMPTY secret still renders as ``''`` rather than as ``***REDACTED***``. The distinction is
        deliberate: the marker reads as "this is set and sensitive", which is actively misleading
        when the real problem is that nobody set it -- usually the very thing being debugged.

        Returns:
            str:
                ``ClientConfig(host=..., password=***REDACTED***, ...)``.
        """
        rendered: List[str] = []
        for field in fields(self):
            value: Any = getattr(self, field.name, None)
            if field.name in self.SECRET_FIELD_NAMES and value:
                rendered.append(f"{field.name}='***REDACTED***'")
            else:
                rendered.append(f"{field.name}={value!r}")
        return f"{type(self).__name__}({', '.join(rendered)})"

    def __post_init__(self) -> None:
        """Validate the config after initialization.

        When any Keycloak field is provided, the full set required for the ROPC offline-token grant must be
        present. A bare host/port config stays valid so unauthenticated usage keeps working.

        Raises:
            ValueError:
                If a partial Keycloak configuration is supplied, or if a Keycloak flow is requested without a
                resolvable user name / password.
        """
        super().__post_init__()

        keycloak_fields = (self.keycloak_url, self.realm, self.client_id)
        keycloak_requested = any(value for value in keycloak_fields)

        if keycloak_requested:
            if not all(value for value in keycloak_fields):
                raise ValueError(
                    "When using Keycloak auth, all of `keycloak_url`, `realm` and `client_id` are mandatory "
                    f"in {self.__class__.__name__}."
                )
            if not self.resolved_username:
                raise ValueError(
                    "The field `username` (or `user_name`) is mandatory for Keycloak auth in "
                    f"{self.__class__.__name__}."
                )
            if not self.password:
                raise ValueError(
                    f"The field `password` is mandatory for Keycloak auth in {self.__class__.__name__}."
                )

    @property
    def use_keycloak(self) -> bool:
        """Whether the D18 Keycloak offline-token flow is configured.

        Returns:
            bool:
                ``True`` when ``keycloak_url``, ``realm`` and ``client_id`` are all set.
        """
        return bool(self.keycloak_url and self.realm and self.client_id)

    @property
    def resolved_username(self) -> str:
        """The user name to use for the ROPC grant.

        Prefers the dedicated ``username`` field and falls back to the legacy ``user_name``.

        Returns:
            str:
                The resolved user name (possibly empty).
        """
        return self.username or self.user_name
