# MachFive MCP Server

[![MCP Badge](https://lobehub.com/badge/mcp/bluecraft-ai-machfive-mcp)](https://lobehub.com/mcp/bluecraft-ai-machfive-mcp)
[![smithery badge](https://smithery.ai/badge/machfive-cold-email)](https://smithery.ai/server/machfive/cold-email)

## What is MachFive MCP Server?

MCP (Model Context Protocol) is an open standard that lets AI assistants like Claude connect to external apps. Think of it as a universal translator between AI and software.

MachFive MCP Server is a connector that lets your AI assistants communicate directly with your MachFive account. Your AI can list campaigns, generate hyper-personalized cold email sequences, manage lead lists, and export results — all through natural conversation.

Instead of logging into MachFive, uploading CSVs, and waiting for results, you can simply tell your AI what you need:

- "Generate a 3-email sequence for jane@acme.com using my SaaS Founders campaign"
- "Show me my MachFive campaigns"
- "Submit these 50 leads for batch processing"
- "Check the status of my latest batch and export the results"

Your AI understands the request, connects to MachFive through MCP, and executes the action — all in seconds.

---

## How to Set Up MachFive MCP

### Step 1: Get Your API Key (2 min)

1. Log in to your MachFive account at [app.machfive.io](https://app.machfive.io)
2. Go to **Settings → API Keys**
3. Click **Create API Key**
4. Copy your key and store it securely

> ⚠️ Keep this key private — it's like a password to your MachFive account.

---

### Step 2: Connect Your AI Client

#### Option A: Claude Desktop (Easiest)

1. Open the Claude Desktop app
2. Go to **Settings → Connectors**
3. Click **Add custom connector**
4. Enter:
   - **Name:** MachFive
   - **Remote MCP server URL:** `https://mcp.machfive.io/mcp/YOUR_API_KEY`
5. Replace `YOUR_API_KEY` with the API key you created
6. Click **Add** — no restart needed!

#### Option B: Claude Desktop (Config File)

If you prefer editing the config file directly:

1. Go to **Settings → Developer → Edit Config**
2. Add this to your config file (replace `YOUR_API_KEY`):

```json
{
  "mcpServers": {
    "machfive": {
      "url": "https://mcp.machfive.io/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

3. Save and restart Claude Desktop

#### Option C: Cursor

1. Open Cursor → **Settings** (⌘ + ,)
2. Search for **MCP**
3. Click **Edit in settings.json**
4. Add the following (replace `YOUR_API_KEY`):

```json
{
  "mcpServers": {
    "machfive": {
      "url": "https://mcp.machfive.io/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

5. Save and restart Cursor

#### Option D: n8n (AI Agents & Workflows)

For automating workflows with AI agents in n8n:

1. Add the **MCP Client** node to your workflow
2. Select **Streamable HTTP** as the transport option
3. Enter the URL: `https://mcp.machfive.io/mcp/YOUR_API_KEY`
4. Connect to your AI agent node

#### Option E: Other MCP Clients

For any MCP-compatible client, use the URL with your API key:

```
https://mcp.machfive.io/mcp/YOUR_API_KEY
```

This URL works with any client that supports Streamable HTTP transport.

---

### Step 3: Test It! (30 sec)

Open your AI assistant and try:

> "List my MachFive campaigns"

If you see your campaign list, you're connected! 🎉

---

## Authentication

MachFive MCP supports three authentication methods:

| Method | Format | Best For |
|--------|--------|----------|
| **URL path** | `https://mcp.machfive.io/mcp/YOUR_API_KEY` | Clients without header support, n8n |
| **Authorization header** | `Authorization: Bearer YOUR_API_KEY` | Claude Desktop, Cursor |
| **Authorization header (no prefix)** | `Authorization: YOUR_API_KEY` | Simplified integrations |

The Bearer prefix is optional for the Authorization header.

---

## Available Tools

MachFive MCP provides **6 tools** for cold email generation:

### 📋 Campaigns

| Tool | Description |
|------|-------------|
| `list_campaigns` | List all campaigns in your workspace. **Call this first** — you need a campaign ID for generation. |

### ✉️ Email Generation

| Tool | Description |
|------|-------------|
| `generate_sequence` | Generate a personalized email sequence for **one lead** (synchronous, 3-10 min). |
| `generate_batch` | Submit **multiple leads** for batch generation (async, returns immediately with a list ID). |

### 📦 List Management

| Tool | Description |
|------|-------------|
| `list_lists` | Browse lead lists and batch jobs. |
| `get_list_status` | Poll a batch job's status until completed or failed. |
| `export_list` | Download results as JSON or CSV when a batch is complete. |

---

## What Can You Do?

### ✉️ Email Generation
- "Generate a cold email sequence for sarah@notion.so using my Gator 100 campaign"
- "Write 5 personalized emails for John Smith, VP of Sales at Acme Corp"
- "Generate emails for this lead with a focus on our ROI case study angle"

### 📦 Batch Processing
- "Submit these 20 leads for batch email generation"
- "Check the status of my latest batch"
- "Export my completed batch as CSV"

### 📋 Campaign Management
- "List my MachFive campaigns"
- "What campaigns do I have?"
- "Show me my campaign IDs"

### 📊 Results & Export
- "Export the results from my last batch as JSON"
- "Download the CSV for my SaaS Founders list"
- "Show me the generated emails for list xyz"

---

## Example Conversations

### Quick Single Lead Generation

> **You:** "Generate a 3-email sequence for jane@acme.com using my Marketing Agencies campaign. Her name is Jane Doe and she's the VP of Growth."
>
> **AI:** "I'll generate that sequence now. This typically takes 3-5 minutes since MachFive researches the prospect and crafts personalized emails..."
>
> *\[3 minutes later\]*
>
> **AI:** "Here's your 3-email sequence for Jane Doe at Acme:
>
> **Email 1** — Subject: Quick question, Jane
> Hi Jane, I noticed Acme's recent expansion into..."

### Batch Processing Workflow

> **You:** "I have 25 leads to process. Here they are: \[paste leads\]. Use my SaaS Founders campaign."
>
> **AI:** "Batch submitted! I got list ID abc-123. Let me check the status..."
>
> *\[polls automatically\]*
>
> **AI:** "Your batch is complete — all 25 leads processed with 75 emails generated. Would you like me to export as CSV or JSON?"

### Morning Workflow Check

> **You:** "What campaigns do I have, and are there any batches still processing?"
>
> **AI:** "You have 3 campaigns: First Campaign, Gator 100, and Marketing Agencies. All current batches are completed — no pending jobs."

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection failed | Double-check your API key is correct |
| "Invalid API key" error | Regenerate your API key in MachFive settings |
| No response | Restart your AI client |
| Timeout on generate_sequence | Normal — generation takes 3-10 minutes. Don't retry. |
| Server unavailable | Check your internet connection and try again |

---

## Frequently Asked Questions

### 1. Do I need to know how to code?
No. Setup takes about 5 minutes and just requires pasting your API key into your AI assistant's settings.

### 2. Which AI assistants work with this?
Any MCP-compatible client, including:
- **Claude Desktop** (Anthropic)
- **Cursor** (AI code editor)
- **n8n** (AI agent workflows)
- Any app supporting Streamable HTTP transport

### 3. Is my data safe?
Yes. The connection uses your personal API key over encrypted HTTPS. Your AI can only access what your API key permits. Each user authenticates with their own key — MachFive never stores or shares API keys on the MCP server.

### 4. What can my AI do with MachFive?
Your AI can:
- List your campaigns
- Generate personalized cold email sequences for individual leads
- Submit batches of leads for bulk generation
- Check batch processing status
- Export completed results as CSV or JSON

### 5. How much does it cost?
The MCP server is free with your MachFive subscription. Email generation uses your account's credits as normal.

### 6. What's the connection URL?
`https://mcp.machfive.io/mcp`

### 7. How long does email generation take?
Single lead generation (`generate_sequence`) takes 3-10 minutes because MachFive researches the prospect and crafts truly personalized emails. Batch generation (`generate_batch`) returns immediately — processing happens in the background, and you poll for completion.

### 8. What if something goes wrong?
Generation is non-destructive — it creates new email sequences without affecting existing data. If a batch fails, simply submit a new one.

---

## API Endpoint

| Endpoint | URL |
|----------|-----|
| Health check | `https://mcp.machfive.io/` |
| MCP protocol | `https://mcp.machfive.io/mcp` |
| MCP with API key | `https://mcp.machfive.io/mcp/YOUR_API_KEY` |

---

**Need help?** Contact us at [support@machfive.io](mailto:support@machfive.io)

**MCP Documentation:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
