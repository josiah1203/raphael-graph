"""SQLite graph store — ported from calliope-core."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any


class GraphStore:
    def __init__(self, db_path: Path | None = None) -> None:
        path = db_path or Path(os.environ.get("RAPHAEL_GRAPH_DB", "/tmp/raphael-graph.db"))
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS nodes (node_id TEXT PRIMARY KEY, labels TEXT NOT NULL, properties TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS edges (id INTEGER PRIMARY KEY AUTOINCREMENT, from_id TEXT, to_id TEXT, edge_type TEXT, properties TEXT);
            """
        )
        self._seed()

    def _seed(self) -> None:
        if self._conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]:
            return
        self.upsert_node("power-board-v2", ["Module"], {"name": "Power Board V2"})

    def upsert_node(self, node_id: str, labels: list[str], properties: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO nodes (node_id, labels, properties) VALUES (?, ?, ?)",
            (node_id, json.dumps(labels), json.dumps(properties)),
        )
        self._conn.commit()

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        row = self._conn.execute("SELECT labels, properties FROM nodes WHERE node_id = ?", (node_id,)).fetchone()
        if not row:
            return None
        return {"id": node_id, "labels": json.loads(row["labels"]), "properties": json.loads(row["properties"])}

    def list_edges(self) -> list[dict[str, Any]]:
        rows = self._conn.execute("SELECT from_id, to_id, edge_type, properties FROM edges").fetchall()
        return [{"from": r[0], "to": r[1], "type": r[2], "properties": json.loads(r[3])} for r in rows]

    def impact(self, node_id: str) -> dict[str, Any]:
        deps = [r[0] for r in self._conn.execute("SELECT from_id FROM edges WHERE to_id = ?", (node_id,))]
        dependents = [r[0] for r in self._conn.execute("SELECT to_id FROM edges WHERE from_id = ?", (node_id,))]
        return {"node_id": node_id, "dependencies": deps, "dependents": dependents}
