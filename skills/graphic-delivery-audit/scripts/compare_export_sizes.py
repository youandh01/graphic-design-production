from __future__ import annotations

import argparse
import csv
import fnmatch
import sys
from pathlib import Path

from asset_utils import inspect_asset, iter_delivery_files, root_from_arg, safe_csv_value


def read_expectations(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"path", "width", "height"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise SystemExit("Expected CSV must include path,width,height columns.")
        return list(reader)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare exported asset dimensions to expected sizes.")
    parser.add_argument("folder", help="Folder containing exported files.")
    parser.add_argument("--expect", required=True, help="CSV with path,width,height columns. path may include wildcards.")
    parser.add_argument("--csv", action="store_true", help="Write CSV to stdout.")
    args = parser.parse_args()

    root = root_from_arg(args.folder)
    expectations = read_expectations(Path(args.expect).expanduser().resolve())
    infos = [inspect_asset(path, root) for path in iter_delivery_files(root, known_only=True)]
    by_path = {info.rel_path.lower(): info for info in infos}

    rows = []
    for item in expectations:
        pattern = item["path"].replace("\\", "/")
        matches = [
            info
            for rel_path, info in by_path.items()
            if fnmatch.fnmatch(rel_path, pattern.lower())
        ]
        if not matches:
            rows.append([pattern, item["width"], item["height"], "", "", "missing"])
            continue
        for info in matches:
            expected_width = int(item["width"])
            expected_height = int(item["height"])
            if info.width is None or info.height is None:
                status = "dimensions_not_detected"
            elif info.width == expected_width and info.height == expected_height:
                status = "ok"
            else:
                status = "size_mismatch"
            rows.append(
                [
                    info.rel_path,
                    expected_width,
                    expected_height,
                    safe_csv_value(info.width),
                    safe_csv_value(info.height),
                    status,
                ]
            )

    if args.csv:
        writer = csv.writer(sys.stdout, lineterminator="\n")
        writer.writerow(["path", "expected_width", "expected_height", "actual_width", "actual_height", "status"])
        writer.writerows(rows)
    else:
        for row in rows:
            print(f"{row[0]}: expected {row[1]}x{row[2]}, actual {row[3]}x{row[4]} [{row[5]}]")
    return 1 if any(row[5] != "ok" for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
