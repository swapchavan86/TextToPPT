from pydantic import BaseModel, Field

class SlideRequest(BaseModel):
    # topic is required and must have a minimum length of 1 character
    topic: str = Field(..., min_length=1, description="The topic for the presentation.")
    
    # tone has a default value, but also requires a minimum length of 1 character if provided
    tone: str = Field("educational", min_length=1, description="The tone of the presentation (e.g., educational, formal, casual).")

