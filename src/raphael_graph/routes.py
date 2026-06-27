"""Graph API — knowledge graph."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from raphael_graph.calliope_graph import create_graph_client

router = APIRouter(tags=["graph"])
_raw = os.environ.get("RAPHAEL_GRAPH_DB", "").strip()
_db = Path(_raw) if _raw else None
_client = create_graph_client(graph_db_path=_db)


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


@router.post("/edges")
def create_edge(body: dict) -> dict:
    created = _client.create_edge(
        body["from_id"],
        body["to_id"],
        body.get("edge_type", "related"),
        body.get("properties", {}),
    )
    _client.upsert_node(body["from_id"], body.get("from_labels", ["Module"]), {})
    _client.upsert_node(body["to_id"], body.get("to_labels", ["Module"]), {})
    return {
        "status": "created" if created else "exists",
        "from_id": body["from_id"],
        "to_id": body["to_id"],
        "edge_type": body.get("edge_type", "related"),
    }


@router.get("/lineage/{node_id}")
def lineage(node_id: str) -> dict:
    edges = _client.list_edges(from_id=node_id) + _client.list_edges(to_id=node_id)
    fork_edges = [e for e in edges if e.get("type") in ("forked_from", "sliced_from")]
    return {"node_id": node_id, "lineage": fork_edges}
