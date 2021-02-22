#!/usr/bin/env python
# coding: utf-8
import io

import IPython.display as ipd
from google.protobuf.empty_pb2 import Empty
import grpc
import soundfile as sf

from ondewo.t2s import text_to_speech_pb2, text_to_speech_pb2_grpc


# DESCRIPTION:
# In this example we do the following:
# 1. Create a stub which is used to connect to the server
# 2. List all avaialable pipelines and filter on english language ones
# 3. Send a synthesis request to the specified pipeline
# 4. Update the specified pipeline
# 5. Send a synthesis request to the updated pipeline
# 6. Revert the update of the specified pipeline

# Set the parameters of the grpc server.
# The example below is for the case when server is running locally
MAX_MESSAGE_LENGTH: int = 6 * 1024 * 1024 # max message length in bytes
GRPC_HOST: str = "localhost"
GRPC_PORT: str = "50555"
CHANNEL: str = f"{GRPC_HOST}:{GRPC_PORT}"

def create_stub():
    options = [
        ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
    ]

    channel = grpc.insecure_channel(CHANNEL, options=options)
    stub = text_to_speech_pb2_grpc.Text2SpeechStub(channel=channel)
    
    return stub


def synthesis_request(stub, **req_kwargs):
    request = text_to_speech_pb2.SynthesizeRequest(**req_kwargs)
    response = stub.Synthesize(request=request)

    print(f'Length of the generated audio is {response.audio_length} sec.',
        f'Generation time is {response.generation_time} sec.')

    bio = io.BytesIO(response.audio)
    audio = sf.read(bio)
    return audio


def main():
    # 1. Create a stub which is used to connect to the server
    stub = create_stub()


    # 2. List all avaialable pipelines and filter on english language ones
    # List all t2s pipelines present on the server
    pipelines = stub.ListT2sPipelines(request=Empty()).pipelines

    # List pipelines based on conditions
    english_pipelines = stub.ListT2sPipelines(request=text_to_speech_pb2.ListT2sPipelinesRequest(
        languages=['en'])).pipelines
    english_pipeline = english_pipelines[0]


    # 3. Send a synthesis request to the specified pipeline
    # Make synthesize request to the server to get audio for given text
    audio = synthesis_request(stub, text='Hi, how are you?', t2s_pipeline_id=english_pipeline.id)
    ipd.Audio(audio[0], rate=audio[1])

    # Adding length scale parameter to make speech faster or slower
    audio = synthesis_request(stub, text='Hi, how are you?', t2s_pipeline_id=english_pipeline.id,
                                                length_scale=0.5)
    ipd.Audio(audio[0], rate=audio[1])


    # 4. Update a specified pipeline
    # Change parameter in the pipeline config. For example default length scale
    english_pipeline.inference.composite_inference.text2mel.glow_tts.length_scale = 2

    # Update pipeline
    stub.UpdateT2sPipeline(request=english_pipeline)


    # 5. Send a synthesis request to the updated pipeline
    # See if generated audio change according to updated config
    audio = synthesis_request(stub, text='Hi, how are you?', t2s_pipeline_id=english_pipeline.id)
    ipd.Audio(audio[0], rate=audio[1])


    # 6. Revert the update of the specified pipeline
    # Change parameter back to previous (length_scale = 1.0)
    english_pipeline.inference.composite_inference.text2mel.glow_tts.length_scale = 1.0
    stub.UpdateT2sPipeline(request=english_pipeline)


if __name__ == '__main__':
    main()