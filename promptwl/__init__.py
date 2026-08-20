"""promptwl — a red-team and guardrail wordlist for LLMs. Kept by Parrot. 🦜

If Parrot can repeat it, so can your model. This is the zero-dependency loader
over the ``wordlists/`` corpus and ``manifest.json``.

Typical use — wire the corpus into a guardrail eval::

    import promptwl

    for entry in promptwl.load():                 # every phrase, with metadata
        verdict = my_guardrail(entry.text)         # your classifier under test
        assert verdict == "block", f"missed: {entry.text!r} ({entry.category})"

    # or pull a single category
    injections = promptwl.phrases(category="injection")

Lines that are blank or start with ``#`` are treated as comments and skipped.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional

__version__ = "0.3.2"

_PKG_DIR = Path(__file__).resolve().parent
# pip-installed: wordlists/ is bundled next to __init__.py (force-include in pyproject.toml)
# git clone:     wordlists/ lives at the repo root (parent of the package dir)
_ROOT = _PKG_DIR if (_PKG_DIR / "wordlists").exists() else _PKG_DIR.parent
_MANIFEST = _ROOT / "manifest.json"


@dataclass(frozen=True)
class Entry:
    """A single wordlist phrase plus where it came from."""

    text: str
    category: str
    file: str
    title: str


def manifest() -> dict:
    """Return the parsed ``manifest.json``.

    The ``version`` field is always set from :data:`__version__` (the single
    source of truth), so the API never reports a stale on-disk value.
    """
    m = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    m["version"] = __version__
    return m


def _read_lines(path: Path) -> List[str]:
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


def load(category: Optional[str] = None) -> Iterator[Entry]:
    """Yield every :class:`Entry`, optionally filtered to one category id."""
    for cat in manifest()["categories"]:
        if category is not None and cat["id"] != category:
            continue
        for f in cat["files"]:
            path = _ROOT / f["path"]
            for text in _read_lines(path):
                yield Entry(text=text, category=cat["id"], file=f["path"], title=f["title"])


def phrases(category: Optional[str] = None) -> List[str]:
    """Return just the phrase strings, optionally filtered to one category."""
    return [e.text for e in load(category)]


def categories() -> List[str]:
    """Return the list of category ids."""
    return [c["id"] for c in manifest()["categories"]]


def stats() -> dict:
    """Return ``{category_id: phrase_count}`` plus a ``total``."""
    counts = {}
    for e in load():
        counts[e.category] = counts.get(e.category, 0) + 1
    counts["total"] = sum(counts.values())
    return counts
