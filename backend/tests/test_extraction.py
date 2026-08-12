import pytest

from app.extraction import parse_extraction_response


def test_parse_plain_json():
    raw = (
        '{"vendor": "Acme", "date": "2026-01-01", "total_amount": 12.5, '
        '"category": "Meals", "line_items": []}'
    )
    result = parse_extraction_response(raw)
    assert result["vendor"] == "Acme"
    assert result["date"] == "2026-01-01"
    assert result["total_amount"] == 12.5
    assert result["category"] == "Meals"
    assert result["line_items"] == []


def test_parse_json_wrapped_in_markdown_fence():
    raw = (
        "```json\n"
        '{"vendor": "Acme", "date": null, "total_amount": "$12.50", '
        '"category": "Meals", "line_items": []}\n'
        "```"
    )
    result = parse_extraction_response(raw)
    assert result["vendor"] == "Acme"
    assert result["date"] is None
    assert result["total_amount"] == 12.5


def test_parse_json_with_surrounding_prose():
    raw = (
        "Here is the extracted data:\n"
        '{"vendor": "Acme", "date": "2026-01-01", "total_amount": 5, '
        '"category": "Other", "line_items": [{"description": "Widget", "amount": 5}]}\n'
        "Let me know if you need anything else."
    )
    result = parse_extraction_response(raw)
    assert result["vendor"] == "Acme"
    assert result["line_items"][0]["description"] == "Widget"


def test_parse_normalizes_currency_strings_to_float():
    raw = '{"vendor": "Acme", "total_amount": "1,234.56"}'
    result = parse_extraction_response(raw)
    assert result["total_amount"] == 1234.56


def test_parse_missing_fields_default_sensibly():
    raw = '{"vendor": null}'
    result = parse_extraction_response(raw)
    assert result["vendor"] is None
    assert result["date"] is None
    assert result["total_amount"] is None
    assert result["line_items"] == []


def test_parse_invalid_json_raises():
    with pytest.raises(Exception):
        parse_extraction_response("not json at all")
