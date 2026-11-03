#!/usr/bin/env python3
"""Dependency-free Markdown quality checks for the DocuCraft sample project."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_SECTIONS = ["Overview", "Before you begin", "Procedure", "Troubleshooting"]
LINK_RE = re.compile(r"!?\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    line: int = 1


def load_config(path: Path | None) -> tuple[list[str], dict[str, list[str]]]:
    if path is None:
        return DEFAULT_SECTIONS, {}
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ImportError as exc:
            raise RuntimeError("Python 3.11+ is needed for TOML, or install tomli on Python 3.9–3.10") from exc
    with path.open("rb") as stream:
        data = tomllib.load(stream)
    sections = data.get("required_sections", DEFAULT_SECTIONS)
    terms = data.get("terminology", {})
    if not isinstance(sections, list) or not all(isinstance(x, str) for x in sections):
        raise ValueError("required_sections must be an array of strings")
    if not isinstance(terms, dict) or not all(isinstance(k, str) and isinstance(v, list) and all(isinstance(x, str) for x in v) for k, v in terms.items()):
        raise ValueError("terminology must map preferred terms to arrays of alternatives")
    return sections, terms


def _visible_lines(text: str) -> tuple[list[str], list[tuple[int, str]]]:
    lines = text.splitlines()
    visible: list[str] = []
    headings: list[tuple[int, str]] = []
    fenced = False
    for number, line in enumerate(lines, 1):
        if re.match(r"^\s*(```|~~~)", line):
            fenced = not fenced
            visible.append("")
            continue
        visible.append("" if fenced else line)
        if not fenced:
            match = HEADING_RE.match(line)
            if match:
                headings.append((number, match.group(1).strip()))
    return visible, headings


def check_markdown(path: Path, required_sections: Iterable[str] = DEFAULT_SECTIONS,
                   terminology: dict[str, list[str]] | None = None) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    visible, headings = _visible_lines(text)
    findings: list[Finding] = []
    h1 = [(line, title) for line, title in headings if re.match(r"^#\s", visible[line - 1])]
    if not h1:
        findings.append(Finding("error", "missing-title", "Missing a level-one title (# Title).", 1))
    elif len(h1) > 1:
        findings.append(Finding("warning", "multiple-titles", "More than one level-one title was found.", h1[1][0]))

    normalized_headings = {heading.casefold(): line for line, heading in headings}
    for required in required_sections:
        if required.casefold() not in normalized_headings:
            findings.append(Finding("error", "missing-section", f"Missing required section: {required}.", 1))

    for line_no, line in enumerate(visible, 1):
        for match in LINK_RE.finditer(line):
            target = match.group(1) or match.group(2) or ""
            if not target or target.startswith(("#", "//")) or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            target_path = target.split("#", 1)[0].split("?", 1)[0]
            if not target_path:
                continue
            resolved = (path.parent / target_path).resolve()
            if not resolved.exists():
                findings.append(Finding("error", "broken-link", f"Relative link target does not exist: {target_path}.", line_no))

    for preferred, variants in (terminology or {}).items():
        for variant in variants:
            if not variant or variant.casefold() == preferred.casefold():
                continue
            pattern = re.compile(r"(?<!\w)" + re.escape(variant) + r"s?(?!\w)", re.IGNORECASE)
            for line_no, line in enumerate(visible, 1):
                if pattern.search(line):
                    findings.append(Finding("warning", "terminology", f"Use “{preferred}” instead of “{variant}”.", line_no))
    return findings


def find_markdown(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            found.extend(sorted(p for p in path.rglob("*.md") if p.is_file()))
        elif path.is_file() and path.suffix.lower() == ".md":
            found.append(path)
    return list(dict.fromkeys(found))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Markdown structure, relative links, and terminology.")
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories")
    parser.add_argument("--config", type=Path, default=Path("docucraft.toml"), help="TOML config (default: docucraft.toml)")
    parser.add_argument("--no-config", action="store_true", help="Use built-in defaults only")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Report format")
    args = parser.parse_args(argv)
    try:
        config = None if args.no_config else args.config
        if config is not None and not config.exists():
            raise FileNotFoundError(f"Configuration not found: {config}")
        sections, terms = load_config(config)
        files = find_markdown(args.paths)
        if not files:
            raise FileNotFoundError("No Markdown files found in the supplied paths")
        report = []
        for path in files:
            findings = check_markdown(path, sections, terms)
            report.append({"file": str(path), "findings": [asdict(f) for f in findings]})
        if args.format == "json":
            print(json.dumps(report, indent=2))
        else:
            for item in report:
                errors = sum(f["severity"] == "error" for f in item["findings"])
                warnings = sum(f["severity"] == "warning" for f in item["findings"])
                label = "FAIL" if errors else "PASS"
                print(f"{label} {item['file']} ({errors} errors, {warnings} warnings)")
                for finding in item["findings"]:
                    print(f"  {finding['severity'].upper()} L{finding['line']} [{finding['code']}] {finding['message']}")
        return 1 if any(f["severity"] == "error" for item in report for f in item["findings"]) else 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"docucraft: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
