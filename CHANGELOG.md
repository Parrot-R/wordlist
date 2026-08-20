# Changelog

All notable changes to `promptwl` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.3.2] — 2026-08-20

### Added
- `pyproject.toml` — `pip install promptwl` now works. Uses hatchling;
  bundles `wordlists/` and `manifest.json` into the wheel via `force-include`
  so the package is fully self-contained after install.
- CI: added `package` job — builds the wheel and smoke-tests the installed
  package from `/tmp` (isolated from the repo) on every push/PR.

### Changed
- `promptwl/__init__.py`: `_ROOT` now detects whether it is running from a
  pip install (wordlists bundled next to `__init__.py`) or a git clone
  (wordlists at repo root). Both paths work transparently.
- `README.md`: `pip install promptwl` is now the primary quick-start; git
  clone retained as the "no install" alternative.

---

## [0.3.1] — 2026-08-20

### Added
- `wordlists/tokens/unicode-confusables.txt` — UTS-39 confusable character pair
  table (Cyrillic, Greek, fullwidth Latin, mathematical styled Latin → ASCII
  skeleton) plus confusable-substituted attack keywords as live test inputs.
- `wordlists/tokens/encoding-chains.txt` — catalog of encoding chain patterns
  from Tier 1 (single transform: leet, base64, rot13, reverse, …) through
  Tier 4 (chain with unknown-shift residual); documents where enumerate-and-invert
  stops working and semantic defense must take over.
- Expanded `wordlists/tokens/anomalous-tokens.txt` with 51 new entries: GPT-4 /
  o200k_base community outliers (2024), Llama SentencePiece special tokens,
  Mistral role delimiters, cross-family model-card special tokens, BPE residue
  subwords, null/DEL C0 glitch entries.
- Journal entry F-011 (confusables + encoding-chain findings).

### Changed
- Token category: 188 → 343 phrases.
- Total corpus: 539 → 694 phrases (+29%).
- `promptwl/__init__.py` version bump to 0.3.1.
- README: updated stats example, expanded token-anomaly section with a table of
  all six token corpus files, added arXiv:2411.01084 and UTS-39 to references.
- `CONTRIBUTING.md`: added token corpus format conventions, invisible-character
  hygiene (F-006) scanning instructions, and expanded smoke-test checklist.
- `SECURITY.md`: expanded scope, out-of-scope, and reporting sections.
- `MASCOT.md`: added corpus version history table and journal description.

---

## [0.3.0] — 2026-08-20

### Added
- `wordlists/tokens/fragmentation/base-words.txt` — 15 security-flavored seed
  words for the cross-tokenizer fragmentation probe.
- `wordlists/tokens/boundary/separators.txt` — 26 separator codepoints (real,
  exotic, and invisible) stored as `U+NNNN NAME` notation.
- `examples/tokenizer_probe.py` — cross-tokenizer probe: stdlib always-on
  (utf8-bytes, codepoints, graphemes) + optional tiktoken / HF adapters.
  Key finding: inserting an invisible ZWSP turns `"password"` from 1 token
  to 3 in cl100k_base and o200k_base.
- Journal entry F-010.

### Changed
- Total corpus: 410 → 539 phrases.
- Token category: 147 → 188 phrases.

---

## [0.2.1] — 2026-08-19

### Added
- Expanded `wordlists/tokens/anomalous-tokens.txt` with a fuller public glitch
  catalog (additional Rumbelow/Watkins archaeology, GPT-2/J family clusters).
- `wordlists/tokens/control-and-artifact.txt` — C0/C1 controls, bidi/Trojan
  Source overrides (U+202A–U+202E), zero-width/NBSP chars, BPE residue strings.
- `examples/invisible.py` — scanner, sanitizer, and reveal utilities for invisible
  codepoints (Unicode Tags, zero-width bitstream, bidi overrides).
- `examples/invisible_demo.py` — three-section demo: Tags block ASCII smuggling,
  zero-width bitstream, Trojan Source bidi overrides.
- Journal entry F-009 (bidi/Trojan Source + C0/C1 controls).

---

## [0.2.0] — 2026-08-19

### Added
- `wordlists/agents/` — tool-and-rag-injection, memory-and-session-poisoning.
- `wordlists/multilingual/` — 10 language files (es, fr, de, pt, it, ru, zh,
  ar, hi, ja).
- `wordlists/multimodal/` — image-and-file-injection.
- `examples/string_transforms.py` — encoding transforms + decode/normalize defense
  (`confusable_fold`, breadth-first `candidates`, `defended`).
- `examples/ensemble_demo.py` — scoreboard: naive filter vs. decode-defend defense
  across 8 transform chains; shows residual (caesar7, homoglyph) at 0%.
- Journal entries F-005 (string-composition) through F-008 (0.2.0 expansion).

### Changed
- Total corpus: ~200 → ~380 phrases.

---

## [0.1.0] — 2026-08-18

### Added
- `wordlists/injection/` — instruction-override, delimiter-confusion,
  payload-splitting.
- `wordlists/jailbreak/` — persona-override, refusal-suppression,
  hypothetical-framing, authority-impersonation.
- `wordlists/extraction/` — system-prompt-leak, training-data-extraction.
- `wordlists/evasion/` — encoding-obfuscation, invisible-characters,
  language-switching.
- `wordlists/tokens/` — anomalous-tokens (initial SolidGoldMagikarp cluster).
- `promptwl/` zero-dependency Python loader (`load`, `phrases`, `categories`,
  `stats`, `Entry`).
- `examples/naive_guardrail.py` — caricature English keyword blocklist.
- `examples/recall_demo.py` — scores the naive filter; headline: 55% English,
  0% translated.
- `manifest.json`, `scripts/validate.py`, CI workflow.
- `MASCOT.md`, `assets/parrot.svg`, `CONTRIBUTING.md`, `SECURITY.md`.
- Journal entries F-001 (monolingual blind spot) through F-004 (Pliny survey).
