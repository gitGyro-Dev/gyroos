from __future__ import annotations

from app.vnext.inspection_validation import canonical_json_utf8_size


def test_canonical_json_utf8_size_uses_compact_sorted_json() -> None:
    assert canonical_json_utf8_size({"b": 2, "a": 1}) == len(b'{"a":1,"b":2}')


def test_canonical_json_utf8_size_counts_multibyte_utf8() -> None:
    assert canonical_json_utf8_size({"label": "日本"}) == len(
        '{"label":"日本"}'.encode("utf-8")
    )


def test_canonical_json_utf8_size_is_independent_of_mapping_order() -> None:
    assert canonical_json_utf8_size({"a": 1, "b": 2}) == canonical_json_utf8_size(
        {"b": 2, "a": 1}
    )


def test_canonical_json_utf8_size_supports_sequences() -> None:
    assert canonical_json_utf8_size(["a", "b"]) == len(b'["a","b"]')
