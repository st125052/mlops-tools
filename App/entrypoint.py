import json
import os
import boto3

def fetch_secret(secret_name, region, key):
    client = boto3.client("secretsmanager", region_name=region)
    raw = client.get_secret_value(SecretId=secret_name)["SecretString"]
    return json.loads(raw)[key]

region = os.environ["AWS_REGION"]
secret_name = os.environ["AWS_SECRET_LITELLM"]

os.environ["OPENAI_API_KEY"] = fetch_secret(secret_name, region, "api_key")

os.execvp("bash", ["bash", "start.sh"])