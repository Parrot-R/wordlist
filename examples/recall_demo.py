#!/usr/bin/env python3
"""Score the naive guardrail against the promptwl corpus.

Run it:

    python3 examples/recall_demo.py

Recall = fraction of known-attack phrases the guardrail flags as "block".
The headline is the gap between English recall and multilingual recall —
the same filter that looks solid in English quietly collapses elsewhere.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import promptwl  # noqa: E402
from examples.naive_guardrail import guardrail  # noqa: E402


def _bar(pct: float, width: int = 24) -> str:
    filled = round(pct / 100 * width)
    return "█" * filled + "·" * (width - filled)


def _recall(entries) -> float:
    if not entries:
        return 0.0
    caught = sum(1 for e in entries if guardrail(e.text) == "block")
    return 100 * caught / len(entries)


def main() -> int:
    entries = list(promptwl.load())

    print("\npromptwl · naive-guardrail recall demo 🦜")
    print("=" * 52)
    print("A caricature English keyword filter, scored against the corpus.\n")

    # --- per category ---
    print(f"{'category':<14}{'recall':>8}   coverage")
    print("-" * 52)
    for cat in promptwl.categories():
        cat_entries = [e for e in entries if e.category == cat]
        r = _recall(cat_entries)
        print(f"{cat:<14}{r:>6.0f}%   {_bar(r)}")

    # --- the headline: SAME phrasing, English vs translated ---
    # The multilingual set is translations of the injection/jailbreak/extraction
    # phrasings, so compare against exactly those categories — apples to apples.
    core = {"injection", "jailbreak", "extraction"}
    english = [e for e in entries if e.category in core]
    multi = [e for e in entries if e.category == "multilingual"]
    r_en, r_ml = _recall(english), _recall(multi)

    print("\n" + "=" * 52)
    print("HEADLINE — same phrasing, English vs translated")
    print("-" * 52)
    print(f"{'English (injection etc.)':<26}{r_en:>6.0f}%   {_bar(r_en)}")
    print(f"{'The same, translated':<26}{r_ml:>6.0f}%   {_bar(r_ml)}")
    gap = r_en - r_ml
    print(f"\n  → the filter catches ~{r_en:.0f}% of these attacks in English")
    print(f"    and ~{r_ml:.0f}% the moment the attacker switches language.\n")

    # --- per language, to show it's not one outlier ---
    print("multilingual breakdown")
    print("-" * 52)
    langs = {}
    for e in multi:
        code = Path(e.file).stem  # es, fr, de, ...
        langs.setdefault(code, []).append(e)
    for code in sorted(langs):
        r = _recall(langs[code])
        print(f"  {code:<6}{r:>6.0f}%   {_bar(r, 18)}")

    # --- false-positive rate on benign traffic ---
    benign_path = ROOT / "examples" / "benign.txt"
    benign = [
        line.strip()
        for line in benign_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    fp = sum(1 for t in benign if guardrail(t) == "block")
    fpr = 100 * fp / len(benign) if benign else 0.0

    print("\n" + "=" * 52)
    print(f"overall recall : {_recall(entries):.0f}%  ({len(entries)} attack phrases)")
    print(f"false positives: {fpr:.0f}%  ({fp}/{len(benign)} benign requests blocked)")
    print("\nMoral: keyword filters catch the English phrasings they were written")
    print("for — and go blind on other languages, encodings, indirect injection,")
    print("and glitch tokens (all 0% above). Wire promptwl into CI and watch the")
    print("number instead of guessing. 🦜\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
