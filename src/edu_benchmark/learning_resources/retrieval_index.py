"""Build a SQLite full-text index for learning-resource fragments."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Sequence

from edu_benchmark.learning_resources.ocr_text_manifest import read_csv_rows
from edu_benchmark.learning_resources.utils import ensure_directory


def _connect(path: Path) -> sqlite3.Connection:
    """Open a writable SQLite connection for the retrieval index.
    
    Args:
        path: Destination SQLite path.
    
    Returns:
        A ``sqlite3.Connection`` with row access by column name. The parent folder is
        created before opening the database.
    """

    ensure_directory(path.parent)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _create_schema(conn: sqlite3.Connection) -> None:
    """Create the learning-resource source, fragment, and FTS tables.
    
    Args:
        conn: Open SQLite connection.
    
    Returns:
        None. Existing index tables are dropped and recreated.
    """

    conn.executescript(
        """
        DROP TABLE IF EXISTS learning_sources;
        DROP TABLE IF EXISTS learning_fragments;
        DROP TABLE IF EXISTS learning_fragments_fts;

        CREATE TABLE learning_sources (
            ocr_text_id TEXT PRIMARY KEY,
            learning_material_id TEXT NOT NULL,
            material_type TEXT NOT NULL,
            grade TEXT NOT NULL,
            book_title TEXT NOT NULL,
            lesson_key TEXT NOT NULL,
            lesson_title TEXT NOT NULL,
            topic_title TEXT,
            source_markdown_path TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE learning_fragments (
            fragment_id TEXT PRIMARY KEY,
            learning_material_id TEXT NOT NULL,
            ocr_text_id TEXT NOT NULL,
            material_type TEXT NOT NULL,
            grade TEXT NOT NULL,
            book_title TEXT NOT NULL,
            lesson_key TEXT NOT NULL,
            lesson_title TEXT NOT NULL,
            topic_title TEXT,
            page_start TEXT,
            page_end TEXT,
            page_marker_start TEXT,
            page_marker_end TEXT,
            section_label TEXT,
            section_path TEXT,
            fragment_type TEXT,
            order_index INTEGER,
            location_note TEXT,
            source_markdown_path TEXT NOT NULL,
            markdown_text TEXT NOT NULL,
            text_preview TEXT,
            status TEXT NOT NULL,
            needs_hnmu_review TEXT,
            notes TEXT
        );

        CREATE VIRTUAL TABLE learning_fragments_fts USING fts5(
            fragment_id UNINDEXED,
            lesson_title,
            section_path,
            markdown_text,
            text_preview,
            tokenize = 'unicode61'
        );
        """
    )


def build_index(*, manifest_path: Path, fragments_path: Path, output_path: Path) -> dict[str, int | str]:
    """Build a rebuildable SQLite FTS index from CSV inputs.
    
    Args:
        manifest_path: Path to ``ocr_text_manifest.csv``.
        fragments_path: Path to ``learning_resource_fragments.csv``.
        output_path: Destination SQLite index path.
    
    Returns:
        A summary dictionary with ``index_path``, ``source_count``, and
        ``fragment_count``.
    """

    source_rows = read_csv_rows(manifest_path)
    fragment_rows = read_csv_rows(fragments_path)
    if output_path.exists():
        output_path.unlink()
    conn = _connect(output_path)
    try:
        _create_schema(conn)
        conn.executemany(
            """
            INSERT INTO learning_sources VALUES (
                :ocr_text_id, :learning_material_id, :material_type, :grade, :book_title,
                :lesson_key, :lesson_title, :topic_title, :source_markdown_path, :status, :notes
            )
            """,
            source_rows,
        )
        conn.executemany(
            """
            INSERT INTO learning_fragments VALUES (
                :fragment_id, :learning_material_id, :ocr_text_id, :material_type, :grade,
                :book_title, :lesson_key, :lesson_title, :topic_title, :page_start, :page_end,
                :page_marker_start, :page_marker_end, :section_label, :section_path,
                :fragment_type, :order_index, :location_note, :source_markdown_path,
                :markdown_text, :text_preview, :status, :needs_hnmu_review, :notes
            )
            """,
            fragment_rows,
        )
        conn.executemany(
            """
            INSERT INTO learning_fragments_fts(fragment_id, lesson_title, section_path, markdown_text, text_preview)
            VALUES (:fragment_id, :lesson_title, :section_path, :markdown_text, :text_preview)
            """,
            fragment_rows,
        )
        conn.commit()
        return {
            "index_path": output_path.as_posix(),
            "source_count": len(source_rows),
            "fragment_count": len(fragment_rows),
        }
    finally:
        conn.close()


def write_index_readme(path: Path) -> None:
    """Write the retrieval-index README.
    
    Args:
        path: Destination README path, usually
            ``shared/learning_resources/indexes/README.md``.
    
    Returns:
        None.
    """

    ensure_directory(path.parent)
    path.write_text(
        """# Learning-resource retrieval index v0

Index này được sinh từ `shared/learning_resources/fragments/learning_resource_fragments.csv`.

File SQLite là artifact sinh lại được và đang được `.gitignore` bỏ qua.

Build lại bằng:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_index.py
```

Query thử bằng:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "Scratch trung bình cộng ba số" --grade 6
```
""",
        encoding="utf-8",
    )
