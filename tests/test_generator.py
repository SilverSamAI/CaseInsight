import json
from caseinsight.outreach.generator import _parse_response


def test_parse_clean_json():
    subject, body = _parse_response('{"subject": "Hello", "body": "Test body"}')
    assert subject == "Hello"
    assert body == "Test body"


def test_parse_json_with_code_fences():
    text = '```json\n{"subject": "Hi", "body": "Foo"}\n```'
    subject, body = _parse_response(text)
    assert subject == "Hi"
    assert body == "Foo"


def test_parse_regex_fallback():
    text = 'Here is the output: "subject": "Subject Here", "body": "Body content"}'
    subject, body = _parse_response(text)
    assert "Subject Here" in subject
    assert "Body content" in body
