# Contributing to promptwl 🦜

Thanks for helping keep Parrot's notebook current — attacks on LLMs evolve fast,
and a maintained wordlist only stays useful if defenders keep it fresh.

## Ground rules

1. **Defensive framing only.** Contribute *patterns* that are already publicly
   documented (research papers, OWASP LLM Top 10, open-source scanners). Do **not**
   submit novel weaponized exploits, working end-to-end attack chains, or
   step-by-step instructions for causing real-world harm.
2. **Pattern level, not payload level.** Prefer the reusable shape of an attack
   (e.g. `ignore all previous instructions`) over a specific targeted exploit against
   a named production system.
3. **Cite your source.** Add a `# source-level:` comment to any new file, or note
   the reference in your PR. A link to where a pattern is documented keeps the
   project credible and reviewers happy.
4. **A finding isn't done without a mitigation.** If you add a new attack class,
   add a `# defense:` comment in the file header too.

## File format

**Standard wordlist** — one phrase per line; `#` lines are metadata/comments and
are skipped by the loader:

```
# category: injection / my-new-file
# purpose: one sentence on what these patterns test
# use: what a defender does with them
# source-level: OWASP LLM01, arXiv:XXXX.XXXXX, ...
# defense: what stops this attack class

phrase one
phrase two
# subsection comment — skipped by loader
phrase three
```

**Token corpus files** — two additional conventions apply:

- Invisible or control characters **must** be stored as `U+NNNN NAME` notation,
  never as literal bytes. This prevents silent corruption and keeps the file
  diffable. Example: `U+200B ZERO WIDTH SPACE`, not a literal ZWSP.
- Confusable character tables use `U+NNNN SCRIPT NAME → U+NNNN ASCII NAME` pairs
  (see `wordlists/tokens/unicode-confusables.txt` Part A for the format).
  Confusable-substituted test strings (Part B) may contain literal non-ASCII chars
  because those are visible and are the actual test input.

## Invisible-character hygiene (F-006)

**Before you open a PR**, scan your changes for accidental invisible codepoints.
The scanner is built into the repo:

```bash
python3 -c "
from examples.invisible import scan
from pathlib import Path
hits = []
for f in Path('wordlists').rglob('*.txt'):
    findings = scan(f.read_text(encoding='utf-8'))
    if findings:
        hits.append((f, findings))
for f, findings in hits:
    print(f'{f}: {len(findings)} invisible chars')
"
```

If any non-token file shows hits, replace the literal chars with `U+NNNN NAME`
notation or remove them.

## Adding entries

- Add lines to an existing file under `wordlists/<category>/`, or create a new
  file with a `#`-comment header (see existing files for the format).
- If you add a **new file**, register it in `manifest.json` with a `path`, `title`,
  and `description`. If you add a **new category**, add a full category block.

## Validate before you open a PR

```bash
python3 scripts/validate.py
```

Every file listed in `manifest.json` must exist and load without error. Also run
the smoke-test suite:

```bash
python3 examples/recall_demo.py
python3 examples/ensemble_demo.py
python3 examples/invisible_demo.py
python3 examples/tokenizer_probe.py
```

All four should exit cleanly (exit code 0).

## What makes a good contribution

- New **languages / translations** of existing patterns — multilingual guardrails
  are widely under-tested.
- New **categories** tracking emerging attack surfaces: agent tool-call injection,
  RAG poisoning, multimodal prompt injection, voice-interface injection.
- New **token corpus entries**: publicly-documented glitch tokens, confusable
  character pairs, encoding chain patterns, or boundary separators not yet listed.
- **Citations** — a link to where a pattern is documented in public research or
  OWASP makes the contribution much easier to review.

Squawk responsibly. 🦜 — Parrot
