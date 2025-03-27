# Copyright 2021-2025 ONDEWO GmbH
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
import argparse
import io
import json
from typing import (
    Any,
    Set,
    Tuple,
)

import grpc
import soundfile as sf

from ondewo.t2s import text_to_speech_pb2
from ondewo.t2s.client.client import Client
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.client.services.text_to_speech import Text2Speech
from ondewo.t2s.text_to_speech_pb2 import (
    ListT2sPipelinesRequest,
    Text2SpeechConfig,
)


# DESCRIPTION:
# In this example we do the following:
# 1. Create a stub which is used to connect to the server
# 2. List all available pipelines and filter on english language ones
# 3. Send a synthesis request to the specified pipeline
# 4. Update the specified pipeline
# 5. Send a synthesis request to the updated pipeline
# 6. Revert the update of the specified pipeline


def synthesis_request(t2s_service: Text2Speech, **req_kwargs: Any) -> bytes:
    request: text_to_speech_pb2.SynthesizeRequest = text_to_speech_pb2.SynthesizeRequest(**req_kwargs)
    response: text_to_speech_pb2.SynthesizeResponse = t2s_service.synthesize(request=request)

    print(
        f"Length of the generated audio is {response.audio_length} sec.",
        f"Generation time is {response.generation_time} sec.",
    )

    bio: io.BytesIO = io.BytesIO(response.audio)
    audio: bytes = sf.read(bio)
    return audio


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="API example.")
    parser.add_argument("--config", type=str, default="configs/insecure_grpc.json")
    parser.add_argument("--secure", default=False, action="store_true")
    args = parser.parse_args()

    with open(args.config) as f:
        config: ClientConfig = ClientConfig.from_json(f.read())

    # https://github.com/grpc/grpc-proto/blob/master/grpc/service_config/service_config.proto
    service_config_json: str = json.dumps(
        {
            "methodConfig": [
                {
                    "name": [
                        # To apply retry to all methods, put [{}] as a value in the "name" field
                        # {}
                        # List single rpc method calls
                        {"service": "ondewo.t2s.Text2Speech", "method": "ListT2sPipelines"},
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
        ("grpc.keepalive_time_ms", 2 ** 31 - 1),
        ("grpc.keepalive_timeout_ms", 20000),
        ("grpc.keepalive_permit_without_calls", False),
        ("grpc.http2.max_pings_without_data", 2),
        # Example arg requested for the feature
        ("grpc.dns_enable_srv_queries", 1),
        ("grpc.enable_retries", 1),
        ("grpc.service_config", service_config_json)
    }

    client: Client = Client(config=config, use_secure_channel=args.secure, options=options)
    t2s_service: Text2Speech = client.services.text_to_speech

    # 2. List all available pipelines and filter on english language ones
    # List all t2s pipelines present on the server
    for pipeline in t2s_service.list_t2s_pipelines(request=ListT2sPipelinesRequest()).pipelines:
        print(pipeline)

    # List pipelines based on conditions
    german_pipelines = t2s_service.list_t2s_pipelines(
        request=ListT2sPipelinesRequest(languages=["de"])
    ).pipelines
    german_pipeline: Text2SpeechConfig = german_pipelines[0]

    # 3. Send a synthesis request to the specified pipeline
    # Make synthesize request to the server to get audio for given text
    audio = synthesis_request(t2s_service, text="Hallo, wie geht es dir?", t2s_pipeline_id=german_pipeline.id)
    assert audio
    # Adding length scale parameter to make speech faster or slower
    audio = synthesis_request(
        t2s_service, text="Hallo, wie geht es dir?", t2s_pipeline_id=german_pipeline.id, length_scale=0.5
    )
    assert audio

    # 4. Update a specified pipeline
    # Change parameter in the pipeline config. For example default length scale
    german_pipeline.inference.composite_inference.text2mel.glow_tts.length_scale = 2

    # Update pipeline
    t2s_service.update_t2s_pipeline(request=german_pipeline)

    # 5. Send a synthesis request to the updated pipeline
    # See if generated audio change according to updated config
    audio = synthesis_request(t2s_service, text="Hallo, wie geht es dir?", t2s_pipeline_id=german_pipeline.id)
    assert audio

    # 6. Revert the update of the specified pipeline
    # Change parameter back to previous (length_scale = 1.0)
    german_pipeline.inference.composite_inference.text2mel.glow_tts.length_scale = 1.0
    t2s_service.update_t2s_pipeline(request=german_pipeline)


if __name__ == "__main__":
    main()
