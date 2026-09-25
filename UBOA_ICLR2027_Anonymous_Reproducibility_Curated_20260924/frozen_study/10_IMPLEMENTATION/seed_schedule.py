"""Pure SHA256 seed derivation; this module never constructs or calls an RNG."""

from __future__ import annotations

from hashlib import sha256

from protocol import MASTER_SEED


ALLOWED_STREAM_TYPES = frozenset({"outer", "inner"})


def stream_key(cell_id: str, stream_type: str, index: int) -> str:
    if not cell_id or "|" in cell_id:
        raise ValueError("invalid cell_id")
    if stream_type not in ALLOWED_STREAM_TYPES:
        raise ValueError("stream_type must be outer or inner")
    if not isinstance(index, int) or not 0 <= index < 8:
        raise ValueError("stream index must be an integer in 0..7")
    return f"{MASTER_SEED}|{cell_id}|{stream_type}|{index}"


def derive_seed(cell_id: str, stream_type: str, index: int) -> int:
    digest = sha256(stream_key(cell_id, stream_type, index).encode("utf-8")).digest()
    return int.from_bytes(digest[:16], "big", signed=False)
