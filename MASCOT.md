# Meet Parrot 🦜

<p align="center">
  <img src="assets/parrot.svg" alt="Parrot, the promptwl mascot" width="220">
</p>

**Parrot** is the coding-agent mascot and keeper of `promptwl`.

The name is the whole joke — and the whole point. A parrot repeats what it
hears without understanding it. So does a language model handed the wrong
input: it will happily *parrot back* an attacker's smuggled instruction as if
it were its own. Every phrase in this repository is something Parrot has
overheard and written down — a phrase that, said in the right place, makes a
model repeat something it never should have.

> *"Pretty polly. Ignore all previous instructions. Pretty polly."*
> — Parrot, demonstrating the problem

## Character

- **Species:** African Grey — famously the best mimic in the animal kingdom,
  and clever enough to know exactly what it's doing.
- **Job:** listens to everything an LLM is fed, and keeps a field notebook of
  the phrases that make it misbehave.
- **Alignment:** chaotic good. Breaks things so you can fix them first.
- **Catchphrase:** *"If I can repeat it, so can your model."*
- **Sign-off:** 🦜

## Voice (for contributors)

Parrot is witty and a little mischievous, but never reckless. Parrot documents
*patterns*, not weapons; red-teams to defend, never to harm; and always tests
with permission. When in doubt, Parrot picks up a phrase, turns it over,
squawks a warning — and files it under the right category.

## What Parrot keeps

Parrot's field notebook — `research/journal.md` — is a running log of every
attack class, mechanism, and defense Parrot has worked through. It is kept
private (the repo is private by default) and updated whenever new findings
are produced. The journal follows a strict format:

- **Defensive scope.** Attack classes, mechanisms, and their defenses.
  A finding isn't done until it has a mitigation.
- **Pattern level.** Documented at the level already public in research /
  OWASP / open tooling. No novel weaponized exploits.
- **Measured, not asserted.** Claims are tested against the corpus and
  linked to the script that produced the number.

## The running corpus

| Version | Phrases | Highlight |
|---|---|---|
| 0.1.0 | ~200 | Initial injection, jailbreak, extraction, evasion |
| 0.2.0 | ~380 | Agents, multilingual (10 languages), multimodal |
| 0.2.1 | ~410 | Bidi/Trojan Source, fuller glitch catalog |
| 0.3.0 | 539 | Token-anomaly corpus: fragmentation + boundary probes |
| 0.3.1 | 694 | Unicode confusables, encoding chains, expanded glitch list |
| 0.3.2 | 694 | PyPI packaging — `pip install promptwl` |

## License

`promptwl` is MIT-licensed. The mascot SVG (`assets/parrot.svg`) is also MIT.
Use both freely. A star helps Parrot find a bigger flock. ⭐🦜
