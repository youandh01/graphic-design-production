from __future__ import annotations

import argparse
import csv
from pathlib import Path

from asset_utils import format_bytes, inspect_asset, iter_delivery_files, root_from_arg, safe_csv_value


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a CSV manifest for graphic delivery assets.")
    parser.add_argument("folder", help="Folder containing delivery assets.")
    parser.add_argument("--output", help="Output CSV path. Defaults to manifest.csv inside the inspected folder.")
    parser.add_argument("--all-files", action="store_true", help="Include unknown extensions as metadata-only rows.")
    args = parser.parse_args()

    root = root_from_arg(args.folder)
    output = Path(args.output).expanduser().resolve() if args.output else root / "manifest.csv"
    infos = [inspect_asset(path, root) for path in iter_delivery_files(root, known_only=not args.all_files)]

    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "path",
                "extension",
                "file_size_bytes",
                "file_size",
                "width",
                "height",
                "color_hint",
                "transparency_hint",
                "inspection",
                "modified",
                "notes",
                "review_status",
                "intended_use",
            ]
        )
        for info in infos:
            writer.writerow(
                [
                    info.rel_path,
                    info.extension,
                    info.file_size,
                    format_bytes(info.file_size),
                    safe_csv_value(info.width),
                    safe_csv_value(info.height),
                    info.color_hint,
                    info.transparency_hint,
                    info.inspection,
                    info.modified,
                    info.notes,
                    "",
                    "",
                ]
            )

    print(f"Wrote {len(infos)} file(s) to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
