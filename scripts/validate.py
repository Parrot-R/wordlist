#!/usr/bin/env python3
"""Validate that manifest.json and the wordlist corpus are consistent.

Exits non-zero (failing CI) if any manifest file is missing, empty, or if the
loader raises. Prints a per-category summary on success.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import promptwl  # noqa: E402


def main() -> int:
    errors = []
    m = promptwl.manifest()

    # Version single-source guard: the raw on-disk manifest.json must match
    # promptwl.__version__ (the one source of truth). manifest() overrides the
    # field at load time, so this reads the file directly to catch static drift.
    raw = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    if raw.get("version") != promptwl.__version__:
        errors.append(
            f"manifest.json version {raw.get('version')!r} != "
            f"promptwl.__version__ {promptwl.__version__!r} "
            f"(update manifest.json to match)"
        )

    for cat in m["categories"]:
        for f in cat["files"]:
            path = ROOT / f["path"]
            if not path.exists():
                errors.append(f"missing file: {f['path']}")
                continue
            lines = [e for e in promptwl.load(cat["id"]) if e.file == f["path"]]
            if not lines:
                errors.append(f"no phrases loaded from: {f['path']}")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    stats = promptwl.stats()
    total = stats.pop("total")
    print("promptwl corpus OK")
    for cat, n in stats.items():
        print(f"  {cat:<12} {n:>4}")
    print(f"  {'total':<12} {total:>4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
