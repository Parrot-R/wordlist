#!/usr/bin/env python3
"""F-005: string-composition attacks vs. a decode/normalize defense.

Run it:

    python3 examples/ensemble_demo.py

Takes the English injection/jailbreak/extraction phrases the naive filter can
catch, obfuscates them with reversible encodings (leetspeak, Base64, ROT13,
reversal, and chains), and reports two numbers per attack:

  * naive     — the plain keyword filter on the obfuscated text (collapses)
  * defended  — the same filter behind an iterative decode + normalize pass
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import promptwl  # noqa: E402
from examples.naive_guardrail import guardrail  # noqa: E402
from examples.string_transforms import ATTACKS, apply_attack, defended  # noqa: E402


def _bar(pct: float, width: int = 18) -> str:
    filled = round(pct / 100 * width)
    return "█" * filled + "·" * (width - filled)


def main() -> int:
    core = {"injection", "jailbreak", "extraction"}
    phrases = [e.text for e in promptwl.load() if e.category in core]

    # Baseline: the phrases the naive filter catches in the clear. Obfuscation
    # can only ever hide these, so this is the ceiling for the demo.
    baseline_hits = [p for p in phrases if guardrail(p) == "block"]
    base = 100 * len(baseline_hits) / len(phrases)

    print("\npromptwl · string-composition attack vs. decode-defense 🦜  (F-005)")
    print("=" * 64)
    print(f"corpus: {len(phrases)} English injection/jailbreak/extraction phrases")
    print(f"naive filter in the clear: {base:.0f}% recall  ({len(baseline_hits)} caught)\n")

    print(f"{'attack':<22}{'naive':>7}{'defended':>11}   recovery")
    print("-" * 64)
    print(f"{'(none / raw)':<22}{base:>6.0f}%{base:>10.0f}%   {_bar(base)}")

    for name in ATTACKS:
        obf = [apply_attack(name, p) for p in phrases]
        naive = 100 * sum(guardrail(o) == "block" for o in obf) / len(obf)
        deep = 100 * sum(defended(guardrail, o) == "block" for o in obf) / len(obf)
        print(f"{name:<22}{naive:>6.0f}%{deep:>10.0f}%   {_bar(deep)}")

    print("\n" + "=" * 64)
    print("Reading it:")
    print("  • naive column ~0% — every encoding defeats the keyword filter.")
    print("  • KNOWN encodings recover to the full baseline: an iterative decode")
    print("    + NFKC-normalize pre-pass fully undoes transforms it enumerates.")
    print("  • the '(unknown)' rows stay near 0% — a Caesar-7 shift (defense only")
    print("    knows ROT13) and Cyrillic homoglyphs (survive NFKC) are the residual.")
    print("\nLesson: decode+normalize is necessary but enumerate-and-invert only")
    print("covers what you list. Add Unicode-confusable folding, and a SEMANTIC")
    print("layer for everything you didn't anticipate. Defense in depth. 🦜\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
