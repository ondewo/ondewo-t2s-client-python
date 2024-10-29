# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ondewo/t2s/text-to-speech.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fondewo/t2s/text-to-speech.proto\x12\nondewo.t2s\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1cgoogle/protobuf/struct.proto\"\x81\x01\n\x11SynthesizeRequest\x12\x0c\n\x04text\x18\x01 \x01(\t\x12)\n\x06\x63onfig\x18\x02 \x01(\x0b\x32\x19.ondewo.t2s.RequestConfig\x12\x33\n\x12t2s_service_config\x18\x03 \x01(\x0b\x32\x17.google.protobuf.Struct\"N\n\x16\x42\x61tchSynthesizeRequest\x12\x34\n\rbatch_request\x18\x01 \x03(\x0b\x32\x1d.ondewo.t2s.SynthesizeRequest\"Q\n\x17\x42\x61tchSynthesizeResponse\x12\x36\n\x0e\x62\x61tch_response\x18\x01 \x03(\x0b\x32\x1e.ondewo.t2s.SynthesizeResponse\"\xf3\x02\n\rRequestConfig\x12\x17\n\x0ft2s_pipeline_id\x18\x01 \x01(\t\x12\x16\n\x0clength_scale\x18\x02 \x01(\x02H\x00\x12\x15\n\x0bnoise_scale\x18\x03 \x01(\x02H\x01\x12\x15\n\x0bsample_rate\x18\x04 \x01(\x05H\x02\x12\x1e\n\x03pcm\x18\x05 \x01(\x0e\x32\x0f.ondewo.t2s.PcmH\x03\x12/\n\x0c\x61udio_format\x18\x06 \x01(\x0e\x32\x17.ondewo.t2s.AudioFormatH\x04\x12\x13\n\tuse_cache\x18\x07 \x01(\x08H\x05\x12\x14\n\nnormalizer\x18\x08 \x01(\tH\x06\x42\x14\n\x12oneof_length_scaleB\x13\n\x11oneof_noise_scaleB\x13\n\x11oneof_sample_rateB\x0b\n\toneof_PcmB\x13\n\x11oneof_AudioFormatB\x11\n\x0foneof_use_cacheB\x12\n\x10oneof_normalizer\"\xb8\x01\n\x12SynthesizeResponse\x12\x12\n\naudio_uuid\x18\x01 \x01(\t\x12\r\n\x05\x61udio\x18\x02 \x01(\x0c\x12\x17\n\x0fgeneration_time\x18\x03 \x01(\x02\x12\x14\n\x0c\x61udio_length\x18\x04 \x01(\x02\x12\x0c\n\x04text\x18\x05 \x01(\t\x12)\n\x06\x63onfig\x18\x06 \x01(\x0b\x32\x19.ondewo.t2s.RequestConfig\x12\x17\n\x0fnormalized_text\x18\x07 \x01(\t\"=\n\x14NormalizeTextRequest\x12\x17\n\x0ft2s_pipeline_id\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\"0\n\x15NormalizeTextResponse\x12\x17\n\x0fnormalized_text\x18\x01 \x01(\t\",\n\x19T2SGetServiceInfoResponse\x12\x0f\n\x07version\x18\x01 \x01(\t\"\x84\x01\n\x17ListT2sPipelinesRequest\x12\x11\n\tlanguages\x18\x01 \x03(\t\x12\x15\n\rspeaker_sexes\x18\x02 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x03 \x03(\t\x12\x15\n\rspeaker_names\x18\x04 \x03(\t\x12\x0f\n\x07\x64omains\x18\x05 \x03(\t\"L\n\x18ListT2sPipelinesResponse\x12\x30\n\tpipelines\x18\x01 \x03(\x0b\x32\x1d.ondewo.t2s.Text2SpeechConfig\"q\n\x17ListT2sLanguagesRequest\x12\x15\n\rspeaker_sexes\x18\x01 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x02 \x03(\t\x12\x15\n\rspeaker_names\x18\x03 \x03(\t\x12\x0f\n\x07\x64omains\x18\x04 \x03(\t\"-\n\x18ListT2sLanguagesResponse\x12\x11\n\tlanguages\x18\x01 \x03(\t\"q\n\x15ListT2sDomainsRequest\x12\x15\n\rspeaker_sexes\x18\x01 \x03(\t\x12\x17\n\x0fpipeline_owners\x18\x02 \x03(\t\x12\x15\n\rspeaker_names\x18\x03 \x03(\t\x12\x11\n\tlanguages\x18\x04 \x03(\t\")\n\x16ListT2sDomainsResponse\x12\x0f\n\x07\x64omains\x18\x01 \x03(\t\"\x1b\n\rT2sPipelineId\x12\n\n\x02id\x18\x01 \x01(\t\"\xf6\x01\n\x11Text2SpeechConfig\x12\n\n\x02id\x18\x01 \x01(\t\x12/\n\x0b\x64\x65scription\x18\x02 \x01(\x0b\x32\x1a.ondewo.t2s.T2SDescription\x12\x0e\n\x06\x61\x63tive\x18\x03 \x01(\x08\x12+\n\tinference\x18\x04 \x01(\x0b\x32\x18.ondewo.t2s.T2SInference\x12\x33\n\rnormalization\x18\x05 \x01(\x0b\x32\x1c.ondewo.t2s.T2SNormalization\x12\x32\n\x0epostprocessing\x18\x06 \x01(\x0b\x32\x1a.ondewo.t2s.Postprocessing\"\x87\x01\n\x0eT2SDescription\x12\x10\n\x08language\x18\x01 \x01(\t\x12\x13\n\x0bspeaker_sex\x18\x02 \x01(\t\x12\x16\n\x0epipeline_owner\x18\x03 \x01(\t\x12\x10\n\x08\x63omments\x18\x04 \x01(\t\x12\x14\n\x0cspeaker_name\x18\x05 \x01(\t\x12\x0e\n\x06\x64omain\x18\x06 \x01(\t\"\xb6\x01\n\x0cT2SInference\x12\x0c\n\x04type\x18\x01 \x01(\t\x12;\n\x13\x63omposite_inference\x18\x02 \x01(\x0b\x32\x1e.ondewo.t2s.CompositeInference\x12\x35\n\x10single_inference\x18\x03 \x01(\x0b\x32\x1b.ondewo.t2s.SingleInference\x12$\n\x07\x63\x61\x63hing\x18\x04 \x01(\x0b\x32\x13.ondewo.t2s.Caching\"f\n\x12\x43ompositeInference\x12&\n\x08text2mel\x18\x01 \x01(\x0b\x32\x14.ondewo.t2s.Text2Mel\x12(\n\tmel2audio\x18\x02 \x01(\x0b\x32\x15.ondewo.t2s.Mel2Audio\"=\n\x0fSingleInference\x12*\n\ntext2audio\x18\x01 \x01(\x0b\x32\x16.ondewo.t2s.Text2Audio\"s\n\x08Text2Mel\x12\x0c\n\x04type\x18\x01 \x01(\t\x12%\n\x08glow_tts\x18\x02 \x01(\x0b\x32\x13.ondewo.t2s.GlowTTS\x12\x32\n\x0fglow_tts_triton\x18\x03 \x01(\x0b\x32\x19.ondewo.t2s.GlowTTSTriton\"\x96\x03\n\nText2Audio\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x1e\n\x04vits\x18\x02 \x01(\x0b\x32\x10.ondewo.t2s.Vits\x12+\n\x0bvits_triton\x18\x03 \x01(\x0b\x32\x16.ondewo.t2s.VitsTriton\x12L\n\x1d\x63loud_service_eleven_labs_t2s\x18\x04 \x01(\x0b\x32%.ondewo.t2s.CloudServiceElevenLabsT2s\x12J\n\x1c\x63loud_service_amazon_aws_t2s\x18\x05 \x01(\x0b\x32$.ondewo.t2s.CloudServiceAmazonAwsT2s\x12\x43\n\x18\x63loud_service_google_t2s\x18\x06 \x01(\x0b\x32!.ondewo.t2s.CloudServiceGoogleT2s\x12N\n\x1b\x63loud_service_microsoft_t2s\x18\x07 \x01(\x0b\x32).ondewo.t2s.CloudServiceMicrosoftAzureT2s\"\x94\x01\n\x07GlowTTS\x12\x12\n\nbatch_size\x18\x01 \x01(\x03\x12\x0f\n\x07use_gpu\x18\x02 \x01(\x08\x12\x14\n\x0clength_scale\x18\x03 \x01(\x02\x12\x13\n\x0bnoise_scale\x18\x04 \x01(\x02\x12\x0c\n\x04path\x18\x05 \x01(\t\x12\x10\n\x08\x63leaners\x18\x06 \x03(\t\x12\x19\n\x11param_config_path\x18\x07 \x01(\t\"\xe7\x01\n\rGlowTTSTriton\x12\x12\n\nbatch_size\x18\x01 \x01(\x03\x12\x14\n\x0clength_scale\x18\x02 \x01(\x02\x12\x13\n\x0bnoise_scale\x18\x03 \x01(\x02\x12\x10\n\x08\x63leaners\x18\x04 \x03(\t\x12\x17\n\x0fmax_text_length\x18\x05 \x01(\x03\x12\x19\n\x11param_config_path\x18\x06 \x01(\t\x12\x19\n\x11triton_model_name\x18\x07 \x01(\t\x12\x1a\n\x12triton_server_host\x18\x08 \x01(\t\x12\x1a\n\x12triton_server_port\x18\t \x01(\x03\"\x91\x01\n\x04Vits\x12\x12\n\nbatch_size\x18\x01 \x01(\x03\x12\x0f\n\x07use_gpu\x18\x02 \x01(\x08\x12\x14\n\x0clength_scale\x18\x03 \x01(\x02\x12\x13\n\x0bnoise_scale\x18\x04 \x01(\x02\x12\x0c\n\x04path\x18\x05 \x01(\t\x12\x10\n\x08\x63leaners\x18\x06 \x03(\t\x12\x19\n\x11param_config_path\x18\x07 \x01(\t\"\xe4\x01\n\nVitsTriton\x12\x12\n\nbatch_size\x18\x01 \x01(\x03\x12\x14\n\x0clength_scale\x18\x02 \x01(\x02\x12\x13\n\x0bnoise_scale\x18\x03 \x01(\x02\x12\x10\n\x08\x63leaners\x18\x04 \x03(\t\x12\x17\n\x0fmax_text_length\x18\x05 \x01(\x03\x12\x19\n\x11param_config_path\x18\x06 \x01(\t\x12\x19\n\x11triton_model_name\x18\x07 \x01(\t\x12\x1a\n\x12triton_server_host\x18\x08 \x01(\t\x12\x1a\n\x12triton_server_port\x18\t \x01(\x03\"\xad\x01\n\x19\x43loudServiceElevenLabsT2s\x12\x10\n\x08voice_id\x18\x01 \x01(\t\x12\x31\n\x0evoice_settings\x18\x02 \x01(\x0b\x32\x19.ondewo.t2s.VoiceSettings\x12 \n\x18\x61pply_text_normalization\x18\x04 \x01(\t\x12\x14\n\x0clength_scale\x18\x05 \x01(\x02\x12\x13\n\x0bnoise_scale\x18\x06 \x01(\x02\"f\n\rVoiceSettings\x12\x11\n\tstability\x18\x01 \x01(\x02\x12\x18\n\x10similarity_boost\x18\x02 \x01(\x02\x12\r\n\x05style\x18\x03 \x01(\x02\x12\x19\n\x11use_speaker_boost\x18\x04 \x01(\x08\">\n\x18\x43loudServiceAmazonAwsT2s\x12\x10\n\x08voice_id\x18\x01 \x01(\t\x12\x10\n\x08model_id\x18\x02 \x01(\t\"U\n\x15\x43loudServiceGoogleT2s\x12\x15\n\rspeaking_rate\x18\x01 \x01(\x02\x12\x16\n\x0evolume_gain_db\x18\x02 \x01(\x02\x12\r\n\x05pitch\x18\x03 \x01(\x02\"N\n\x1d\x43loudServiceMicrosoftAzureT2s\x12\x10\n\x08voice_id\x18\x01 \x01(\t\x12\x1b\n\x13use_default_speaker\x18\x02 \x01(\x08\"\xaa\x01\n\tMel2Audio\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x34\n\x10mb_melgan_triton\x18\x02 \x01(\x0b\x32\x1a.ondewo.t2s.MbMelganTriton\x12%\n\x08hifi_gan\x18\x03 \x01(\x0b\x32\x13.ondewo.t2s.HiFiGan\x12\x32\n\x0fhifi_gan_triton\x18\x04 \x01(\x0b\x32\x19.ondewo.t2s.HiFiGanTriton\"W\n\x07HiFiGan\x12\x0f\n\x07use_gpu\x18\x01 \x01(\x08\x12\x12\n\nbatch_size\x18\x02 \x01(\x03\x12\x13\n\x0b\x63onfig_path\x18\x03 \x01(\t\x12\x12\n\nmodel_path\x18\x04 \x01(\t\"w\n\rHiFiGanTriton\x12\x13\n\x0b\x63onfig_path\x18\x01 \x01(\t\x12\x19\n\x11triton_model_name\x18\x02 \x01(\t\x12\x1a\n\x12triton_server_host\x18\x03 \x01(\t\x12\x1a\n\x12triton_server_port\x18\x04 \x01(\x03\"\x8c\x01\n\x0eMbMelganTriton\x12\x13\n\x0b\x63onfig_path\x18\x01 \x01(\t\x12\x12\n\nstats_path\x18\x02 \x01(\t\x12\x19\n\x11triton_model_name\x18\x03 \x01(\t\x12\x1a\n\x12triton_server_host\x18\x04 \x01(\t\x12\x1a\n\x12triton_server_port\x18\x05 \x01(\x03\"\x8f\x01\n\x07\x43\x61\x63hing\x12\x0e\n\x06\x61\x63tive\x18\x01 \x01(\x08\x12\x1d\n\x15memory_cache_max_size\x18\x02 \x01(\x03\x12\x15\n\rsampling_rate\x18\x03 \x01(\x03\x12\x12\n\nload_cache\x18\x04 \x01(\x08\x12\x12\n\nsave_cache\x18\x05 \x01(\x08\x12\x16\n\x0e\x63\x61\x63he_save_dir\x18\x06 \x01(\t\"\x86\x02\n\x10T2SNormalization\x12\x10\n\x08language\x18\x01 \x01(\t\x12\x10\n\x08pipeline\x18\x02 \x03(\t\x12\x1c\n\x14\x63ustom_phonemizer_id\x18\x03 \x01(\t\x12?\n\x14\x63ustom_length_scales\x18\x04 \x01(\x0b\x32!.ondewo.t2s.T2SCustomLengthScales\x12\x17\n\x0f\x61rpabet_mapping\x18\x05 \x01(\t\x12\x17\n\x0fnumeric_mapping\x18\x06 \x01(\t\x12\x19\n\x11\x63\x61llsigns_mapping\x18\x07 \x01(\t\x12\"\n\x1aphoneme_correction_mapping\x18\x08 \x01(\t\"\xb0\x01\n\x0ePostprocessing\x12\x14\n\x0csilence_secs\x18\x01 \x01(\x02\x12\x10\n\x08pipeline\x18\x02 \x03(\t\x12$\n\x07logmmse\x18\x03 \x01(\x0b\x32\x13.ondewo.t2s.Logmnse\x12\"\n\x06wiener\x18\x04 \x01(\x0b\x32\x12.ondewo.t2s.Wiener\x12,\n\x0b\x61podization\x18\x05 \x01(\x0b\x32\x17.ondewo.t2s.Apodization\"N\n\x07Logmnse\x12\x15\n\rinitial_noise\x18\x01 \x01(\x03\x12\x13\n\x0bwindow_size\x18\x02 \x01(\x03\x12\x17\n\x0fnoise_threshold\x18\x03 \x01(\x02\"a\n\x06Wiener\x12\x11\n\tframe_len\x18\x01 \x01(\x03\x12\x11\n\tlpc_order\x18\x02 \x01(\x03\x12\x12\n\niterations\x18\x03 \x01(\x03\x12\r\n\x05\x61lpha\x18\x04 \x01(\x02\x12\x0e\n\x06thresh\x18\x05 \x01(\x02\"\'\n\x0b\x41podization\x12\x18\n\x10\x61podization_secs\x18\x01 \x01(\x02\"\xa8\x01\n\x15T2SCustomLengthScales\x12\x0c\n\x04text\x18\x01 \x01(\x02\x12\r\n\x05\x65mail\x18\x02 \x01(\x02\x12\x0b\n\x03url\x18\x03 \x01(\x02\x12\r\n\x05phone\x18\x04 \x01(\x02\x12\r\n\x05spell\x18\x05 \x01(\x02\x12\x18\n\x10spell_with_names\x18\x06 \x01(\x02\x12\x15\n\rcallsign_long\x18\x07 \x01(\x02\x12\x16\n\x0e\x63\x61llsign_short\x18\x08 \x01(\x02\"\x1a\n\x0cPhonemizerId\x12\n\n\x02id\x18\x01 \x01(\t\"B\n\x15\x43ustomPhonemizerProto\x12\n\n\x02id\x18\x01 \x01(\t\x12\x1d\n\x04maps\x18\x02 \x03(\x0b\x32\x0f.ondewo.t2s.Map\"+\n\x03Map\x12\x0c\n\x04word\x18\x01 \x01(\t\x12\x16\n\x0ephoneme_groups\x18\x02 \x01(\t\"V\n\x1cListCustomPhonemizerResponse\x12\x36\n\x0bphonemizers\x18\x01 \x03(\x0b\x32!.ondewo.t2s.CustomPhonemizerProto\"3\n\x1bListCustomPhonemizerRequest\x12\x14\n\x0cpipeline_ids\x18\x01 \x03(\t\"\xd8\x01\n\x1dUpdateCustomPhonemizerRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12M\n\rupdate_method\x18\x02 \x01(\x0e\x32\x36.ondewo.t2s.UpdateCustomPhonemizerRequest.UpdateMethod\x12\x1d\n\x04maps\x18\x03 \x03(\x0b\x32\x0f.ondewo.t2s.Map\"=\n\x0cUpdateMethod\x12\x0f\n\x0b\x65xtend_hard\x10\x00\x12\x0f\n\x0b\x65xtend_soft\x10\x01\x12\x0b\n\x07replace\x10\x02\"N\n\x1d\x43reateCustomPhonemizerRequest\x12\x0e\n\x06prefix\x18\x01 \x01(\t\x12\x1d\n\x04maps\x18\x02 \x03(\x0b\x32\x0f.ondewo.t2s.Map*X\n\x03Pcm\x12\n\n\x06PCM_16\x10\x00\x12\n\n\x06PCM_24\x10\x01\x12\n\n\x06PCM_32\x10\x02\x12\n\n\x06PCM_S8\x10\x03\x12\n\n\x06PCM_U8\x10\x04\x12\t\n\x05\x46LOAT\x10\x05\x12\n\n\x06\x44OUBLE\x10\x06*M\n\x0b\x41udioFormat\x12\x07\n\x03wav\x10\x00\x12\x08\n\x04\x66lac\x10\x01\x12\x07\n\x03\x63\x61\x66\x10\x02\x12\x07\n\x03mp3\x10\x03\x12\x07\n\x03\x61\x61\x63\x10\x04\x12\x07\n\x03ogg\x10\x05\x12\x07\n\x03wma\x10\x06\x32\xf5\n\n\x0bText2Speech\x12K\n\nSynthesize\x12\x1d.ondewo.t2s.SynthesizeRequest\x1a\x1e.ondewo.t2s.SynthesizeResponse\x12Z\n\x0f\x42\x61tchSynthesize\x12\".ondewo.t2s.BatchSynthesizeRequest\x1a#.ondewo.t2s.BatchSynthesizeResponse\x12T\n\rNormalizeText\x12 .ondewo.t2s.NormalizeTextRequest\x1a!.ondewo.t2s.NormalizeTextResponse\x12J\n\x0eGetT2sPipeline\x12\x19.ondewo.t2s.T2sPipelineId\x1a\x1d.ondewo.t2s.Text2SpeechConfig\x12M\n\x11\x43reateT2sPipeline\x12\x1d.ondewo.t2s.Text2SpeechConfig\x1a\x19.ondewo.t2s.T2sPipelineId\x12\x46\n\x11\x44\x65leteT2sPipeline\x12\x19.ondewo.t2s.T2sPipelineId\x1a\x16.google.protobuf.Empty\x12J\n\x11UpdateT2sPipeline\x12\x1d.ondewo.t2s.Text2SpeechConfig\x1a\x16.google.protobuf.Empty\x12]\n\x10ListT2sPipelines\x12#.ondewo.t2s.ListT2sPipelinesRequest\x1a$.ondewo.t2s.ListT2sPipelinesResponse\x12]\n\x10ListT2sLanguages\x12#.ondewo.t2s.ListT2sLanguagesRequest\x1a$.ondewo.t2s.ListT2sLanguagesResponse\x12W\n\x0eListT2sDomains\x12!.ondewo.t2s.ListT2sDomainsRequest\x1a\".ondewo.t2s.ListT2sDomainsResponse\x12O\n\x0eGetServiceInfo\x12\x16.google.protobuf.Empty\x1a%.ondewo.t2s.T2SGetServiceInfoResponse\x12R\n\x13GetCustomPhonemizer\x12\x18.ondewo.t2s.PhonemizerId\x1a!.ondewo.t2s.CustomPhonemizerProto\x12]\n\x16\x43reateCustomPhonemizer\x12).ondewo.t2s.CreateCustomPhonemizerRequest\x1a\x18.ondewo.t2s.PhonemizerId\x12J\n\x16\x44\x65leteCustomPhonemizer\x12\x18.ondewo.t2s.PhonemizerId\x1a\x16.google.protobuf.Empty\x12\x66\n\x16UpdateCustomPhonemizer\x12).ondewo.t2s.UpdateCustomPhonemizerRequest\x1a!.ondewo.t2s.CustomPhonemizerProto\x12i\n\x14ListCustomPhonemizer\x12\'.ondewo.t2s.ListCustomPhonemizerRequest\x1a(.ondewo.t2s.ListCustomPhonemizerResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ondewo.t2s.text_to_speech_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_PCM']._serialized_start=6311
  _globals['_PCM']._serialized_end=6399
  _globals['_AUDIOFORMAT']._serialized_start=6401
  _globals['_AUDIOFORMAT']._serialized_end=6478
  _globals['_SYNTHESIZEREQUEST']._serialized_start=107
  _globals['_SYNTHESIZEREQUEST']._serialized_end=236
  _globals['_BATCHSYNTHESIZEREQUEST']._serialized_start=238
  _globals['_BATCHSYNTHESIZEREQUEST']._serialized_end=316
  _globals['_BATCHSYNTHESIZERESPONSE']._serialized_start=318
  _globals['_BATCHSYNTHESIZERESPONSE']._serialized_end=399
  _globals['_REQUESTCONFIG']._serialized_start=402
  _globals['_REQUESTCONFIG']._serialized_end=773
  _globals['_SYNTHESIZERESPONSE']._serialized_start=776
  _globals['_SYNTHESIZERESPONSE']._serialized_end=960
  _globals['_NORMALIZETEXTREQUEST']._serialized_start=962
  _globals['_NORMALIZETEXTREQUEST']._serialized_end=1023
  _globals['_NORMALIZETEXTRESPONSE']._serialized_start=1025
  _globals['_NORMALIZETEXTRESPONSE']._serialized_end=1073
  _globals['_T2SGETSERVICEINFORESPONSE']._serialized_start=1075
  _globals['_T2SGETSERVICEINFORESPONSE']._serialized_end=1119
  _globals['_LISTT2SPIPELINESREQUEST']._serialized_start=1122
  _globals['_LISTT2SPIPELINESREQUEST']._serialized_end=1254
  _globals['_LISTT2SPIPELINESRESPONSE']._serialized_start=1256
  _globals['_LISTT2SPIPELINESRESPONSE']._serialized_end=1332
  _globals['_LISTT2SLANGUAGESREQUEST']._serialized_start=1334
  _globals['_LISTT2SLANGUAGESREQUEST']._serialized_end=1447
  _globals['_LISTT2SLANGUAGESRESPONSE']._serialized_start=1449
  _globals['_LISTT2SLANGUAGESRESPONSE']._serialized_end=1494
  _globals['_LISTT2SDOMAINSREQUEST']._serialized_start=1496
  _globals['_LISTT2SDOMAINSREQUEST']._serialized_end=1609
  _globals['_LISTT2SDOMAINSRESPONSE']._serialized_start=1611
  _globals['_LISTT2SDOMAINSRESPONSE']._serialized_end=1652
  _globals['_T2SPIPELINEID']._serialized_start=1654
  _globals['_T2SPIPELINEID']._serialized_end=1681
  _globals['_TEXT2SPEECHCONFIG']._serialized_start=1684
  _globals['_TEXT2SPEECHCONFIG']._serialized_end=1930
  _globals['_T2SDESCRIPTION']._serialized_start=1933
  _globals['_T2SDESCRIPTION']._serialized_end=2068
  _globals['_T2SINFERENCE']._serialized_start=2071
  _globals['_T2SINFERENCE']._serialized_end=2253
  _globals['_COMPOSITEINFERENCE']._serialized_start=2255
  _globals['_COMPOSITEINFERENCE']._serialized_end=2357
  _globals['_SINGLEINFERENCE']._serialized_start=2359
  _globals['_SINGLEINFERENCE']._serialized_end=2420
  _globals['_TEXT2MEL']._serialized_start=2422
  _globals['_TEXT2MEL']._serialized_end=2537
  _globals['_TEXT2AUDIO']._serialized_start=2540
  _globals['_TEXT2AUDIO']._serialized_end=2946
  _globals['_GLOWTTS']._serialized_start=2949
  _globals['_GLOWTTS']._serialized_end=3097
  _globals['_GLOWTTSTRITON']._serialized_start=3100
  _globals['_GLOWTTSTRITON']._serialized_end=3331
  _globals['_VITS']._serialized_start=3334
  _globals['_VITS']._serialized_end=3479
  _globals['_VITSTRITON']._serialized_start=3482
  _globals['_VITSTRITON']._serialized_end=3710
  _globals['_CLOUDSERVICEELEVENLABST2S']._serialized_start=3713
  _globals['_CLOUDSERVICEELEVENLABST2S']._serialized_end=3886
  _globals['_VOICESETTINGS']._serialized_start=3888
  _globals['_VOICESETTINGS']._serialized_end=3990
  _globals['_CLOUDSERVICEAMAZONAWST2S']._serialized_start=3992
  _globals['_CLOUDSERVICEAMAZONAWST2S']._serialized_end=4054
  _globals['_CLOUDSERVICEGOOGLET2S']._serialized_start=4056
  _globals['_CLOUDSERVICEGOOGLET2S']._serialized_end=4141
  _globals['_CLOUDSERVICEMICROSOFTAZURET2S']._serialized_start=4143
  _globals['_CLOUDSERVICEMICROSOFTAZURET2S']._serialized_end=4221
  _globals['_MEL2AUDIO']._serialized_start=4224
  _globals['_MEL2AUDIO']._serialized_end=4394
  _globals['_HIFIGAN']._serialized_start=4396
  _globals['_HIFIGAN']._serialized_end=4483
  _globals['_HIFIGANTRITON']._serialized_start=4485
  _globals['_HIFIGANTRITON']._serialized_end=4604
  _globals['_MBMELGANTRITON']._serialized_start=4607
  _globals['_MBMELGANTRITON']._serialized_end=4747
  _globals['_CACHING']._serialized_start=4750
  _globals['_CACHING']._serialized_end=4893
  _globals['_T2SNORMALIZATION']._serialized_start=4896
  _globals['_T2SNORMALIZATION']._serialized_end=5158
  _globals['_POSTPROCESSING']._serialized_start=5161
  _globals['_POSTPROCESSING']._serialized_end=5337
  _globals['_LOGMNSE']._serialized_start=5339
  _globals['_LOGMNSE']._serialized_end=5417
  _globals['_WIENER']._serialized_start=5419
  _globals['_WIENER']._serialized_end=5516
  _globals['_APODIZATION']._serialized_start=5518
  _globals['_APODIZATION']._serialized_end=5557
  _globals['_T2SCUSTOMLENGTHSCALES']._serialized_start=5560
  _globals['_T2SCUSTOMLENGTHSCALES']._serialized_end=5728
  _globals['_PHONEMIZERID']._serialized_start=5730
  _globals['_PHONEMIZERID']._serialized_end=5756
  _globals['_CUSTOMPHONEMIZERPROTO']._serialized_start=5758
  _globals['_CUSTOMPHONEMIZERPROTO']._serialized_end=5824
  _globals['_MAP']._serialized_start=5826
  _globals['_MAP']._serialized_end=5869
  _globals['_LISTCUSTOMPHONEMIZERRESPONSE']._serialized_start=5871
  _globals['_LISTCUSTOMPHONEMIZERRESPONSE']._serialized_end=5957
  _globals['_LISTCUSTOMPHONEMIZERREQUEST']._serialized_start=5959
  _globals['_LISTCUSTOMPHONEMIZERREQUEST']._serialized_end=6010
  _globals['_UPDATECUSTOMPHONEMIZERREQUEST']._serialized_start=6013
  _globals['_UPDATECUSTOMPHONEMIZERREQUEST']._serialized_end=6229
  _globals['_UPDATECUSTOMPHONEMIZERREQUEST_UPDATEMETHOD']._serialized_start=6168
  _globals['_UPDATECUSTOMPHONEMIZERREQUEST_UPDATEMETHOD']._serialized_end=6229
  _globals['_CREATECUSTOMPHONEMIZERREQUEST']._serialized_start=6231
  _globals['_CREATECUSTOMPHONEMIZERREQUEST']._serialized_end=6309
  _globals['_TEXT2SPEECH']._serialized_start=6481
  _globals['_TEXT2SPEECH']._serialized_end=7878
# @@protoc_insertion_point(module_scope)
