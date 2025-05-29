from fastapi import FastAPI, HTTPException, Request, Response, Depends # Import Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.models import SlideRequest # Assuming backend.models defines SlideRequest
from backend.ppt_utils import create_presentation_from_slides_data # Assuming this creates the PPT
from backend.openai_service import generate_prompt, call_openai_with_retry # Assuming these handle OpenAI interactions
from starlette.responses import StreamingResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import json
import logging
import os
import redis.asyncio as redis # Use async Redis client for FastAPI-Limiter
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Consider restricting this in production to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate Limiting Configuration (Conditional for Testing) ---
# Check if running in a test environment
# To run in test mode, set the environment variable:
# On Linux/macOS: TESTING=True uvicorn main:app --reload
# On Windows (PowerShell): $env:TESTING="True"; uvicorn main:app --reload
# On Windows (Command Prompt): set TESTING=True && uvicorn main:app --reload
IS_TESTING = os.getenv("TESTING") == "True"

if not IS_TESTING:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    @app.on_event("startup")
    async def startup():
        logger.info(f"Connecting to Redis for rate limiting at {REDIS_URL}")
        try:
            redis_connection = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            await FastAPILimiter.init(redis_connection)
            logger.info("FastAPILimiter initialized.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis for rate limiting: {e}. Rate limiting will be disabled.", exc_info=True)
            # If Redis connection fails, rate limiting will effectively be disabled.
            # You might want to make this more explicit or crash the app if Redis is critical.
            global IS_TESTING # Mark as if in test mode if Redis fails
            IS_TESTING = True 

    @app.on_event("shutdown")
    async def shutdown():
        if FastAPILimiter.redis:
            await FastAPILimiter.redis.close()
            logger.info("FastAPILimiter Redis connection closed.")

else:
    logger.info("TESTING environment detected: Rate limiting is DISABLED.")


# Custom exception handler for rate limiting errors (optional, FastAPILimiter handles it by default)
# This can be used to customize the 429 response.
@app.exception_handler(HTTP_429_TOO_MANY_REQUESTS)
async def rate_limit_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"Rate limit exceeded for request from {request.client.host} to {request.url}")
    return Response("Too Many Requests. Please try again later.", media_type="text/plain", status_code=HTTP_429_TOO_MANY_REQUESTS)

# --- API Endpoint ---
# Apply rate limiting if NOT in testing mode
# Adjust the rate (e.g., "5/minute") as per your requirements.
# The default key function uses the client's IP address.
# IMPORTANT: RateLimiter() must be wrapped in Depends() when used in dependencies list.
@app.post("/generate-ppt/", dependencies=[Depends(RateLimiter(times=5, seconds=60))] if not IS_TESTING else [])
async def generate_ppt(slide_request: SlideRequest):
    logger.info(f"Received request for topic: '{slide_request.topic}' with tone: '{slide_request.tone}'")

    # --- Input Validation (Pydantic model handles basic checks) ---
    # If you need more specific length validations beyond Pydantic's default,
    # define min_length and max_length for 'topic' and 'tone' in backend/models.py like this:
    # from pydantic import BaseModel, Field
    # class SlideRequest(BaseModel):
    #     topic: str = Field(..., min_length=5, max_length=500)
    #     tone: str = Field(..., min_length=3, max_length=50)

    try:
        prompt = generate_prompt(slide_request.topic, slide_request.tone)
        logger.debug(f"Generated prompt: {prompt[:100]}...") # Log first 100 chars
    except Exception as e:
        logger.error(f"Error generating prompt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate prompt: {e}")

    try:
        response = await call_openai_with_retry(prompt)
        output_text = response.choices[0].message.content
        
        if output_text is None:
            logger.error("OpenAI returned an empty message content.")
            raise HTTPException(status_code=500, detail="Empty response from OpenAI")
        
        output_text = output_text.strip()
        logger.debug(f"OpenAI raw response (first 200 chars): {output_text[:200]}...")
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}", exc_info=True)
        # Catch specific exceptions from call_openai_with_retry if possible (e.g., openai.APIErrors)
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation content from AI: {e}")

    try:
        data = json.loads(output_text)
        slides = data.get("slides", [])
        if not slides:
            logger.warning(f"OpenAI response contained no slides or an empty 'slides' array. Raw text: {output_text}")
            raise HTTPException(status_code=500, detail="OpenAI response did not contain valid slide data.")
        logger.info(f"Successfully parsed {len(slides)} slides from OpenAI response.")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from OpenAI response: {e}. Raw text: {output_text}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error parsing JSON from OpenAI response. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error processing OpenAI response data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing OpenAI response: {e}")

    try:
        ppt_io = create_presentation_from_slides_data(slides)
        logger.info("PPT file successfully created in memory.")
    except Exception as e:
        logger.error(f"Error creating PowerPoint presentation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create presentation file: {e}")

    return StreamingResponse(
        ppt_io,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": "attachment; filename=generated_ppt.pptx"}
    )
