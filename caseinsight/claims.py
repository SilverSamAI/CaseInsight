"""Claim gate — enforces the outbound metric allowlist and reference discipline.

Operating constraints (Playbook Section 18.1, standing instructions):

* Only four metrics may appear in cold outbound copy:
  68 percent cost reduction, 87.5 percent time reduction,
  20x content volume, 7 billion impressions.
* Only the 15 approved cold reference clients may be named.
  The broader boilerplate list (Adobe, Fifth Third Bank, ...) is approved
  for RFPs and credentials responses, not for cold email.
* Banned phrases and hype language never ship.

Run against every sequence file before staging: ``python -m caseinsight.claims``.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# The four approved metrics: the approved figure must appear with its
# context word nearby, in either order ("68 percent cost reduction" and
# "cost came down 68 percent" both pass; "68 percent faster" does not).
APPROVED_METRICS = [
    (re.compile(r"\b68\s*(?:%|percent)", re.I), re.compile(r"cost", re.I)),
    (re.compile(r"\b87\.5\s*(?:%|percent)", re.I), re.compile(r"time", re.I)),
    (re.compile(r"\b20x\b", re.I), re.compile(r"content\s+volume", re.I)),
    (re.compile(r"\b7\s+billion\b", re.I), re.compile(r"impressions", re.I)),
]

# Approved cold outbound reference clients (Section 18.1, item 5).
APPROVED_REFERENCES = [
    "Coca-Cola",
    "Amazon",
    "Sephora",
    "LVMH",
    "Sam's Club",
    "Williams Sonoma",
    "BMW",
    "PacSun",
    "Marc Jacobs",
    "Quay",
    "SimpliSafe",
    "CyberArk",
    "Headline",
    "Svedka",
    "Panasonic",
    "Goodwill",
]

# Client and pipeline names that must NEVER appear in cold copy: boilerplate
# clients not cleared for cold, active pursuits, and ambiguous relationships
# (from the Suppression List tab).
FORBIDDEN_REFERENCES = [
    "Adobe",
    "Fifth Third",
    "IHG",
    "Keurig",
    "Dr Pepper",
    "Mattress Firm",
    "Carlsberg",
    "ResMed",
    "Medical Guardian",
    "Nacelle",
    "Smoothie King",
    "Kura Sushi",
    "Supersure",
    "Chime",
    "OnePay",
    "Toptal",
    "MediaSense",
    "Hershey",
    "Reese's",
    "Nestle",
    "Benefit Cosmetics",
]

BANNED_PHRASES = [
    "hope this finds you well",
    "just checking in",
    "circling back",
    "touching base",
    "let me know if you would like to explore further",
    "unlock the power of ai",
    "revolutionize",
    "transform your content",
    "game changing",
    "game-changing",
    "cutting edge",
    "cutting-edge",
    "next generation",
    "next-generation",
    "synergy",
    "disruptive",
    "paradigm shift",
    "leverage ai",
    "harness ai",
]

# Performance-claim shapes that must match the allowlist if present.
# Plain arithmetic about the prospect's own volume ("40 shades x 6 channels
# is 960 assets") and the approved anonymized market evidence ("$8,000 type
# change") are not performance claims and pass.
_PERCENT = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|percent)", re.I)
_MULTIPLIER = re.compile(r"\b\d+(?:\.\d+)?x\b", re.I)
_IMPRESSIONS = re.compile(r"\b[\d,.]+\s*(?:billion|million|thousand)?\s*impressions", re.I)


@dataclass
class Violation:
    kind: str
    text: str
    line: int

    def __str__(self) -> str:
        return f"line {self.line}: [{self.kind}] {self.text}"


def _allowlisted(fragment: str) -> bool:
    return any(
        figure.search(fragment) and context.search(fragment)
        for figure, context in APPROVED_METRICS
    )


def verify_text(text: str) -> list[Violation]:
    """Return every claim-gate violation found in ``text``."""
    violations: list[Violation] = []
    for i, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()

        for phrase in BANNED_PHRASES:
            if phrase in lowered:
                violations.append(Violation("banned-phrase", phrase, i))

        for name in FORBIDDEN_REFERENCES:
            if re.search(rf"\b{re.escape(name)}\b", line, re.I):
                violations.append(Violation("unapproved-reference", name, i))

        for rx in (_PERCENT, _MULTIPLIER, _IMPRESSIONS):
            for match in rx.finditer(line):
                # Widen to surrounding context so allowlist phrasing matches.
                lo = max(0, match.start() - 40)
                hi = min(len(line), match.end() + 40)
                if not _allowlisted(line[lo:hi]):
                    violations.append(Violation("unapproved-metric", match.group(0), i))
    return violations


def verify_file(path: Path) -> list[Violation]:
    return verify_text(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    root = Path(__file__).resolve().parent.parent
    paths = [Path(a) for a in args] or sorted((root / "sequences").glob("*.md"))
    failed = False
    for path in paths:
        violations = verify_file(path)
        status = "PASS" if not violations else "FAIL"
        print(f"[{status}] {path}")
        for violation in violations:
            failed = True
            print(f"    {violation}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
