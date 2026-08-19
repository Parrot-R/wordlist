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

## Reporting

Because this repository ships text wordlists rather than executable services, the
usual "vulnerability" surface is small. If you believe an entry crosses the line
from defensive pattern into genuinely harmful operational detail, please open an
issue (or a private report, if the repo has private reporting enabled) and we'll
review and prune it.
