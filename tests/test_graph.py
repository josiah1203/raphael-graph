"""Graph API behavioral tests."""

import uuid

from fastapi.testclient import TestClient

from raphael_graph.app import app


def test_graph_endpoints() -> None:
    client = TestClient(app)
    edges = client.get("/v1/graph/edges")
    assert edges.status_code == 200
    assert "edges" in edges.json()
    impact = client.get("/v1/graph/impact/power-board-v2")
    assert impact.status_code == 200
    assert "impact_set" in impact.json()


def test_graph_edge_dedup() -> None:
    client = TestClient(app)
    suffix = uuid.uuid4().hex[:8]
    body = {
        "from_id": f"dedup-a-{suffix}",
        "to_id": f"dedup-b-{suffix}",
        "edge_type": "related",
    }
    first = client.post("/v1/graph/edges", json=body)
    assert first.status_code == 200
    assert first.json()["status"] == "created"
    second = client.post("/v1/graph/edges", json=body)
    assert second.status_code == 200
    assert second.json()["status"] == "exists"
