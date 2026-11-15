
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    video_id: str
    question: str = Field(min_length=1)


class ChatResponse(BaseModel):
    video_id: str
    question: str
    answer: str
