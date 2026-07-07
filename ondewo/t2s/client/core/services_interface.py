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
from abc import ABC
from typing import (
    Any,
    List,
    Optional,
    Set,
    Tuple,
)

from ondewo.utils.base_services_interface import BaseServicesInterface

from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.utils.keycloak import (
    KeycloakTokenProvider,
    get_keycloak_token_provider,
)


class ServicesInterface(BaseServicesInterface, ABC):
    """Base for the generated T2S service wrappers, attaching Keycloak bearer auth (D18).

    Every generated wrapper method forwards :attr:`metadata` to its gRPC stub call, so this
    interface is the single place that turns the ``ClientConfig`` Keycloak fields into the
    ``Authorization: Bearer`` header sent with each request.
    """

    def __init__(
        self,
        config: ClientConfig,
        use_secure_channel: bool,
        options: Optional[Set[Tuple[str, Any]]] = None,
    ) -> None:
        """Build the gRPC channel and, when configured, the shared Keycloak token provider.

        Args:
            config (ClientConfig):
                The T2S client config; its Keycloak fields (``use_keycloak``) decide whether a
                bearer token is attached to outgoing calls.
            use_secure_channel (bool):
                Whether to use a secure gRPC channel.
            options (Optional[Set[Tuple[str, Any]]]):
                Additional options for the gRPC channel.
        """
        super(ServicesInterface, self).__init__(
            config=config,
            use_secure_channel=use_secure_channel,
            options=options,
        )
        # When Keycloak headless auth (D18) is configured, every call carries a freshly
        # auto-refreshed `Authorization: Bearer` token; the provider is shared per config so
        # the offline-token ROPC login happens once for all services on the client.
        self._keycloak_provider: Optional[KeycloakTokenProvider] = (
            get_keycloak_token_provider(config) if config.use_keycloak else None
        )

    @property
    def metadata(self) -> List[Tuple[str, str]]:
        """The gRPC metadata attached to every outgoing call.

        With Keycloak auth this rebuilds (and auto-refreshes) the ``Authorization: Bearer``
        token on each access; without it the SDK sends no auth metadata.

        Returns:
            List[Tuple[str, str]]:
                The metadata tuples for the next gRPC call (empty when Keycloak is not configured).
        """
        if self._keycloak_provider is not None:
            return self._keycloak_provider.bearer_metadata()
        return []
