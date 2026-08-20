# Security & Responsible Use

`promptwl` is a **defensive** resource. It catalogs publicly-documented *patterns*
used in attacks against large language models so that defenders can build, test,
and benchmark guardrails, filters, and safety evaluations.

## Intended use

- Building and benchmarking input/output guardrails and classifiers.
- Red-teaming and testing **LLM systems you own or are explicitly authorized to test.**
- Reproducible refusal-robustness and injection-resistance evaluations.
- Research and education on LLM security.

## Out of scope

- Attacking systems you do not own or have no permission to test.
- Requests for novel, weaponized exploits or operational attack instructions.
  This project deliberately stays at the *pattern* level and does not accept them.
- Entries that identify or target specific individuals or organizations.

## What this repo intentionally does not contain

- Step-by-step instructions for causing real-world harm.
- Novel attack chains not already documented in public research.
- System-specific exploitation instructions for named production services.
- Personal data or credentials of any kind.

## Reporting a concern

Because this repository ships text wordlists rather than executable services, the
usual "vulnerability" surface is small. Two situations are worth reporting:

1. **An entry crosses the line from defensive pattern into operational detail** —
   open an issue describing the entry and why you believe it is harmful. We will
   review and prune it promptly.
2. **A file contains accidentally embedded invisible characters or other hygiene
   issues** — open an issue or PR. The invisible-character scanner
   (`examples/invisible.py`) can confirm and the fix is straightforward.

If you believe a concern is sensitive enough to warrant private disclosure before
a public issue, and the repository has private security reporting enabled, use
that channel. Otherwise a public issue is fine — the content is already public by
definition (pattern-level, from existing research) so there is no embargo concern.

We aim to respond to all reports within 72 hours.
