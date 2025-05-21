from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import openai
from pptx import Presentation
from pptx.util import Inches
import uuid
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

class PPTRequest(BaseModel):
    text: str
    tone: str = "formal"  # optional tone parameter

def generate_pptx(slides_data, filename):
    prs = Presentation()
    for slide_content in slides_data:
        slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title and Content layout
        title = slide.shapes.title
        body = slide.shapes.placeholders[1].text_frame

        title.text = slide_content.get("title", "No Title")
        body.clear()
        for bullet in slide_content.get("bullets", []):
            p = body.add_paragraph()
            p.text = bullet
            p.level = 0
    prs.save(filename)

def parse_gpt_response_to_slides(gpt_response_text):
    # Example: parse GPT output into list of slides with title and bullets
    # This depends on your GPT prompt formatting
    # Here’s a simple example assuming slides separated by "---"
    slides = []
    parts = gpt_response_text.split("---")
    for part in parts:
        lines = part.strip().split("\n")
        if not lines:
            continue
        title = lines[0]
        bullets = [line.strip("- ").strip() for line in lines[1:] if line.startswith("-")]
        slides.append({"title": title, "bullets": bullets})
    return slides

@app.post("/generate-ppt/")
async def generate_ppt(request: PPTRequest):
    prompt = f"Create a professional PowerPoint presentation outline on the topic below with slide titles and bullet points in {request.tone} tone:\n\n{request.text}\n\nFormat the response as:\nSlide Title\n- Bullet point 1\n- Bullet point 2\n---\nNext Slide Title\n- Bullet 1\n- Bullet 2"
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=800,
            temperature=0.7,
            n=1,
            stop=None,
        )
        gpt_text = response.choices[0].text.strip()
        slides_data = parse_gpt_response_to_slides(gpt_text)
        filename = f"{uuid.uuid4()}.pptx"
        generate_pptx(slides_data, filename)
        return FileResponse(path=filename, filename="presentation.pptx", media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
