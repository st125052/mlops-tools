import json
import os
import subprocess
from pathlib import Path
import boto3

def read_secret(secret_name, region):
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return response["SecretString"]


def secret_value(secret_name_env, json_key=None):
    region = os.environ["AWS_REGION"]
    secret_name = os.environ[secret_name_env]
    if not secret_name:
        return ""

    raw = read_secret(secret_name, region)
    if json_key is None:
        return raw

    parsed = json.loads(raw)
    value = parsed.get(json_key, "")
    return value if isinstance(value, str) else str(value)


def main():
    litellm_master_key = secret_value("AWS_SECRET_LITELLM_MASTER_KEY")
    OPENAI_API_BASE = secret_value("AWS_SECRET_OPENTYPHOON", "api_base")
    OPENAI_API_KEY = secret_value("AWS_SECRET_OPENTYPHOON", "api_key")
    OPENAI_MODEL = secret_value("AWS_SECRET_OPENTYPHOON", "model")
    mcp_server_url = os.environ["MCP_SERVER_URL"]

    missing = [
        name
        for name, value in [
            ("AWS_SECRET_LITELLM_MASTER_KEY (secret value)", litellm_master_key),
            ("AWS_SECRET_OPENTYPHOON api_base", OPENAI_API_BASE),
            ("AWS_SECRET_OPENTYPHOON api_key", OPENAI_API_KEY),
            ("AWS_SECRET_OPENTYPHOON model", OPENAI_MODEL),
            ("MCP_SERVER_URL", mcp_server_url),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")

    template = Path("/app/config.template.yaml").read_text()
    rendered = (
        template.replace("{{LITELLM_MASTER_KEY}}", litellm_master_key)
        .replace("{{OPENAI_API_BASE}}", OPENAI_API_BASE)
        .replace("{{OPENAI_API_KEY}}", OPENAI_API_KEY)
        .replace("{{OPENAI_MODEL}}", OPENAI_MODEL)
        .replace("{{MCP_SERVER_URL}}", mcp_server_url)
    )

    config_path = Path("/app/config.yaml")
    config_path.write_text(rendered)

    subprocess.run(
        [
            "litellm",
            "--config",
            str(config_path),
            "--host",
            "0.0.0.0",
            "--port",
            "4000",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
