import os
import logging
import json
import time
from openai import OpenAI
from fastapi import HTTPException
from pathlib import Path
from dotenv import load_dotenv

# This file (`openai_service.py`) is responsible for all interactions with the OpenAI API.
# It includes functions for generating prompts, calling the API (with retries),
# and processing the API's responses to extract relevant data for presentation generation.
# API keys and client initialization are also handled here.

# Logging setup
logger = logging.getLogger(__name__)

# Environment variable loading for OPENAI_API_KEY
dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY not found in .env file or environment variables.")
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file or as an environment variable.")

# OpenAI client initialization
client = OpenAI(api_key=api_key)

def generate_prompt(topic: str, tone: str) -> str:
    """
    Generates a prompt for the OpenAI API to create presentation slides.
    """
    return f"""
Create a 7-slide presentation on the topic: '{topic}'.
The tone of the presentation should be '{tone}'.
Each slide should have a "title" and "content".
The content should be a few bullet points.
Return the presentation as a JSON object with a single key "slides",
which is a list of slide objects.
Example:
{{
  "slides": [
    {{
      "title": "Slide 1 Title",
      "content": "- Bullet point 1\n- Bullet point 2"
    }},
    // ... more slides
  ]
}}
"""

def call_openai_with_retry(prompt: str, retries=3, initial_delay=5):
    """
    Calls the OpenAI API with a retry mechanism.
    """
    delay = initial_delay
    for attempt in range(retries):
        try:
            logger.info(f"Attempt {attempt + 1} to call OpenAI API.")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            logger.info("OpenAI API call successful.")
            return response
        except Exception as e:
            logger.error(f"OpenAI API call failed on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.error("Max retries reached. OpenAI API call failed.")
                raise HTTPException(status_code=500, detail=f"OpenAI API call failed after {retries} retries: {str(e)}")

def generate_presentation_slides_with_openai(topic: str, tone: str) -> list:
    """
    Generates presentation slides by calling the OpenAI API.
    """
    prompt = generate_prompt(topic, tone)
    response = call_openai_with_retry(prompt)

    if not response or not response.choices:
        logger.error("Invalid response from OpenAI API: No choices found.")
        raise HTTPException(status_code=500, detail="Invalid response from OpenAI API: No choices found.")

    output_text = response.choices[0].message.content
    if output_text is None:
        logger.error("Invalid response from OpenAI API: No content found in message.")
        raise HTTPException(status_code=500, detail="Invalid response from OpenAI API: No content.")

    output_text = output_text.strip()

    try:
        logger.info("Parsing JSON response from OpenAI.")
        # Handle potential ```json ... ``` markers
        if output_text.startswith("```json"):
            output_text = output_text[7:]
            if output_text.endswith("```"):
                output_text = output_text[:-3]
        elif output_text.startswith("```"): # Handle cases where only ``` is present
             output_text = output_text[3:]
             if output_text.endswith("```"):
                output_text = output_text[:-3]
        
        data = json.loads(output_text)
        slides = data.get("slides", [])
        if not slides:
            logger.warning("No slides found in the parsed JSON data.")
        return slides
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response from OpenAI: {e}")
        logger.error(f"Problematic JSON string: {output_text[:500]}...") # Log first 500 chars
        raise HTTPException(status_code=500, detail=f"Failed to decode JSON response from OpenAI: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing OpenAI response: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
