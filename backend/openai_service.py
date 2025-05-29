import os
import time
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastapi import HTTPException

# Setup logging
logger = logging.getLogger(__name__)

# Load .env file from the backend directory
# Assumes openai_service.py is in the backend/ directory, and .env is also in backend/
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY is missing or invalid. Ensure .env file is present in backend/ and correctly configured.")
    raise RuntimeError("OPENAI_API_KEY is missing or invalid in the .env file. Service cannot start.")

client = AsyncOpenAI(api_key=api_key)
logger.info(f"OpenAI client initialized in openai_service. OPENAI_API_KEY loaded: {api_key is not None}")

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

async def call_openai_with_retry(prompt: str, retries=3, initial_delay=5):
    delay = initial_delay
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"OpenAI API call attempt {attempt}")
            # Define a total timeout for the attempt, e.g., 45 seconds
            attempt_timeout = 45
            try:
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert in generating presentation slides."},
                            {"role": "user", "content": prompt},
                        ],
                        timeout=30 # This is OpenAI's own timeout for the operation
                    ),
                    timeout=attempt_timeout # This is the asyncio timeout for the entire awaitable
                )
            except asyncio.TimeoutError:
                logger.error(f"OpenAI API call attempt {attempt} timed out after {attempt_timeout} seconds by asyncio.wait_for.")
                if attempt == retries:
                    raise HTTPException(status_code=504, detail=f"OpenAI API call timed out after {attempt_timeout}s and {retries} retries.")
                raise TimeoutError(f"asyncio.wait_for timed out after {attempt_timeout}s") # This will be caught by `except Exception as e`

            # Ensure response and content are valid before returning
            if not response or not response.choices or response.choices[0].message.content is None:
                logger.error(f"OpenAI returned an empty or invalid response on attempt {attempt}.")
                if attempt == retries:
                    raise HTTPException(status_code=500, detail="OpenAI returned an empty or invalid response after multiple retries.")
                # Allow retry for empty/invalid responses as well
                await asyncio.sleep(delay) # wait before retrying for this case too
                delay *= 2 # increase delay
                continue # Explicitly continue to next attempt

            return response
        except HTTPException as http_exc: # Re-raise HTTPException if it's already one
            raise http_exc
        except Exception as e:
            err_msg = str(e)
            if "rate limit" in err_msg.lower() or "429" in err_msg:
                if attempt == retries:
                    logger.error("Rate limit exceeded, no more retries left.")
                    raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
                logger.warning(f"Rate limit hit, retrying after {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2
            # Check if it's an asyncio timeout specifically, to ensure it's handled for retry
            elif isinstance(e, TimeoutError) and "asyncio.wait_for timed out" in err_msg:
                 logger.warning(f"Asyncio timeout error on attempt {attempt}, retrying after {delay} seconds... Error: {err_msg}")
                 if attempt == retries: # Should have been handled by the specific asyncio.TimeoutError block, but as a safeguard
                     raise HTTPException(status_code=504, detail=f"OpenAI API call timed out after {attempt_timeout}s and {retries} retries.")
                 await asyncio.sleep(delay)
                 delay *= 2
            else:
                logger.error(f"OpenAI API error: {err_msg}")
                # On the last attempt, or for generic errors, raise HTTPException
                if attempt == retries:
                    raise HTTPException(status_code=500, detail=f"OpenAI API error: {err_msg}")
                # If not the last attempt, log and retry for other errors too
                logger.warning(f"Encountered API error, retrying after {delay} seconds... Error: {err_msg}")
                await asyncio.sleep(delay)
                delay *= 2


    # This part should ideally not be reached if retries > 0 because an exception
    # should have been raised from within the loop (either the final attempt's error or a re-raised one).
    logger.error("call_openai_with_retry exhausted retries without returning a response or raising a specific handled error.")
    raise HTTPException(status_code=500, detail="Failed to get a response from OpenAI after multiple retries.")
