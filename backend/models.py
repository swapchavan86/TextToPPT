from pydantic import BaseModel

class SlideRequest(BaseModel):
    topic: str
    tone: str = "educational"
