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
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json
from ondewo.utils.base_client_config import BaseClientConfig


@dataclass_json
@dataclass(frozen=True)
class ClientConfig(BaseClientConfig):
    """Config for the ONDEWO T2S client.

    In addition to the host/port/cert inherited from ``BaseClientConfig`` this config carries the
    credentials for the headless Keycloak offline-token auth flow (D18) used by the ONDEWO CCAI platform.

    Two authentication shapes are supported:

    * **Keycloak headless offline-token (D18, preferred).** Set ``keycloak_url``, ``realm``, ``client_id``,
      ``username`` and ``password``. The SDK performs a Resource-Owner-Password-Credentials (ROPC) grant with
      ``scope=offline_access`` against the **public** SDK client (``ondewo-nlu-cai-sdk-public`` — there is **no**
      ``client_secret``, Q1), then auto-refreshes the short-lived access token and attaches it as the
      ``Authorization: Bearer`` metadata. ``token_expiration_in_s`` optionally bounds how long the refresh loop runs.
    * **Legacy ROPC (``user_name``/``password``).** Kept working for backward compatibility / dual-mode. ``http_token``
      (the Envoy HTTP-Basic header) is **no longer required** — Envoy now validates the bearer JWT (D5).

    Attributes:
        http_token (str):
            Legacy ``Authorization: Basic`` token for proxies/Envoy. Optional now (D5) — kept for backward
            compatibility; new deployments should leave it empty.
        user_name (str):
            User name / email used for the legacy ROPC ``Login`` path (e.g. ``"testuser@ondewo.com"``).
        password (str):
            Password associated with ``user_name`` (also used as the Keycloak ROPC password).
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
    """

    http_token: str = ""
    user_name: str = ""
    password: str = ""
    keycloak_url: Optional[str] = None
    realm: Optional[str] = None
    client_id: Optional[str] = None
    username: Optional[str] = None
    token_expiration_in_s: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate the config after initialization.

        ``http_token`` is intentionally **not** required (D5 — Envoy validates the bearer JWT). When any Keycloak
        field is provided, the full set required for the ROPC offline-token grant must be present.

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
