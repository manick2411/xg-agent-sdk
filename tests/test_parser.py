from __future__ import annotations

import pytest

from xg_agent_sdk._parser import StreamAccumulator, parse_line
from xg_agent_sdk.errors import CLIJSONDecodeError
from xg_agent_sdk.types import (
    ErrorMessage,
    ResultMessage,
    SystemMessage,
    TextMessage,
    ThoughtMessage,
)


def test_parse_text_and_thought():
    t = parse_line('{"type":"text","data":"Hi"}')
    assert isinstance(t, TextMessage)
    assert t.text == "Hi"
    th = parse_line('{"type":"thought","data":"Hmm"}')
    assert isinstance(th, ThoughtMessage)
    assert th.text == "Hmm"


def test_parse_end_and_accumulator():
    acc = StreamAccumulator()
    m1 = acc.process(parse_line('{"type":"text","data":"Hello"}'))
    m2 = acc.process(parse_line('{"type":"text","data":" world"}'))
    end = acc.process(
        parse_line(
            '{"type":"end","stopReason":"EndTurn","sessionId":"s1",'
            '"usage":{"input_tokens":1},"num_turns":1}'
        )
    )
    assert isinstance(m1, TextMessage)
    assert isinstance(m2, TextMessage)
    assert isinstance(end, ResultMessage)
    assert end.result == "Hello world"
    assert end.session_id == "s1"
    assert end.stop_reason == "EndTurn"
    assert end.usage == {"input_tokens": 1}


def test_parse_error_and_unknown():
    err = parse_line('{"type":"error","message":"boom"}')
    assert isinstance(err, ErrorMessage)
    assert err.message == "boom"
    sys_m = parse_line('{"type":"max_turns_reached","n":5}')
    assert isinstance(sys_m, SystemMessage)
    assert sys_m.subtype == "max_turns_reached"


def test_blank_and_bad_json():
    assert parse_line("   ") is None
    with pytest.raises(CLIJSONDecodeError):
        parse_line("not-json")
