from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import SlideRequest
from backend.ppt_utils import create_presentation_from_slides_data
from backend.openai_service import generate_prompt, call_openai_with_retry
from starlette.responses import StreamingResponse
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    ppt_io = create_presentation_from_slides_data(slides)

    return StreamingResponse(
        ppt_io,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": "attachment; filename=generated_ppt.pptx"}
    )
