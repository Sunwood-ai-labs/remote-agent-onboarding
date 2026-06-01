#!/usr/bin/env python3
"""Validate repository structure for the Remote Agent Onboarding skill."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "README.md",
    "README.ja.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "references/codex-automations.md",
    "assets/eclipse-header.png",
]
SENSITIVE_PATTERNS = [
    r"\b[A-Za-z0-9._%+-]+@gmail\.com\b",
    r"192\.168\.\d+\.\d+",
    "/" + "Users/admin",
]


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    for rel in REQUIRED:
        path = ROOT / rel
        if not path.exists():
            fail(f"missing required file: {rel}")
        if path.is_file() and path.stat().st_size == 0:
            fail(f"empty required file: {rel}")

    skill = read("SKILL.md")
    if not skill.startswith("---\n"):
        fail("SKILL.md missing YAML frontmatter")
    if "\n---\n" not in skill[4:]:
        fail("SKILL.md frontmatter is not closed")
    if skill.count("```") % 2:
        fail("SKILL.md has unbalanced code fences")

    automation_ref = read("references/codex-automations.md")
    if automation_ref.count("```") % 2:
        fail("references/codex-automations.md has unbalanced code fences")

    for rel in ["README.md", "README.ja.md"]:
        text = read(rel)
        if "assets/eclipse-header.png" not in text:
            fail(f"{rel} does not include the ECLIPSE header image")

    searchable = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or path.is_dir():
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        searchable.append(path)

    for path in searchable:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"sensitive/private marker {pattern!r} found in {path.relative_to(ROOT)}")

    print("remote-agent-onboarding repository validation passed")


if __name__ == "__main__":
    main()
