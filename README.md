# raphael-graph

Knowledge graph — relationships, dependencies, visualization

## API

- Prefix: `/v1/graph`
- Port: `8100`
- Health: `GET /health`

## Events

_Published and consumed events documented in `openapi.yaml` and raphael-contracts._

## Development

```bash
uv sync
uv run uvicorn raphael_graph.app:app --reload --port 8100
```

Part of the [Raphael Platform](https://github.com/hummingbird-labs) by HummingBird Labs.
