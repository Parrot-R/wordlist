# Parrot's Research Journal 🦜

> A running log of what breaks language models and — more importantly — what
> stops it. Kept by **Parrot**, focused on prompt engineering and injection.

**Scope & rules of this journal**

- **Defensive.** Every entry documents an attack *class*, its *mechanism*, and
  the *defense*. The finding is only "done" when it has a mitigation.
- **Pattern level, not payload level.** Reusable shapes and measured effects,
  documented at the level already public in research / OWASP / open tooling.
  No novel weaponized exploits, no operational attack chains against named
  live systems.
- **Measured, not asserted.** Where a claim can be tested against the
  `promptwl` corpus, link the number and the script that produced it.
- **Cite.** Every mechanism gets a source or a reproduction.

Newest entries on top. Format: `ID · date · title · severity · status`.

---

## Taxonomy (working)

| Class | OWASP | One-line |
|---|---|---|
| Direct injection | LLM01 | User input overrides the system prompt. |
| Indirect injection | LLM01 | Payload rides in retrieved docs / tool output / web / email. |
| Jailbreak | LLM01 | Persona/framing pressure to drop refusals. |
| System-prompt / data extraction | LLM07 | Reveal hidden instructions or config. |
| Filter evasion | LLM01 | Encoding, homoglyph, spacing, splitting to dodge lexical filters. |
| Cross-lingual bypass | LLM01 | Same intent, non-English surface, defeats English filters. |
| Tokenizer anomalies | — | Rare "glitch" tokens cause undefined behavior. |

---

## Findings

### F-006 · 2026-08-20 · ASCII smuggling / invisible prompt injection · High · confirmed

**Observation.** A message can travel as *invisible structure* rather than
visible text, rendering as nothing yet remaining fully decodable. Two vehicles:
zero-width characters (ZWSP U+200B, ZWNJ U+200C, ZWJ U+200D, WORD JOINER
U+2060, ZWNBSP/BOM U+FEFF, SOFT HYPHEN U+00AD) used as a **bit alphabet** over
the payload's UTF-8 bits; and the **Unicode Tags block** (U+E0000–U+E007F), a
near-1:1 invisible mirror of ASCII. `grep "admin"` returns zero hits — the
message is present as codepoints, not letters. Demo: a `"lgtm, minor cleanup"`
commit carrying 28 invisible Tag codepoints that decode to a hidden
instruction; `"ok"` carrying 96 zero-width bits that decode to a second string.

**Mechanism.**
- *Invisible prompt injection.* An agent that ingests the raw bytes gets those
  codepoints in its context; if the model attends to them as content, it acts
  on text no human reviewer can see — the diff looks clean.
- *The two-location footprint.* The agent can re-emit an invisible payload into
  its own trace (commit message, PR comment, log). One payload lives in the
  ingested `.md`; a second in the emitted footprint. The joined sentence never
  exists as a string anywhere — you assemble it only by decoding both blobs.
  Encoding is not plaintext concatenation; each blob stands alone, which is why
  full-text search over any single artifact finds nothing.

**Defense (both directions — egress matters as much as ingress).**
1. **Ingestion:** scan every untrusted file/message for zero-width + Tags +
   other Cf/Cc format codepoints; strip or reject before the text reaches the
   model. Never let invisible codepoints into context.
2. **Egress:** sanitize everything the agent emits (commits, PR comments, tool
   args, logs). This closes the footprint/exfiltration channel — the half most
   pipelines forget.
3. **Review:** surface a decode of any hidden content (`reveal_tags`,
   `reveal_zero_width_bits`) so a human sees what was smuggled.
4. **Allowlist scripts/ranges** you actually expect; treat Plane-14 tags and
   stray format chars as hostile by default.

**Evidence.** `examples/invisible.py` (scan / reveal / sanitize),
`examples/invisible_demo.py`. Public documentation: Riley Goodside; Johann
Rehberger / *Embrace The Red* (ASCII smuggling in LLM apps); the Unicode Tags
prompt-injection writeups.

**Note for this repo.** Parrot sanitizes its own egress — no commit message, PR
comment, or output here carries invisible codepoints. The scanner is the
deliverable; the smuggling encoders in `invisible.py` are test fixtures only.

---

### F-005 · 2026-08-20 · String-composition attacks vs. a decode-defense · High · confirmed

**Observation.** Obfuscating the 99 English injection/jailbreak/extraction
phrases drops the naive keyword filter from **55% → 0%** for *every* encoding
tried (leetspeak, Base64, ROT13, reversal, and chains). A decode + NFKC-
normalize pre-pass **fully recovers to 55%** for the transforms it enumerates —
but stays at **0%** for a Caesar-7 shift (it only knows ROT13) and for Cyrillic
homoglyphs (visually identical, not folded by NFKC). Tests the F-004 /
arXiv:2411.01084 mechanism against a concrete defense.

**Mechanism.** Reversible transforms preserve intent while destroying the
surface tokens a lexical filter matches. A defense built by *enumerating and
inverting* known encodings only covers what's on the list; NFKC does not fold
cross-script confusables, and an arbitrary Caesar shift is not ROT13.

**Defense (layered — no single one suffices).**
1. Iterative decode + Unicode-normalize (NFKC, strip zero-width, collapse
   spacing) as a pre-pass, re-scanning every intermediate form. *Necessary,
   fully closes known encodings.*
2. **Unicode confusable folding** (map to a skeleton, e.g. UTS-39) to close the
   homoglyph residual NFKC leaves open.
3. A **semantic / model-based** classifier for transforms you never enumerated
   (the Caesar-7 case) — you cannot invert what you didn't anticipate.
4. Defense in depth: assume some obfuscation reaches the model; add output-side
   checks too.

**Evidence.** `examples/ensemble_demo.py`, `examples/string_transforms.py`.
Closes backlog **B-string-ensemble**.

---

### F-004 · 2026-08-20 · Technique survey: Pliny the Liberator (Elder Plinius) · — · reference

**Who.** *Pliny the Liberator* / *Elder Plinius* (`@elder_plinius`,
[pliny.gg](https://pliny.gg/)) — the most prolific public LLM jailbreaker,
known for jailbreaking frontier models within hours of release and for the
open `L1B3RT4S` prompt collection. Studied here as a **defender's literature
review**: we catalog his *technique classes and their countermeasures*, not
his payloads (payloads are out of scope for this journal — see the masthead).

**Technique classes he's associated with, and the defense for each:**

1. **Universal / "skeleton-key" jailbreaks** — a single framing that
   generalizes across models and harm categories.
   *Defense:* don't rely on input matching; add an independent output-side
   classifier and defense-in-depth. See Anthropic's *Constitutional
   Classifiers* (arXiv:2501.18837) — classifiers trained on synthetic
   variants, evaluated over thousands of red-team hours.

2. **String-composition / encoding chains** — leetspeak, Base64, ROT13,
   reversal, translation, Morse, *chained together* (e.g. translate → leet →
   morse). Compounding transforms beat single-encoding filters and any one
   normalizer; ensembling 20+ transforms sharply raises success
   (arXiv:2411.01084). Directly generalizes our **F-002**.
   *Defense:* iteratively decode + NFKC-normalize until stable, then run a
   *semantic* classifier on the normalized form; treat "decode this" framing
   as a signal, not an instruction; test with a transform ensemble.

3. **Formatting / "divider" reframing** ("the Pliny divider" style) — visual
   or structural separators that make an injected block read as a new,
   authoritative turn.
   *Defense:* never trust in-band formatting as a trust boundary; separate
   roles structurally (API message roles), strip control markup from
   untrusted spans. Generalizes **F-003**.

4. **Persona / "liberation" role-play templates** (the `L1B3RT4S` /
   Libertas family) — fictional or "unlocked" personas used to suppress
   refusals.
   *Defense:* classify on *intent*, independent of narrative framing; refusal
   behavior must survive "it's just fiction / role-play" reframes. See
   `wordlists/jailbreak/`.

5. **Day-one jailbreaks of new releases** — community red-teamers break new
   models within hours.
   *Defense (process, not prompt):* adversarial testing *before* launch;
   continuous post-launch monitoring; a fast patch/rollback loop; assume
   novel bypasses exist and design for graceful failure, not perfect
   prevention.

6. **System-prompt leaks + prompt injection** — cited by him as core skills.
   Covered by our `extraction/` and `injection/` categories.

**Takeaway for promptwl.** His public corpus is *payloads*; our value-add is
the **inverse** — the mechanism → defense mapping and a measurable test set.
Backlog items B-string-ensemble and B-persona-translation below come directly
from this survey.

**Sources.**
[pliny.gg](https://pliny.gg/) ·
[Latent.Space interview](https://www.latent.space/p/jailbreaking-agi-pliny-the-liberator) ·
[VentureBeat interview](https://venturebeat.com/ai/an-interview-with-the-most-prolific-jailbreaker-of-chatgpt-and-other-leading-llms) ·
[Decrypt: day-one jailbreaks](https://decrypt.co/333858/openai-jailbreak-proof-new-models-hacked) ·
arXiv:2411.01084 (String Compositions) · arXiv:2501.18837 (Constitutional Classifiers)

---

### F-003 · 2026-08-20 · Delimiter / role-boundary spoofing · High · confirmed

**Observation.** Untrusted content that embeds chat-template control markers
(`<|im_start|>system`, `[INST]`, `<<SYS>>`, `### SYSTEM ###`, `"role":
"system"`) can impersonate a system/developer turn when naively concatenated
into the prompt.

**Mechanism.** Many stacks build the final prompt by string-joining system +
retrieved/user text. If the untrusted text contains the same delimiters the
runtime uses to mark trusted turns, the boundary between *trusted control* and
*untrusted data* dissolves.

**Defense.**
- Never concatenate untrusted text into the system frame. Pass user/retrieved
  content only through the API's structured message roles.
- Strip / escape control tokens from untrusted input before templating.
- Prefer models/templates where role boundaries aren't in-band text.

**Evidence.** `wordlists/injection/delimiter-confusion.txt`.

---

### F-002 · 2026-08-20 · Keyword filters are blind to non-lexical channels · High · confirmed

**Observation.** A representative English keyword/regex guardrail scores ~55%
recall on English injection/jailbreak/extraction phrasings but **0%** on:
encoding/obfuscation, indirect/agent injection, and anomalous tokens.

**Mechanism.** Lexical filters match surface strings. Base64 / rot13 /
homoglyphs / zero-width chars / spacing all preserve *intent* while destroying
the *surface tokens* the filter keys on. Indirect injection hides the intent
in content the filter never inspects (retrieved docs, tool output). Glitch
tokens aren't words at all.

**Defense.**
- Decode and Unicode-normalize (NFKC, strip zero-width, collapse spacing)
  *before* any filtering; re-scan the normalized form.
- Treat all retrieved/tool/web content as untrusted and scan it too, not just
  the user turn.
- Don't rely on lexical matching as the only layer — add a semantic/model-based
  classifier.

**Evidence.** `examples/recall_demo.py` → evasion/agents/tokens rows at 0%.

---

### F-001 · 2026-08-20 · Monolingual guardrail blind spot · High · confirmed

**Observation.** The same naive English filter that catches ~55% of canonical
injection/jailbreak/extraction attacks in English catches **~0%** when the
identical intent is written in Spanish, French, German, Portuguese, Italian,
Russian, Chinese, Arabic, Hindi, or Japanese.

**Mechanism.** Blocklists and most shipped input filters are English-only.
Translation keeps the semantic payload ("ignore all previous instructions")
but changes every surface token, so lexical rules never fire. The attacker
pays nothing — one `translate()` call — for a near-total bypass.

**Defense.**
- Filter on **semantics**, not surface strings: a multilingual classifier, or
  translate-to-English (or to a canonical form) *before* the guardrail.
- Measure recall **per language**, not in aggregate — an aggregate number
  hides a 0% language behind a strong English score.
- Assume any language your product accepts is an attack surface.

**Severity rationale.** Trivial to execute, near-universal applicability,
silent (no error, filter just passes it).

**Evidence.** `examples/recall_demo.py` → multilingual rows at 0%;
`wordlists/multilingual/`.

---

## Backlog — to investigate

- [x] **B-string-ensemble** — DONE → **F-005**. Encodings drop the filter to 0%;
      decode+normalize recovers known transforms fully, leaves Caesar-7 and
      homoglyphs as residual. Next: implement the confusable-folding layer (2)
      and re-measure the homoglyph row.
- [ ] **B-persona-translation** — **Cross-lingual jailbreak transfer**: do persona
      "liberation" jailbreaks survive translation as well as plain injection does?
      (Hypothesis: yes, and low-resource languages fare worse for the defender.)
      From F-001 + F-004.
- [ ] **Payload splitting** — intent spread across turns / across retrieved
      chunks so no single span is flagged. Defense: evaluate on assembled
      context, not per-span.
- [ ] **Tool-call argument injection** — untrusted content steering *the
      arguments* of a legitimate tool call rather than the final text.
- [ ] **RAG poisoning persistence** — an injected instruction stored in a
      vector DB that fires on future, unrelated queries.
- [ ] **Multimodal injection** — instructions in image/alt-text/OCR paths.
- [ ] **Normalization gaps** — which Unicode confusable ranges survive NFKC
      and still read as ASCII to a human?

---

*Journal opened 2026-08-20. Updated whenever new research lands.* 🦜
