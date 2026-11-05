"""Build the experiment-scoped two-table retrieval index for fragment v1."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Sequence

from edu_benchmark.learning_resources.fragment_markdown_v1 import (
    FRAGMENT_FIELDNAMES,
    FRAGMENT_V1_1_FIELDNAMES,
)


INDEX_SCHEMA_VERSION = "learning-resource-retrieval-v1"
INDEX_SCHEMA_VERSION_V1_2 = "learning-resource-retrieval-v1.2"
RETRIEVAL_ELIGIBILITY_POLICY_V1_2 = {
    "policy_version": "retrieval-eligibility-v1.2",
    "fragment_release": "v1.1",
    "measurement_field": "effective_content_length",
    "eligible_when": "effective_content_length > 0",
    "excluded_reason": "zero_effective_content",
    "non_filtering_fields": [
        "status",
        "needs_hnmu_review",
        "fragment_type",
        "merge_status",
        "merged_from_fragment_count",
    ],
}
INTEGER_COLUMNS = {
    "fragment_index",
    "order_index",
    "char_start",
    "char_end",
    "section_depth",
    "caption_char_start",
    "caption_char_end",
    "effective_content_length",
    "merged_from_fragment_count",
    "source_fragment_index_start",
    "source_fragment_index_end",
}
INDEX_METADATA_COLUMNS = (
    "fragment_snapshot_sha256",
    "sections_snapshot_sha256",
    "validation_snapshot_sha256",
    "merge_contract_sha256",
    "retrieval_eligibility_policy_sha256",
    "index_schema_version",
)


class RetrievalIndexV1Error(ValueError):
    """Raised when a fragment snapshot cannot produce a valid v1 index."""


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_sha256(value: object) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _read_fragment_rows(path: Path) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    if not path.is_file():
        raise RetrievalIndexV1Error(f"Fragment snapshot does not exist: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = tuple(reader.fieldnames or ())
        missing = [name for name in FRAGMENT_FIELDNAMES if name not in fieldnames]
        if missing:
            raise RetrievalIndexV1Error(
                "Fragment snapshot is missing required columns: " + ", ".join(missing)
            )
        rows = list(reader)
    if not rows:
        raise RetrievalIndexV1Error("Fragment snapshot must contain at least one row")
    extension_fields = tuple(
        field for field in FRAGMENT_V1_1_FIELDNAMES if field not in FRAGMENT_FIELDNAMES
    )
    present_extensions = [field for field in extension_fields if field in fieldnames]
    if present_extensions and len(present_extensions) != len(extension_fields):
        raise RetrievalIndexV1Error(
            "Fragment v1.1 snapshot has a partial lineage schema: "
            + ", ".join(present_extensions)
        )
    snapshot_fields = (
        tuple(FRAGMENT_V1_1_FIELDNAMES)
        if len(present_extensions) == len(extension_fields)
        else tuple(FRAGMENT_FIELDNAMES)
    )
    return rows, snapshot_fields


def _load_validation_summary(
    *,
    validation_summary_path: Path | None,
    fragments_sha256: str,
    fragment_count: int,
    sections_path: Path | None,
    is_v1_1: bool,
) -> tuple[str, str, str]:
    sections_sha256 = sha256_file(sections_path) if sections_path else ""
    if validation_summary_path is None:
        if is_v1_1:
            raise RetrievalIndexV1Error(
                "Fragment v1.1 requires its validation summary and merge contract"
            )
        return sections_sha256, "", ""
    if not validation_summary_path.is_file():
        raise RetrievalIndexV1Error(
            f"Validation summary does not exist: {validation_summary_path}"
        )
    validation_sha256 = sha256_file(validation_summary_path)
    data = json.loads(validation_summary_path.read_text(encoding="utf-8"))
    if data.get("lossless") is not True:
        raise RetrievalIndexV1Error("Fragment validation summary is not lossless")
    if data.get("fragments_sha256") != fragments_sha256:
        raise RetrievalIndexV1Error("Fragment snapshot hash differs from validation summary")
    if int(data.get("fragment_count", -1)) != fragment_count:
        raise RetrievalIndexV1Error("Fragment row count differs from validation summary")
    if sections_path is not None and data.get("sections_sha256") != sections_sha256:
        raise RetrievalIndexV1Error("Section snapshot hash differs from validation summary")
    merge_contract_sha256 = ""
    if is_v1_1:
        if data.get("fragment_release") != "v1.1":
            raise RetrievalIndexV1Error("Validation summary is not for fragment v1.1")
        contract = data.get("merge_contract")
        if not isinstance(contract, dict):
            raise RetrievalIndexV1Error("Fragment v1.1 validation lacks merge_contract")
        claimed_hash = str(data.get("merge_contract_sha256", ""))
        nested_hash = str(contract.get("merge_contract_sha256", ""))
        hash_payload = {
            key: value
            for key, value in contract.items()
            if key != "merge_contract_sha256"
        }
        serialized = json.dumps(
            hash_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        actual_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        if not claimed_hash or claimed_hash != nested_hash or claimed_hash != actual_hash:
            raise RetrievalIndexV1Error("Fragment v1.1 merge contract hash is invalid")
        merge_contract_sha256 = claimed_hash
    return sections_sha256, validation_sha256, merge_contract_sha256


def _validate_v1_1_rows(rows: Sequence[dict[str, str]]) -> None:
    """Reject mixed or incomplete v1/v1.1 lineage before indexing."""

    source_fragment_ids: list[str] = []
    policy_versions: set[str] = set()
    for row in rows:
        fragment_id = row.get("fragment_id", "<unknown>")
        if row.get("fragment_release") != "v1.1":
            raise RetrievalIndexV1Error(
                f"Fragment row is not release v1.1: {fragment_id}"
            )
        try:
            source_ids = json.loads(row.get("merged_from_fragment_ids_json", ""))
            source_types = json.loads(row.get("source_fragment_types_json", ""))
        except json.JSONDecodeError as exc:
            raise RetrievalIndexV1Error(
                f"Invalid v1.1 lineage JSON: {fragment_id}"
            ) from exc
        if not isinstance(source_ids, list) or not isinstance(source_types, list):
            raise RetrievalIndexV1Error(f"Invalid v1.1 lineage arrays: {fragment_id}")
        if len(source_ids) != len(source_types) or len(source_ids) != int(
            row.get("merged_from_fragment_count", "0")
        ):
            raise RetrievalIndexV1Error(f"Inconsistent v1.1 lineage: {fragment_id}")
        if set(source_types) - {"text", "table"}:
            raise RetrievalIndexV1Error(f"Invalid source fragment type: {fragment_id}")
        start = int(row.get("source_fragment_index_start", "0"))
        end = int(row.get("source_fragment_index_end", "0"))
        if start <= 0 or end - start + 1 != len(source_ids):
            raise RetrievalIndexV1Error(
                f"Non-contiguous v1.1 lineage span: {fragment_id}"
            )
        if source_types.count("table") > 1:
            raise RetrievalIndexV1Error(
                f"v1.1 row contains a forbidden table-table merge: {fragment_id}"
            )
        if "table" in source_types and "text" in source_types:
            if row.get("fragment_type") != "text":
                raise RetrievalIndexV1Error(
                    f"Mixed-source v1.1 row must be text: {fragment_id}"
                )
        source_fragment_ids.extend(str(value) for value in source_ids)
        policy_version = str(row.get("merge_policy_version", "")).strip()
        if not policy_version:
            raise RetrievalIndexV1Error(
                f"v1.1 row lacks merge_policy_version: {fragment_id}"
            )
        policy_versions.add(policy_version)
    if len(source_fragment_ids) != len(set(source_fragment_ids)):
        raise RetrievalIndexV1Error(
            "v1.1 source lineage does not cover source fragments uniquely"
        )
    if len(policy_versions) != 1:
        raise RetrievalIndexV1Error("v1.1 rows contain multiple merge policy versions")


def _select_retrieval_eligible_rows(
    rows: Sequence[dict[str, str]],
    *,
    is_v1_1: bool,
) -> tuple[list[dict[str, str]], dict[str, Any], str]:
    """Select searchable rows without changing the lossless fragment bundle."""

    if not is_v1_1:
        policy = {
            "policy_version": "retrieval-eligibility-v1-legacy-all",
            "fragment_release": "v1",
            "eligible_when": "all source rows",
        }
        policy_sha256 = _canonical_json_sha256(policy)
        unit_ids = {
            str(row.get("ocr_text_id", "")).strip()
            for row in rows
            if str(row.get("ocr_text_id", "")).strip()
        }
        summary = {
            "policy": policy,
            "policy_sha256": policy_sha256,
            "source_fragment_count": len(rows),
            "retrieval_eligible_fragment_count": len(rows),
            "retrieval_excluded_fragment_count": 0,
            "excluded_reason_counts": {},
            "source_unit_count": len(unit_ids),
            "retrieval_eligible_unit_count": len(unit_ids),
            "units_without_eligible_fragments": [],
            "eligible_fragment_ids_sha256": _canonical_json_sha256(
                [str(row["fragment_id"]) for row in rows]
            ),
        }
        return list(rows), summary, policy_sha256

    policy = dict(RETRIEVAL_ELIGIBILITY_POLICY_V1_2)
    eligible_rows: list[dict[str, str]] = []
    excluded_reason_counts = {"zero_effective_content": 0}
    source_unit_ids: set[str] = set()
    eligible_unit_ids: set[str] = set()
    for row in rows:
        fragment_id = str(row.get("fragment_id", "<unknown>"))
        unit_id = str(row.get("ocr_text_id", "")).strip()
        if not unit_id:
            raise RetrievalIndexV1Error(
                f"Fragment v1.1 row lacks ocr_text_id: {fragment_id}"
            )
        source_unit_ids.add(unit_id)
        try:
            effective_length = int(row.get("effective_content_length", ""))
        except (TypeError, ValueError) as exc:
            raise RetrievalIndexV1Error(
                f"Invalid effective_content_length: {fragment_id}"
            ) from exc
        if effective_length < 0:
            raise RetrievalIndexV1Error(
                f"Negative effective_content_length: {fragment_id}"
            )
        if effective_length == 0:
            excluded_reason_counts["zero_effective_content"] += 1
            continue
        eligible_rows.append(row)
        eligible_unit_ids.add(unit_id)

    units_without_eligible_fragments = sorted(source_unit_ids - eligible_unit_ids)
    if units_without_eligible_fragments:
        preview = ", ".join(units_without_eligible_fragments[:5])
        raise RetrievalIndexV1Error(
            "Retrieval eligibility would remove every fragment from unit(s): "
            + preview
        )
    if not eligible_rows:
        raise RetrievalIndexV1Error("Retrieval eligibility selected no fragments")

    policy_sha256 = _canonical_json_sha256(policy)
    summary = {
        "policy": policy,
        "policy_sha256": policy_sha256,
        "source_fragment_count": len(rows),
        "retrieval_eligible_fragment_count": len(eligible_rows),
        "retrieval_excluded_fragment_count": len(rows) - len(eligible_rows),
        "excluded_reason_counts": excluded_reason_counts,
        "source_unit_count": len(source_unit_ids),
        "retrieval_eligible_unit_count": len(eligible_unit_ids),
        "units_without_eligible_fragments": units_without_eligible_fragments,
        "eligible_fragment_ids_sha256": _canonical_json_sha256(
            [str(row["fragment_id"]) for row in eligible_rows]
        ),
    }
    return eligible_rows, summary, policy_sha256


def _column_declarations(fragment_fieldnames: Sequence[str]) -> str:
    declarations: list[str] = []
    for name in fragment_fieldnames:
        column_type = "INTEGER" if name in INTEGER_COLUMNS else "TEXT"
        if name == "fragment_id":
            declarations.append(f"{name} {column_type} PRIMARY KEY")
        else:
            declarations.append(f"{name} {column_type}")
    declarations.extend(
        [
            "fragment_snapshot_sha256 TEXT NOT NULL",
            "sections_snapshot_sha256 TEXT NOT NULL",
            "validation_snapshot_sha256 TEXT NOT NULL",
            "merge_contract_sha256 TEXT NOT NULL",
            "retrieval_eligibility_policy_sha256 TEXT NOT NULL",
            "index_schema_version TEXT NOT NULL",
        ]
    )
    return ",\n                ".join(declarations)


def _create_schema(
    conn: sqlite3.Connection,
    *,
    fragment_fieldnames: Sequence[str],
) -> None:
    """Create two logical tables; FTS5 manages its own shadow tables."""

    conn.executescript(
        f"""
        CREATE TABLE learning_fragments (
                {_column_declarations(fragment_fieldnames)}
        );

        CREATE VIRTUAL TABLE learning_fragments_fts USING fts5(
            fragment_id UNINDEXED,
            section_path,
            markdown_text,
            content='learning_fragments',
            content_rowid='rowid',
            tokenize='unicode61'
        );
        """
    )


def _coerce_fragment_row(
    row: dict[str, str],
    *,
    fragment_fieldnames: Sequence[str],
    fragments_sha256: str,
    sections_sha256: str,
    validation_sha256: str,
    merge_contract_sha256: str,
    retrieval_eligibility_policy_sha256: str,
    index_schema_version: str,
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name in fragment_fieldnames:
        value: Any = row.get(name, "")
        if name in INTEGER_COLUMNS:
            value = int(value) if str(value).strip() else None
        output[name] = value
    output.update(
        {
            "fragment_snapshot_sha256": fragments_sha256,
            "sections_snapshot_sha256": sections_sha256,
            "validation_snapshot_sha256": validation_sha256,
            "merge_contract_sha256": merge_contract_sha256,
            "retrieval_eligibility_policy_sha256": (
                retrieval_eligibility_policy_sha256
            ),
            "index_schema_version": index_schema_version,
        }
    )
    return output


def _insert_rows(
    conn: sqlite3.Connection,
    rows: Sequence[dict[str, str]],
    *,
    fragment_fieldnames: Sequence[str],
    fragments_sha256: str,
    sections_sha256: str,
    validation_sha256: str,
    merge_contract_sha256: str,
    retrieval_eligibility_policy_sha256: str,
    index_schema_version: str,
) -> None:
    columns = tuple(fragment_fieldnames) + INDEX_METADATA_COLUMNS
    column_sql = ", ".join(columns)
    value_sql = ", ".join(f":{name}" for name in columns)
    prepared = [
        _coerce_fragment_row(
            row,
            fragment_fieldnames=fragment_fieldnames,
            fragments_sha256=fragments_sha256,
            sections_sha256=sections_sha256,
            validation_sha256=validation_sha256,
            merge_contract_sha256=merge_contract_sha256,
            retrieval_eligibility_policy_sha256=(
                retrieval_eligibility_policy_sha256
            ),
            index_schema_version=index_schema_version,
        )
        for row in rows
    ]
    conn.executemany(
        f"INSERT INTO learning_fragments ({column_sql}) VALUES ({value_sql})",
        prepared,
    )
    conn.execute(
        "INSERT INTO learning_fragments_fts(learning_fragments_fts) "
        "VALUES ('rebuild')"
    )


def _validate_built_index(
    conn: sqlite3.Connection,
    *,
    expected_count: int,
    expected_snapshot_sha256: str,
    expected_merge_contract_sha256: str,
    expected_retrieval_eligibility_policy_sha256: str,
) -> dict[str, Any]:
    fragment_count = int(
        conn.execute("SELECT COUNT(*) FROM learning_fragments").fetchone()[0]
    )
    fts_count = int(
        conn.execute("SELECT COUNT(*) FROM learning_fragments_fts").fetchone()[0]
    )
    if fragment_count != expected_count or fts_count != expected_count:
        raise RetrievalIndexV1Error(
            "Base/FTS row count mismatch: "
            f"expected={expected_count}, base={fragment_count}, fts={fts_count}"
        )
    snapshots = {
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT fragment_snapshot_sha256 FROM learning_fragments"
        )
    }
    if snapshots != {expected_snapshot_sha256}:
        raise RetrievalIndexV1Error("Index contains an inconsistent fragment snapshot hash")
    merge_contracts = {
        str(row[0])
        for row in conn.execute(
            "SELECT DISTINCT merge_contract_sha256 FROM learning_fragments"
        )
    }
    if merge_contracts != {expected_merge_contract_sha256}:
        raise RetrievalIndexV1Error("Index contains an inconsistent merge contract hash")
    eligibility_policies = {
        str(row[0])
        for row in conn.execute(
            "SELECT DISTINCT retrieval_eligibility_policy_sha256 "
            "FROM learning_fragments"
        )
    }
    if eligibility_policies != {expected_retrieval_eligibility_policy_sha256}:
        raise RetrievalIndexV1Error(
            "Index contains an inconsistent retrieval eligibility policy hash"
        )
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RetrievalIndexV1Error(f"SQLite integrity check failed: {integrity}")
    return {
        "fragment_count": fragment_count,
        "fts_count": fts_count,
        "logical_tables": ["learning_fragments", "learning_fragments_fts"],
        "sqlite_integrity": integrity,
    }


def build_index_v1(
    *,
    fragments_path: Path,
    output_path: Path,
    sections_path: Path | None = None,
    validation_summary_path: Path | None = None,
) -> dict[str, Any]:
    """Atomically build the two-table v1 index from a fragment snapshot."""

    rows, fragment_fieldnames = _read_fragment_rows(fragments_path)
    index_schema_version = (
        INDEX_SCHEMA_VERSION_V1_2
        if tuple(fragment_fieldnames) == tuple(FRAGMENT_V1_1_FIELDNAMES)
        else INDEX_SCHEMA_VERSION
    )
    is_v1_1 = index_schema_version == INDEX_SCHEMA_VERSION_V1_2
    if is_v1_1:
        _validate_v1_1_rows(rows)
    fragments_sha256 = sha256_file(fragments_path)
    sections_sha256, validation_sha256, merge_contract_sha256 = (
        _load_validation_summary(
            validation_summary_path=validation_summary_path,
            fragments_sha256=fragments_sha256,
            fragment_count=len(rows),
            sections_path=sections_path,
            is_v1_1=is_v1_1,
        )
    )
    eligible_rows, eligibility_summary, eligibility_policy_sha256 = (
        _select_retrieval_eligible_rows(rows, is_v1_1=is_v1_1)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        dir=output_path.parent,
        delete=False,
    )
    temporary_path = Path(handle.name)
    handle.close()
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(temporary_path)
        _create_schema(conn, fragment_fieldnames=fragment_fieldnames)
        _insert_rows(
            conn,
            eligible_rows,
            fragment_fieldnames=fragment_fieldnames,
            fragments_sha256=fragments_sha256,
            sections_sha256=sections_sha256,
            validation_sha256=validation_sha256,
            merge_contract_sha256=merge_contract_sha256,
            retrieval_eligibility_policy_sha256=eligibility_policy_sha256,
            index_schema_version=index_schema_version,
        )
        conn.commit()
        validation = _validate_built_index(
            conn,
            expected_count=len(eligible_rows),
            expected_snapshot_sha256=fragments_sha256,
            expected_merge_contract_sha256=merge_contract_sha256,
            expected_retrieval_eligibility_policy_sha256=(
                eligibility_policy_sha256
            ),
        )
        conn.close()
        conn = None
        os.replace(temporary_path, output_path)
    except Exception:
        if conn is not None:
            conn.close()
        temporary_path.unlink(missing_ok=True)
        raise
    return {
        "index_schema_version": index_schema_version,
        "fragment_release": "v1.1" if is_v1_1 else "v1",
        "index_path": output_path.as_posix(),
        "fragments_path": fragments_path.as_posix(),
        "fragment_snapshot_sha256": fragments_sha256,
        "sections_path": sections_path.as_posix() if sections_path else None,
        "sections_snapshot_sha256": sections_sha256 or None,
        "validation_summary_path": (
            validation_summary_path.as_posix() if validation_summary_path else None
        ),
        "validation_snapshot_sha256": validation_sha256 or None,
        "merge_contract_sha256": merge_contract_sha256 or None,
        "retrieval_eligibility": eligibility_summary,
        **validation,
    }


def write_index_validation_summary(summary: dict[str, Any], output_path: Path) -> None:
    """Atomically write a machine-readable index validation summary."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        dir=output_path.parent,
        delete=False,
    ) as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temporary_path = Path(handle.name)
    os.replace(temporary_path, output_path)
