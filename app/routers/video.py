
from fastapi import APIRouter, Request, HTTPException

from app.schemas.video import (
    VideoIngestRequest,
    VideoIngestResponse
)
from app.services.ingestion import ingest_video

router = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)


@router.post("/ingest", response_model=VideoIngestResponse)
def ingest(request: VideoIngestRequest, app_request: Request):

    try:
        result = ingest_video(
            url=str(request.url),
            vector_store=app_request.app.state.vector_store
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete("/{video_id}")
def delete_video(video_id: str, request: Request):

    vector_store = request.app.state.vector_store

    existing = vector_store.get(
        where={"video_id": video_id},
        include=[]
    )

    if not existing["ids"]:
        raise HTTPException(
            status_code=404,
            detail="Video not found"
        )

    vector_store.delete(
        where={"video_id": video_id}
    )

    return {
        "video_id": video_id,
        "deleted_chunks": len(existing["ids"]),
        "status": "deleted"
    }