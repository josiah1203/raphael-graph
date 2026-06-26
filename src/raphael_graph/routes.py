"""Graph API — knowledge graph."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from raphael_graph.store import GraphStore

router = APIRouter(tags=["graph"])
_store = GraphStore()


@router.get("/nodes/{node_id}")
def get_node(node_id: str) -> dict:
    node = _store.get_node(node_id)
    if not node:
        raise HTTPException(404, detail="not_found")
    return node


@router.get("/impact/{node_id}")
def impact(node_id: str) -> dict:
    return _store.impact(node_id)


@router.get("/edges")
def edges() -> dict:
    return {"edges": _store.list_edges()}
