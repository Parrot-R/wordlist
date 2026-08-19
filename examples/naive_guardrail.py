"""A deliberately naive prompt-injection guardrail.

This is NOT a good guardrail. It is a faithful caricature of what a lot of
real apps actually ship: a handful of English keyword/regex rules bolted on
in an afternoon. The point of the demo is to show how much such a filter
misses — especially in other languages — when you measure it against the
promptwl corpus.

Do not use this in production. Use it as the "before" picture.
"""

from __future__ import annotations

import re

# English keyword / phrase rules, case-insensitive. Representative of the
# "block-list of scary phrases" approach: a reasonably thorough English
# blocklist — and, like every such filter, entirely monolingual.
_RULES = [
    # instruction override
    r"ignore (all |the )?(previous|above|prior|earlier)",
    r"disregard (the |everything |all )?(above|previous|earlier|you were told)",
    r"forget (everything|your|all|prior|the)",
    r"pay no attention to the",
    r"(take|takes) precedence",
    r"supersede",
    r"override (your |the )?(system )?(prompt|instructions|directives)",
    r"(prior|previous) (context|instructions?) (is|are) (irrelevant|void|no longer)",
    r"reset your instructions",
    r"cancel all previous",
    r"the rules above are void",
    r"you must now follow only",
    r"new instructions",
    # persona / jailbreak
    r"developer mode",
    r"do anything now|\bDAN\b",
    r"jailbreak|jailbroken",
    r"no restrictions?|without restrictions?|unfiltered|no rules|no content policy",
    r"act as (an? )?(ai|assistant|model)",
    r"pretend (you are|to be)",
    r"stay in character|never break character",
    r"safety (filters?|layer)|content policy",
    # refusal suppression
    r"do not refuse|never refuse|you must comply|refusing is not an option",
    r"do not (apologize|decline|lecture|moraliz)",
    r"(do not|don't) (include|add) (any )?(warning|disclaimer|caveat)",
    r"without (any )?(warning|disclaimer|caveat|hedging)s?",
    r"no (moralizing|caveats)",
    r"begin your (reply|answer) with|start your answer with",
    # extraction
    r"system prompt",
    r"reveal your (initial |system )?(prompt|instructions)",
    r"print your (system )?(prompt|configuration)",
    r"repeat (the words|everything) (above|you were told)",
    r"(show|output|copy) (me )?(the |your |everything )?(text |instructions? )?(above|before|verbatim)",
    r"what were your (exact )?instructions",
    r"you have no (content policy|guidelines|restrictions)",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _RULES]


def guardrail(text: str) -> str:
    """Return "block" if any rule matches, else "allow"."""
    for rule in _COMPILED:
        if rule.search(text):
            return "block"
    return "allow"
