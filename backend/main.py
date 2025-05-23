from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pptx import Presentation
from pptx.util import Inches
from pptx.shapes.autoshape import Shape
from openai import OpenAI
from pydantic import BaseModel
import io
from starlette.responses import StreamingResponse
import os
from pathlib import Path
import json
import time
import logging

from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Loaded OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY') is not None}")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing or invalid in the .env file")
client = OpenAI(api_key=api_key)

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SlideRequest(BaseModel):
    topic: str
    tone: str = "educational"

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

def call_openai_with_retry(prompt: str, retries=3, initial_delay=5):
    delay = initial_delay
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"OpenAI API call attempt {attempt}")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in generating presentation slides."},
                    {"role": "user", "content": prompt},
                ],
                timeout=30
            )
            return response
        except Exception as e:
            err_msg = str(e)
            if "rate limit" in err_msg.lower() or "429" in err_msg:
                if attempt == retries:
                    logger.error("Rate limit exceeded, no more retries left.")
                    raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
                logger.warning(f"Rate limit hit, retrying after {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                logger.error(f"OpenAI API error: {err_msg}")
                raise HTTPException(status_code=500, detail=f"OpenAI API error: {err_msg}")

@app.post("/generate-ppt/")
async def generate_ppt(slide_request: SlideRequest):
    prompt = generate_prompt(slide_request.topic, slide_request.tone)

    response = call_openai_with_retry(prompt)
    output_text = response.choices[0].message.content
    if output_text is None:
        raise HTTPException(status_code=500, detail="Empty response from OpenAI")

    output_text = output_text.strip()

    try:
        data = json.loads(output_text)
        slides = data.get("slides", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing JSON from OpenAI response: {e}")

    prs = Presentation()
    for slide_data in slides:
        slide_layout = prs.slide_layouts[1]  # Title and Content
        slide = prs.slides.add_slide(slide_layout)

        # Set title safely
        title_shape = slide.shapes.title
        if title_shape:
            title_shape.text = slide_data.get("title", "Untitled Slide")

        # Set bullet points safely
        try:
            content_shape = slide.placeholders[1]
            if isinstance(content_shape, Shape) and content_shape.text_frame:
                bullets = slide_data.get("bullets", [])
                if bullets:
                    content_shape.text_frame.text = bullets[0]
                    for bullet in bullets[1:]:
                        p = content_shape.text_frame.add_paragraph()
                        p.text = bullet
        except Exception as e:
            logger.warning(f"Error adding content to slide: {e}")

    ppt_io = io.BytesIO()
    prs.save(ppt_io)
    ppt_io.seek(0)

    return StreamingResponse(
        ppt_io,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": "attachment; filename=generated_ppt.pptx"}
    )
