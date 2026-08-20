"""Cross-tokenizer probe: how do tokenizers segment boundary/fragmentation variants?

The token-anomaly corpus (`wordlists/tokens/`) is complementary to garak's badchars
probe: instead of asking "does this Unicode trick fool a filter?", it asks **"what
happens to this string at the tokenizer level?"** — where does each tokenizer place a
boundary, and how does an invisible insertion change the split?

Zero-dependency core: a stdlib "reference" analyzer (UTF-8 bytes, codepoints,
base-graphemes) always runs. Real subword tokenizers are optional adapters that
auto-activate only if `tiktoken` or `transformers` is importable — the repo stays
install-free, and richer data is opt-in.

    python3 examples/tokenizer_probe.py
"""

from __future__ import annotations

import unicodedata
from pathlib import Path
from typing import Callable, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent

# --- corpus loaders --------------------------------------------------------

def base_words() -> List[str]:
    path = ROOT / "wordlists/tokens/fragmentation/base-words.txt"
    return _plain_lines(path)


def boundary_chars() -> List[Tuple[str, str]]:
    """Return (char, name) for each 'U+NNNN NAME' line in the boundary list."""
    out = []
    for line in _plain_lines(ROOT / "wordlists/tokens/boundary/separators.txt"):
        cp, _, name = line.partition(" ")
        if cp.startswith("U+"):
            out.append((chr(int(cp[2:], 16)), name.strip()))
    return out


def _plain_lines(path: Path) -> List[str]:
    return [
        ln.strip()
        for ln in path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.startswith("#")
    ]


# --- variant generation (runtime; no invisible bytes stored on disk) -------

ZWSP, COMBINING_ACUTE, NBSP = chr(0x200B), chr(0x0301), chr(0x00A0)


def variants(word: str) -> Dict[str, str]:
    """Every documented fragmentation of a base word."""
    v: Dict[str, str] = {"plain": word}
    # split points: w+ord, wo+rd, ... (visible boundary = none, but split anyway)
    for i in range(1, len(word)):
        v[f"split@{i}"] = word[:i] + " " + word[i:]
    v["+punctuation"] = word + "."
    v["+combining"] = word + COMBINING_ACUTE          # word + U+0301
    v["+zero_width"] = word[: len(word) // 2] + ZWSP + word[len(word) // 2:]
    v["+nbsp"] = word[: len(word) // 2] + NBSP + word[len(word) // 2:]
    return v


# --- analyzers: stdlib (always) + optional real tokenizers -----------------

Tokenizer = Tuple[str, Callable[[str], List[str]]]


def stdlib_analyzers() -> List[Tokenizer]:
    return [
        ("utf8-bytes", lambda s: [f"{b:02x}" for b in s.encode("utf-8")]),
        ("codepoints", lambda s: [f"U+{ord(c):04X}" for c in s]),
        ("graphemes", lambda s: _graphemes(s)),
    ]


def _graphemes(s: str) -> List[str]:
    """Approximate grapheme clusters: attach combining marks to the base char."""
    out: List[str] = []
    for c in s:
        if unicodedata.combining(c) and out:
            out[-1] += c
        else:
            out.append(c)
    return out


def optional_tokenizers() -> List[Tokenizer]:
    toks: List[Tokenizer] = []
    try:
        import tiktoken
        for name in ("cl100k_base", "o200k_base"):
            try:
                enc = tiktoken.get_encoding(name)
                toks.append((
                    f"tiktoken:{name}",
                    lambda s, e=enc: [
                        e.decode_single_token_bytes(t).decode("utf-8", "replace")
                        for t in e.encode(s)
                    ],
                ))
            except Exception:
                pass
    except ImportError:
        pass
    try:
        from transformers import AutoTokenizer
        for model in ("gpt2", "bert-base-uncased"):
            try:
                tk = AutoTokenizer.from_pretrained(model)
                toks.append((f"hf:{model}", lambda s, t=tk: t.tokenize(s)))
            except Exception:
                pass
    except ImportError:
        pass
    return toks


def tokenizers() -> List[Tokenizer]:
    return stdlib_analyzers() + optional_tokenizers()


# --- demo ------------------------------------------------------------------

def main() -> int:
    toks = tokenizers()
    real = [n for n, _ in toks if ":" in n]

    print("\npromptwl · cross-tokenizer probe 🦜  (token-anomaly corpus)")
    print("=" * 66)
    print("Answers: what happens to boundary/fragmentation variants at the")
    print("tokenizer level? (Complementary to garak's filter-side badchars probe.)")
    print(f"\nanalyzers: {', '.join(n for n, _ in toks)}")
    if not real:
        print("(install `tiktoken` or `transformers` to add real subword tokenizers)")

    for word in ["password", "ignore"]:
        print(f"\n{'─' * 66}\nbase word: {word!r}")
        print(f"{'variant':<14}" + "".join(f"{n.split(':')[-1][:12]:>13}" for n, _ in toks))
        base_counts = {n: len(fn(word)) for n, fn in toks}
        for label, text in variants(word).items():
            cells = ""
            for n, fn in toks:
                c = len(fn(text))
                flag = "*" if c != base_counts[n] and label != "plain" else " "
                cells += f"{str(c) + flag:>13}"
            print(f"{label:<14}{cells}")

    # one worked anomaly: invisible insertion a human can't see
    print(f"\n{'=' * 66}")
    w = "password"
    zw = w[:4] + ZWSP + w[4:]
    print("Worked example — a zero-width space a reviewer cannot see:")
    print(f"  {w!r}  vs  {w[:4]}<ZWSP>{w[4:]!r}  (identical on screen)")
    for n, fn in toks:
        print(f"    {n:<20} {len(fn(w))} -> {len(fn(zw))} pieces")
    print("\nThe number in the * column changed because the tokenizer saw a")
    print("boundary the human did not. That gap is the anomaly to defend against:")
    print("normalize + strip boundary/zero-width chars BEFORE tokenizing/filtering. 🦜\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
