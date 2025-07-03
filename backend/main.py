# main.py
import json
import logging
import os
import re

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from starlette.responses import StreamingResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import redis.asyncio as redis

from models import SlideRequest
from ppt_utils import create_presentation_from_slides_data
from openai_service import generate_prompt, call_openai_with_retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("main")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IS_TESTING = os.getenv("TESTING", "").lower() == "true"

if not IS_TESTING:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    @app.on_event("startup")
    async def startup():
        try:
            redis_conn = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            await FastAPILimiter.init(redis_conn)
            logger.info("Rate limiter initialized.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            global IS_TESTING
            IS_TESTING = True

    @app.on_event("shutdown")
    async def shutdown():
        if FastAPILimiter.redis:
            await FastAPILimiter.redis.aclose()

@app.exception_handler(HTTP_429_TOO_MANY_REQUESTS)
async def rate_limit_exceeded_handler(request: Request, exc: HTTPException):
    logger.warning(f"Rate limit hit: {request.client.host}")
    return Response("Too Many Requests", status_code=HTTP_429_TOO_MANY_REQUESTS)

def strip_markdown_code_fence(text: str) -> str:
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()

@app.post("/generate-ppt/", dependencies=[Depends(RateLimiter(times=5, seconds=60))] if not IS_TESTING else [])
async def generate_ppt(slide_request: SlideRequest):
    logger.info(f"Received topic: '{slide_request.topic}' with tone: '{slide_request.tone}'")

    try:
        prompt = generate_prompt(slide_request.topic, slide_request.tone)
    except Exception as e:
        logger.error(f"Prompt generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate prompt")

    try:
        response = call_openai_with_retry(prompt)  # sync call
        message = response.choices[0].message.content
        if not message:
            raise HTTPException(status_code=500, detail="Empty response from OpenAI")
        message = strip_markdown_code_fence(message)
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="OpenAI API call failed")

    try:
        data = json.loads(message)
        slides = data.get("slides", [])
        if not slides:
            raise ValueError("No slides found in response")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="OpenAI output is not valid JSON.")
    except Exception as e:
        logger.error(f"Parsing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to parse OpenAI output")

    try:
        ppt_io = create_presentation_from_slides_data(slides)
    except Exception as e:
        logger.error(f"PPT creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate PowerPoint file")

    return StreamingResponse(
        ppt_io,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": "attachment; filename=generated_ppt.pptx"},
    )
