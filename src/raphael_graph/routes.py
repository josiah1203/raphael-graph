"""Graph API — knowledge graph stub."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["graph"])


@router.get("/nodes/{node_id}")
def get_node(node_id: str) -> dict:
    return {"id": node_id, "type": "module", "label": node_id}


@router.get("/impact/{node_id}")
def impact(node_id: str) -> dict:
    return {"node_id": node_id, "dependents": [], "dependencies": []}


@router.get("/edges")
def edges() -> dict:
    return {"edges": []}
