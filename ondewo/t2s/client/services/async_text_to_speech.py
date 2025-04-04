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
from google.protobuf.empty_pb2 import Empty
from ondewo.utils.async_base_services_interface import AsyncBaseServicesInterface

from ondewo.t2s.text_to_speech_pb2 import (
    BatchSynthesizeRequest,
    BatchSynthesizeResponse,
    CreateCustomPhonemizerRequest,
    CustomPhonemizerProto,
    ListCustomPhonemizerRequest,
    ListCustomPhonemizerResponse,
    ListT2sDomainsRequest,
    ListT2sDomainsResponse,
    ListT2sLanguagesRequest,
    ListT2sLanguagesResponse,
    ListT2sPipelinesRequest,
    ListT2sPipelinesResponse,
    NormalizeTextRequest,
    NormalizeTextResponse,
    PhonemizerId,
    SynthesizeRequest,
    SynthesizeResponse,
    T2SGetServiceInfoResponse,
    T2sPipelineId,
    Text2SpeechConfig,
    UpdateCustomPhonemizerRequest,
)
from ondewo.t2s.text_to_speech_pb2_grpc import Text2SpeechStub


class Text2Speech(AsyncBaseServicesInterface):
    """
    Exposes the t2s endpoints of ONDEWO t2s in a user-friendly way.

    See text_to_speech.proto.
    """

    @property
    def stub(self) -> Text2SpeechStub:
        stub: Text2SpeechStub = Text2SpeechStub(channel=self.grpc_channel)
        return stub

    async def synthesize(self, request: SynthesizeRequest) -> SynthesizeResponse:
        response: SynthesizeResponse = await self.stub.Synthesize(request)
        return response

    async def batch_synthesize(self, request: BatchSynthesizeRequest) -> BatchSynthesizeResponse:
        response: BatchSynthesizeResponse = await self.stub.BatchSynthesize(request)
        return response

    async def normalize_text(self, request: NormalizeTextRequest) -> NormalizeTextResponse:
        response: NormalizeTextResponse = await self.stub.NormalizeText(request)
        return response

    async def get_t2s_pipeline(self, request: T2sPipelineId) -> Text2SpeechConfig:
        response: Text2SpeechConfig = await self.stub.GetT2sPipeline(request)
        return response

    async def create_t2s_pipeline(self, request: Text2SpeechConfig) -> T2sPipelineId:
        response: T2sPipelineId = await self.stub.CreateT2sPipeline(request)
        return response

    async def delete_t2s_pipeline(self, request: T2sPipelineId) -> Empty:
        response: Empty = await self.stub.DeleteT2sPipeline(request)
        return response

    async def update_t2s_pipeline(self, request: Text2SpeechConfig) -> Empty:
        response: Empty = await self.stub.UpdateT2sPipeline(request)
        return response

    async def list_t2s_pipelines(self, request: ListT2sPipelinesRequest) -> ListT2sPipelinesResponse:
        response: ListT2sPipelinesResponse = await self.stub.ListT2sPipelines(request)
        return response

    async def get_service_info(self) -> T2SGetServiceInfoResponse:
        response: T2SGetServiceInfoResponse = await self.stub.GetServiceInfo(request=Empty())
        return response

    async def list_t2s_languages(self, request: ListT2sLanguagesRequest) -> ListT2sLanguagesResponse:
        response: ListT2sLanguagesResponse = await self.stub.ListT2sLanguages(request)
        return response

    async def list_t2s_domains(self, request: ListT2sDomainsRequest) -> ListT2sDomainsResponse:
        response: ListT2sDomainsResponse = await self.stub.ListT2sDomains(request)
        return response

    # region phonemizer
    async def create_custom_phonemizer(self, request: CreateCustomPhonemizerRequest) -> PhonemizerId:
        response: PhonemizerId = await self.stub.CreateCustomPhonemizer(request)
        return response

    async def delete_custom_phonemizer(self, request: PhonemizerId) -> Empty:
        response: Empty = await self.stub.DeleteCustomPhonemizer(request)
        return response

    async def update_custom_phonemizer(self, request: UpdateCustomPhonemizerRequest) -> CustomPhonemizerProto:
        response: CustomPhonemizerProto = await self.stub.UpdateCustomPhonemizer(request)
        return response

    async def list_custom_phonemizer(self, request: ListCustomPhonemizerRequest) -> ListCustomPhonemizerResponse:
        response: ListCustomPhonemizerResponse = await self.stub.ListCustomPhonemizer(request)
        return response

    # endregion phonemizer
