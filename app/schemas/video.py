# app/schemas/video.py

from pydantic import BaseModel, HttpUrl


class VideoIngestRequest(BaseModel):
    url: HttpUrl


class VideoIngestResponse(BaseModel):
    video_id: str
    total_chunks: int
    status: str