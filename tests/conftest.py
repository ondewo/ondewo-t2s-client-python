import json
import grpc
from typing import (
    Any,
    Set,
    Tuple,
)

import pytest

from ondewo.t2s.client.client import Client
from ondewo.t2s.client.client_config import ClientConfig


MAX_MESSAGE_LENGTH: int = 60000000
GRPC_HOST: str = "localhost"
GRPC_PORT: str = "50555"
CHANNEL: str = f"{GRPC_HOST}:{GRPC_PORT}"
CERT = ""
USE_SECURE_CHANNEL: bool = True if CERT else False
SERVICE_CONFIG_JSON: str = json.dumps(
    {
        "methodConfig": [
            {
                "name": [
                    # To apply retry to all methods, put [{}] as a value in the "name" field
                    # {}
                    # List single rpc method calls
                    {"service": "ondewo.t2s.Text2Speech", "method": "BatchSynthesize"},
                    {"service": "ondewo.t2s.Text2Speech", "method": "ListT2sLanguages"},
                    {"service": "ondewo.t2s.Text2Speech", "method": "ListT2sPipelines"},
                    {"service": "ondewo.t2s.Text2Speech", "method": "Synthesize"},
                ],
                "retryPolicy": {
                    "maxAttempts": 10,
                    "initialBackoff": "1.1s",
                    "maxBackoff": "3000s",
                    "backoffMultiplier": 2,
                    "retryableStatusCodes": [
                        grpc.StatusCode.CANCELLED.name,
                        grpc.StatusCode.UNKNOWN.name,
                        grpc.StatusCode.DEADLINE_EXCEEDED.name,
                        grpc.StatusCode.NOT_FOUND.name,
                        grpc.StatusCode.RESOURCE_EXHAUSTED.name,
                        grpc.StatusCode.ABORTED.name,
                        grpc.StatusCode.INTERNAL.name,
                        grpc.StatusCode.UNAVAILABLE.name,
                        grpc.StatusCode.DATA_LOSS.name,
                    ],
                },
            }
        ]
    }
)

OPTIONS: Set[Tuple[str, Any]] = {
    # Define custom max message sizes: 1MB here is an arbitrary example.
    ("grpc.max_send_message_length", 1024 * 1024),
    ("grpc.max_receive_message_length", 1024 * 1024),
    # Example of setting KeepAlive options through generic channel_args
    ("grpc.keepalive_time_ms", 2 ** 31 - 1),
    ("grpc.keepalive_timeout_ms", 20000),
    ("grpc.keepalive_permit_without_calls", False),
    ("grpc.http2.max_pings_without_data", 2),
    # Example arg requested for the feature
    ("grpc.dns_enable_srv_queries", 1),
    ("grpc.enable_retries", 1),
    ("grpc.service_config", SERVICE_CONFIG_JSON)
}


@pytest.fixture(scope='function')
def client() -> Client:
    config: ClientConfig = ClientConfig(host=GRPC_HOST, port=GRPC_PORT, grpc_cert=CERT)
    client: Client = Client(config=config, use_secure_channel=False, options=OPTIONS)
    return client
