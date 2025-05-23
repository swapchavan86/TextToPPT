# backend/models.py
from pydantic import BaseModel
from typing import Optional, List

class TextToPPTRequest(BaseModel):
    text_input: str
    num_slides: Optional[int] = 5
    # generate_images: Optional[bool] = False # Keep for future image generation
    # desired_tone: Optional[str] = "professional" # Keep for future tone selection

class PPTGenerationInfoResponse(BaseModel):
    message: str
    file_name: str
    download_url: str

# You can add more models here if needed, for example, for AI responses
class AISlideContent(BaseModel):
    title: str
    points: List[str]
    image_keywords: Optional[str] = None # For future image generation