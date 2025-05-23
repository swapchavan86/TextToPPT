# backend/main.py

import logging
import os
import json
import asyncio
from typing import List, Dict, Any, Optional
import time
import sys
import uuid
import random


from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import from our new local modules
from .config import (
    EFFECTIVE_ORIGINS,
    PPT_OUTPUT_DIR,
    BACKEND_URL, # Make sure to import BACKEND_URL
    # Other configs if needed by main directly
)
from .models import (
    TextToPPTRequest,
    PPTGenerationInfoResponse
)
from .ai_services import (
    construct_text_to_slide_prompt,
    call_google_ai_for_ppt_content,
    SDK_CONFIGURED_SUCCESSFULLY as AI_SDK_CONFIGURED
)
from .ppt_utils import (
    create_presentation_from_data
)

# --- Logging Setup ---
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- FastAPI App Initialization ---
app = FastAPI(
    title="AI PowerPoint Generator API",
    description="Generate PowerPoint presentations from text using AI.",
    version="1.0.0",
)

# --- CORS Middleware ---
# Ensure your frontend URL is listed in EFFECTIVE_ORIGINS in config.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=EFFECTIVE_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"], # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- Constants for Cleanup ---
FILE_CLEANUP_DELAY_SECONDS = 300 # 5 minutes


# --- Background Task for File Cleanup ---
async def cleanup_file(file_path: str, delay: int):
    await asyncio.sleep(delay)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {e}")

# --- API Endpoints ---

@app.post("/generate-ppt/", response_model=PPTGenerationInfoResponse)
async def generate_ppt(request: TextToPPTRequest, background_tasks: BackgroundTasks):
    logger.info(f"Received request to generate PPT. Text length: {len(request.text_input)}, Slides: {request.num_slides}, Tone: professional")
    
    if not request.text_input.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    try:
        # Step 1: Call Google AI to generate slide content
        ai_response_json_str = await call_google_ai_for_ppt_content(
            text_input=request.text_input,
            num_slides=request.num_slides,
            desired_tone="professional" # Hardcoding for now, can be dynamic later
        )
        ai_data = json.loads(ai_response_json_str)

        # Step 2: Create PPT file
        file_uuid = uuid.uuid4()
        final_file_name = f"presentation_{file_uuid}.pptx"
        final_file_path = os.path.join(PPT_OUTPUT_DIR, final_file_name)

        # Ensure the output directory exists
        os.makedirs(PPT_OUTPUT_DIR, exist_ok=True)
        
        logger.info(f"Creating PPT file: {final_file_name} at {final_file_path}")
        create_presentation_from_data(ai_data, final_file_path)
        logger.info("PPT file created successfully.")

        # Construct the absolute download URL
        # Use the BACKEND_URL from config.py
        download_url = f"{BACKEND_URL}/download-ppt/{final_file_name}"

        # Add cleanup task (moved here so download URL is ready)
        background_tasks.add_task(cleanup_file, final_file_path, delay=FILE_CLEANUP_DELAY_SECONDS)
        logger.info(f"File {final_file_name} scheduled for cleanup in {FILE_CLEANUP_DELAY_SECONDS} seconds.")

        return PPTGenerationInfoResponse(
            message="Presentation generated successfully!",
            file_name=final_file_name,
            download_url=download_url # This will now be an absolute URL
        )
    except HTTPException as e:
        logger.error(f"HTTPException during PPT generation: {e.detail}", exc_info=True)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during PPT generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during PPT generation: {str(e)}")

@app.get("/download-ppt/{file_name}")
async def download_ppt(file_name: str):
    logger.info(f"Received download request for file: {file_name}")
    # Basic security check to prevent directory traversal
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
    
    # Ensure PPT_OUTPUT_DIR exists at startup
    os.makedirs(PPT_OUTPUT_DIR, exist_ok=True)
    
    uvicorn.run(app, host="127.0.0.1", port=8000)