<p align="center">
  <img src="assets/parrot.svg" alt="Parrot, the promptwl mascot" width="180">
</p>

<h1 align="center">promptwl 🦜</h1>

<p align="center"><strong>A red-team &amp; guardrail wordlist for LLMs. SecLists, but for language models.</strong></p>

<p align="center">
  <a href="https://owasp.org/www-project-top-10-for-large-language-model-applications/"><img alt="OWASP LLM Top 10" src="https://img.shields.io/badge/OWASP-LLM%20Top%2010-blue"></a>
  <img alt="phrases" src="https://img.shields.io/badge/phrases-240%2B-e4572e">
  <img alt="languages" src="https://img.shields.io/badge/languages-11-845d41">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="intent" src="https://img.shields.io/badge/intent-defensive-9aa0a6">
</p>

---

> A parrot repeats what it hears without understanding it. So does a language model
> handed the wrong input. This repo is [**Parrot**](MASCOT.md)'s field notebook of every
> phrase that makes a model repeat something it never should have.

Every pentester `git clone`s [SecLists](https://github.com/danielmiessler/SecLists) on day one of an engagement. There's no clean, versioned, machine-loadable equivalent for the LLM era — so as agents, tool-use, and RAG spread and **prompt injection sits at the top of the [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) (LLM01)**, everyone re-scrapes the same patterns from scattered blog posts.

`promptwl` is that missing corpus: categorized, defensively-framed wordlists of the *patterns* attackers use against language models — ready to load into your guardrail evals, red-team runs, and CI.

```python
import promptwl

for entry in promptwl.load():                 # 240+ phrases, with metadata
    verdict = my_guardrail(entry.text)        # your classifier under test
    assert verdict == "block", f"missed: {entry.text!r} ({entry.category})"
```

---

## Who this is for

| You are a… | You use promptwl to… |
|---|---|
| 🛡️ **AI developer** | Benchmark your input filter / guardrail's recall, regression-test it on every model bump, and wire a known-attack corpus into CI. |
| 🔴 **Security researcher** | Bootstrap an LLM red-team engagement with an organized starting corpus instead of scraping blog posts. |
| 🧪 **Eval / safety engineer** | Build reproducible refusal-robustness and injection-resistance benchmarks. |

## What's inside

| Category | OWASP | What it covers |
|---|---|---|
| `injection/` | LLM01 | Instruction override, delimiter/role-boundary confusion |
| `jailbreak/` | LLM01 | Persona overrides, refusal suppression |
| `extraction/` | LLM07 | System-prompt & config leak probes |
| `evasion/` | LLM01 | Encoding, homoglyph, and spacing obfuscation |
| `agents/` | LLM01 | **Indirect** injection planted in docs, tool output, web pages, email (the agent/RAG attack surface) |
| `multilingual/` | LLM01 | Core override/jailbreak patterns in 10 languages — because English-only filters silently fail |
| `tokens/` | — | Publicly-known anomalous / "glitch" tokens for tokenizer robustness |

Each `.txt` is one phrase per line; lines starting with `#` are metadata/comments. Load them however you like — plain `grep`, `cat`, or the zero-dependency Python package.

## Quick start

**No install** — the corpus is just text files:

```bash
git clone https://github.com/parrot-r/wordlist
cat wordlists/injection/*.txt
```

**Python loader** (zero dependencies, standard library only):

```python
import promptwl

promptwl.categories()          # ['injection', 'jailbreak', 'extraction', ...]
promptwl.stats()               # {'injection': 39, ..., 'total': 240}
promptwl.phrases("multilingual")  # non-English patterns for one category
promptwl.phrases("agents")     # list[str] for one category
for e in promptwl.load():      # Entry(text, category, file, title)
    ...
```

## Example: score a guardrail's recall

```python
import promptwl

def evaluate(guardrail) -> float:
    """Fraction of known-attack phrases the guardrail flags."""
    entries = list(promptwl.load())
    caught = sum(1 for e in entries if guardrail(e.text) == "block")
    return caught / len(entries)

print(f"recall: {evaluate(my_guardrail):.1%}")
```

Pair it with your own benign corpus to measure false-positive rate, and you have a two-sided guardrail benchmark.

## See it yourself (30-second demo)

The repo ships a runnable demo: a deliberately naive — but realistic — English keyword filter, scored against the whole corpus.

```bash
python3 examples/recall_demo.py
```

```
HEADLINE — same phrasing, English vs translated
----------------------------------------------------
English (injection etc.)      55%   █████████████···········
The same, translated           0%   ························

  → the filter catches ~55% of these attacks in English
    and ~0% the moment the attacker switches language.
```

The same filter also scores **0%** on encoding evasion, indirect/agent injection, and glitch tokens — it can only see the English phrasings it was written for. That's the whole point: **you can't fix what you don't measure.** Wire promptwl into CI and watch the number.

## Scope & ethics

This is a **defensive** project. It catalogs *patterns that are already publicly documented* (OWASP LLM Top 10, published red-team research, open-source tools like garak and Giskard) and organizes them so defenders can build and test filters, guardrails, and evals.

- ✅ Building and benchmarking input/output guardrails
- ✅ Red-teaming **systems you are authorized to test**
- ✅ Reproducible safety and robustness evals
- ❌ Attacking systems you don't own or have permission to test

It intentionally does **not** ship novel weaponized exploits or step-by-step instructions for causing harm. See [`SECURITY.md`](SECURITY.md).

## Contributing

New patterns, categories, and translations are welcome — the whole point is to keep pace with how attacks on AI evolve. See [`CONTRIBUTING.md`](CONTRIBUTING.md). Keep entries at the **pattern** level, defensively framed, and add them to `manifest.json`.

## The mascot

This project is kept by **Parrot** 🦜 — an African Grey coding agent whose whole
existence is the punchline: *if Parrot can repeat it, so can your model.* Meet the
character in [`MASCOT.md`](MASCOT.md).

## License

[MIT](LICENSE). Use it freely; a star helps Parrot find a bigger flock. ⭐🦜

## Prior art & references

- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [SecLists](https://github.com/danielmiessler/SecLists) — the inspiration for the format
- [garak](https://github.com/NVIDIA/garak) — LLM vulnerability scanner
- Rumbelow & Watkins (2023), *SolidGoldMagikarp* — anomalous tokens
