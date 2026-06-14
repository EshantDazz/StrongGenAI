# Deploying Weather MCP Server to Vercel — Self Study Guide

Vercel is a serverless platform — you push code, it handles servers, scaling, and HTTPS automatically. Free tier is generous enough for self-study.

---

## How This Works

FastMCP's `streamable_http_app()` method returns a standard **Starlette ASGI app**. Vercel can run ASGI apps natively as serverless Python functions. You just expose it as `app` and Vercel picks it up.

```
Your laptop / any tool
        |
        | POST https://your-project.vercel.app/mcp
        |
   ┌────▼───────────────────────────┐
   │  Vercel Serverless Function     │
   │  Python 3.12 runtime            │
   │                                 │
   │  app = mcp.streamable_http_app()│
   │  FastMCP handles /mcp route     │
   └─────────────────────────────────┘
```

---

## Important Limitations Before You Start

| Limitation | Detail |
|---|---|
| **Execution timeout** | 10 seconds (Hobby), 60 seconds (Pro) |
| **Stateless** | No memory between requests — fine for tool calls |
| **Cold starts** | First request after idle takes ~1-2s extra |
| **No persistent connections** | Long SSE streams will hit the timeout |

For basic MCP tool calls like `get_weather("London")`, Vercel works fine. For heavy streaming agents with long response chains, use EC2 instead.

---

## Prerequisites

- Vercel account — sign up free at [vercel.com](https://vercel.com)
- Vercel CLI installed:

```bash
npm install -g vercel
```

- Log in:

```bash
vercel login
```

---

## Step 1 — Create a Separate Folder for the Vercel Project

Vercel deploys a whole folder. Keep it separate and clean:

```bash
mkdir weather-mcp-vercel
cd weather-mcp-vercel
```

Your final structure will look like this:

```
weather-mcp-vercel/
├── api/
│   └── index.py        ← the MCP ASGI app
├── requirements.txt
└── vercel.json
```

---

## Step 2 — Create the ASGI Entry Point

Create the `api/` folder and `api/index.py`:

```bash
mkdir api
```

**`api/index.py`**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")


@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The current weather in {city} is sunny with a temperature of 25°C."


# Vercel looks for a variable named 'app' as the ASGI entry point
app = mcp.streamable_http_app()
```

Two things happening here:
- `streamable_http_app()` returns the Starlette app with `/mcp` route wired up internally
- `app` is the magic variable name Vercel recognises as the ASGI handler

---

## Step 3 — Create requirements.txt

At the root of `weather-mcp-vercel/`:

**`requirements.txt`**

```
mcp[cli]
fastmcp
starlette
uvicorn
```

---

## Step 4 — Create vercel.json

This tells Vercel to route all incoming requests to your `api/index.py` function:

**`vercel.json`**

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/api/index" }
  ]
}
```

Without this, Vercel would only route `/api/index` to your function. With this rewrite, a request to `/mcp` hits `/api/index`, and the Starlette app inside handles the `/mcp` path.

---

## Step 5 — Deploy

From inside `weather-mcp-vercel/`:

```bash
vercel
```

Vercel will ask a few questions on first deploy:

```
? Set up and deploy "weather-mcp-vercel"? → Yes
? Which scope? → your account
? Link to existing project? → No
? What's your project's name? → weather-mcp-vercel
? In which directory is your code located? → ./
? Want to override the settings? → No
```

When it finishes you get a URL like:

```
https://weather-mcp-vercel-abc123.vercel.app
```

Your MCP endpoint is live at:

```
https://weather-mcp-vercel-abc123.vercel.app/mcp
```

---

## Step 6 — Test the Live Endpoint

```bash
curl -X POST https://weather-mcp-vercel-abc123.vercel.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

Expected response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get the current weather for a given city.",
        "inputSchema": { ... }
      }
    ]
  }
}
```

If you see this, the server is working.

---

## Step 7 — Update client.py

Back in your main project, update `client.py` with the Vercel URL:

```python
client = MultiServerMCPClient({
    "math": {
        "command": "python",
        "args": ["mcp/mathsserver.py"],
        "transport": "stdio",
    },
    "weather": {
        "url": "https://weather-mcp-vercel-abc123.vercel.app/mcp",  # ← Vercel URL
        "transport": "streamable-http",
    },
})
```

Run the client:

```bash
python mcp/client.py
```

The math server still runs locally via stdio. The weather server is now hitting Vercel over the internet.

---

## Step 8 — Promote to a Production URL (Optional)

The URL from `vercel` command is a preview URL. To get a stable production URL:

```bash
vercel --prod
```

This gives you:

```
https://weather-mcp-vercel.vercel.app
```

This URL stays the same on every future deploy — use this in `client.py`.

---

## Redeploying After Changes

Every time you change `api/index.py` (add a new tool, update logic), just run:

```bash
vercel --prod
```

Vercel redeploys in ~30 seconds. The URL stays the same.

---

## Adding a Custom Domain (Optional)

If you want `https://mcp.yourdomain.com/mcp` instead of a `vercel.app` URL:

1. Go to Vercel Dashboard → your project → Settings → Domains
2. Add your domain
3. Vercel gives you DNS records to add at your domain registrar
4. Takes ~5 minutes to propagate

---

## Adding Environment Variables (for real API keys later)

When you replace the dummy weather logic with a real weather API (like OpenWeatherMap), you'll need an API key. Do NOT hardcode it.

```bash
# Add a secret to your Vercel project
vercel env add WEATHER_API_KEY
```

Then in `api/index.py`:

```python
import os

@mcp.tool()
def get_weather(city: str) -> str:
    api_key = os.environ["WEATHER_API_KEY"]
    # use api_key to call real weather API
```

Vercel injects `WEATHER_API_KEY` at runtime — it never appears in your code or git history.

---

## Comparing EC2 vs Vercel for MCP

| | EC2 | Vercel |
|---|---|---|
| Setup time | ~20 minutes | ~5 minutes |
| Cost | ~$8/mo (always on) | Free tier available |
| Persistent connections | Yes — no timeout | No — 10s limit |
| Cold starts | None | ~1-2s first request |
| HTTPS | Manual (Nginx + Certbot) | Automatic |
| Custom domain | Manual setup | One-click |
| Best for | Long-running agents, streaming | Quick tool calls, self-study |

---

## Quick Reference

```bash
# First deploy
cd weather-mcp-vercel
vercel

# Production deploy
vercel --prod

# View logs
vercel logs https://weather-mcp-vercel.vercel.app

# List deployments
vercel ls

# Remove a deployment
vercel remove weather-mcp-vercel
```
