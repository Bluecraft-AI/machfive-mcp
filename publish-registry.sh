#!/bin/bash
# Publish both MCP Registry entries with the same version

set -e

VERSION=${1:-"1.0.0"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📦 Publishing both registry entries at v${VERSION}..."

# Template for machfive entry (brand-focused, base URL)
MACHFIVE_JSON=$(cat <<EOF
{
  "\$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.Bluecraft-AI/machfive",
  "description": "Generate hyper-personalized cold email sequences via MachFive API.",
  "repository": {
    "url": "https://github.com/Bluecraft-AI/machfive-mcp",
    "source": "github"
  },
  "version": "${VERSION}",
  "remotes": [
    {
      "type": "streamable-http",
      "url": "https://mcp.machfive.io/mcp"
    }
  ]
}
EOF
)

# Template for cold-email entry (category-focused, URL template)
COLD_EMAIL_JSON=$(cat <<EOF
{
  "\$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.Bluecraft-AI/cold-email",
  "description": "Generate hyper-personalized cold email sequences via AI.",
  "repository": {
    "url": "https://github.com/Bluecraft-AI/machfive-mcp",
    "source": "github"
  },
  "version": "${VERSION}",
  "remotes": [
    {
      "type": "streamable-http",
      "url": "https://mcp.machfive.io/mcp/{api_key}",
      "variables": {
        "api_key": {
          "description": "Your MachFive API key",
          "isRequired": true
        }
      }
    }
  ]
}
EOF
)

# Publish machfive entry
echo ""
echo "1️⃣  Publishing io.github.Bluecraft-AI/machfive..."
echo "$MACHFIVE_JSON" > server.json
./mcp-publisher validate && ./mcp-publisher publish

# Publish cold-email entry
echo ""
echo "2️⃣  Publishing io.github.Bluecraft-AI/cold-email..."
echo "$COLD_EMAIL_JSON" > server.json
./mcp-publisher validate && ./mcp-publisher publish

echo ""
echo "✅ Both entries published at v${VERSION}"
echo ""
echo "Note: server.json now contains the cold-email entry (with URL template)."
echo "This is the more complete version for your repo."
