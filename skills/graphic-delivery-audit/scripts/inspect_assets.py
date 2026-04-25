from __future__ import annotations

import argparse
import csv
import sys

from asset_utils import format_bytes, inspect_asset, iter_delivery_files, root_from_arg, safe_csv_value


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect common graphic delivery assets.")
    parser.add_argument("folder", help="Folder containing exported or delivery assets.")
    parser.add_argument("--csv", action="store_true", help="Write CSV to stdout.")
    parser.add_argument("--all-files", action="store_true", help="Include unknown extensions as metadata-only rows.")
    args = parser.parse_args()

    root = root_from_arg(args.folder)
    infos = [inspect_asset(path, root) for path in iter_delivery_files(root, known_only=not args.all_files)]

    fields = [
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
    ]
    if args.csv:
        writer = csv.writer(sys.stdout, lineterminator="\n")
        writer.writerow(fields)
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
                ]
            )
        return 0

    print(f"Inspected {len(infos)} file(s) in {root}")
    for info in infos:
        dimensions = f"{info.width}x{info.height}" if info.width and info.height else "unknown"
        notes = f" [{info.notes}]" if info.notes else ""
        print(f"- {info.rel_path}: {dimensions}, {format_bytes(info.file_size)}, {info.inspection}{notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
