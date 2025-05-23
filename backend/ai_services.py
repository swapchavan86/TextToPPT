# backend/ai_services.py
import logging
import asyncio
import json
from typing import List, Dict, Any, Optional

from fastapi import HTTPException
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Define the Generative Model to use
MODEL_NAME = "models/gemini-1.5-flash-latest" 

# Global flag for model availability/support
MODEL_IS_AVAILABLE_AND_SUPPORTED = False 

# Attempt to import and configure GenAI
try:
    from .config import GOOGLE_API_KEY # Import from local config
    
    SDK_CONFIGURED_SUCCESSFULLY = False
    if GOOGLE_API_KEY:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            SDK_CONFIGURED_SUCCESSFULLY = True
            logger.info("Google Generative AI SDK configured successfully in ai_services.py.")
            
            found_desired_model = False
            listed_any_models = False 
            try:
                logger.info("Attempting to list available Generative AI models:")
                models_list = list(genai.list_models()) 
                
                if not models_list:
                    logger.warning("No Generative AI models were listed. This could indicate API key issues, region limitations, or a problem with the SDK itself.")
                else:
                    listed_any_models = True
                    for m in models_list:
                        logger.info(f"  - Found model: {m.name} (Supports: {m.supported_generation_methods})")
                        if m.name == MODEL_NAME and "generateContent" in m.supported_generation_methods:
                            found_desired_model = True
                            logger.info(f"  -> Configured model '{MODEL_NAME}' is available and supports 'generateContent'.")

                if not listed_any_models: 
                    logger.error("No models were found or listed, indicating a potential issue with API connectivity or key permissions.")
                    SDK_CONFIGURED_SUCCESSFULLY = False 
                elif not found_desired_model:
                    logger.error(f"Configured model '{MODEL_NAME}' is not found in the available list or does not support 'generateContent'. Please check available models above.")
                    SDK_CONFIGURED_SUCCESSFULLY = False 
                else:
                    MODEL_IS_AVAILABLE_AND_SUPPORTED = True 

            except Exception as e:
                logger.error(f"CRITICAL ERROR during Generative AI model listing: {e}", exc_info=True)
                SDK_CONFIGURED_SUCCESSFULLY = False 

        except Exception as e:
            logger.error(f"Failed to configure Google Generative AI SDK in ai_services.py: {e}", exc_info=True)
            SDK_CONFIGURED_SUCCESSFULLY = False
    else:
        logger.error("GOOGLE_API_KEY not found for ai_services.py. SDK configuration failed.")
        SDK_CONFIGURED_SUCCESSFULLY = False
    
except ImportError:
    logger.error("'google.generativeai' library not found. Text AI features will be unavailable. Please install it using: pip install google-generativeai")
    genai = None
    SDK_CONFIGURED_SUCCESSFULLY = False


def construct_text_to_slide_prompt(text_input: str, num_slides: int, desired_tone: str = "professional", include_image_keywords: bool = False) -> str:
    """
    Constructs a detailed prompt for the Google AI model to generate PowerPoint slide content.
    """
    image_instruction = ""
    if include_image_keywords:
        image_instruction = "For each slide, also suggest 2-3 concise keywords for a relevant image, in a field named 'image_keywords'."

    prompt = f"""
You are an expert presentation designer and content summarizer. Your task is to transform raw text into a structured JSON format suitable for a PowerPoint presentation.

Based on the following text, create content for {num_slides} distinct slides.
Each slide should have a concise 'title', a 'description' summarizing the main point, and a 'points' array containing 3-5 key bullet points.
**Crucially, ensure that the 'description' field is complete and all bullet points in the 'points' array are fully formed sentences or phrases, not truncated.**
The overall tone of the presentation should be: {desired_tone}.

Ensure the output is a JSON array of slide objects, with each object structured as follows:
{{
  "title": "Concise Slide Title",
  "description": "Brief summary of the slide's content.",
  "points": [
    "Key point 1",
    "Key point 2",
    "Key point 3"
  ]
}}
{image_instruction}

Example of desired JSON structure (array of objects):
[
  {{
    "title": "Introduction to Topic",
    "description": "An overview of the main subject.",
    "points": [
      "Define key concepts",
      "Set the stage for discussion"
    ]
  }},
  {{
    "title": "Deep Dive into Subtopic",
    "description": "Exploring specific aspects.",
    "points": [
      "Detail mechanism A",
      "Discuss impact B",
      "Highlight challenge C"
    ]
  }}
]

Here is the text to analyze:
"{text_input}"

Please provide only the JSON output, without any additional text or formatting outside the JSON array.
"""
    logger.debug(f"Constructed AI prompt (first 200 chars): {prompt[:200]}...")
    return prompt

async def call_google_ai_for_ppt_content(text_input: str, num_slides: int, desired_tone: str) -> str:
    """
    Calls the Google Generative AI model to generate structured content for PowerPoint slides.
    """
    if not SDK_CONFIGURED_SUCCESSFULLY:
        raise HTTPException(status_code=503, detail="Google Generative AI SDK is not configured. Please check API key and server logs for details.")
    
    if not MODEL_IS_AVAILABLE_AND_SUPPORTED: 
         raise HTTPException(status_code=503, detail=f"The configured AI model '{MODEL_NAME}' is not available or does not support text generation. Check server logs for available models.")

    max_retries = 3
    delay_seconds = 2
    request_timeout_seconds = 120 

    model = genai.GenerativeModel(MODEL_NAME) 

    prompt = construct_text_to_slide_prompt(text_input, num_slides, desired_tone)

    for attempt in range(max_retries):
        try:
            logger.info(f"Calling Google AI for PPT content (Attempt {attempt + 1})...")
            
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=genai.GenerationConfig(max_output_tokens=4096), # Added this line
                request_options={"timeout": request_timeout_seconds}
            )
            
            generated_text = ""
            if response and response.parts:
                for part in response.parts:
                    generated_text += part.text
            
            # Remove markdown code block fences
            generated_text_cleaned = generated_text.strip()
            if generated_text_cleaned.startswith("```json"):
                generated_text_cleaned = generated_text_cleaned[len("```json"):].strip()
            if generated_text_cleaned.endswith("```"):
                generated_text_cleaned = generated_text_cleaned[:-len("```")].strip()
            
            logger.info(f"Raw AI Generated Text (Attempt {attempt + 1}): '{generated_text.strip()[:500]}'...") # Log original for debugging
            logger.info(f"Cleaned AI Generated Text (Attempt {attempt + 1}): '{generated_text_cleaned[:500]}'...") # Log cleaned for debugging

            if not generated_text_cleaned: # Check cleaned text
                logger.warning(f"Attempt {attempt + 1}: Google AI returned empty or only markdown content for PPT.")
                if attempt == max_retries - 1: 
                    raise HTTPException(status_code=500, detail="AI service returned empty content after multiple retries.")
                await asyncio.sleep(delay_seconds * (attempt + 1)) 
                continue
            
            try:
                json_data = json.loads(generated_text_cleaned) # Parse cleaned text
                if not isinstance(json_data, list):
                    raise ValueError("AI response is not a JSON array.")
                for item in json_data:
                    if not all(k in item for k in ["title", "description", "points"]):
                        raise ValueError("AI response JSON objects are missing required fields.")
                    if not isinstance(item.get("points"), list):
                        raise ValueError("AI response 'points' field is not a list.")
            except json.JSONDecodeError as e:
                logger.error(f"Attempt {attempt + 1}: AI response is not valid JSON: {e}")
                if attempt == max_retries - 1:
                    raise HTTPException(status_code=500, detail=f"AI service returned invalid JSON: {str(e)}")
                await asyncio.sleep(delay_seconds * (attempt + 1))
                continue
            except ValueError as e:
                logger.error(f"Attempt {attempt + 1}: AI response JSON structure is invalid: {e}")
                if attempt == max_retries - 1:
                    raise HTTPException(status_code=500, detail=f"AI service returned invalid JSON structure: {str(e)}")
                await asyncio.sleep(delay_seconds * (attempt + 1))
                continue

            logger.info("Google AI API call for PPT content successful.")
            return generated_text_cleaned 
        except Exception as e:
            logger.error(f"Error during Google AI API call attempt {attempt + 1} for PPT content: {e}", exc_info=True)
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail=f"Failed to get response from AI service (Text): {str(e)}")
            await asyncio.sleep(delay_seconds * (attempt + 2))
            
    raise HTTPException(status_code=500, detail="AI service call (Text) failed after all retries.")