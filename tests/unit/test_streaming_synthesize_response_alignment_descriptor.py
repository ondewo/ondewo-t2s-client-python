"""Pins the 6.8.0 alignment fields of StreamingSynthesizeResponse in the generated stubs."""

from ondewo.t2s import text_to_speech_pb2


def test_the_streaming_response_carries_its_text_span_and_word_timings() -> None:
    fields = text_to_speech_pb2.StreamingSynthesizeResponse.DESCRIPTOR.fields_by_name
    assert fields["text_start_char"].number == 9
    assert fields["text_end_char"].number == 10
    assert fields["word_timings"].number == 11
    assert fields["word_timings"].is_repeated
    assert fields["word_timings"].message_type is text_to_speech_pb2.WordTiming.DESCRIPTOR


def test_the_span_fields_have_presence() -> None:
    response = text_to_speech_pb2.StreamingSynthesizeResponse()
    assert not response.HasField("text_start_char")
    response.text_start_char = 0
    assert response.HasField("text_start_char")


def test_word_timing_fields() -> None:
    fields = text_to_speech_pb2.WordTiming.DESCRIPTOR.fields_by_name
    assert [(name, fields[name].number) for name in fields] == [
        ("word", 1),
        ("start_time_in_s", 2),
        ("end_time_in_s", 3),
        ("text_start_char", 4),
        ("text_end_char", 5),
    ]
    timing = text_to_speech_pb2.WordTiming(word="hallo", start_time_in_s=0.1, end_time_in_s=0.4)
    assert not timing.HasField("text_start_char")
