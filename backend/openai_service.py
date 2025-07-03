import os
import time
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from fastapi import HTTPException
from openai import AzureOpenAI

# Setup logging
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Fetch required values
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("OPENAI_API_VERSION")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Basic validations
if not all([api_key, endpoint, api_version, deployment_name]):
    raise RuntimeError("One or more Azure OpenAI environment variables are missing.")

# Initialize AzureOpenAI client
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=endpoint,
    api_version=api_version
)

logger.info("Azure OpenAI client initialized.")

def generate_prompt(topic: str, tone: str) -> str:
    return (
        f"Create a {tone} PowerPoint presentation outline on the topic: '{topic}'.\n"
        "Return it in this JSON format:\n"
        "{\n"
        "  \"slides\": [\n"
        "    {\"title\": \"Slide Title\", \"bullets\": [\"Point 1\", \"Point 2\"]},\n"
        "    {\"title\": \"Another Slide\", \"bullets\": [\"Bullet A\", \"Bullet B\"]}\n"
        "  ]\n"
        "}"
    )

def call_openai_with_retry(prompt: str, retries=3, delay=5):
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Azure OpenAI call attempt {attempt}")
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),  # e.g., "gpt-4o"
                messages=[
                    {"role": "system", "content": "You are an expert in generating presentation slides."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=0.95,
                frequency_penalty=0
            )
            return response
        except Exception as e:
            logger.error(f"Azure OpenAI error: {e}")
            if attempt == retries:
                raise HTTPException(status_code=500, detail=f"OpenAI call failed after {retries} retries.")
            time.sleep(delay)
            delay *= 2

    raise HTTPException(status_code=500, detail="Azure OpenAI failed after multiple retries.")
