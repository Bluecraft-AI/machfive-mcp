"""
MachFive MCP Server
====================
Exposes the MachFive Cold Email API as MCP tools for AI agents.

Auth model:
  - Remote (HTTP): Each user passes their own MachFive API key via
    Authorization header in their MCP client config
  - Local (stdio): Uses MACHFIVE_API_KEY environment variable

Tools:
  1. list_campaigns        - Discover campaigns (call first)
  2. generate_sequence     - Generate emails for one lead (sync, 3-10 min)
  3. generate_batch        - Submit multiple leads (async, returns list_id)
  4. list_lists            - Browse lead lists / batch jobs
  5. get_list_status       - Poll a list until completed or failed
  6. export_list           - Download results as CSV or JSON
"""

import os
import json as _json
import logging
import httpx
from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_http_headers

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("machfive-mcp")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Fallback key for local/stdio usage; remote users pass their own
MACHFIVE_API_KEY = os.environ.get("MACHFIVE_API_KEY", "")
MACHFIVE_BASE_URL = os.environ.get("MACHFIVE_BASE_URL", "https://app.machfive.io")
PORT = int(os.environ.get("PORT", 8000))
TRANSPORT = os.environ.get("MCP_TRANSPORT", "streamable-http")

mcp = FastMCP(
    name="machfive",
    instructions=(
        "MachFive generates hyper-personalized cold email sequences. "
        "Start by calling list_campaigns to find a campaign ID, then use "
        "generate_sequence (single lead) or generate_batch (multiple leads). "
        "For batches: poll get_list_status until completed, then call export_list."
    ),
)


# ---------------------------------------------------------------------------
# Auth helper — resolves the API key per request
# ---------------------------------------------------------------------------

def _get_api_key() -> str:
    """Get the MachFive API key for the current request.

    Priority:
      1. Authorization header from the incoming HTTP request (per-user)
         - Accepts "Bearer YOUR_KEY" or just "YOUR_KEY" (Bearer prefix optional)
      2. MACHFIVE_API_KEY environment variable (fallback for stdio/local)
    """
    try:
        headers = get_http_headers()
        if headers:
            auth = headers.get("authorization", "").strip()
            if auth:
                # Strip Bearer prefix if present
                if auth.startswith("Bearer "):
                    return auth.removeprefix("Bearer ").strip()
                return auth
    except Exception:
        # Not in HTTP context (stdio mode) — fall through to env var
        pass

    return MACHFIVE_API_KEY


def _headers() -> dict[str, str]:
    """Return auth + content-type headers for MachFive API calls."""
    return {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
    }


def _error_message(response: httpx.Response) -> str:
    """Extract a human-readable error from a failed MachFive API response."""
    try:
        body = response.json()
        code = body.get("error", response.status_code)
        msg = body.get("message", response.text)
        return f"MachFive API error {code}: {msg}"
    except Exception:
        return f"MachFive API error {response.status_code}: {response.text}"


# ---------------------------------------------------------------------------
# Tool 1 — List Campaigns
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_campaigns(query: str = "") -> str:
    """List campaigns in the user's MachFive workspace.

    CALL THIS FIRST before generate_sequence or generate_batch — you need a
    campaign ID to generate emails. If the user hasn't specified a campaign,
    call this and ask them to pick one.

    Args:
        query: Optional search string to filter campaigns by name
               (case-insensitive substring match). Leave empty to list all.

    Returns:
        JSON array of campaigns with id, name, and created_at.
        Use the 'id' field as campaign_id in generate calls.
    """
    params = {}
    if query:
        params["q"] = query

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{MACHFIVE_BASE_URL}/api/v1/campaigns",
            headers=_headers(),
            params=params,
        )

    if resp.status_code != 200:
        return _error_message(resp)

    data = resp.json()
    campaigns = data.get("campaigns", [])

    if not campaigns:
        return "No campaigns found. Create a campaign at https://app.machfive.io first."

    lines = ["Available campaigns:\n"]
    for c in campaigns:
        lines.append(f"  - {c['name']}  (ID: {c['id']})  created: {c.get('created_at', 'N/A')}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 2 — Generate Sequence (single lead, synchronous)
# ---------------------------------------------------------------------------

@mcp.tool()
async def generate_sequence(
    campaign_id: str,
    email: str,
    name: str = "",
    title: str = "",
    company: str = "",
    company_website: str = "",
    linkedin_url: str = "",
    email_count: int = 3,
    list_name: str = "",
    email_signature: str = "",
    campaign_angle: str = "",
    approved_ctas: str = "",
) -> str:
    """Generate a personalized cold email sequence for ONE lead.

    This is SYNCHRONOUS — the request takes 3-10 minutes because MachFive
    researches the prospect and crafts unique emails. Do NOT retry if it
    seems slow; wait for the response.

    You must have a campaign_id first. Call list_campaigns if you don't have one.

    Args:
        campaign_id: Campaign UUID (from list_campaigns).
        email: Lead's email address (REQUIRED).
        name: Lead's full name (improves personalization).
        title: Lead's job title (improves personalization).
        company: Lead's company name (improves personalization).
        company_website: Company URL for AI research.
        linkedin_url: LinkedIn profile URL for deeper personalization.
        email_count: Number of emails in sequence, 1-5 (default 3).
        list_name: Display name for this list in MachFive UI.
        email_signature: Signature appended to each email.
        campaign_angle: Additional context/angle for personalization.
        approved_ctas: Comma-separated CTAs (e.g. "Direct Meeting CTA, Lead Magnet CTA").
                       Omit to use campaign defaults.

    Returns:
        The generated email sequence (step, subject, body per email)
        plus credits remaining. If the request times out, use the returned
        list_id with get_list_status and export_list to recover results.
    """
    lead = {"email": email}
    if name:
        lead["name"] = name
    if title:
        lead["title"] = title
    if company:
        lead["company"] = company
    if company_website:
        lead["company_website"] = company_website
    if linkedin_url:
        lead["linkedin_url"] = linkedin_url

    options: dict = {}
    if email_count != 3:
        options["email_count"] = email_count
    if list_name:
        options["list_name"] = list_name
    if email_signature:
        options["email_signature"] = email_signature
    if campaign_angle:
        options["campaign_angle"] = campaign_angle
    if approved_ctas:
        options["approved_ctas"] = [c.strip() for c in approved_ctas.split(",")]

    payload: dict = {"lead": lead}
    if options:
        payload["options"] = options

    async with httpx.AsyncClient(timeout=660) as client:
        resp = await client.post(
            f"{MACHFIVE_BASE_URL}/api/v1/campaigns/{campaign_id}/generate",
            headers=_headers(),
            json=payload,
        )

    if resp.status_code != 200:
        return _error_message(resp)

    data = resp.json()
    sequence = data.get("sequence", [])
    credits = data.get("credits_remaining", "unknown")
    list_id = data.get("list_id", "N/A")

    lines = [f"Generated {len(sequence)}-email sequence (list_id: {list_id})"]
    lines.append(f"Credits remaining: {credits}\n")

    for step in sequence:
        lines.append(f"--- Email {step.get('step', '?')} ---")
        lines.append(f"Subject: {step.get('subject', '')}")
        lines.append(f"{step.get('body', '')}\n")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 3 — Generate Batch (multiple leads, asynchronous)
# ---------------------------------------------------------------------------

@mcp.tool()
async def generate_batch(
    campaign_id: str,
    leads_json: str,
    email_count: int = 3,
    list_name: str = "",
    email_signature: str = "",
    campaign_angle: str = "",
    approved_ctas: str = "",
) -> str:
    """Submit multiple leads for batch email sequence generation (ASYNC).

    Returns IMMEDIATELY with a list_id. Processing runs in the background.

    IMPORTANT — after calling this, you MUST:
      1. Call get_list_status with the returned list_id
      2. Poll every 15-30 seconds until processing_status is 'completed' or 'failed'
      3. When completed, call export_list to get the results

    You must have a campaign_id first. Call list_campaigns if you don't have one.

    Args:
        campaign_id: Campaign UUID (from list_campaigns).
        leads_json: JSON array of lead objects. Each lead MUST have an 'email' field.
                    Optional fields: name, title, company, company_website, linkedin_url.
                    Example: '[{"email":"jane@acme.com","name":"Jane Doe","company":"Acme"}]'
        email_count: Number of emails per lead, 1-5 (default 3).
        list_name: Display name for this batch in MachFive UI.
        email_signature: Signature appended to each email.
        campaign_angle: Additional context/angle for personalization.
        approved_ctas: Comma-separated CTAs. Omit to use campaign defaults.

    Returns:
        list_id and status. Use list_id to poll with get_list_status,
        then export with export_list when completed.
    """
    try:
        leads = _json.loads(leads_json)
    except _json.JSONDecodeError as e:
        return f"Invalid leads_json — could not parse JSON: {e}"

    if not isinstance(leads, list) or len(leads) == 0:
        return "leads_json must be a non-empty JSON array of lead objects."

    for i, lead in enumerate(leads):
        if not isinstance(lead, dict) or not lead.get("email"):
            return f"Lead at index {i} is missing a required 'email' field."

    options: dict = {}
    if email_count != 3:
        options["email_count"] = email_count
    if list_name:
        options["list_name"] = list_name
    if email_signature:
        options["email_signature"] = email_signature
    if campaign_angle:
        options["campaign_angle"] = campaign_angle
    if approved_ctas:
        options["approved_ctas"] = [c.strip() for c in approved_ctas.split(",")]

    payload: dict = {"leads": leads}
    if options:
        payload["options"] = options

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{MACHFIVE_BASE_URL}/api/v1/campaigns/{campaign_id}/generate-batch",
            headers=_headers(),
            json=payload,
        )

    if resp.status_code not in (200, 202):
        return _error_message(resp)

    data = resp.json()
    list_id = data.get("list_id", "unknown")
    status = data.get("status", "processing")
    message = data.get("message", "")

    return (
        f"Batch submitted successfully.\n"
        f"  list_id: {list_id}\n"
        f"  status:  {status}\n"
        f"  leads:   {len(leads)}\n"
        f"  message: {message}\n\n"
        f"NEXT STEP: Call get_list_status(list_id='{list_id}') and poll until "
        f"processing_status is 'completed', then call export_list(list_id='{list_id}')."
    )


# ---------------------------------------------------------------------------
# Tool 4 — List Lists
# ---------------------------------------------------------------------------

@mcp.tool()
async def list_lists(
    campaign_id: str = "",
    status: str = "",
    limit: int = 20,
    offset: int = 0,
) -> str:
    """List lead lists (batch jobs) in the user's MachFive workspace.

    Useful for browsing past batches, checking what's in progress, or finding
    a list_id to export. Results are ordered newest first.

    Args:
        campaign_id: Filter by campaign UUID (optional).
        status: Filter by processing status: 'pending', 'processing',
                'completed', or 'failed' (optional).
        limit: Max results to return, 1-100 (default 20).
        offset: Pagination offset (default 0).

    Returns:
        List of lead lists with id, name, status, and timestamps.
    """
    params: dict = {"limit": limit, "offset": offset}
    if campaign_id:
        params["campaign_id"] = campaign_id
    if status:
        params["status"] = status

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{MACHFIVE_BASE_URL}/api/v1/lists",
            headers=_headers(),
            params=params,
        )

    if resp.status_code != 200:
        return _error_message(resp)

    data = resp.json()
    lists = data.get("lists", [])

    if not lists:
        return "No lists found matching the filters."

    lines = [f"Found {len(lists)} list(s):\n"]
    for lst in lists:
        name = lst.get("custom_name") or "(unnamed)"
        lines.append(
            f"  - {name}\n"
            f"    ID: {lst['id']}\n"
            f"    Status: {lst.get('processing_status', 'unknown')}\n"
            f"    Created: {lst.get('created_at', 'N/A')}\n"
            f"    Completed: {lst.get('completed_at', 'N/A')}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 5 — Get List Status (polling)
# ---------------------------------------------------------------------------

@mcp.tool()
async def get_list_status(list_id: str) -> str:
    """Check the processing status of a lead list.

    Use this to POLL after calling generate_batch. Call every 15-30 seconds
    until processing_status is 'completed' or 'failed'.

    When completed: call export_list to download results.
    When failed: the batch cannot be exported; submit a new batch.

    Args:
        list_id: The list UUID (from generate_batch or generate_sequence response).

    Returns:
        Status details including processing_status, leads_count, and emails_created
        (when completed).
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{MACHFIVE_BASE_URL}/api/v1/lists/{list_id}",
            headers=_headers(),
        )

    if resp.status_code != 200:
        return _error_message(resp)

    data = resp.json()
    status = data.get("processing_status", "unknown")

    lines = [
        f"List: {data.get('id', list_id)}",
        f"Name: {data.get('custom_name') or '(unnamed)'}",
        f"Status: {status}",
        f"Created: {data.get('created_at', 'N/A')}",
        f"Updated: {data.get('updated_at', 'N/A')}",
    ]

    if status == "completed":
        lines.append(f"Leads processed: {data.get('leads_count', 'N/A')}")
        lines.append(f"Emails created: {data.get('emails_created', 'N/A')}")
        lines.append(f"Completed at: {data.get('completed_at', 'N/A')}")
        lines.append(
            f"\nReady to export! Call export_list(list_id='{list_id}') to get results."
        )
    elif status == "failed":
        lines.append(f"Failed at: {data.get('failed_at', 'N/A')}")
        lines.append("\nThis list cannot be exported. Submit a new batch to retry.")
    else:
        lines.append("\nStill processing. Poll again in 15-30 seconds.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 6 — Export List Results
# ---------------------------------------------------------------------------

@mcp.tool()
async def export_list(list_id: str, format: str = "json") -> str:
    """Download the generated email sequences for a COMPLETED list.

    Only call this AFTER get_list_status shows processing_status = 'completed'.
    If the list is not yet completed, you'll get a 409 error — poll first.

    Args:
        list_id: The list UUID to export.
        format: Output format — 'json' (default, structured) or 'csv' (raw CSV string).
                Use 'json' when the agent needs to read/process the sequences.
                Use 'csv' when the user wants a file to upload to their sending tool.

    Returns:
        JSON: Structured lead + sequence data.
        CSV: Raw CSV content (same format as MachFive UI download).
    """
    params = {"format": format}

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.get(
            f"{MACHFIVE_BASE_URL}/api/v1/lists/{list_id}/export",
            headers=_headers(),
            params=params,
        )

    if resp.status_code == 409:
        return (
            "List is not yet completed. Call get_list_status first to check "
            "processing_status, and wait until it shows 'completed'."
        )

    if resp.status_code != 200:
        return _error_message(resp)

    if format == "csv":
        return f"CSV export for list {list_id}:\n\n{resp.text}"

    try:
        data = resp.json()
    except Exception:
        return resp.text

    leads = data.get("leads", [])
    lines = [f"Exported {len(leads)} lead(s) from list {list_id}:\n"]

    for lead in leads:
        lead_label = lead.get("name") or lead.get("email", "unknown")
        company = lead.get("company", "")
        if company:
            lead_label += f" ({company})"
        lines.append(f"=== {lead_label} ===")
        lines.append(f"Email: {lead.get('email', 'N/A')}")

        for step in lead.get("sequence", []):
            lines.append(f"\n  --- Email {step.get('step', '?')} ---")
            lines.append(f"  Subject: {step.get('subject', '')}")
            lines.append(f"  {step.get('body', '')}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if TRANSPORT == "stdio":
        if not MACHFIVE_API_KEY:
            print("WARNING: MACHFIVE_API_KEY is not set.")
            print("Set it: export MACHFIVE_API_KEY=mf_live_...")
        mcp.run()
    else:
        # Lazy imports — only needed for HTTP transport, not stdio
        import uvicorn
        from fastapi import FastAPI
        from starlette.middleware.base import BaseHTTPMiddleware
        from starlette.requests import Request as StarletteRequest
        from starlette.datastructures import MutableHeaders

        # Create the MCP ASGI app
        mcp_app = mcp.http_app(path="/mcp", stateless_http=True)

        # Create wrapper FastAPI app with health endpoint
        app = FastAPI(title="MachFive MCP Server", lifespan=mcp_app.lifespan)

        # -- Middleware: /mcp/{api_key} → /mcp with Authorization header --
        class URLPathAuthMiddleware(BaseHTTPMiddleware):
            """Rewrite /mcp/{api_key} to /mcp and inject Authorization header.

            This lets MCP clients that don't support custom headers pass
            the API key directly in the URL path instead.
            """
            async def dispatch(self, request: StarletteRequest, call_next):
                path = request.scope.get("path", "")
                # Match /mcp/{api_key} — key is everything after /mcp/
                if path.startswith("/mcp/") and len(path) > 5:
                    api_key = path[5:]  # strip "/mcp/"
                    # Rewrite path to /mcp
                    request.scope["path"] = "/mcp"
                    # Inject Authorization header if not already present
                    if not request.headers.get("authorization"):
                        headers = MutableHeaders(scope=request.scope)
                        headers.append("authorization", f"Bearer {api_key}")
                return await call_next(request)

        app.add_middleware(URLPathAuthMiddleware)

        @app.get("/")
        async def health():
            """Health check — returns server status and auth info."""
            return {
                "status": "healthy",
                "server": "machfive-mcp",
                "version": "1.0.0",
                "endpoints": {
                    "mcp": "/mcp",
                    "mcp_with_key": "/mcp/{api_key}",
                },
                "authentication": {
                    "methods": [
                        "URL path: /mcp/YOUR_API_KEY",
                        "Header: Authorization: Bearer YOUR_API_KEY",
                        "Header: Authorization: YOUR_API_KEY (Bearer prefix optional)",
                    ],
                    "note": "Each user passes their own MachFive API key. Bearer prefix is optional for Authorization header.",
                },
            }

        # Mount MCP server
        app.mount("/", mcp_app)

        logger.info(f"Starting MachFive MCP server on 0.0.0.0:{PORT}")
        uvicorn.run(app, host="0.0.0.0", port=PORT)
