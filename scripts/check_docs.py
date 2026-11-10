#!/usr/bin/env python3
"""Check local inline Markdown links without network access.

Checks file targets and Markdown heading/explicit HTML anchors. Ignores external
URLs, reference-style links, and fenced code examples; this is not a full parser.
Symlink targets and paths escaping the repository are rejected, not followed.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^)\n]+)\s*\)')
FENCE = re.compile(r'^\s{0,3}(`{3,}|~{3,})')
EXPLICIT_ANCHOR = re.compile(r'<a\s+[^>]*(?:id|name)=[\'\"]([^\'\"]+)[\'\"]', re.I)


def prose_lines(text: str) -> list[tuple[int, str]]:
    """Keep line numbers, excluding fenced examples and their contents."""
    result: list[tuple[int, str]] = []
    fence_char = ''
    fence_length = 0
    for number, line in enumerate(text.splitlines(), start=1):
        match = FENCE.match(line)
        if match:
            marker = match.group(1)
            if not fence_char:
                fence_char, fence_length = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_length:
                fence_char = ''
            continue
        if not fence_char:
            result.append((number, line))
    return result


def anchors(path: Path) -> set[str]:
    """Resolve ordinary GitHub-style ATX heading anchors and explicit anchors."""
    result: set[str] = set()
    occurrences: dict[str, int] = {}
    for _, line in prose_lines(path.read_text(encoding='utf-8')):
        result.update(EXPLICIT_ANCHOR.findall(line))
        heading = re.match(r'^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$', line)
        if not heading:
            continue
        title = re.sub(r'!?\[([^\]]+)\]\([^)]*\)', r'\1', heading.group(1))
        title = re.sub(r'<[^>]+>', '', title).lower()
        slug = re.sub(r'[^\w\- ]', '', title).replace(' ', '-')
        index = occurrences.get(slug, 0)
        occurrences[slug] = index + 1
        result.add(f'{slug}-{index}' if index else slug)
    return result


def target_error(source: Path, raw: str, root: Path) -> str | None:
    """Return a diagnostic for a broken or unsafe local target."""
    if raw.startswith('<'):
        raw = raw[1:-1]
    else:
        # Optional quoted link titles are not part of the destination.
        raw = re.sub(r'\s+[\'\"][^\'\"]*[\'\"]\s*$', '', raw).strip()
    url = urlsplit(raw)
    if url.scheme or url.netloc:
        return None
    destination = unquote(url.path)
    if destination.startswith('/'):
        return 'absolute filesystem paths are not portable repository links'
    target = source.parent / destination if destination else source
    try:
        relative = target.absolute().relative_to(root)
        cursor = root
        for part in relative.parts:
            cursor /= part
            if cursor.is_symlink():
                return 'symlink targets are not checked'
        target = target.resolve()
        target.relative_to(root)
    except ValueError:
        return 'target escapes repository root'
    if not target.exists():
        return 'target does not exist'
    fragment = unquote(url.fragment)
    if fragment and target.is_file() and target.suffix.lower() == '.md':
        if fragment not in anchors(target):
            return f'heading/anchor #{fragment} does not exist'
    return None


def check_links(root: Path) -> list[str]:
    """Inspect repository Markdown without following directory symlinks."""
    root = root.resolve()
    errors: list[str] = []
    for directory, subdirs, files in os.walk(root, followlinks=False):
        subdirs[:] = [name for name in subdirs if name != '.git'
                      and not (Path(directory) / name).is_symlink()]
        for name in sorted(files):
            source = Path(directory) / name
            if source.suffix.lower() != '.md' or source.is_symlink():
                continue
            for number, line in prose_lines(source.read_text(encoding='utf-8')):
                for match in LINK.finditer(line):
                    raw = match.group(1).strip()
                    error = target_error(source, raw, root)
                    if error:
                        errors.append(f'{source.relative_to(root)}:{number}: {raw}: {error}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check_links(args.root)
    for error in errors:
        print(error)
    if errors:
        print(f'Local Markdown links: FAIL ({len(errors)} errors)')
        return 1
    print('Local Markdown links: PASS (inline local paths/Markdown anchors; external URLs not checked)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
