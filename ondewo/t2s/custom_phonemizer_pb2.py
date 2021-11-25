# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ondewo/t2s/custom_phonemizer.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='ondewo/t2s/custom_phonemizer.proto',
  package='ondewo.t2s',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\"ondewo/t2s/custom_phonemizer.proto\x12\nondewo.t2s\x1a\x1bgoogle/protobuf/empty.proto\"\x1a\n\x0cPhonemizerId\x12\n\n\x02id\x18\x01 \x01(\t\"B\n\x15\x43ustomPhonemizerProto\x12\n\n\x02id\x18\x01 \x01(\t\x12\x1d\n\x04maps\x18\x02 \x03(\x0b\x32\x0f.ondewo.t2s.Map\"+\n\x03Map\x12\x0c\n\x04word\x18\x01 \x01(\t\x12\x16\n\x0ephoneme_groups\x18\x02 \x01(\t\"V\n\x1cListCustomPhonemizerResponse\x12\x36\n\x0bphonemizers\x18\x01 \x03(\x0b\x32!.ondewo.t2s.CustomPhonemizerProto\"3\n\x1bListCustomPhonemizerRequest\x12\x14\n\x0cpipeline_ids\x18\x01 \x03(\t\"\xd8\x01\n\x1dUpdateCustomPhonemizerRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12M\n\rupdate_method\x18\x02 \x01(\x0e\x32\x36.ondewo.t2s.UpdateCustomPhonemizerRequest.UpdateMethod\x12\x1d\n\x04maps\x18\x03 \x03(\x0b\x32\x0f.ondewo.t2s.Map\"=\n\x0cUpdateMethod\x12\x0f\n\x0b\x65xtend_hard\x10\x00\x12\x0f\n\x0b\x65xtend_soft\x10\x01\x12\x0b\n\x07replace\x10\x02\"N\n\x1d\x43reateCustomPhonemizerRequest\x12\x0e\n\x06prefix\x18\x01 \x01(\t\x12\x1d\n\x04maps\x18\x02 \x03(\x0b\x32\x0f.ondewo.t2s.Map2\xef\x03\n\x11\x43ustomPhonemizers\x12T\n\x13GetCustomPhonemizer\x12\x18.ondewo.t2s.PhonemizerId\x1a!.ondewo.t2s.CustomPhonemizerProto\"\x00\x12_\n\x16\x43reateCustomPhonemizer\x12).ondewo.t2s.CreateCustomPhonemizerRequest\x1a\x18.ondewo.t2s.PhonemizerId\"\x00\x12L\n\x16\x44\x65leteCustomPhonemizer\x12\x18.ondewo.t2s.PhonemizerId\x1a\x16.google.protobuf.Empty\"\x00\x12h\n\x16UpdateCustomPhonemizer\x12).ondewo.t2s.UpdateCustomPhonemizerRequest\x1a!.ondewo.t2s.CustomPhonemizerProto\"\x00\x12k\n\x14ListCustomPhonemizer\x12\'.ondewo.t2s.ListCustomPhonemizerRequest\x1a(.ondewo.t2s.ListCustomPhonemizerResponse\"\x00\x62\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])



_UPDATECUSTOMPHONEMIZERREQUEST_UPDATEMETHOD = _descriptor.EnumDescriptor(
  name='UpdateMethod',
  full_name='ondewo.t2s.UpdateCustomPhonemizerRequest.UpdateMethod',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='extend_hard', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='extend_soft', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='replace', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=517,
  serialized_end=578,
)
_sym_db.RegisterEnumDescriptor(_UPDATECUSTOMPHONEMIZERREQUEST_UPDATEMETHOD)


_PHONEMIZERID = _descriptor.Descriptor(
  name='PhonemizerId',
  full_name='ondewo.t2s.PhonemizerId',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='ondewo.t2s.PhonemizerId.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=79,
  serialized_end=105,
)


_CUSTOMPHONEMIZERPROTO = _descriptor.Descriptor(
  name='CustomPhonemizerProto',
  full_name='ondewo.t2s.CustomPhonemizerProto',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='ondewo.t2s.CustomPhonemizerProto.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='maps', full_name='ondewo.t2s.CustomPhonemizerProto.maps', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=107,
  serialized_end=173,
)


_MAP = _descriptor.Descriptor(
  name='Map',
  full_name='ondewo.t2s.Map',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='word', full_name='ondewo.t2s.Map.word', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='phoneme_groups', full_name='ondewo.t2s.Map.phoneme_groups', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=175,
  serialized_end=218,
)


_LISTCUSTOMPHONEMIZERRESPONSE = _descriptor.Descriptor(
  name='ListCustomPhonemizerResponse',
  full_name='ondewo.t2s.ListCustomPhonemizerResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='phonemizers', full_name='ondewo.t2s.ListCustomPhonemizerResponse.phonemizers', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=220,
  serialized_end=306,
)


_LISTCUSTOMPHONEMIZERREQUEST = _descriptor.Descriptor(
  name='ListCustomPhonemizerRequest',
  full_name='ondewo.t2s.ListCustomPhonemizerRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='pipeline_ids', full_name='ondewo.t2s.ListCustomPhonemizerRequest.pipeline_ids', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=308,
  serialized_end=359,
)


_UPDATECUSTOMPHONEMIZERREQUEST = _descriptor.Descriptor(
  name='UpdateCustomPhonemizerRequest',
  full_name='ondewo.t2s.UpdateCustomPhonemizerRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='ondewo.t2s.UpdateCustomPhonemizerRequest.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='update_method', full_name='ondewo.t2s.UpdateCustomPhonemizerRequest.update_method', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='maps', full_name='ondewo.t2s.UpdateCustomPhonemizerRequest.maps', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _UPDATECUSTOMPHONEMIZERREQUEST_UPDATEMETHOD,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=362,
  serialized_end=578,
)


_CREATECUSTOMPHONEMIZERREQUEST = _descriptor.Descriptor(
  name='CreateCustomPhonemizerRequest',
  full_name='ondewo.t2s.CreateCustomPhonemizerRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='prefix', full_name='ondewo.t2s.CreateCustomPhonemizerRequest.prefix', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='maps', full_name='ondewo.t2s.CreateCustomPhonemizerRequest.maps', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=580,
  serialized_end=658,
)

_CUSTOMPHONEMIZERPROTO.fields_by_name['maps'].message_type = _MAP
_LISTCUSTOMPHONEMIZERRESPONSE.fields_by_name['phonemizers'].message_type = _CUSTOMPHONEMIZERPROTO
_UPDATECUSTOMPHONEMIZERREQUEST.fields_by_name['update_method'].enum_type = _UPDATECUSTOMPHONEMIZERREQUEST_UPDATEMETHOD
_UPDATECUSTOMPHONEMIZERREQUEST.fields_by_name['maps'].message_type = _MAP
_UPDATECUSTOMPHONEMIZERREQUEST_UPDATEMETHOD.containing_type = _UPDATECUSTOMPHONEMIZERREQUEST
_CREATECUSTOMPHONEMIZERREQUEST.fields_by_name['maps'].message_type = _MAP
DESCRIPTOR.message_types_by_name['PhonemizerId'] = _PHONEMIZERID
DESCRIPTOR.message_types_by_name['CustomPhonemizerProto'] = _CUSTOMPHONEMIZERPROTO
DESCRIPTOR.message_types_by_name['Map'] = _MAP
DESCRIPTOR.message_types_by_name['ListCustomPhonemizerResponse'] = _LISTCUSTOMPHONEMIZERRESPONSE
DESCRIPTOR.message_types_by_name['ListCustomPhonemizerRequest'] = _LISTCUSTOMPHONEMIZERREQUEST
DESCRIPTOR.message_types_by_name['UpdateCustomPhonemizerRequest'] = _UPDATECUSTOMPHONEMIZERREQUEST
DESCRIPTOR.message_types_by_name['CreateCustomPhonemizerRequest'] = _CREATECUSTOMPHONEMIZERREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

PhonemizerId = _reflection.GeneratedProtocolMessageType('PhonemizerId', (_message.Message,), {
  'DESCRIPTOR' : _PHONEMIZERID,
  '__module__' : 'ondewo.t2s.custom_phonemizer_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.t2s.PhonemizerId)
  })
_sym_db.RegisterMessage(PhonemizerId)

CustomPhonemizerProto = _reflection.GeneratedProtocolMessageType('CustomPhonemizerProto', (_message.Message,), {
  'DESCRIPTOR' : _CUSTOMPHONEMIZERPROTO,
  '__module__' : 'ondewo.t2s.custom_phonemizer_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.t2s.CustomPhonemizerProto)
  })
_sym_db.RegisterMessage(CustomPhonemizerProto)

Map = _reflection.GeneratedProtocolMessageType('Map', (_message.Message,), {
  'DESCRIPTOR' : _MAP,
  '__module__' : 'ondewo.t2s.custom_phonemizer_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.t2s.Map)
  })
_sym_db.RegisterMessage(Map)

ListCustomPhonemizerResponse = _reflection.GeneratedProtocolMessageType('ListCustomPhonemizerResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTCUSTOMPHONEMIZERRESPONSE,
  '__module__' : 'ondewo.t2s.custom_phonemizer_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.t2s.ListCustomPhonemizerResponse)
  })
_sym_db.RegisterMessage(ListCustomPhonemizerResponse)

ListCustomPhonemizerRequest = _reflection.GeneratedProtocolMessageType('ListCustomPhonemizerRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTCUSTOMPHONEMIZERREQUEST,
  '__module__' : 'ondewo.t2s.custom_phonemizer_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.t2s.ListCustomPhonemizerRequest)
  })
_sym_db.RegisterMessage(ListCustomPhonemizerRequest)

UpdateCustomPhonemizerRequest = _reflection.GeneratedProtocolMessageType('UpdateCustomPhonemizerRequest', (_message.Message,), {
  'DESCRIPTOR' : _UPDATECUSTOMPHONEMIZERREQUEST,
  '__module__' : 'ondewo.t2s.custom_phonemizer_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.t2s.UpdateCustomPhonemizerRequest)
  })
_sym_db.RegisterMessage(UpdateCustomPhonemizerRequest)

CreateCustomPhonemizerRequest = _reflection.GeneratedProtocolMessageType('CreateCustomPhonemizerRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATECUSTOMPHONEMIZERREQUEST,
  '__module__' : 'ondewo.t2s.custom_phonemizer_pb2'
  # @@protoc_insertion_point(class_scope:ondewo.t2s.CreateCustomPhonemizerRequest)
  })
_sym_db.RegisterMessage(CreateCustomPhonemizerRequest)



_CUSTOMPHONEMIZERS = _descriptor.ServiceDescriptor(
  name='CustomPhonemizers',
  full_name='ondewo.t2s.CustomPhonemizers',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=661,
  serialized_end=1156,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetCustomPhonemizer',
    full_name='ondewo.t2s.CustomPhonemizers.GetCustomPhonemizer',
    index=0,
    containing_service=None,
    input_type=_PHONEMIZERID,
    output_type=_CUSTOMPHONEMIZERPROTO,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='CreateCustomPhonemizer',
    full_name='ondewo.t2s.CustomPhonemizers.CreateCustomPhonemizer',
    index=1,
    containing_service=None,
    input_type=_CREATECUSTOMPHONEMIZERREQUEST,
    output_type=_PHONEMIZERID,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='DeleteCustomPhonemizer',
    full_name='ondewo.t2s.CustomPhonemizers.DeleteCustomPhonemizer',
    index=2,
    containing_service=None,
    input_type=_PHONEMIZERID,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='UpdateCustomPhonemizer',
    full_name='ondewo.t2s.CustomPhonemizers.UpdateCustomPhonemizer',
    index=3,
    containing_service=None,
    input_type=_UPDATECUSTOMPHONEMIZERREQUEST,
    output_type=_CUSTOMPHONEMIZERPROTO,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='ListCustomPhonemizer',
    full_name='ondewo.t2s.CustomPhonemizers.ListCustomPhonemizer',
    index=4,
    containing_service=None,
    input_type=_LISTCUSTOMPHONEMIZERREQUEST,
    output_type=_LISTCUSTOMPHONEMIZERRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_CUSTOMPHONEMIZERS)

DESCRIPTOR.services_by_name['CustomPhonemizers'] = _CUSTOMPHONEMIZERS

# @@protoc_insertion_point(module_scope)
