"""Small retrieval API for learning-resource fragments."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[\wÀ-ỹ]+", re.UNICODE)

DEFAULT_INDEX_PATH = Path("shared/learning_resources/indexes/learning_resources_v0.sqlite")


def connect(index_path: Path = DEFAULT_INDEX_PATH) -> sqlite3.Connection:
    """Open the learning-resource SQLite index.
    
    Args:
        index_path: Path to the generated SQLite FTS index. Defaults to
            ``shared/learning_resources/indexes/learning_resources_v0.sqlite``.
    
    Returns:
        A ``sqlite3.Connection`` whose rows can be accessed by column name.
    """

    conn = sqlite3.connect(index_path)
    conn.row_factory = sqlite3.Row
    return conn


def _fts_query(query: str) -> str:
    """Normalize free-text input into a conservative SQLite FTS query.
    
    Args:
        query: User or agent keyword query.
    
    Returns:
        A whitespace-joined token query safe for the current FTS setup. Empty-token
        input falls back to the original query string.
    """

    tokens = TOKEN_RE.findall(query)
    if not tokens:
        return query
    return " ".join(tokens)


def _as_list(value: Any) -> list[str]:
    """Normalize filter values into a list of strings.
    
    Args:
        value: A scalar, sequence, set, tuple, or ``None``.
    
    Returns:
        A list of non-empty string values suitable for SQL ``IN`` filters.
    """

    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if str(item)]
    return [str(value)] if str(value) else []


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a SQLite row into a plain dictionary.
    
    Args:
        row: ``sqlite3.Row`` returned by a query.
    
    Returns:
        A dictionary preserving all returned columns, including provenance fields.
    """

    return {key: row[key] for key in row.keys()}


def get_learning_fragment(fragment_id: str, *, index_path: Path = DEFAULT_INDEX_PATH) -> dict[str, Any] | None:
    """Return one learning-resource fragment by ID.
    
    Args:
        fragment_id: Stable fragment identifier, for example
            ``SGK-TIN6#F0001`` depending on the source registry.
        index_path: Path to the generated SQLite FTS index.
    
    Returns:
        A dictionary containing fragment text and provenance fields, or ``None`` if
        the ID is not present. Audit agents should cite this result as evidence
        rather than reading arbitrary Markdown files.
    """

    with connect(index_path) as conn:
        row = conn.execute("SELECT * FROM learning_fragments WHERE fragment_id = ?", (fragment_id,)).fetchone()
        return _row_to_dict(row) if row else None


def resolve_learning_resource(metadata: dict[str, Any], *, index_path: Path = DEFAULT_INDEX_PATH, limit: int = 10) -> dict[str, Any]:
    """Find candidate fragments from structured metadata.
    
    Args:
        metadata: Dictionary that may include ``grade``, ``material_type`` or
            ``book_type``, ``lesson_key``, ``lesson_title``, ``topic_title``, and
            ``query``.
        index_path: Path to the generated SQLite FTS index.
        limit: Maximum number of candidate fragments to return.
    
    Returns:
        A dictionary with ``candidate_fragments``, full ``results``, a rough
        ``confidence`` score, and ``needs_review``. Use this first when an HNMU row
        already has lesson/topic metadata.
    """

    filters = {
        "grade": metadata.get("grade"),
        "material_type": metadata.get("material_type") or metadata.get("book_type"),
        "lesson_key": metadata.get("lesson_key"),
    }
    query = " ".join(str(metadata.get(key, "")) for key in ("lesson_title", "topic_title", "query") if metadata.get(key))
    results = search_learning_fragments(query=query or "Tin học", filters=filters, index_path=index_path, limit=limit)
    return {
        "candidate_fragments": [item["fragment_id"] for item in results],
        "results": results,
        "confidence": 0.9 if results else 0.0,
        "needs_review": not bool(results),
    }


def search_learning_fragments(
    query: str,
    filters: dict[str, Any] | None = None,
    *,
    index_path: Path = DEFAULT_INDEX_PATH,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search fragments by keywords and metadata filters.
    
    Args:
        query: Keyword query from a question, answer, dialogue, or reviewer note.
        filters: Optional filters. Supported keys: ``grade``, ``material_type``,
            ``lesson_key``, ``fragment_type``, and ``status``. Values may be scalar
            or list-like.
        index_path: Path to the generated SQLite FTS index.
        limit: Maximum number of rows to return.
    
    Returns:
        A ranked list of fragment dictionaries. Each result includes Markdown text,
        preview text, location fields, status, and other provenance needed for
        Plan 04 audit evidence.
    """

    filters = filters or {}
    where = ["learning_fragments_fts MATCH ?"]
    params: list[Any] = [_fts_query(query)]

    for column in ("grade", "material_type", "lesson_key", "fragment_type", "status"):
        values = _as_list(filters.get(column))
        if not values:
            continue
        placeholders = ",".join("?" for _ in values)
        where.append(f"f.{column} IN ({placeholders})")
        params.extend(values)

    sql = f"""
        SELECT f.*, bm25(learning_fragments_fts) AS rank
        FROM learning_fragments_fts
        JOIN learning_fragments f USING(fragment_id)
        WHERE {' AND '.join(where)}
        ORDER BY rank, f.order_index
        LIMIT ?
    """
    params.append(limit)
    with connect(index_path) as conn:
        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            rows = _fallback_like_search(conn, query, filters, limit)
        return [_row_to_dict(row) for row in rows]


def _fallback_like_search(conn: sqlite3.Connection, query: str, filters: dict[str, Any], limit: int) -> list[sqlite3.Row]:
    """Fallback to SQL LIKE matching when FTS parsing fails.
    
    Args:
        conn: Open SQLite connection.
        query: Original keyword query.
        filters: Metadata filters using the same keys as ``search_learning_fragments``.
        limit: Maximum number of rows to return.
    
    Returns:
        SQLite rows ordered by source order. This fallback is less precise than FTS
        but avoids hard failure on malformed queries.
    """

    tokens = TOKEN_RE.findall(query)
    where = []
    params: list[Any] = []
    for token in tokens[:4]:
        where.append("f.markdown_text LIKE ?")
        params.append(f"%{token}%")
    for column in ("grade", "material_type", "lesson_key", "fragment_type", "status"):
        values = _as_list(filters.get(column))
        if values:
            placeholders = ",".join("?" for _ in values)
            where.append(f"f.{column} IN ({placeholders})")
            params.extend(values)
    sql = f"SELECT f.*, 0.0 AS rank FROM learning_fragments f WHERE {' AND '.join(where) if where else '1=1'} ORDER BY f.order_index LIMIT ?"
    params.append(limit)
    return conn.execute(sql, params).fetchall()
