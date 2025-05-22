from fastapi import FastAPI, HTTPException, Request
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

from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
print("OpenAI API Key:", os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

@app.post("/generate-ppt/")
async def generate_ppt(slide_request: SlideRequest):
    prompt = generate_prompt(slide_request.topic, slide_request.tone)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in generating presentation slides."},
                {"role": "user", "content": prompt}
            ]
        )
        output_text = response.choices[0].message.content
        if output_text is None:
            raise ValueError("Empty response from OpenAI")
        output_text = output_text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Extract JSON from response
    import json
    try:
        data = json.loads(output_text)
        slides = data.get("slides", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing JSON: {e}")

    # Create the PPT
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
            print(f"Error adding content: {e}")

    # Save PPT to memory buffer
    ppt_io = io.BytesIO()
    prs.save(ppt_io)
    ppt_io.seek(0)

    return StreamingResponse(
        ppt_io,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": "attachment; filename=generated_ppt.pptx"}
    )
