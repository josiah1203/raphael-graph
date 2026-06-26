"""Graph API — knowledge graph."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from raphael_graph.calliope_graph.sqlite_store import SqliteGraphClient

router = APIRouter(tags=["graph"])
_raw = os.environ.get("RAPHAEL_GRAPH_DB", "").strip()
_db = Path(_raw) if _raw else None
_client = SqliteGraphClient(db_path=_db)


@router.get("/nodes/{node_id}")
def get_node(node_id: str) -> dict:
    node = _client.get_node(node_id)
    if not node:
        raise HTTPException(404, detail="not_found")
    return node


@router.get("/impact/{node_id}")
def impact(node_id: str, depth: int = 5) -> dict:
    impacted = _client.query_impact_set(node_id, depth=depth)
    return {"node_id": node_id, "impact_set": sorted(impacted)}


@router.get("/edges")
def edges(from_id: str | None = None, to_id: str | None = None) -> dict:
    return {"edges": _client.list_edges(from_id=from_id, to_id=to_id)}
