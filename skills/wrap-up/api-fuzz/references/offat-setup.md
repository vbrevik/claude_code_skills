# OFFAT Setup

## OWASP OFFAT (OWASP Offensive API Tester)

OFFAT is an automated API security testing tool that fuzzes REST API endpoints using OpenAPI/Swagger specifications.

## Installation

### pip (recommended)

```bash
pip install offat
```

### pipx (isolated environment)

```bash
pipx install offat
```

### Verify

```bash
offat --help
offat --version
```

## Air-Gap Installation

For RESTRICTED environments without internet access:

### On Connected Machine

```bash
# Download wheel and all dependencies
mkdir offat-offline
pip download offat -d offat-offline/

# Create requirements file for reference
pip freeze | grep -i offat > offat-offline/requirements.txt

# Archive for transfer
tar czf offat-offline.tar.gz offat-offline/
```

### On Air-Gapped Machine

```bash
# Extract archive (transferred via approved media)
tar xzf offat-offline.tar.gz

# Install from local wheels
pip install --no-index --find-links=offat-offline/ offat
```

## Configuration Options

OFFAT accepts the following key arguments:

| Flag | Description |
|------|-------------|
| `-f <spec>` | Path to OpenAPI/Swagger spec file (JSON or YAML) |
| `-o <file>` | Output file path (JSON) |
| `--rate-limit <n>` | Maximum requests per second |
| `--proxy <url>` | HTTP proxy for request inspection |
| `--headers <json>` | Custom headers as JSON string |
| `--auth-token <token>` | Bearer token for authenticated testing |

### Example: Full scan with rate limiting

```bash
offat -f openapi.json -o results.json --rate-limit 10
```

### Example: Authenticated scan

```bash
offat -f openapi.json -o results.json --auth-token "Bearer eyJ..."
```

## OpenAPI Spec Generation

For projects without existing OpenAPI specs, you can generate them:

### From Hono routes

If using Hono with Zod validation, consider `@hono/zod-openapi` to auto-generate specs.

### From Convex functions

Convex does not natively export OpenAPI specs. To create one manually:

1. List all exported functions in `convex/` directories:
   - `query` exports become `POST /api/query` with function name in body
   - `mutation` exports become `POST /api/mutation` with function name in body
   - `action` exports become `POST /api/action` with function name in body
   - `httpAction` exports map to their registered HTTP routes

2. For each function, inspect the `args` validator to determine the request schema.

3. Create a minimal OpenAPI 3.0 spec:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Convex API",
    "version": "1.0.0"
  },
  "servers": [
    {"url": "http://localhost:3210"}
  ],
  "paths": {
    "/api/query": {
      "post": {
        "summary": "Execute a Convex query",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "path": {"type": "string"},
                  "args": {"type": "object"}
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### Store generated specs

Place generated OpenAPI specs in:

```
~/.claude/skills/api-fuzz/assets/openapi-specs/
```

These persist across sessions and can be reused for regression testing.

## Convex-Specific Endpoint Discovery

Convex backends expose a standard set of HTTP endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/query` | POST | Execute a query function |
| `/api/mutation` | POST | Execute a mutation function |
| `/api/action` | POST | Execute an action function |
| `/version` | GET | Backend version info |
| `/api/` | GET | API root |

Additionally, any `httpAction` endpoints registered via `http.ts` will be available at their configured paths.

To discover httpAction routes, inspect `convex/http.ts` in the target backend package for `http.route()` calls.
