"""Graph client factory tests."""

import os

import pytest

from raphael_graph.calliope_graph import (
    InMemoryGraphClient,
    PostgresGraphClient,
    SqliteGraphClient,
    create_graph_client,
)


def test_create_graph_client_defaults_to_sqlite_not_in_memory(
    monkeypatch: pytest.MonkeyPatch, tmp_path,
) -> None:
    monkeypatch.delenv("RAPHAEL_DATABASE_URL", raising=False)
    monkeypatch.delenv("RAPHAEL_NEO4J_URL", raising=False)
    monkeypatch.delenv("NEO4J_URI", raising=False)
    client = create_graph_client(graph_db_path=tmp_path / "graph.db")
    assert isinstance(client, SqliteGraphClient)
    assert not isinstance(client, InMemoryGraphClient)


def test_create_graph_client_uses_postgres_without_neo4j(
    monkeypatch: pytest.MonkeyPatch, postgres_or_sqlite: str,
) -> None:
    monkeypatch.delenv("RAPHAEL_NEO4J_URL", raising=False)
    monkeypatch.delenv("NEO4J_URI", raising=False)
    client = create_graph_client()
    if postgres_or_sqlite == "postgres":
        assert isinstance(client, PostgresGraphClient)
    else:
        assert isinstance(client, SqliteGraphClient)


def test_create_graph_client_falls_back_when_neo4j_unreachable(
    monkeypatch: pytest.MonkeyPatch, tmp_path,
) -> None:
    monkeypatch.setenv("RAPHAEL_NEO4J_URL", "bolt://127.0.0.1:17687")
    monkeypatch.delenv("RAPHAEL_DATABASE_URL", raising=False)
    client = create_graph_client(graph_db_path=tmp_path / "graph.db")
    assert isinstance(client, SqliteGraphClient)
