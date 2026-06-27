"""PostgreSQL-backed knowledge graph store."""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class PostgresGraphClient:
    """Persisted graph backed by shared Postgres migrations."""

    def __init__(self) -> None:
        from raphael_contracts import db as rdb

        rdb.ensure_migrations()
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: list[dict[str, Any]] = []
        self._hydrate_cache()

    def _hydrate_cache(self) -> None:
        from raphael_contracts.db import pg_fetchall

        for row in pg_fetchall("SELECT node_id, labels, properties FROM graph_nodes"):
            labels = row["labels"]
            props = row["properties"]
            if isinstance(labels, str):
                labels = json.loads(labels)
            if isinstance(props, str):
                props = json.loads(props)
            self._nodes[row["node_id"]] = {
                "id": row["node_id"],
                "labels": labels,
                "properties": props,
            }
        for row in pg_fetchall(
            "SELECT from_id, to_id, edge_type, properties, from_timestamp, to_timestamp FROM graph_edges"
        ):
            props = row["properties"]
            if isinstance(props, str):
                props = json.loads(props)
            self._edges.append(
                {
                    "from": row["from_id"],
                    "to": row["to_id"],
                    "type": row["edge_type"],
                    "properties": props,
                    "from_timestamp": row["from_timestamp"],
                    "to_timestamp": row["to_timestamp"],
                }
            )

    def upsert_node(self, node_id: str, labels: list[str], properties: dict[str, Any]) -> None:
        merged = dict(self._nodes.get(node_id, {}).get("properties", {}))
        merged.update(properties)
        self._nodes[node_id] = {"id": node_id, "labels": labels, "properties": merged}
        from raphael_contracts.db import connection

        with connection() as conn:
            conn.execute(
                """
                INSERT INTO graph_nodes (node_id, labels, properties)
                VALUES (%s, %s::jsonb, %s::jsonb)
                ON CONFLICT (node_id) DO UPDATE SET
                    labels = EXCLUDED.labels,
                    properties = EXCLUDED.properties
                """,
                (node_id, json.dumps(labels), json.dumps(merged)),
            )
            conn.commit()
        logger.debug("Upserted graph node %s", node_id)

    def create_edge(
        self,
        from_id: str,
        to_id: str,
        edge_type: str,
        properties: dict[str, Any],
        from_timestamp: str | None = None,
        to_timestamp: str | None = None,
    ) -> bool:
        """Insert edge; return False if an identical edge already exists."""
        for edge in self._edges:
            if edge["from"] == from_id and edge["to"] == to_id and edge["type"] == edge_type:
                return False
        edge = {
            "from": from_id,
            "to": to_id,
            "type": edge_type,
            "properties": properties,
            "from_timestamp": from_timestamp,
            "to_timestamp": to_timestamp,
        }
        self._edges.append(edge)
        from raphael_contracts.db import connection

        with connection() as conn:
            conn.execute(
                """
                INSERT INTO graph_edges (from_id, to_id, edge_type, properties, from_timestamp, to_timestamp)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s)
                ON CONFLICT (from_id, to_id, edge_type) DO NOTHING
                """,
                (
                    from_id,
                    to_id,
                    edge_type,
                    json.dumps(properties),
                    from_timestamp,
                    to_timestamp,
                ),
            )
            conn.commit()
        return True

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        return self._nodes.get(node_id)

    def query_impact_set(self, start_node_id: str, depth: int = 5) -> set[str]:
        impact_set = {start_node_id}
        current_layer = {start_node_id}
        for _ in range(depth):
            next_layer: set[str] = set()
            for node_id in current_layer:
                for edge in self._edges:
                    if edge["from"] == node_id and edge["to"] not in impact_set:
                        next_layer.add(edge["to"])
            if not next_layer:
                break
            if len(next_layer) > 100:
                next_layer = set(list(next_layer)[:100])
            impact_set.update(next_layer)
            current_layer = next_layer
        return impact_set

    def find_temporal_edges(self, start_ts: str, end_ts: str) -> list[dict[str, Any]]:
        results = []
        for edge in self._edges:
            e_start = edge.get("from_timestamp")
            e_end = edge.get("to_timestamp")
            if not e_start or not e_end:
                continue
            if e_start <= end_ts and e_end >= start_ts:
                results.append(edge)
        return results

    def list_edges(self, from_id: str | None = None, to_id: str | None = None) -> list[dict[str, Any]]:
        edges = self._edges
        if from_id:
            edges = [e for e in edges if e["from"] == from_id]
        if to_id:
            edges = [e for e in edges if e["to"] == to_id]
        return edges

    def close(self) -> None:
        return None
