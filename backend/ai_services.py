# backend/ai_services.py
import logging
import asyncio
from typing import List, Dict, Any

from fastapi import HTTPException

# Attempt to import and configure GenAI
try:
    import google.generativeai as genai
    from .config import GOOGLE_API_KEY # Import from local config
    
    SDK_CONFIGURED_SUCCESSFULLY = False
    if GOOGLE_API_KEY and genai:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            SDK_CONFIGURED_SUCCESSFULLY = True
            logging.info("Google Generative AI SDK configured successfully in ai_services.py.")
        except Exception as e:
            logging.error(f"Failed to configure Google Generative AI SDK in ai_services.py: {e}")
            SDK_CONFIGURED_SUCCESSFULLY = False
    elif not GOOGLE_API_KEY:
        logging.error("GOOGLE_API_KEY not found for ai_services.py.")
        SDK_CONFIGURED_SUCCESSFULLY = False
    
except ImportError:
    logging.error("'google.generativeai' library not found. Text AI features will be unavailable.")
    genai = None
    SDK_CONFIGURED_SUCCESSFULLY = False

logger = logging.getLogger(__name__)

def construct_text_to_slide_prompt(text_input: str, num_slides: int, desired_tone: str = "professional", include_image_keywords: bool = False) -> str:
    image_instruction = ""
    image_example_field = ""
    # For now, image generation is off, so include_image_keywords will be false
    # if include_image_keywords:
    #     image_instruction = "\n7. For each content slide, also provide 'image_keywords': 2-3 relevant keywords."
    #     image_example_field = ', "image_keywords": "technology, future"'

    return f"""
    You are an expert presentation designer. Your goal is to transform the following raw text into a structured, engaging, and {desired_tone} PowerPoint presentation outline.

    Instructions:
    1. Generate content for approximately {num_slides} main content slides.
    2. Create a clear title slide as the first item in the JSON list. Its 'title' should be the presentation title, and 'points' can be a short subtitle (e.g., ["A brief overview"]) or an empty list.
    3. For each subsequent content slide, provide a concise 'title' and a list of 3 to 5 key 'points'.{image_instruction}
    4. The entire output MUST be a valid JSON list of objects. Each object represents one slide.
    5. Only output the JSON list. Do not include any conversational text or explanations.

    Example of a content slide object:
    {{"title": "Example Slide Title", "points": ["Key takeaway 1", "Detail A"]{image_example_field}}}
    
    Example of a title slide object:
    {{"title": "The Impact of AI", "points": ["Exploring new frontiers"]}}

    Text to analyze:
    ---
    {text_input}
    ---
    JSON output:
    """

async def call_google_ai_for_ppt_content(prompt_text: str, model_name: str = "gemini-1.5-flash-latest", max_retries: int = 3, delay_seconds: int = 5) -> str:
    if not SDK_CONFIGURED_SUCCESSFULLY or not genai:
        logger.error("Google AI SDK not configured or library not loaded. Cannot make API call.")
        raise HTTPException(status_code=503, detail="AI Service (Text) Unconfigured or Unavailable.")
    
    model = genai.GenerativeModel(model_name)
    for attempt in range(max_retries):
        try:
            logger.info(f"Google AI API call attempt {attempt + 1} using model {model_name} for PPT content.")
            response = await model.generate_content_async(prompt_text)
            
            generated_text = ""
            # Robust extraction logic for Gemini
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                generated_text = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
            elif response.parts: # Older or simpler response structures
                generated_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
            elif hasattr(response, 'text') and response.text: # General fallback
                 generated_text = response.text
            else:
                logger.warning(f"Attempt {attempt + 1}: Unexpected response structure or no text from Gemini: {response}")

            if not generated_text or not generated_text.strip():
                logger.warning(f"Attempt {attempt + 1}: Google AI returned empty content for PPT.")
                if attempt == max_retries - 1: 
                    raise HTTPException(status_code=500, detail="AI service returned empty content after multiple retries.")
                await asyncio.sleep(delay_seconds * (attempt + 1)) # Exponential backoff
                continue
            
            logger.info("Google AI API call for PPT content successful.")
            return generated_text.strip()
        except Exception as e:
            logger.error(f"Error during Google AI API call attempt {attempt + 1} for PPT content: {e}", exc_info=True)
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail=f"Failed to get response from AI service (Text): {str(e)}")
            await asyncio.sleep(delay_seconds * (attempt + 2)) # Slightly increased exponential backoff
            
    raise HTTPException(status_code=500, detail="AI service call (Text) failed after all retries.")

# Placeholder for future image generation service
# async def generate_image_from_keywords(keywords: str, slide_index: int) -> Optional[str]:
#     logger.info(f"Image generation requested for slide {slide_index} with keywords: {keywords}")
#     # Replace with actual image generation API call
#     await asyncio.sleep(1) # Simulate delay
#     return "path/to/generated_image.png" # Return path to saved image