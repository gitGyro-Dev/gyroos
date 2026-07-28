from __future__ import annotations

import json
from typing import Any


def canonical_json_utf8_size(value: Any) -> int:
    """Return the UTF-8 byte size of compact, key-sorted canonical JSON."""

    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return len(encoded)
