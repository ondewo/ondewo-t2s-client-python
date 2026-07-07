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
import io
import json
import os
import sys
from pathlib import Path
from typing import (
    Any,
    Optional,
    Set,
    Tuple,
)

import grpc
import soundfile as sf
from dotenv import load_dotenv
from loguru import logger as log

from ondewo.t2s import text_to_speech_pb2
from ondewo.t2s.client.client import Client
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.services.text_to_speech import Text2Speech
from ondewo.t2s.text_to_speech_pb2 import (
    ListT2sPipelinesRequest,
    Text2SpeechConfig,
)

# Load the example configuration (host/port/secure channel) from environment.env sitting next to
# this script, so the example works regardless of the current working directory.
load_dotenv(Path(__file__).with_name("environment.env"))


# DESCRIPTION:
# In this example we do the following:
# 1. Create a stub which is used to connect to the server
# 2. List all available pipelines and filter on german language ones
# 3. Send a synthesis request to the specified pipeline
# 4. Update the specified pipeline
# 5. Send a synthesis request to the updated pipeline
# 6. Revert the update of the specified pipeline


def load_config() -> Tuple[ClientConfig, bool]:
    """Build the client config and secure-channel flag from the canonical environment variables.

    Returns:
        Tuple[ClientConfig, bool]:
            The populated ``ClientConfig`` and whether a secure (TLS) channel should be used.
    """
    use_secure_channel: bool = os.getenv("ONDEWO_USE_SECURE_CHANNEL", "false").strip().lower() == "true"

    grpc_cert: Optional[str] = None
    cert_path: str = os.getenv("ONDEWO_GRPC_CERT", "").strip()
    if use_secure_channel and cert_path:
        grpc_cert = Path(cert_path).read_text()

    config: ClientConfig = ClientConfig(
        host=os.environ["ONDEWO_HOST"],
        port=os.environ["ONDEWO_PORT"],
        grpc_cert=grpc_cert,
    )
    return config, use_secure_channel


def synthesis_request(
    t2s_service: Text2Speech,
    text: str,
    t2s_pipeline_id: str,
    length_scale: float = 1.0,
) -> bytes:
    """Synthesize ``text`` on the given pipeline and return the decoded audio.

    Args:
        t2s_service (Text2Speech):
            The T2S service wrapper bound to the client's channel.
        text (str):
            The text to convert to speech.
        t2s_pipeline_id (str):
            Id of the T2S pipeline that should synthesize the text.
        length_scale (float):
            Time-stretch factor (``1.0`` is natural speed; lower is faster).

    Returns:
        bytes:
            The decoded audio samples.

    Raises:
        grpc.RpcError:
            If the ``Synthesize`` RPC fails.
    """
    log.info(f"START: synthesis_request: t2s_pipeline_id={t2s_pipeline_id} length_scale={length_scale}")
    # In the current API the pipeline id and the modulation parameters live on the nested
    # RequestConfig, not directly on SynthesizeRequest (which only carries `text` + `config`).
    request: text_to_speech_pb2.SynthesizeRequest = text_to_speech_pb2.SynthesizeRequest(
        text=text,
        config=text_to_speech_pb2.RequestConfig(
            t2s_pipeline_id=t2s_pipeline_id,
            length_scale=length_scale,
        ),
    )
    try:
        response: text_to_speech_pb2.SynthesizeResponse = t2s_service.synthesize(request=request)
    except grpc.RpcError as rpc_error:
        log.error(
            f"Synthesize RPC failed for pipeline {t2s_pipeline_id}: "
            f"code={rpc_error.code()} details={rpc_error.details()}"
        )
        raise

    log.info(
        f"DONE: synthesis_request: audio_length={response.audio_length}s "
        f"generation_time={response.generation_time}s"
    )

    bio: io.BytesIO = io.BytesIO(response.audio)
    audio: bytes = sf.read(bio)
    return audio


def main() -> None:
    """Run the end-to-end T2S API example against the configured server."""
    log.info("START: example_api: main")
    config, use_secure_channel = load_config()
    log.info(f"Connecting to ONDEWO T2S at {config.host}:{config.port} (secure={use_secure_channel})")

    # https://github.com/grpc/grpc-proto/blob/master/grpc/service_config/service_config.proto
    service_config_json: str = json.dumps(
        {
            "methodConfig": [
                {
                    "name": [
                        # To apply retry to all methods, put [{}] as a value in the "name" field
                        # {}
                        # List single rpc method calls
                        {
                            "service": "ondewo.t2s.Text2Speech",
                            "method": "ListT2sPipelines",
                        },
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

    options: Set[Tuple[str, Any]] = {
        # Define custom max message sizes: 1MB here is an arbitrary example.
        ("grpc.max_send_message_length", 1024 * 1024),
        ("grpc.max_receive_message_length", 1024 * 1024),
        # Example of setting KeepAlive options through generic channel_args
        ("grpc.keepalive_time_ms", 2**31 - 1),
        ("grpc.keepalive_timeout_ms", 20000),
        ("grpc.keepalive_permit_without_calls", False),
        ("grpc.http2.max_pings_without_data", 2),
        # Example arg requested for the feature
        ("grpc.dns_enable_srv_queries", 1),
        ("grpc.enable_retries", 1),
        ("grpc.service_config", service_config_json),
    }

    client: Client = Client(
        config=config, use_secure_channel=use_secure_channel, options=options
    )
    t2s_service: Text2Speech = client.services.text_to_speech

    # 2. List all available pipelines and filter on german language ones
    # List all t2s pipelines present on the server
    log.info("Listing all available T2S pipelines")
    for pipeline in t2s_service.list_t2s_pipelines(
        request=ListT2sPipelinesRequest()
    ).pipelines:
        log.info(f"Pipeline: {pipeline.id}")

    # List pipelines based on conditions
    german_pipelines = t2s_service.list_t2s_pipelines(
        request=ListT2sPipelinesRequest(languages=["de"])
    ).pipelines
    if not german_pipelines:
        raise RuntimeError("No German (de) T2S pipelines are available on the server.")
    german_pipeline: Text2SpeechConfig = german_pipelines[0]
    log.info(f"Using German pipeline {german_pipeline.id}")

    # 3. Send a synthesis request to the specified pipeline
    # Make synthesize request to the server to get audio for given text
    audio = synthesis_request(
        t2s_service, text="Hallo, wie geht es dir?", t2s_pipeline_id=german_pipeline.id
    )
    assert audio
    # Adding length scale parameter to make speech faster or slower
    audio = synthesis_request(
        t2s_service,
        text="Hallo, wie geht es dir?",
        t2s_pipeline_id=german_pipeline.id,
        length_scale=0.5,
    )
    assert audio

    # 4. Update a specified pipeline
    # Change parameter in the pipeline config. For example default length scale
    log.info(f"Updating pipeline {german_pipeline.id}: length_scale=2")
    german_pipeline.inference.composite_inference.text2mel.glow_tts.length_scale = 2

    # Update pipeline
    t2s_service.update_t2s_pipeline(request=german_pipeline)

    # 5. Send a synthesis request to the updated pipeline
    # See if generated audio change according to updated config
    audio = synthesis_request(
        t2s_service, text="Hallo, wie geht es dir?", t2s_pipeline_id=german_pipeline.id
    )
    assert audio

    # 6. Revert the update of the specified pipeline
    # Change parameter back to previous (length_scale = 1.0)
    log.info(f"Reverting pipeline {german_pipeline.id}: length_scale=1.0")
    german_pipeline.inference.composite_inference.text2mel.glow_tts.length_scale = 1.0
    t2s_service.update_t2s_pipeline(request=german_pipeline)
    log.info("DONE: example_api: main")


if __name__ == "__main__":
    try:
        main()
    except grpc.RpcError as rpc_error:
        log.exception(
            f"T2S example failed with a gRPC error: code={rpc_error.code()} details={rpc_error.details()}"
        )
        sys.exit(1)
    except Exception:
        log.exception("T2S example failed with an unexpected error.")
        sys.exit(1)
