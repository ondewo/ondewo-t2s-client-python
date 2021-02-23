#!/usr/bin/env python
# coding: utf-8
import argparse
import io

import IPython.display as ipd
from google.protobuf.empty_pb2 import Empty
import grpc
import soundfile as sf

from ondewo.t2s import text_to_speech_pb2, text_to_speech_pb2_grpc, grpc_utils


# DESCRIPTION:
# In this example we do the following:
# 1. Create a stub which is used to connect to the server
# 2. List all avaialable pipelines and filter on english language ones
# 3. Send a synthesis request to the specified pipeline
# 4. Update the specified pipeline
# 5. Send a synthesis request to the updated pipeline
# 6. Revert the update of the specified pipeline


def synthesis_request(stub, **req_kwargs):
    request = text_to_speech_pb2.SynthesizeRequest(**req_kwargs)
    response = stub.Synthesize(request=request)

    print(f'Length of the generated audio is {response.audio_length} sec.',
        f'Generation time is {response.generation_time} sec.')

    bio = io.BytesIO(response.audio)
    audio = sf.read(bio)
    return audio


def main():
    parser = argparse.ArgumentParser(description='API example.')
    parser.add_argument("--config", type=str)
    parser.add_argument("--secure", default=False, action='store_true')
    args = parser.parse_args()

    # 1. Create a stub which is used to connect to the server
    stub = grpc_utils.create_stub(args.config, args.secure)

    # 2. List all avaialable pipelines and filter on english language ones
    # List all t2s pipelines present on the server
    pipelines = stub.ListT2sPipelines(request=Empty()).pipelines

    # List pipelines based on conditions
    german_pipelines = stub.ListT2sPipelines(request=text_to_speech_pb2.ListT2sPipelinesRequest(
        languages=['de'])).pipelines
    german_pipeline = german_pipelines[0]

    # 3. Send a synthesis request to the specified pipeline
    # Make synthesize request to the server to get audio for given text
    audio = synthesis_request(stub, text="Hallo, wie geht es dir?", t2s_pipeline_id=german_pipeline.id)
    ipd.Audio(audio[0], rate=audio[1])

    # Adding length scale parameter to make speech faster or slower
    audio = synthesis_request(stub, text='Hallo, wie geht es dir?', t2s_pipeline_id=german_pipeline.id,
                                                length_scale=0.5)
    ipd.Audio(audio[0], rate=audio[1])

    # 4. Update a specified pipeline
    # Change parameter in the pipeline config. For example default length scale
    german_pipeline.inference.composite_inference.text2mel.glow_tts.length_scale = 2

    # Update pipeline
    stub.UpdateT2sPipeline(request=german_pipeline)

    # 5. Send a synthesis request to the updated pipeline
    # See if generated audio change according to updated config
    audio = synthesis_request(stub, text='Hallo, wie geht es dir?', t2s_pipeline_id=german_pipeline.id)
    ipd.Audio(audio[0], rate=audio[1])

    # 6. Revert the update of the specified pipeline
    # Change parameter back to previous (length_scale = 1.0)
    german_pipeline.inference.composite_inference.text2mel.glow_tts.length_scale = 1.0
    stub.UpdateT2sPipeline(request=german_pipeline)


if __name__ == '__main__':
    main()