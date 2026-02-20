# MachFive MCP Server

MCP server that lets AI agents generate hyper-personalized cold email sequences via [MachFive](https://machfive.io).

**Auth model:** Each user passes their own MachFive API key. No server-side secrets required.

## Quick Start

### Option 1: Connect to Remote Server (Recommended)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "machfive": {
      "url": "https://mcp.machfive.io/mcp",
      "headers": {
        "Authorization": "Bearer mf_live_YOUR_API_KEY_HERE"
      }
    }
  }
}
```

Replace `mf_live_YOUR_API_KEY_HERE` with your MachFive API key from [app.machfive.io/settings](https://app.machfive.io/settings).

Restart Claude Desktop and you're ready to go.

### Option 2: Run Locally

1. **Clone this repo:**
   ```bash
   git clone https://github.com/Bluecraft-AI/machfive-mcp.git
   cd machfive-mcp
   ```

2. **Install dependencies:**
   ```bash
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or use pip
   pip install fastmcp httpx
   ```

3. **Configure Claude Desktop:**
   - Copy `claude_desktop_config.json.example` to your Claude Desktop config location
   - Update the paths and add your API key
   - Or set `MACHFIVE_API_KEY` environment variable

4. **Restart Claude Desktop**

## Deploy to Railway (For Server Owners)

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
3. **No environment variables needed** — users pass their own API keys
4. Generate a domain (or add custom domain: `mcp.machfive.io`)
5. **Important:** Increase Railway timeout to 700 seconds (Settings → Networking) for `generate_sequence` calls

Your MCP endpoint will be at: `https://YOUR-DOMAIN/mcp`

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

## Example Prompts

Once connected, try asking Claude:

- "List my MachFive campaigns"
- "Generate a 3-email cold email sequence for Jane Doe, VP Marketing at Acme Inc (jane@acme.com)"
- "Create outreach sequences for these 5 leads using my Q1 Outbound campaign"
- "Check the status of my latest batch"
- "Export the results from list abc-123 as CSV"

## Local Development

For local testing with Claude Desktop (stdio mode):

```bash
export MACHFIVE_API_KEY=mf_live_YOUR_KEY
export MCP_TRANSPORT=stdio
uv run --python 3.12 --with fastmcp --with httpx server.py
```

Or use the Claude Desktop config in `claude_desktop_config.json.example`.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MACHFIVE_API_KEY` | Local only | — | Your MachFive API key (for stdio mode only) |
| `PORT` | No | `8000` | HTTP port (Railway sets this automatically) |
| `MCP_TRANSPORT` | No | `streamable-http` | `stdio` for local, `streamable-http` for remote |
| `MACHFIVE_BASE_URL` | No | `https://app.machfive.io` | Override API base URL |
| `LOG_LEVEL` | No | `INFO` | Logging level |

**Note:** For remote HTTP deployments, users pass their API key via the `Authorization` header. The server doesn't need `MACHFIVE_API_KEY` set.

## Pricing

MachFive credits (1 credit = 1 lead processed):

- **Free:** 100 credits/month
- **Starter:** 2,000 credits/month
- **Growth:** 5,000 credits/month
- **Enterprise:** Custom

## Links

- [MachFive](https://machfive.io) — Platform
- [API Docs](https://developer.machfive.io) — API reference
- [MachFive on ClawHub](https://clawhub.ai/skills/cold-email) — OpenClaw skill
- [MCP Protocol](https://modelcontextprotocol.io) — Protocol docs

## License

MIT
