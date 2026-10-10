import boto3
from dotenv import load_dotenv

load_dotenv()

client = boto3.client("bedrock-runtime", region_name="eu-north-1")

response = client.converse(
    modelId="eu.anthropic.claude-haiku-4-5-20251001-v1:0",
    messages=[{"role": "user", "content": [{"text": "Say hello in one short sentence."}]}],
)

print(response["output"]["message"]["content"][0]["text"])