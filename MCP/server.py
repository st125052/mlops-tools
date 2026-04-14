import json
import os
import boto3
import httpx
from fastmcp import FastMCP

mcp = FastMCP("AIT")


def read_secret(secret_name, region):
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return response["SecretString"]


def get_firecrawl_api_key():
    secret_name = os.getenv("AWS_SECRET_FIRECRAWL")
    if not secret_name:
        return ""

    region = os.environ["AWS_REGION"]
    raw = read_secret(secret_name, region)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return str(parsed.get("api_key", ""))
    except json.JSONDecodeError:
        pass
    return raw


async def firecrawl_extract(url):
    api_key = get_firecrawl_api_key()
    if not api_key:
        raise RuntimeError("Firecrawl API key is not configured (AWS_SECRET_FIRECRAWL / Secrets Manager)")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "url": url,
        "formats": ["markdown", "html"],
        "onlyMainContent": True,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.firecrawl.dev/v1/scrape", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    if not data.get("success"):
        raise RuntimeError(f"Firecrawl scrape failed: {data}")

    result = data.get("data", {})
    return {
        "source": "firecrawl",
        "url": url,
        "title": result.get("metadata", {}).get("title", ""),
        "markdown": result.get("markdown", ""),
        "html": result.get("html", ""),
        "metadata": result.get("metadata", {}),
    }


@mcp.tool
def healthcheck():
    return {"status": "ok", "server": "AIT"}


@mcp.tool
async def fetch_official_page(url):
    return await firecrawl_extract(url)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp/")