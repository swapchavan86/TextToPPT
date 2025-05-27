# backend/main.py
import logging
import os
import json
import asyncio
from typing import List, Dict, Any, Optional # Keep this for type hinting
import time # Keep for cleanup task
import sys # Keep for path manipulation / __main__ block
import uuid # Keep for ppt_utils if not moved there
import random # Keep for ppt_utils if not moved there


from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware # <<<<<<<<<<<< ADDED THIS IMPORT BACK
import uvicorn

# Import from our new local modules
from .config import (
    EFFECTIVE_ORIGINS,
    PPT_OUTPUT_DIR,
    # Other configs if needed by main directly
)
from .models import (
    TextToPPTRequest,
    PPTGenerationInfoResponse
)
from .ai_services import (
    construct_text_to_slide_prompt,
    call_google_ai_for_ppt_content,
    SDK_CONFIGURED_SUCCESSFULLY as AI_SDK_CONFIGURED # Alias for clarity
)
from .ppt_utils import (
    create_presentation_from_data
)

# --- Logging Setup ---
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- FastAPI App Initialization ---
app = FastAPI(title="Text-to-PPT Generator API V2")

# CORS Middleware
app.add_middleware(
    CORSMiddleware, # Now defined
    allow_origins=EFFECTIVE_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Background Task for Cleanup ---
def cleanup_file_task(file_path: str, delay_seconds: int = 600):
    logger.info(f"Scheduled cleanup for {file_path} in {delay_seconds}s.")
    time.sleep(delay_seconds) 
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")
        elif file_path:
            logger.info(f"Cleanup: File not found (already deleted or moved): {file_path}")
    except OSError as e:
        logger.error(f"Error cleaning up file {file_path}: {e}")


# --- API Endpoints ---
@app.post("/generate-ppt/", response_model=PPTGenerationInfoResponse)
async def generate_ppt_endpoint(request_data: TextToPPTRequest, background_tasks: BackgroundTasks, http_request: Request):
    if not AI_SDK_CONFIGURED:
        raise HTTPException(status_code=503, detail="AI Service is not configured on the server.")
    
    if not request_data.text_input or len(request_data.text_input.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text input is too short (minimum 10 characters).")

    APPLY_STYLING_IN_PPT = True 
    logger.info(f"Received /generate-ppt/. Text len: {len(request_data.text_input)}, "
                f"Slides: {request_data.num_slides}, Styling: {APPLY_STYLING_IN_PPT}")
    logger.info(f"Received text input (first 100 chars): {request_data.text_input[:100]}")
    
    try:
        prompt_for_ai = construct_text_to_slide_prompt(
            request_data.text_input,
            request_data.num_slides or 5
        )
        raw_slide_content_json = await call_google_ai_for_ppt_content(prompt_for_ai)
        logger.info(f"Raw AI JSON response (first 500 chars): {raw_slide_content_json[:500]}")
        try:
            cleaned_json = raw_slide_content_json.strip()
            if cleaned_json.startswith("```json"): cleaned_json = cleaned_json[len("```json"):].strip()
            elif cleaned_json.startswith("```"): cleaned_json = cleaned_json[len("```"):].strip()
            if cleaned_json.endswith("```"): cleaned_json = cleaned_json[:-len("```")].strip()
            
            parsed_ai_response: Dict[str, Any] = json.loads(cleaned_json)

            if not isinstance(parsed_ai_response, dict):
                logger.error(f"AI output was not a dictionary as expected. Type: {type(parsed_ai_response)}. Content: {cleaned_json[:300]}")
                raise HTTPException(status_code=500, detail="AI service returned improperly structured data (expected a JSON object).")

            slide_data_list: List[Dict[str, Any]] = parsed_ai_response.get("slides", [])
            theme_suggestions_list: List[str] = parsed_ai_response.get("theme_suggestions", [])

            logger.info(f"Extracted slide data count: {len(slide_data_list)}")
            logger.info(f"Extracted theme suggestions: {theme_suggestions_list}")
            logger.debug(f"Full extracted slide_data_list: {slide_data_list}")
            logger.debug(f"Full parsed_ai_response: {parsed_ai_response}")

            # Validation
            if not isinstance(slide_data_list, list) or \
               not isinstance(theme_suggestions_list, list) or \
               not all(isinstance(item, dict) for item in slide_data_list) or \
               not all(isinstance(item, str) for item in theme_suggestions_list):
                logger.error(f"AI output structure is incorrect. 'slides' must be a list of dicts, 'theme_suggestions' must be a list of strings. "
                             f"Got slides type: {type(slide_data_list)}, themes type: {type(theme_suggestions_list)}. Content: {cleaned_json[:300]}")
                raise HTTPException(status_code=500, detail="AI service returned improperly structured data (slides or themes are not lists).")

            if not slide_data_list: # Check if slides list is empty, which might be an error or intended
                logger.warning(f"AI output's 'slides' list is empty. Content: {cleaned_json[:300]}")
                # Depending on requirements, you might raise an error here if slides are always expected
                # For now, we allow empty slide lists to proceed to create_presentation_from_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI: {e}. Raw content: {raw_slide_content_json[:500]}...")
            raise HTTPException(status_code=500, detail="AI service returned invalid JSON content.")

        ppt_file_path = await asyncio.to_thread(
            create_presentation_from_data,
            slide_data_list,
            "presentation",
            APPLY_STYLING_IN_PPT,
            theme_suggestions=theme_suggestions_list # Added this
        )
        background_tasks.add_task(cleanup_file_task, ppt_file_path)
        file_name = os.path.basename(ppt_file_path)
        download_url = f"{http_request.url.scheme}://{http_request.url.netloc}/download/{file_name}"
        logger.info(f"PPT generation successful. File: {file_name}, Download URL: {download_url}")
        return PPTGenerationInfoResponse(
            message="PPT generated successfully. Use the download URL.",
            file_name=file_name,
            download_url=download_url
        )
    except HTTPException: 
        raise
    except Exception as e: 
        logger.error(f"An unexpected error occurred in /generate-ppt/ endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred while generating the presentation.")

@app.get("/download/{file_name}")
async def download_ppt_file(file_name: str):
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    file_path = os.path.join(PPT_OUTPUT_DIR, file_name)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
    else:
        logger.warning(f"Download request for non-existent or invalid file: {file_name} at path {file_path}")
        raise HTTPException(status_code=404, detail="File not found. It may have been cleaned up or the filename is incorrect.")

@app.get("/")
async def root_path(): 
    return {"message": "Text-to-PPT Generator API is running. Access /docs for API documentation."}

if __name__ == "__main__":
    if 'AI_SDK_CONFIGURED' in globals() and not AI_SDK_CONFIGURED:
         print("\nWARNING: Google AI SDK is not configured. AI-dependent features will fail. "
               "Check GOOGLE_API_KEY in your environment or .env file.\n", file=sys.stderr)
    elif 'AI_SDK_CONFIGURED' not in globals():
        print("\nWARNING: AI_SDK_CONFIGURED flag not found. AI service status unknown.\n", file=sys.stderr)

    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Uvicorn server programmatically on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port) # Changed from "main:app" to just `app`