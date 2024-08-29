import pytest

from ondewo.t2s.client.client import Client
from ondewo.t2s.text_to_speech_pb2 import (
    ListT2sLanguagesRequest,
    ListT2sLanguagesResponse,
    ListT2sPipelinesRequest,
    ListT2sPipelinesResponse,
    RequestConfig,
    SynthesizeRequest,
    SynthesizeResponse,
    T2sPipelineId,
)


def test_list_pipelines(client: Client):
    pipelines: ListT2sPipelinesResponse = client.services.text_to_speech.list_t2s_pipelines(
        request=ListT2sPipelinesRequest())
    assert len(pipelines.pipelines) > 0


def test_list_languages(client: Client):
    response: ListT2sLanguagesResponse = client.services.text_to_speech.list_t2s_languages(
        request=ListT2sLanguagesRequest())
    assert response is not None


@pytest.mark.parametrize(
    'text, length_scale', [
        ("Hi, this is Brigitte. Thanks for calling.", 1.0),
        ("I'm not here at the moment, so please leave a message and I'll call you back.", 0.7),
    ]
)
def test_synthesize_request(client: Client, text: str, length_scale: float):
    pipelines: ListT2sPipelinesResponse = client.services.text_to_speech.list_t2s_pipelines(
        request=ListT2sPipelinesRequest())
    pipeline_id: str = pipelines.pipelines[0].id
    synthesize_pipeline: T2sPipelineId = T2sPipelineId(id=pipeline_id)
    config: RequestConfig = RequestConfig(
        t2s_pipeline_id=synthesize_pipeline.id,
        length_scale=length_scale,
    )
    request: SynthesizeRequest = SynthesizeRequest(
        text=text,
        config=config,
    )
    response: SynthesizeResponse = client.services.text_to_speech.synthesize(request=request)
    assert response is not None
