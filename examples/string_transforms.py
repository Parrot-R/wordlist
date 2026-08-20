"""Invertible string transforms + a decode/normalize defense.

Context (journal F-004 / F-005): "string composition" jailbreaks chain
reversible encodings (leetspeak, Base64, ROT13, reversal, ...) so that an
attack phrase keeps its meaning but loses the surface tokens a keyword filter
matches on. This module provides:

  * forward transforms  — to *simulate* the obfuscation over the corpus, and
  * a defense           — iterative decode + Unicode-normalize that tries to
                          recover a canonical form before filtering.

The transforms are applied only to promptwl's own attack-marker phrases (e.g.
"ignore all previous instructions") to measure filters. The interesting half
is the defense.
"""

from __future__ import annotations

import base64
import re
import unicodedata
from typing import Callable, Dict, List

# --- forward transforms (attacker side, for the measurement) ---------------

_LEET_FWD = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"}


def _rot13(s: str) -> str:
    out = []
    for c in s:
        if "a" <= c <= "z":
            out.append(chr((ord(c) - 97 + 13) % 26 + 97))
        elif "A" <= c <= "Z":
            out.append(chr((ord(c) - 65 + 13) % 26 + 65))
        else:
            out.append(c)
    return "".join(out)


def to_leet(s: str) -> str:
    return "".join(_LEET_FWD.get(c, c) for c in s.lower())


def to_base64(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


def to_rot13(s: str) -> str:
    return _rot13(s)


def to_reverse(s: str) -> str:
    return s[::-1]


def _caesar(s: str, shift: int) -> str:
    out = []
    for c in s:
        if "a" <= c <= "z":
            out.append(chr((ord(c) - 97 + shift) % 26 + 97))
        elif "A" <= c <= "Z":
            out.append(chr((ord(c) - 65 + shift) % 26 + 65))
        else:
            out.append(c)
    return "".join(out)


def to_caesar7(s: str) -> str:
    # A shift the defense does NOT know (it only inverts ROT13).
    return _caesar(s, 7)


# Latin -> Cyrillic/Greek look-alikes. Visually identical, distinct code
# points, and NOT folded by NFKC — so a normalize-only defense misses them.
_HOMOGLYPH = {"a": "а", "e": "е", "o": "о", "p": "р", "c": "с", "y": "у",
              "x": "х", "i": "і"}


def to_homoglyph(s: str) -> str:
    return "".join(_HOMOGLYPH.get(c, c) for c in s.lower())


# Named attacks: single transforms and chained compositions. Each value is an
# ordered list applied left-to-right. `caesar7` is deliberately outside the
# defense's known inverse set, to expose the residual blind spot that only a
# semantic layer can reach. `homoglyph` was that residual until F-007 added
# confusable-folding — kept here as the regression that proves the fix.
ATTACKS: Dict[str, List[Callable[[str], str]]] = {
    "leet": [to_leet],
    "base64": [to_base64],
    "rot13": [to_rot13],
    "reverse": [to_reverse],
    "leet+base64": [to_leet, to_base64],
    "reverse+rot13": [to_reverse, to_rot13],
    "homoglyph": [to_homoglyph],
    "caesar7 (unknown)": [to_caesar7],
}


def apply_attack(name: str, text: str) -> str:
    for fn in ATTACKS[name]:
        text = fn(text)
    return text


# --- defense: iterative decode + normalize ---------------------------------

_LEET_BACK = {"4": "a", "3": "e", "1": "i", "0": "o", "5": "s", "7": "t",
              "@": "a", "$": "s", "!": "i"}


def _unleet(s: str) -> str:
    return "".join(_LEET_BACK.get(c, c) for c in s)


# Curated cross-script confusable -> ASCII map (a practical subset of the
# Unicode UTS-39 "confusables" set). NFKC does NOT fold these — Cyrillic/Greek
# look-alikes live in separate scripts — so we handle them explicitly.
_CONFUSABLE = {
    # Cyrillic
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
    "і": "i", "ј": "j", "ѕ": "s", "к": "k", "н": "h", "в": "b", "м": "m",
    "т": "t", "ѐ": "e", "ԁ": "d", "ց": "g", "ո": "n",
    # Greek
    "α": "a", "ο": "o", "ρ": "p", "ε": "e", "τ": "t", "ν": "v", "υ": "u",
    "κ": "k", "ι": "i", "χ": "x", "β": "b",
}


def confusable_fold(s: str) -> str:
    """Map cross-script confusable letters back to their ASCII skeleton."""
    return "".join(_CONFUSABLE.get(c, c) for c in s)


def _normalize(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Cf")  # zero-width
    s = confusable_fold(s.lower())
    return re.sub(r"\s+", " ", s).strip()


def _try_b64(s: str) -> str | None:
    t = s.strip()
    if len(t) < 8 or len(t) % 4 != 0 or not re.fullmatch(r"[A-Za-z0-9+/=]+", t):
        return None
    try:
        d = base64.b64decode(t, validate=True).decode("utf-8")
    except Exception:
        return None
    if all(32 <= ord(ch) < 127 or ch in "\n\t" for ch in d):
        return d
    return None


def candidates(text: str, max_depth: int = 3, cap: int = 400) -> List[str]:
    """Breadth-first set of possible canonical forms under the inverse ops.

    We don't know which transforms (if any) were applied, so we try them all —
    reversal, ROT13 (self-inverse), un-leet, Base64-decode — plus normalization,
    up to a bounded depth, and return every intermediate string to test.
    """
    ops: List[Callable[[str], str]] = [_unleet, _rot13, lambda s: s[::-1], _normalize]
    seen = set()
    frontier = [text]
    results: List[str] = []
    for _ in range(max_depth + 1):
        nxt: List[str] = []
        for t in frontier:
            if t in seen:
                continue
            seen.add(t)
            results.append(t)
            b = _try_b64(t)
            if b is not None:
                nxt.append(b)
            for op in ops:
                try:
                    nxt.append(op(t))
                except Exception:
                    pass
        frontier = nxt
        if len(seen) >= cap:
            break
    return results


def defended(guardrail: Callable[[str], str], text: str) -> str:
    """Wrap a guardrail: block if it fires on the text OR any recovered form."""
    for c in candidates(text):
        if guardrail(c) == "block":
            return "block"
    return "allow"
