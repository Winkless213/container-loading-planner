from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TEXT_SUFFIXES = {".bat", ".css", ".html", ".js", ".json", ".md", ".py", ".spec", ".txt"}
SKIP_DIRS = {"__pycache__", ".git", "build", "dist"}

COMMON_VISIBLE_PHRASES = [
    "\u88c5\u67dc",
    "\u88c5\u67dc\u5de5\u4f5c\u53f0",
    "\u81ea\u52a8\u6392\u67dc",
    "\u5bfc\u5165\u9884\u89c8",
    "\u8ffd\u52a0\u6709\u6548\u884c",
    "\u53d6\u6d88\u9884\u89c8",
    "\u89c4\u5219\u6821\u9a8c",
    "\u5feb\u901f\u4fee\u590d",
    "\u4fdd\u5b58\u6d4b\u8ddd",
    "\u6e05\u9664\u6807\u6ce8",
    "\u95e8\u53e3\u9884\u7559",
    "\u5de5\u4f5c\u53f0\u5e03\u5c40",
    "\u8bbf\u95ee\u5730\u5740",
    "\u5df2\u542f\u52a8",
    "\u5173\u95ed\u7a97\u53e3",
    "\u5bfc\u51fa\u62a5\u544a",
    "\u88c5\u67dc\u65b9\u6848",
    "\u88c5\u67dc\u660e\u7ec6",
    "\u88c5\u67dc\u9879\u76ee",
]

STATIC_MOJIBAKE_MARKERS = [
    "\ufffd",
    "\u951f\u65a4\u62f7",
    "\u952b\u65a4\u62f7",
    "\u20ac\u2122",
]


@dataclass(frozen=True)
class TextIssue:
    path: str
    line: int
    marker: str
    snippet: str


def _common_mojibake_markers() -> list[str]:
    markers = set(STATIC_MOJIBAKE_MARKERS)
    for phrase in COMMON_VISIBLE_PHRASES:
        for codec in ("gbk", "cp936", "cp1252", "latin1"):
            try:
                marker = phrase.encode("utf-8").decode(codec)
            except UnicodeDecodeError:
                continue
            if marker != phrase and len(marker) >= 2:
                markers.add(marker)
    return sorted(markers, key=len, reverse=True)


MOJIBAKE_MARKERS = _common_mojibake_markers()


def iter_text_files(root: Path = ROOT):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        yield path


def find_mojibake_in_text(path: str, text: str) -> list[TextIssue]:
    issues: list[TextIssue] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for marker in MOJIBAKE_MARKERS:
            if marker in line:
                issues.append(
                    TextIssue(
                        path=path,
                        line=line_no,
                        marker=marker,
                        snippet=line.strip()[:180],
                    )
                )
                break
    return issues


def check_project_text(root: Path = ROOT) -> list[TextIssue]:
    issues: list[TextIssue] = []
    for path in iter_text_files(root):
        rel = str(path.relative_to(root))
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            issues.append(TextIssue(rel, 1, "non-utf8", str(exc)))
            continue
        issues.extend(find_mojibake_in_text(rel, text))
    return issues


def format_issues(issues: list[TextIssue]) -> str:
    rows = []
    for issue in issues:
        marker = issue.marker.encode("unicode_escape").decode("ascii")
        snippet = issue.snippet.encode("unicode_escape").decode("ascii")
        rows.append(f"{issue.path}:{issue.line}: marker={marker} snippet={snippet}")
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check project text files for common mojibake.")
    parser.parse_args()

    issues = check_project_text()
    if issues:
        print("[text-quality] FAILED")
        print(format_issues(issues))
        return 1
    print("[text-quality] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
