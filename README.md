# MachFive MCP Server

MCP server that lets AI agents generate hyper-personalized cold email sequences via [MachFive](https://machfive.io).

## Deploy to Railway

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "MachFive MCP server"
git remote add origin https://github.com/YOUR_ORG/machfive-mcp.git
git push -u origin main
```

### 2. Deploy on Railway

1. Go to [railway.com](https://railway.com) → New Project → Deploy from GitHub repo
2. Railway auto-detects the Dockerfile and deploys
3. Add environment variable in Railway dashboard:
   - `MACHFIVE_API_KEY` = your MachFive API key
4. Generate a domain (or add custom domain: `mcp.machfive.io`)

Your MCP endpoint will be at: `https://YOUR-DOMAIN/mcp`

## How users connect

Users add this to their Claude Desktop config:

```json
{
  "mcpServers": {
    "machfive": {
      "url": "https://mcp.machfive.io/mcp"
    }
  }
}
```

No installation required — just the URL.

## Tools

| Tool | Description |
|------|-------------|
| `list_campaigns` | List campaigns. **Call first** to get a campaign ID. |
| `generate_sequence` | Generate emails for one lead (sync, 3-10 min). |
| `generate_batch` | Submit multiple leads (async). Returns `list_id`. |
| `list_lists` | Browse past batch jobs. |
| `get_list_status` | Poll batch status until completed/failed. |
| `export_list` | Download results (JSON or CSV). |

## Workflows

**Single lead:** `list_campaigns → generate_sequence → done`

**Batch:** `list_campaigns → generate_batch → get_list_status (poll) → export_list`

## Local development

For local testing with Claude Desktop (stdio mode):

```bash
export MACHFIVE_API_KEY=mf_live_YOUR_KEY
export MCP_TRANSPORT=stdio
uv run --python 3.12 --with mcp --with httpx server.py
```

Or use the Claude Desktop config in `claude_desktop_config.json`.

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MACHFIVE_API_KEY` | Yes | — | Your MachFive API key (`mf_live_...`) |
| `PORT` | No | `8000` | HTTP port (Railway sets this automatically) |
| `MCP_TRANSPORT` | No | `streamable-http` | `stdio` for local, `streamable-http` for remote |
| `MACHFIVE_BASE_URL` | No | `https://app.machfive.io` | Override API base URL |
| `LOG_LEVEL` | No | `INFO` | Logging level |

## Links

- [MachFive](https://machfive.io)
- [API Docs](https://help.machfive.io)
- [ClawHub Skill](https://clawhub.ai/skills/cold-email)
- [MCP Protocol](https://modelcontextprotocol.io)
