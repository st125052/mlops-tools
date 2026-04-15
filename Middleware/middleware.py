import json
import os
import subprocess
from pathlib import Path
import boto3

def read_secret(secret_name, region):
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return response["SecretString"]


def secret_value(secret_name_env, json_key):
    region = os.environ["AWS_REGION"]
    secret_name = os.environ[secret_name_env]
    
    raw = read_secret(secret_name, region)
    parsed = json.loads(raw)
    value = parsed.get(json_key, "")
    
    return value if isinstance(value, str) else str(value)


def main():
    MCP_SERVER_URL = os.environ["MCP_SERVER_URL"]
    MCP_API_KEY = secret_value("AWS_SECRET_MCP", "api_key")
    LITELLM_MASTER_KEY = secret_value("AWS_SECRET_LITELLM", "api_key")
    OPENAI_API_BASE = secret_value("AWS_SECRET_OPENAI", "api_base")
    OPENAI_API_KEY = secret_value("AWS_SECRET_OPENAI", "api_key")
    OPENAI_MODEL = secret_value("AWS_SECRET_OPENAI", "model")

    missing = [
        name
        for name, value in [
            ("api_base", OPENAI_API_BASE),
            ("api_key", OPENAI_API_KEY),
            ("model", OPENAI_MODEL),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")

    template = Path("/app/config.template.yaml").read_text()
    rendered = (
        template.replace("{{LITELLM_MASTER_KEY}}", LITELLM_MASTER_KEY)
        .replace("{{OPENAI_API_BASE}}", OPENAI_API_BASE)
        .replace("{{OPENAI_API_KEY}}", OPENAI_API_KEY)
        .replace("{{OPENAI_MODEL}}", OPENAI_MODEL)
        .replace("{{MCP_SERVER_URL}}", MCP_SERVER_URL)
        .replace("{{MCP_API_KEY}}", MCP_API_KEY)
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
