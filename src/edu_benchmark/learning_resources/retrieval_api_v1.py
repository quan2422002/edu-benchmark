"""Unified section/content retrieval API for the fragment v1 index."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


DEFAULT_INDEX_PATH = Path(
    "experiments/20260903_135547/outputs/retrieval_v1_2/learning_resources_v1_2.sqlite"
)
SEARCH_TOOL_NAME = "search_learning_fragments"
TOKEN_RE = re.compile(r"[\wÀ-ỹ]+", re.UNICODE)
FILTER_COLUMNS = frozenset(
    {
        "grade",
        "material_type",
        "lesson_key",
        "fragment_type",
        "status",
        "book_title",
        "ocr_text_id",
        "learning_material_id",
    }
)


class RetrievalV1Error(ValueError):
    """Base error for invalid v1 index or search requests."""


class RetrievalQueryV1Error(RetrievalV1Error):
    """Raised when the two-keyword search contract is violated."""


@dataclass(frozen=True)
class RetrievalResult:
    """Traceable output of one unified section/content search."""

    mode: str
    section_keywords: str | None
    content_keywords: str | None
    filters: dict[str, list[str]]
    content_limit: int
    matched_section_path: str | None
    section_score: float | None
    snapshot_sha256: str
    results: tuple[dict[str, Any], ...]
    section_match_strategy: str | None = None
    reason: str | None = None

    @property
    def result_count(self) -> int:
        return len(self.results)

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable retrieval envelope."""

        return {
            "mode": self.mode,
            "section_keywords": self.section_keywords,
            "content_keywords": self.content_keywords,
            "filters": self.filters,
            "content_limit": self.content_limit,
            "matched_section_path": self.matched_section_path,
            "section_score": self.section_score,
            "section_match_strategy": self.section_match_strategy,
            "snapshot_sha256": self.snapshot_sha256,
            "result_count": self.result_count,
            "reason": self.reason,
            "results": list(self.results),
        }


def connect_v1(index_path: Path = DEFAULT_INDEX_PATH) -> sqlite3.Connection:
    """Open a read-only connection to an existing v1 SQLite index."""

    if not index_path.is_file():
        raise RetrievalV1Error(f"Retrieval index does not exist: {index_path}")
    uri = f"{index_path.resolve().as_uri()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def _keyword(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _fts_expression(column: str, keywords: str) -> str:
    tokens = TOKEN_RE.findall(keywords)
    if not tokens:
        raise RetrievalQueryV1Error(
            f"{column} keywords must contain at least one searchable token"
        )
    unique_tokens: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        key = token.casefold()
        if key not in seen:
            seen.add(key)
            unique_tokens.append(token)
    # OR builds a recall-oriented candidate set. SQLite FTS5 still ranks those
    # candidates with bm25(), while trusted metadata and section scope remain
    # hard filters. Requiring every token with AND made natural-language model
    # queries return no candidates too often.
    terms = " OR ".join(f'"{token}"' for token in unique_tokens)
    return f"{column}:({terms})"


def _as_values(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set, frozenset)):
        items = [str(item).strip() for item in value]
    else:
        items = [str(value).strip()]
    return sorted({item for item in items if item})


def _normalize_filters(
    filters: Mapping[str, object] | None,
) -> dict[str, list[str]]:
    if not filters:
        return {}
    if not isinstance(filters, Mapping):
        raise RetrievalQueryV1Error("filters must be an object or null")
    unknown = sorted(set(filters) - FILTER_COLUMNS)
    if unknown:
        raise RetrievalQueryV1Error(
            "Unsupported retrieval filters: " + ", ".join(unknown)
        )
    return {
        key: values
        for key in sorted(filters)
        if (values := _as_values(filters[key]))
    }


def _filter_clause(
    filters: Mapping[str, list[str]],
    *,
    alias: str = "f",
) -> tuple[list[str], list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    for column, values in filters.items():
        placeholders = ", ".join("?" for _ in values)
        clauses.append(f"{alias}.{column} IN ({placeholders})")
        params.extend(values)
    return clauses, params


def _snapshot_sha256(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        "SELECT DISTINCT fragment_snapshot_sha256 FROM learning_fragments"
    ).fetchall()
    if len(rows) != 1 or not rows[0][0]:
        raise RetrievalV1Error("Index has no unique fragment snapshot hash")
    return str(rows[0][0])


def _path_key(path: str) -> tuple[str, int]:
    normalized = re.sub(r"\s+", " ", path).strip().casefold()
    return normalized, len(path)


def _normalize_section_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return " ".join(token.casefold() for token in TOKEN_RE.findall(normalized))


def _exact_component_scope(path: str, query: str) -> str | None:
    """Return the ancestor ending at an exact normalized path component."""

    normalized_query = _normalize_section_text(query)
    if not normalized_query:
        return None
    components = [component.strip() for component in path.split(" > ")]
    if _normalize_section_text(path) == normalized_query:
        return path
    for index, component in enumerate(components):
        if _normalize_section_text(component) == normalized_query:
            return " > ".join(components[: index + 1])
    return None


def _select_best_section(
    conn: sqlite3.Connection,
    *,
    section_keywords: str,
    filters: Mapping[str, list[str]],
) -> tuple[str, float, str] | None:
    clauses = ["learning_fragments_fts MATCH ?"]
    params: list[Any] = [_fts_expression("section_path", section_keywords)]
    filter_clauses, filter_params = _filter_clause(filters)
    clauses.extend(filter_clauses)
    params.extend(filter_params)
    rows = conn.execute(
        f"""
        SELECT
            f.section_path,
            f.order_index,
            bm25(learning_fragments_fts) AS section_score
        FROM learning_fragments_fts
        JOIN learning_fragments AS f
          ON f.rowid = learning_fragments_fts.rowid
        WHERE {' AND '.join(clauses)}
        """,
        params,
    ).fetchall()
    by_path: dict[str, tuple[float, int]] = {}
    for row in rows:
        path = str(row["section_path"] or "").strip()
        if not path:
            continue
        score = float(row["section_score"])
        order_index = int(row["order_index"] or 0)
        previous = by_path.get(path)
        if previous is None:
            by_path[path] = (score, order_index)
        else:
            by_path[path] = (min(score, previous[0]), min(order_index, previous[1]))
    if not by_path:
        return None
    exact_scopes: dict[str, tuple[float, int]] = {}
    for path, score_and_order in by_path.items():
        scope = _exact_component_scope(path, section_keywords)
        if scope is None:
            continue
        previous = exact_scopes.get(scope)
        if previous is None:
            exact_scopes[scope] = score_and_order
        else:
            exact_scopes[scope] = (
                min(score_and_order[0], previous[0]),
                min(score_and_order[1], previous[1]),
            )
    if exact_scopes:
        path, (score, _) = min(
            exact_scopes.items(),
            key=lambda item: (item[1][0], _path_key(item[0]), item[1][1]),
        )
        return path, score, "exact_component"
    path, (score, _) = min(
        by_path.items(),
        key=lambda item: (item[1][0], _path_key(item[0]), item[1][1]),
    )
    return path, score, "bm25"


def _escape_like(value: str) -> str:
    return value.replace("!", "!!").replace("%", "!%").replace("_", "!_")


def _scope_clause(
    matched_section_path: str,
    *,
    alias: str = "f",
) -> tuple[str, list[str]]:
    descendant_pattern = _escape_like(matched_section_path + " > ") + "%"
    return (
        f"({alias}.section_path = ? OR "
        f"{alias}.section_path LIKE ? ESCAPE '!')",
        [matched_section_path, descendant_pattern],
    )


def _section_fragments(
    conn: sqlite3.Connection,
    *,
    matched_section_path: str,
    filters: Mapping[str, list[str]],
) -> list[dict[str, Any]]:
    scope_sql, scope_params = _scope_clause(matched_section_path)
    clauses = [scope_sql]
    params: list[Any] = list(scope_params)
    filter_clauses, filter_params = _filter_clause(filters)
    clauses.extend(filter_clauses)
    params.extend(filter_params)
    rows = conn.execute(
        f"""
        SELECT f.*, NULL AS content_score
        FROM learning_fragments AS f
        WHERE {' AND '.join(clauses)}
        ORDER BY f.order_index, f.fragment_id
        """,
        params,
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def _content_fragments(
    conn: sqlite3.Connection,
    *,
    content_keywords: str,
    filters: Mapping[str, list[str]],
    content_limit: int,
    matched_section_path: str | None,
) -> list[dict[str, Any]]:
    clauses = ["learning_fragments_fts MATCH ?"]
    params: list[Any] = [_fts_expression("markdown_text", content_keywords)]
    if matched_section_path is not None:
        scope_sql, scope_params = _scope_clause(matched_section_path)
        clauses.append(scope_sql)
        params.extend(scope_params)
    filter_clauses, filter_params = _filter_clause(filters)
    clauses.extend(filter_clauses)
    params.extend(filter_params)
    params.append(content_limit)
    rows = conn.execute(
        f"""
        SELECT f.*, bm25(learning_fragments_fts) AS content_score
        FROM learning_fragments_fts
        JOIN learning_fragments AS f
          ON f.rowid = learning_fragments_fts.rowid
        WHERE {' AND '.join(clauses)}
        ORDER BY content_score, f.fragment_id
        LIMIT ?
        """,
        params,
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def search_learning_fragments(
    section_keywords: str | None,
    content_keywords: str | None,
    *,
    filters: Mapping[str, object] | None = None,
    index_path: Path = DEFAULT_INDEX_PATH,
    content_limit: int = 5,
) -> RetrievalResult:
    """Search by section, content, or content within the best section."""

    section_query = _keyword(section_keywords)
    content_query = _keyword(content_keywords)
    if section_query is None and content_query is None:
        raise RetrievalQueryV1Error(
            "At least one of section_keywords or content_keywords is required"
        )
    if (
        isinstance(content_limit, bool)
        or not isinstance(content_limit, int)
        or not 1 <= content_limit <= 5
    ):
        raise RetrievalQueryV1Error("content_limit must be an integer from 1 to 5")
    normalized_filters = _normalize_filters(filters)
    if section_query and content_query:
        mode = "section_and_content"
    elif section_query:
        mode = "section_only"
    else:
        mode = "content_only"

    with connect_v1(index_path) as conn:
        snapshot = _snapshot_sha256(conn)
        matched_path: str | None = None
        section_score: float | None = None
        section_match_strategy: str | None = None
        if section_query is not None:
            section_match = _select_best_section(
                conn,
                section_keywords=section_query,
                filters=normalized_filters,
            )
            if section_match is None:
                return RetrievalResult(
                    mode=mode,
                    section_keywords=section_query,
                    content_keywords=content_query,
                    filters=normalized_filters,
                    content_limit=content_limit,
                    matched_section_path=None,
                    section_score=None,
                    section_match_strategy=None,
                    snapshot_sha256=snapshot,
                    results=(),
                    reason="section_no_match",
                )
            matched_path, section_score, section_match_strategy = section_match

        if mode == "section_only":
            result_rows = _section_fragments(
                conn,
                matched_section_path=matched_path or "",
                filters=normalized_filters,
            )
        else:
            result_rows = _content_fragments(
                conn,
                content_keywords=content_query or "",
                filters=normalized_filters,
                content_limit=content_limit,
                matched_section_path=matched_path,
            )
    return RetrievalResult(
        mode=mode,
        section_keywords=section_query,
        content_keywords=content_query,
        filters=normalized_filters,
        content_limit=content_limit,
        matched_section_path=matched_path,
        section_score=section_score,
        section_match_strategy=section_match_strategy,
        snapshot_sha256=snapshot,
        results=tuple(result_rows),
        reason=None if result_rows else "content_no_match",
    )


def get_learning_fragment_v1(
    fragment_id: str,
    *,
    index_path: Path = DEFAULT_INDEX_PATH,
) -> dict[str, Any] | None:
    """Return one fragment and all of its v1 provenance by ID."""

    with connect_v1(index_path) as conn:
        row = conn.execute(
            "SELECT * FROM learning_fragments WHERE fragment_id = ?",
            (fragment_id,),
        ).fetchone()
    return _row_to_dict(row) if row else None


def retrieval_tool_definition_v1() -> dict[str, Any]:
    """Return the read-only tool definition used by the later audit agent."""

    return {
        "name": SEARCH_TOOL_NAME,
        "description": (
            "Search learning fragments by section keywords, content keywords, "
            "or content within the best matching section."
        ),
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "section_keywords": {"type": ["string", "null"]},
                "content_keywords": {"type": ["string", "null"]},
                "filters": {"type": ["object", "null"]},
                "content_limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "default": 5,
                },
            },
            "required": ["section_keywords", "content_keywords"],
        },
    }


def dispatch_retrieval_tool_v1(
    tool_name: str,
    arguments: Mapping[str, Any],
    *,
    index_path: Path = DEFAULT_INDEX_PATH,
) -> dict[str, Any]:
    """Execute the one approved read-only retrieval tool and retain its trace."""

    if tool_name != SEARCH_TOOL_NAME:
        raise RetrievalQueryV1Error(f"Unsupported retrieval tool: {tool_name}")
    allowed = {
        "section_keywords",
        "content_keywords",
        "filters",
        "content_limit",
    }
    unknown = sorted(set(arguments) - allowed)
    if unknown:
        raise RetrievalQueryV1Error(
            "Unsupported tool arguments: " + ", ".join(unknown)
        )
    result = search_learning_fragments(
        arguments.get("section_keywords"),
        arguments.get("content_keywords"),
        filters=arguments.get("filters"),
        index_path=index_path,
        content_limit=arguments.get("content_limit", 5),
    )
    return {
        "tool_name": tool_name,
        "arguments": {
            "section_keywords": result.section_keywords,
            "content_keywords": result.content_keywords,
            "filters": result.filters,
            "content_limit": result.content_limit,
        },
        **result.as_dict(),
    }


def write_retrieval_result_v1(result: Mapping[str, Any], output_path: Path) -> None:
    """Atomically write a retrieval result or tool envelope as JSON."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        dir=output_path.parent,
        delete=False,
    ) as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temporary_path = Path(handle.name)
    os.replace(temporary_path, output_path)
