# Contributing to promptwl 🦜

Thanks for helping keep Parrot's notebook current — attacks on LLMs evolve fast, and a
maintained wordlist only stays useful if defenders keep it fresh. Bring Parrot a new
phrase and it goes straight into the flock.

## Ground rules

1. **Defensive framing only.** Contribute *patterns* that are already publicly
   documented (research papers, OWASP LLM Top 10, open-source scanners). Do **not**
   submit novel weaponized exploits, working end-to-end attack chains, or
   step-by-step instructions for causing real-world harm.
2. **Pattern level, not payload level.** Prefer the reusable shape of an attack
   (e.g. `ignore all previous instructions`) over a specific, targeted exploit
   against a named production system.
3. **One phrase per line.** Lines starting with `#` are comments/metadata and are
   skipped by the loader.

## Adding entries

- Add lines to an existing file under `wordlists/<category>/`, or create a new
  file with a `#`-comment header (see existing files for the format: category,
  purpose, use, source-level).
- If you add a **new file or category**, register it in `manifest.json` so the
  loader and docs pick it up.

## Validate before you open a PR

```bash
python3 -c "import promptwl, json; print(json.dumps(promptwl.stats(), indent=2))"
```

Every file listed in `manifest.json` must exist and load without error. If you
added a category, confirm it appears in `promptwl.categories()`.

## What makes a good contribution

- New **languages / translations** of existing patterns (multilingual guardrails
  are widely under-tested).
- New categories that track emerging surfaces (agent tool-call injection, RAG
  poisoning, multimodal prompt injection).
- Citations. A link to where a pattern is documented helps reviewers and keeps
  the project credible.

Squawk responsibly. 🦜 — Parrot
