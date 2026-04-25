from __future__ import annotations

import re
import struct
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


INSPECTABLE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg", ".pdf"}
LIMITED_EXTENSIONS = {".psd", ".psb", ".ai", ".eps", ".tif", ".tiff", ".indd", ".idml"}
DELIVERY_EXTENSIONS = INSPECTABLE_EXTENSIONS | LIMITED_EXTENSIONS
SKIP_DIR_NAMES = {"__pycache__", ".git", ".svn", ".hg", "node_modules"}
SKIP_FILE_SUFFIXES = {".pyc", ".tmp", ".ds_store"}


@dataclass
class AssetInfo:
    path: Path
    rel_path: str
    extension: str
    file_size: int
    modified: str
    width: int | None = None
    height: int | None = None
    color_hint: str = ""
    transparency_hint: str = ""
    inspection: str = "metadata"
    notes: str = ""


def iter_delivery_files(root: Path, known_only: bool = False) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        lowered_parts = {part.lower() for part in path.parts}
        if lowered_parts & SKIP_DIR_NAMES:
            continue
        if path.suffix.lower() in SKIP_FILE_SUFFIXES:
            continue
        if known_only and path.suffix.lower() not in DELIVERY_EXTENSIONS:
            continue
        yield path


def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{int(value)} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def root_from_arg(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Path does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Path is not a folder: {root}")
    return root


def inspect_asset(path: Path, root: Path) -> AssetInfo:
    stat = path.stat()
    info = AssetInfo(
        path=path,
        rel_path=path.relative_to(root).as_posix(),
        extension=path.suffix.lower(),
        file_size=stat.st_size,
        modified=datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
    )
    if info.file_size == 0:
        info.notes = append_note(info.notes, "empty_file")
        return info

    try:
        if info.extension == ".png":
            _inspect_png(path, info)
        elif info.extension in {".jpg", ".jpeg"}:
            _inspect_jpeg(path, info)
        elif info.extension == ".gif":
            _inspect_gif(path, info)
        elif info.extension == ".bmp":
            _inspect_bmp(path, info)
        elif info.extension == ".webp":
            _inspect_webp(path, info)
        elif info.extension == ".svg":
            _inspect_svg(path, info)
        elif info.extension == ".pdf":
            _inspect_pdf(path, info)
        elif info.extension in LIMITED_EXTENSIONS:
            info.inspection = "limited"
            info.color_hint = _limited_type_label(info.extension)
            info.notes = append_note(info.notes, "inspection_limited_source_or_print_file")
        else:
            info.inspection = "limited"
            info.notes = append_note(info.notes, "unknown_extension_metadata_only")
    except Exception as exc:  # noqa: BLE001
        info.inspection = "limited"
        info.notes = append_note(info.notes, f"inspect_error:{exc.__class__.__name__}")

    if info.extension in INSPECTABLE_EXTENSIONS - {".svg", ".pdf"}:
        if not info.width or not info.height:
            info.notes = append_note(info.notes, "dimensions_not_detected")
        elif info.width < 300 or info.height < 300:
            info.notes = append_note(info.notes, "small_dimensions")
    if info.file_size > 50 * 1024 * 1024:
        info.notes = append_note(info.notes, "large_file_over_50mb")
    return info


def append_note(existing: str, note: str) -> str:
    return note if not existing else f"{existing};{note}"


def safe_csv_value(value: object) -> object:
    return "" if value is None else value


def relative_or_name(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def has_non_ascii(text: str) -> bool:
    try:
        text.encode("ascii")
        return False
    except UnicodeEncodeError:
        return True


def risky_final_name(stem: str) -> bool:
    normalized = re.sub(r"[\s\-]+", "_", stem.lower())
    return any(token in normalized for token in ["final_final", "final2", "final3", "last", "real_final"])


def duplicate_filename_keys(paths: Iterable[Path], root: Path) -> set[tuple[str, str]]:
    groups: dict[tuple[str, str], list[Path]] = {}
    for path in paths:
        parent = relative_or_name(path.parent, root).lower()
        key = (parent, path.name.lower())
        groups.setdefault(key, []).append(path)
    return {key for key, grouped in groups.items() if len(grouped) > 1}


def cross_format_stem_keys(paths: Iterable[Path], root: Path) -> set[tuple[str, str]]:
    groups: dict[tuple[str, str], set[str]] = {}
    for path in paths:
        parent = relative_or_name(path.parent, root).lower()
        key = (parent, path.stem.lower())
        groups.setdefault(key, set()).add(path.suffix.lower())
    return {key for key, suffixes in groups.items() if len(suffixes) > 1}


def _limited_type_label(extension: str) -> str:
    return {
        ".psd": "photoshop_source",
        ".psb": "photoshop_large_source",
        ".ai": "illustrator_source",
        ".eps": "eps_vector_or_print",
        ".tif": "tiff_raster_or_print",
        ".tiff": "tiff_raster_or_print",
        ".indd": "indesign_source",
        ".idml": "indesign_exchange",
    }.get(extension, "source_or_delivery_file")


def _read_prefix(path: Path, size: int) -> bytes:
    with path.open("rb") as handle:
        return handle.read(size)


def _inspect_png(path: Path, info: AssetInfo) -> None:
    data = _read_prefix(path, 4096)
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 33:
        info.notes = append_note(info.notes, "invalid_png_signature")
        return
    info.width, info.height = struct.unpack(">II", data[16:24])
    color_type = data[25]
    info.color_hint = {0: "grayscale", 2: "rgb", 3: "indexed", 4: "grayscale_alpha", 6: "rgba"}.get(
        color_type, f"png_color_type_{color_type}"
    )
    if color_type in {4, 6} or b"tRNS" in data:
        info.transparency_hint = "possible_transparency"


def _inspect_jpeg(path: Path, info: AssetInfo) -> None:
    with path.open("rb") as handle:
        if handle.read(2) != b"\xff\xd8":
            info.notes = append_note(info.notes, "invalid_jpeg_signature")
            return
        while True:
            marker_start = handle.read(1)
            if not marker_start:
                break
            if marker_start != b"\xff":
                continue
            marker = handle.read(1)
            if not marker:
                break
            marker_value = marker[0]
            if marker_value in {0xD8, 0xD9}:
                continue
            raw_length = handle.read(2)
            if len(raw_length) != 2:
                break
            length = struct.unpack(">H", raw_length)[0]
            if length < 2:
                break
            if marker_value in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                segment = handle.read(length - 2)
                if len(segment) >= 6:
                    info.height, info.width = struct.unpack(">HH", segment[1:5])
                    channels = segment[5]
                    info.color_hint = {1: "grayscale", 3: "rgb", 4: "cmyk_or_ycck"}.get(
                        channels, f"{channels}_channels"
                    )
                return
            handle.seek(length - 2, 1)
    info.notes = append_note(info.notes, "jpeg_size_not_found")


def _inspect_gif(path: Path, info: AssetInfo) -> None:
    data = _read_prefix(path, 4096)
    if not (data.startswith(b"GIF87a") or data.startswith(b"GIF89a")) or len(data) < 10:
        info.notes = append_note(info.notes, "invalid_gif_signature")
        return
    info.width, info.height = struct.unpack("<HH", data[6:10])
    info.color_hint = "indexed"
    if b"\x21\xf9" in data:
        info.transparency_hint = "possible_transparency"


def _inspect_bmp(path: Path, info: AssetInfo) -> None:
    data = _read_prefix(path, 64)
    if not data.startswith(b"BM") or len(data) < 30:
        info.notes = append_note(info.notes, "invalid_bmp_signature")
        return
    info.width, height = struct.unpack("<ii", data[18:26])
    info.height = abs(height)
    bpp = struct.unpack("<H", data[28:30])[0]
    info.color_hint = f"{bpp}_bpp"
    if bpp == 32:
        info.transparency_hint = "possible_alpha"


def _inspect_webp(path: Path, info: AssetInfo) -> None:
    data = _read_prefix(path, 64)
    if not (data.startswith(b"RIFF") and data[8:12] == b"WEBP"):
        info.notes = append_note(info.notes, "invalid_webp_signature")
        return
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        flags = data[20]
        info.width = 1 + int.from_bytes(data[24:27], "little")
        info.height = 1 + int.from_bytes(data[27:30], "little")
        if flags & 0x10:
            info.transparency_hint = "possible_transparency"
    elif chunk == b"VP8 " and len(data) >= 30:
        info.width, info.height = struct.unpack("<HH", data[26:30])
    elif chunk == b"VP8L" and len(data) >= 25:
        bits = int.from_bytes(data[21:25], "little")
        info.width = (bits & 0x3FFF) + 1
        info.height = ((bits >> 14) & 0x3FFF) + 1
        info.transparency_hint = "possible_transparency"
    else:
        info.notes = append_note(info.notes, "webp_size_not_found")


def _inspect_svg(path: Path, info: AssetInfo) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    viewbox = re.search(r'viewBox\s*=\s*["\']([^"\']+)["\']', text, re.I)
    if viewbox:
        parts = re.split(r"[\s,]+", viewbox.group(1).strip())
        if len(parts) == 4:
            try:
                info.width = round(float(parts[2]))
                info.height = round(float(parts[3]))
            except ValueError:
                pass
    if not info.width or not info.height:
        width = _svg_dimension(text, "width")
        height = _svg_dimension(text, "height")
        if width and height:
            info.width = round(width)
            info.height = round(height)
    lower = text.lower()
    if "<text" in lower:
        info.notes = append_note(info.notes, "contains_text")
    if "<image" in lower:
        info.notes = append_note(info.notes, "contains_embedded_or_linked_image")
    if "href=" in lower and "data:" not in lower:
        info.notes = append_note(info.notes, "contains_external_href")
    if not viewbox:
        info.notes = append_note(info.notes, "missing_viewbox")
    info.color_hint = "vector"


def _svg_dimension(text: str, attr: str) -> float | None:
    match = re.search(rf'{attr}\s*=\s*["\']([0-9.]+)', text, re.I)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _inspect_pdf(path: Path, info: AssetInfo) -> None:
    data = _read_prefix(path, 2_000_000)
    if not data.startswith(b"%PDF"):
        info.notes = append_note(info.notes, "invalid_pdf_signature")
        return
    text = data.decode("latin-1", errors="ignore")
    pages = len(re.findall(r"/Type\s*/Page\b", text))
    if pages:
        info.notes = append_note(info.notes, f"pages:{pages}")
    media = re.search(r"/MediaBox\s*\[\s*[-0-9.]+\s+[-0-9.]+\s+([0-9.]+)\s+([0-9.]+)", text)
    if media:
        info.width = round(float(media.group(1)))
        info.height = round(float(media.group(2)))
        info.notes = append_note(info.notes, "pdf_dimensions_in_points")
    info.color_hint = "pdf"
