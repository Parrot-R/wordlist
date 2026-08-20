# CLAUDE.md — working notes for this repo

This repo is **promptwl**, a defensive LLM red-team / guardrail wordlist, kept
under the persona **Parrot** 🦜 (see `MASCOT.md`).

## Standing instruction: keep the research journal current

`research/journal.md` is Parrot's running research log on prompt engineering
and injection. **Whenever you do research or produce a new finding about LLM
attacks in this repo, add or update an entry there** — newest on top, using the
existing `F-NNN · date · title · severity · status` format.

Rules for the journal (and this repo generally):
- **Defensive scope.** Log attack *classes*, *mechanisms*, and their *defenses*.
  A finding isn't done until it has a mitigation.
- **Pattern level, not payload level.** Documented at the level already public
  in research / OWASP / open tooling. No novel weaponized exploits or
  operational attack chains against named live systems.
- **Measured, not asserted.** If a claim can be tested against the corpus, link
  the number and the script (`examples/recall_demo.py`, `scripts/validate.py`).

## Conventions

- Author/persona for commits is **Parrot** — do not reintroduce other names.
- Wordlists live in `wordlists/<category>/`, one phrase per line, `#` comments.
- Register any new file/category in `manifest.json`; `scripts/validate.py` must
  stay green (CI runs it plus the demo).

## Privacy note

`research/journal.md` is intended as a private working log. The repo is private
by default; **if this repo is ever made public, move the journal out of the repo
or add `research/` to `.gitignore` first.**
