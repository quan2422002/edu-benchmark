"""Authenticated read-only portal for reviewing learning-resource fragments."""

from __future__ import annotations

import base64
import csv
import gzip
import hashlib
import hmac
import json
import mimetypes
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import unquote, urlparse

from .config import PortalConfig, ReviewProductsConfig


class PortalDataError(ValueError):
    """Raised when fragment, image, or PDF portal data is invalid."""


MARKDOWN_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HTML_IMAGE_RE = re.compile(
    r"<img\b[^>]*?\bsrc\s*=\s*([\"'])(?P<src>.*?)\1[^>]*>", re.IGNORECASE
)
PDF_NAME_RE = re.compile(r"^(?P<kind>sgk|sgv|sbt)_tin_hoc_(?P<grade>[6-9])\.pdf$")
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/portal.css": ("portal.css", "text/css; charset=utf-8"),
    "/portal.js": ("portal.js", "text/javascript; charset=utf-8"),
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise PortalDataError(f"Fragment CSV has no header: {path}")
        required = {
            "fragment_id",
            "learning_material_id",
            "ocr_text_id",
            "material_type",
            "grade",
            "book_title",
            "lesson_key",
            "lesson_title",
            "topic_title",
            "section_path",
            "fragment_type",
            "source_markdown_path",
            "markdown_text",
            "status",
            "effective_content_length",
            "order_index",
        }
        missing = required - set(reader.fieldnames)
        if missing:
            raise PortalDataError(f"Fragment CSV is missing columns: {sorted(missing)}")
        return [dict(row) for row in reader]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _path_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _image_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if " " in target:
        candidate, _, suffix = target.partition(" ")
        if suffix.strip().startswith(("\"", "'")):
            target = candidate
    return unquote(target)


def _asset_id(repository_relative_path: str) -> str:
    return hashlib.sha256(repository_relative_path.encode("utf-8")).hexdigest()[:24]


def _rewrite_images(
    markdown: str,
    *,
    grade: int,
    source_markdown_path: Path,
    repository_root: Path,
    image_root: Path,
    fallback_assets: Mapping[str, tuple[Path, ...]],
    image_assets: dict[str, Path],
    image_paths: dict[str, str],
    missing_images: list[str],
) -> tuple[str, int, int]:
    count = 0
    fallback_count = 0

    def register(raw_target: str, alt: str) -> str:
        nonlocal count, fallback_count
        target = _image_target(raw_target)
        if target.startswith(("http://", "https://", "data:")):
            missing_images.append(f"External image is not allowed: {target}")
            return f"[Ảnh ngoài không được phục vụ: {target}]"
        candidate = (source_markdown_path.parent / target).resolve()
        if not _path_within(candidate, image_root) or not candidate.is_file():
            organized_candidate = (
                source_markdown_path.parent / "images" / Path(target).name
            ).resolve()
            if _path_within(organized_candidate, image_root) and organized_candidate.is_file():
                candidate = organized_candidate
        if not _path_within(candidate, image_root) or not candidate.is_file():
            fallback_candidates = fallback_assets.get(Path(target).name, ())
            grade_candidates = tuple(
                path
                for path in fallback_candidates
                if f"grade_{grade}" in path.parts
            )
            if len(grade_candidates) == 1:
                candidate = grade_candidates[0]
                fallback_count += 1
            elif len(fallback_candidates) == 1:
                candidate = fallback_candidates[0]
                fallback_count += 1
            else:
                candidate = Path()
        if not candidate.is_file():
            missing_images.append(
                f"Missing/unsafe image from {source_markdown_path}: {target}"
            )
            return f"[Không tìm thấy ảnh: {target}]"
        relative = candidate.relative_to(repository_root.resolve()).as_posix()
        token = _asset_id(relative)
        existing = image_assets.get(token)
        if existing is not None and existing != candidate:
            raise PortalDataError(f"Image asset hash collision: {token}")
        image_assets[token] = candidate
        image_paths[token] = relative
        count += 1
        return f"![{alt}](/media/image/{token})"

    def replace_markdown(match: re.Match[str]) -> str:
        return register(match.group(2), match.group(1))

    rewritten = MARKDOWN_IMAGE_RE.sub(replace_markdown, markdown)

    def replace_html(match: re.Match[str]) -> str:
        return register(match.group("src"), "Ảnh học liệu")

    rewritten = HTML_IMAGE_RE.sub(replace_html, rewritten)
    return rewritten, count, fallback_count


def _fallback_image_assets(roots: tuple[Path, ...]) -> dict[str, tuple[Path, ...]]:
    """Index explicitly approved OCR image roots for grade-aware resolution."""

    candidates: dict[str, list[Path]] = {}
    for root in roots:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                candidates.setdefault(path.name, []).append(path.resolve())
    return {
        name: tuple(sorted(set(paths)))
        for name, paths in candidates.items()
    }


@dataclass(frozen=True)
class PortalCatalog:
    fragments: tuple[dict[str, Any], ...]
    fragment_json: bytes
    fragment_json_gzip: bytes
    catalog_json: bytes
    image_assets: Mapping[str, Path]
    image_paths: Mapping[str, str]
    pdf_assets: Mapping[str, Path]
    validation: Mapping[str, Any]


def _pdf_catalog(pdf_root: Path, repository_root: Path) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    pdfs: list[dict[str, Any]] = []
    assets: dict[str, Path] = {}
    kind_labels = {"sgk": "SGK", "sgv": "SGV", "sbt": "SBT"}
    title_labels = {"sgk": "Sách giáo khoa", "sgv": "Sách giáo viên", "sbt": "Sách bài tập"}
    for path in sorted(pdf_root.glob("*.pdf")):
        match = PDF_NAME_RE.fullmatch(path.name)
        if not match:
            raise PortalDataError(f"Unexpected PDF filename: {path.name}")
        kind = match.group("kind")
        grade = int(match.group("grade"))
        assets[path.name] = path.resolve()
        pdfs.append(
            {
                "filename": path.name,
                "grade": grade,
                "material_type": kind_labels[kind],
                "title": f"{title_labels[kind]} Tin học {grade}",
                "url": f"/media/pdf/{path.name}",
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "source_label": "PDF dẫn xuất từ ảnh trang để xem nhanh",
                "repository_path": path.relative_to(repository_root).as_posix(),
            }
        )
    pdfs.sort(key=lambda row: (row["grade"], ("SGK", "SGV", "SBT").index(row["material_type"])))
    return pdfs, assets


def build_portal_catalog(config: ReviewProductsConfig) -> PortalCatalog:
    """Validate and prepare all fragment, image, and PDF data in memory."""

    portal = config.portal
    rows = _read_csv(portal.fragment_csv)
    repository_root = config.repository_root.resolve()
    fragment_ids: set[str] = set()
    fragments: list[dict[str, Any]] = []
    image_assets: dict[str, Path] = {}
    image_paths: dict[str, str] = {}
    fallback_assets = _fallback_image_assets(portal.image_fallback_roots)
    missing_images: list[str] = []
    image_reference_count = 0
    fallback_image_reference_count = 0
    searchable_count = 0
    for row in rows:
        fragment_id = str(row["fragment_id"]).strip()
        if not fragment_id or fragment_id in fragment_ids:
            raise PortalDataError(f"Missing or duplicate fragment_id: {fragment_id}")
        fragment_ids.add(fragment_id)
        source_markdown_path = (repository_root / row["source_markdown_path"]).resolve()
        if not source_markdown_path.is_file():
            raise PortalDataError(f"Missing source Markdown: {row['source_markdown_path']}")
        if not _path_within(source_markdown_path, portal.image_root):
            raise PortalDataError(
                f"Source Markdown is outside the approved OCR root: {source_markdown_path}"
            )
        try:
            effective_length = int(row["effective_content_length"])
            grade = int(row["grade"])
            order_index = int(row["order_index"])
        except ValueError as exc:
            raise PortalDataError(f"Invalid numeric fragment field: {fragment_id}") from exc
        rewritten, image_count, fallback_image_count = _rewrite_images(
            str(row["markdown_text"]),
            grade=grade,
            source_markdown_path=source_markdown_path,
            repository_root=repository_root,
            image_root=portal.image_root,
            fallback_assets=fallback_assets,
            image_assets=image_assets,
            image_paths=image_paths,
            missing_images=missing_images,
        )
        image_reference_count += image_count
        fallback_image_reference_count += fallback_image_count
        searchable = effective_length > 0
        searchable_count += int(searchable)
        fragments.append(
            {
                "fragment_id": fragment_id,
                "learning_material_id": row["learning_material_id"],
                "ocr_text_id": row["ocr_text_id"],
                "grade": grade,
                "material_type": row["material_type"],
                "book_title": row["book_title"],
                "lesson_key": row["lesson_key"],
                "lesson_title": row["lesson_title"],
                "topic_title": row["topic_title"],
                "section_path": row["section_path"],
                "fragment_type": row["fragment_type"],
                "page_start": row.get("page_start", ""),
                "page_end": row.get("page_end", ""),
                "order_index": order_index,
                "status": row["status"],
                "searchable": searchable,
                "effective_content_length": effective_length,
                "markdown_text": rewritten,
                "image_count": image_count,
            }
        )
    if missing_images:
        preview = "\n".join(missing_images[:20])
        raise PortalDataError(
            f"Portal validation found {len(missing_images)} missing/unsafe images:\n{preview}"
        )
    fragments.sort(
        key=lambda row: (
            row["grade"],
            row["material_type"],
            row["book_title"],
            row["lesson_key"],
            row["order_index"],
            row["fragment_id"],
        )
    )
    pdfs, pdf_assets = _pdf_catalog(portal.pdf_root, repository_root)
    if len(pdfs) != 11:
        raise PortalDataError(f"Expected 11 derived PDFs, found {len(pdfs)}")
    if any(row["material_type"] == "SBT" and row["grade"] == 9 for row in pdfs):
        raise PortalDataError("SBT grade 9 must not be exposed by the current portal")

    options = {
        "grades": sorted({row["grade"] for row in fragments}),
        "material_types": sorted({row["material_type"] for row in fragments}),
        "books": sorted({row["book_title"] for row in fragments}),
        "lessons": sorted({row["lesson_title"] for row in fragments}),
        "fragment_types": sorted({row["fragment_type"] for row in fragments}),
    }
    validation = {
        "schema_version": "plan04-learning-resource-portal-validation-v1",
        "experiment_id": config.experiment_id,
        "created_at": datetime.now(UTC).isoformat(),
        "fragment_csv": portal.fragment_csv.relative_to(repository_root).as_posix(),
        "fragment_csv_sha256": _sha256(portal.fragment_csv),
        "fragment_count": len(fragments),
        "unique_fragment_count": len(fragment_ids),
        "searchable_fragment_count": searchable_count,
        "storage_only_fragment_count": len(fragments) - searchable_count,
        "image_reference_count": image_reference_count,
        "unique_image_asset_count": len(image_assets),
        "fallback_image_root_count": len(portal.image_fallback_roots),
        "fallback_image_asset_count": len(fallback_assets),
        "fallback_image_reference_count": fallback_image_reference_count,
        "missing_image_count": 0,
        "pdf_count": len(pdfs),
        "pdf_total_size_bytes": sum(row["size_bytes"] for row in pdfs),
        "sbt_grade9_present": False,
        "host": portal.host,
        "port": portal.port,
        "max_regex_length": portal.max_regex_length,
    }
    payload = {
        "schema_version": "plan04-learning-resource-portal-data-v1",
        "fragment_count": len(fragments),
        "fragments": fragments,
    }
    catalog_payload = {
        "schema_version": "plan04-learning-resource-portal-catalog-v1",
        "fragment_count": len(fragments),
        "searchable_fragment_count": searchable_count,
        "storage_only_fragment_count": len(fragments) - searchable_count,
        "options": options,
        "pdfs": pdfs,
        "max_regex_length": portal.max_regex_length,
    }
    fragment_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )
    return PortalCatalog(
        fragments=tuple(fragments),
        fragment_json=fragment_json,
        fragment_json_gzip=gzip.compress(fragment_json, compresslevel=6),
        catalog_json=json.dumps(
            catalog_payload, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8"),
        image_assets=image_assets,
        image_paths=image_paths,
        pdf_assets=pdf_assets,
        validation=validation,
    )


def write_portal_validation(config: ReviewProductsConfig, catalog: PortalCatalog) -> Path:
    """Write portal validation atomically at the approved experiment path."""

    path = config.portal.validation_output
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(catalog.validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)
    return path


def _static_bytes(name: str) -> bytes:
    return resources.files("edu_benchmark.review_delivery.static").joinpath(name).read_bytes()


def _parse_basic_auth(header: str | None) -> tuple[str, str] | None:
    if not header or not header.startswith("Basic "):
        return None
    try:
        decoded = base64.b64decode(header[6:], validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None
    if ":" not in decoded:
        return None
    return tuple(decoded.split(":", 1))  # type: ignore[return-value]


def _make_handler(
    *,
    catalog: PortalCatalog,
    username: str,
    password: str,
) -> type[BaseHTTPRequestHandler]:
    class PortalRequestHandler(BaseHTTPRequestHandler):
        server_version = "HNMULearningResourcePortal/1.0"

        def log_message(self, format_string: str, *args: Any) -> None:
            message = format_string % args
            print(f"{self.address_string()} - {message}", flush=True)

        def _security_headers(self) -> None:
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "SAMEORIGIN")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Robots-Tag", "noindex, nofollow, noarchive")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; img-src 'self' data:; style-src 'self'; "
                "script-src 'self'; frame-src 'self'; frame-ancestors 'self'; "
                "base-uri 'none'; form-action 'none'",
            )

        def _authorized(self) -> bool:
            parsed = _parse_basic_auth(self.headers.get("Authorization"))
            if parsed is None:
                return False
            supplied_user, supplied_password = parsed
            return hmac.compare_digest(supplied_user, username) and hmac.compare_digest(
                supplied_password, password
            )

        def _require_auth(self) -> bool:
            if self._authorized():
                return True
            self.send_response(HTTPStatus.UNAUTHORIZED)
            self.send_header("WWW-Authenticate", 'Basic realm="Kho hoc lieu HNMU"')
            self._security_headers()
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return False

        def _send_bytes(
            self,
            body: bytes,
            content_type: str,
            *,
            status: HTTPStatus = HTTPStatus.OK,
            content_encoding: str | None = None,
            cache_control: str = "no-store",
        ) -> None:
            self.send_response(status)
            self._security_headers()
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", cache_control)
            if content_encoding:
                self.send_header("Content-Encoding", content_encoding)
                self.send_header("Vary", "Accept-Encoding")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _send_file(self, path: Path, *, inline_pdf: bool = False) -> None:
            size = path.stat().st_size
            start = 0
            end = size - 1
            status = HTTPStatus.OK
            range_header = self.headers.get("Range")
            if range_header:
                match = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header.strip())
                if not match:
                    self.send_error(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                    return
                left, right = match.groups()
                if left:
                    start = int(left)
                    end = int(right) if right else end
                elif right:
                    suffix = int(right)
                    start = max(0, size - suffix)
                if start < 0 or end < start or end >= size:
                    self.send_error(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                    return
                status = HTTPStatus.PARTIAL_CONTENT
            length = end - start + 1
            self.send_response(status)
            self._security_headers()
            self.send_header(
                "Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            )
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "private, max-age=3600")
            if status == HTTPStatus.PARTIAL_CONTENT:
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            if inline_pdf:
                self.send_header("Content-Disposition", f'inline; filename="{path.name}"')
            self.end_headers()
            if self.command == "HEAD":
                return
            with path.open("rb") as handle:
                handle.seek(start)
                remaining = length
                while remaining:
                    block = handle.read(min(1024 * 1024, remaining))
                    if not block:
                        break
                    self.wfile.write(block)
                    remaining -= len(block)

        def do_HEAD(self) -> None:  # noqa: N802 - stdlib handler contract
            self.do_GET()

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler contract
            path = urlparse(self.path).path
            if path == "/healthz":
                self._send_bytes(b'{"status":"ok"}', "application/json; charset=utf-8")
                return
            if path == "/robots.txt":
                self._send_bytes(b"User-agent: *\nDisallow: /\n", "text/plain; charset=utf-8")
                return
            if not self._require_auth():
                return
            if path in STATIC_FILES:
                name, content_type = STATIC_FILES[path]
                self._send_bytes(
                    _static_bytes(name),
                    content_type,
                    cache_control="private, max-age=300",
                )
                return
            if path == "/api/catalog":
                self._send_bytes(catalog.catalog_json, "application/json; charset=utf-8")
                return
            if path == "/api/fragments":
                if "gzip" in self.headers.get("Accept-Encoding", ""):
                    self._send_bytes(
                        catalog.fragment_json_gzip,
                        "application/json; charset=utf-8",
                        content_encoding="gzip",
                    )
                else:
                    self._send_bytes(
                        catalog.fragment_json, "application/json; charset=utf-8"
                    )
                return
            if path.startswith("/media/image/"):
                token = path.removeprefix("/media/image/")
                image_path = catalog.image_assets.get(token)
                if image_path is None:
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                self._send_file(image_path)
                return
            if path.startswith("/media/pdf/"):
                filename = path.removeprefix("/media/pdf/")
                pdf_path = catalog.pdf_assets.get(filename)
                if pdf_path is None:
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                self._send_file(pdf_path, inline_pdf=True)
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler contract
            self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)

    return PortalRequestHandler


def serve_portal(
    config: ReviewProductsConfig,
    *,
    username: str,
    password: str,
    host: str | None = None,
    port: int | None = None,
) -> None:
    """Run the read-only portal until interrupted."""

    if not username or not password:
        raise PortalDataError("Portal username and password must be non-empty")
    if len(password) < 12:
        raise PortalDataError("Portal password must contain at least 12 characters")
    catalog = build_portal_catalog(config)
    write_portal_validation(config, catalog)
    bind_host = host or config.portal.host
    bind_port = port or config.portal.port
    handler = _make_handler(catalog=catalog, username=username, password=password)
    server = ThreadingHTTPServer((bind_host, bind_port), handler)
    print(
        f"HNMU learning-resource portal ready at http://{bind_host}:{bind_port} "
        f"({len(catalog.fragments)} fragments, {len(catalog.pdf_assets)} PDFs)",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping HNMU learning-resource portal.", flush=True)
    finally:
        server.server_close()


def credentials_from_environment(portal: PortalConfig) -> tuple[str, str]:
    """Load portal credentials without placing them in config or source."""

    username = os.environ.get(portal.username_env, "")
    password = os.environ.get(portal.password_env, "")
    if not username or not password:
        raise PortalDataError(
            f"Set {portal.username_env} and {portal.password_env} before starting the portal"
        )
    return username, password
