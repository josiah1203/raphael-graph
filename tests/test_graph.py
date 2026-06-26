"""Graph API behavioral tests."""

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
