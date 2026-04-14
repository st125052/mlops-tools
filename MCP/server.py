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


def _load_firecrawl_credentials():
    region = os.environ["AWS_REGION"]
    secret_name = os.environ["AWS_SECRET_FIRECRAWL"]
    if not secret_name:
        return "", ""

    raw = read_secret(secret_name, region)
    parsed = json.loads(raw)

    return parsed.get("api_base", ""), parsed.get("api_key", "")


FIRECRAWL_API_BASE, FIRECRAWL_API_KEY = _load_firecrawl_credentials()


async def firecrawl_extract(url):
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "url": url,
        "formats": ["markdown", "html"],
        "onlyMainContent": True,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(FIRECRAWL_API_BASE, headers=headers, json=payload)
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
