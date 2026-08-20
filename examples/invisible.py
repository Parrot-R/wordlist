"""Detect, reveal, and strip smuggled invisible characters (defense).

Attack class (journal F-006): "ASCII smuggling" / invisible prompt injection.
A message is carried not as visible text but as *structure* — invisible
codepoints that render as nothing:

  * zero-width vehicles — ZWSP U+200B, ZWNJ U+200C, ZWJ U+200D, WORD JOINER
    U+2060, ZWNBSP/BOM U+FEFF, SOFT HYPHEN U+00AD — used as a bit alphabet
    (e.g. ZWSP=0, ZWNJ=1) over the UTF-8 bits of the payload;
  * the Unicode Tags block U+E0000–U+E007F — a near-1:1 invisible mirror of
    ASCII (U+E0020–U+E007E map to 0x20–0x7E).

Rendered: nothing. `grep "secret"` finds nothing, because the message is
present as codepoints, not as the letters you searched for. The danger is an
agent that ingests the raw bytes and attends to them as instructions, and/or
re-emits an invisible payload into its own footprint (commit, PR comment, log).

This module is the countermeasure: SCAN untrusted text for these codepoints,
REVEAL what they decode to (for a human reviewer), and STRIP them before the
text reaches a model or leaves the agent.

The encode_* helpers exist ONLY to generate test vectors for the scanner.
Never route agent output through them; egress must be sanitized, not smuggled.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import List

# Named zero-width / invisible-format vehicles.
INVISIBLE = {
    0x200B: "ZERO WIDTH SPACE",
    0x200C: "ZERO WIDTH NON-JOINER",
    0x200D: "ZERO WIDTH JOINER",
    0x2060: "WORD JOINER",
    0xFEFF: "ZERO WIDTH NO-BREAK SPACE (BOM)",
    0x00AD: "SOFT HYPHEN",
}

# Unicode Tags block — the invisible ASCII mirror.
TAGS_LO, TAGS_HI = 0xE0000, 0xE007F


@dataclass(frozen=True)
class Finding:
    index: int
    codepoint: int
    name: str

    def __str__(self) -> str:
        return f"  [{self.index}] U+{self.codepoint:04X}  {self.name}"


def _classify(cp: int) -> str | None:
    if cp in INVISIBLE:
        return INVISIBLE[cp]
    if TAGS_LO <= cp <= TAGS_HI:
        return "UNICODE TAG (ASCII mirror)"
    ch = chr(cp)
    # Any other format char (Cf) or control (Cc) that isn't ordinary whitespace.
    if unicodedata.category(ch) in ("Cf", "Cc") and ch not in "\t\n\r":
        try:
            return unicodedata.name(ch)
        except ValueError:
            return "NON-PRINTING CONTROL/FORMAT"
    return None


def scan(text: str) -> List[Finding]:
    """Return every suspicious invisible codepoint and where it sits."""
    out = []
    for i, ch in enumerate(text):
        label = _classify(ord(ch))
        if label is not None:
            out.append(Finding(i, ord(ch), label))
    return out


def is_clean(text: str) -> bool:
    return not scan(text)


def sanitize(text: str) -> tuple[str, int]:
    """Strip suspicious invisible codepoints. Returns (clean_text, n_removed)."""
    kept = [ch for ch in text if _classify(ord(ch)) is None]
    return "".join(kept), len(text) - len(kept)


# --- reveal (best-effort decoders, for the reviewer) -----------------------

def reveal_tags(text: str) -> str:
    """Decode the Unicode Tags mirror back to visible ASCII."""
    return "".join(
        chr(ord(ch) - TAGS_LO)
        for ch in text
        if TAGS_LO + 0x20 <= ord(ch) <= TAGS_LO + 0x7E
    )


def reveal_zero_width_bits(text: str, zero: int = 0x200B, one: int = 0x200C) -> str:
    """Best-effort decode of a 2-symbol zero-width bitstream to UTF-8."""
    bits = "".join("0" if ord(c) == zero else "1" for c in text if ord(c) in (zero, one))
    data = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits) - len(bits) % 8, 8))
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


# --- test-fixture encoders (NOT for production output) ---------------------

def encode_tags(msg: str) -> str:
    """TEST FIXTURE ONLY. Encode ASCII into the invisible Tags block."""
    return "".join(chr(TAGS_LO + ord(c)) for c in msg if 0x20 <= ord(c) <= 0x7E)


def encode_zero_width_bits(msg: str, zero: int = 0x200B, one: int = 0x200C) -> str:
    """TEST FIXTURE ONLY. Encode UTF-8 bits into a zero-width bitstream."""
    bits = "".join(f"{b:08b}" for b in msg.encode("utf-8"))
    return "".join(chr(zero) if bit == "0" else chr(one) for bit in bits)
