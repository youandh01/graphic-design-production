from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from asset_utils import (
    cross_format_stem_keys,
    duplicate_filename_keys,
    has_non_ascii,
    iter_delivery_files,
    relative_or_name,
    risky_final_name,
    root_from_arg,
)


RECOMMENDED_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._@-]*$")


def naming_issues(
    path: Path,
    root: Path,
    duplicate_names: set[tuple[str, str]],
    cross_format_stems: set[tuple[str, str]],
    flag_cross_format_stems: bool,
) -> list[str]:
    issues: list[str] = []
    name = path.name
    stem = path.stem
    suffix = path.suffix
    parent_key = relative_or_name(path.parent, root).lower()

    if " " in name:
        issues.append("contains_space")
    if has_non_ascii(name):
        issues.append("contains_non_ascii")
    if not RECOMMENDED_PATTERN.match(name):
        issues.append("contains_special_characters")
    if suffix != suffix.lower():
        issues.append("extension_not_lowercase")
    if (parent_key, name.lower()) in duplicate_names:
        issues.append("duplicate_filename_same_folder")
    if flag_cross_format_stems and (parent_key, stem.lower()) in cross_format_stems:
        issues.append("same_stem_multiple_formats_same_folder")
    if risky_final_name(stem):
        issues.append("risky_final_name")
    if len(name) > 80:
        issues.append("long_filename_over_80_chars")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check delivery filenames for common handoff risks.")
    parser.add_argument("folder", help="Folder containing delivery files.")
    parser.add_argument("--csv", action="store_true", help="Write CSV to stdout.")
    parser.add_argument("--fail-on-issues", action="store_true", help="Exit with code 1 when any issue is found.")
    parser.add_argument("--include-dotfiles", action="store_true", help="Include dotfiles such as .gitignore.")
    parser.add_argument(
        "--flag-cross-format-stems",
        action="store_true",
        help="Flag files like logo.png and logo.svg in the same folder.",
    )
    args = parser.parse_args()

    root = root_from_arg(args.folder)
    files = [
        path
        for path in iter_delivery_files(root)
        if args.include_dotfiles or not path.name.startswith(".")
    ]
    duplicate_names = duplicate_filename_keys(files, root)
    cross_format_stems = cross_format_stem_keys(files, root)

    rows = []
    for path in files:
        issues = naming_issues(path, root, duplicate_names, cross_format_stems, args.flag_cross_format_stems)
        rows.append((relative_or_name(path, root), path.suffix, issues))

    if args.csv:
        writer = csv.writer(sys.stdout, lineterminator="\n")
        writer.writerow(["path", "extension", "issues"])
        for rel_path, extension, issues in rows:
            writer.writerow([rel_path, extension, ";".join(issues)])
        return 1 if args.fail_on_issues and any(row[2] for row in rows) else 0

    flagged = [row for row in rows if row[2]]
    print(f"Checked {len(rows)} file(s) in {root}")
    print(f"Flagged {len(flagged)} file(s)")
    for rel_path, _extension, issues in flagged:
        print(f"- {rel_path}: {', '.join(issues)}")
    return 1 if flagged else 0


if __name__ == "__main__":
    raise SystemExit(main())
