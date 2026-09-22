# IoT SiteWise Gateway

An AWS Lambda gateway for querying industrial IoT assets from AWS IoT SiteWise, originally built for the pipe extrusion line monitoring solution demonstrated at Hannover Messe. Lambda handlers behind a local router, fully mockable without AWS credentials.

## Tech Stack

- Python 3.14
- AWS Lambda (handler pattern)
- boto3 / AWS IoT SiteWise
- Flask (local HTTP server)
- pytest + unittest.mock
- Maven-style project layout (`src/`, `tests/`, `tools/`)

## Features

- Query asset hierarchies to configurable depth
- Fetch latest values for properties by suffix
- Retrieve historical property values over a date range
- Compute property aggregates (SUM, COUNT, etc.) over time intervals
- List child assets by name
- Walk parent → child → grandchild asset trees
- Local router that mimics API Gateway path dispatching
- Fully mocked test suite — no AWS credentials required

## Architecture

```
Flask (local_server.py)
    ↓ HTTP
Router (src/common/router.py)          ← mimics API Gateway
    ↓ dispatch by METHOD:/api/<domain>
Handlers (src/handlers/)               ← thin event wrappers
    ↓ dispatch by action
Services (src/services/)               ← business logic
    ↓ boto3
AWS IoT SiteWise
```

Each layer has one responsibility:

- **Router** — matches `METHOD:/api/<domain>` to a handler
- **Handler** — parses the event, dispatches to the right service, formats the response
- **Service** — talks to SiteWise and assembles the result

## Getting Started

### 1. Install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run locally

```powershell
python local_server.py
```

The API will be available at `http://localhost:5000`.

### 3. Run tests

```powershell
pytest -v
```

All tests use mocks — no AWS account needed.

## API Endpoints

All endpoints are `GET` and take a JSON body (or query params in a real deployment).

| Path | Description |
|---|---|
| `/api/asset/hierarchy` | Asset hierarchy tree |
| `/api/asset/metric/lat-val` | Latest value for properties by suffix |
| `/api/asset/prop/hist/val` | Historical property values over a date range |
| `/api/child/assets` | Child assets by name |
| `/api/hierarchy/props` | Full hierarchy with properties, depth-limited |
| `/api/property/agg` | Property aggregates (SUM, COUNT, etc.) |

### Example — get asset hierarchy

```
GET /api/asset/hierarchy
Content-Type: application/json

{
  "assetId": "asset-1",
  "lineSuffixes": ["id", "name", "status"]
}
```

Response:

```json
{
  "parent": {
    "lineId": "line-1",
    "lineName": "Line 1",
    "lineStatus": "ACTIVE"
  },
  "children": [
    {
      "child": {"id": "child-1", "name": "ExtrusionLine_1"},
      "grandchildren": []
    }
  ]
}
```

## Project Structure

```
├── local_server.py           Flask entry point
├── requirements.txt
├── src/
│   ├── common/
│   │   ├── router.py         Dispatch by METHOD:/api/<domain>
│   │   └── sitewise_client.py boto3 client factory (mockable)
│   ├── handlers/             Lambda handlers, one per domain
│   ├── models/               DTOs and enums
│   └── services/             Business logic
├── tests/                    pytest suite
└── tools/                    Standalone utilities (asset export)
```

## Notes

- The router mimics API Gateway's dispatch behavior so handlers can be tested end-to-end without deploying.
- `get_sitewise_client()` is a factory rather than a module-level client so tests can patch it with a mock.
- The original project ran on AWS Lambda behind API Gateway; this version is fully self-contained.