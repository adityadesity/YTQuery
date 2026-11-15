
from fastapi import APIRouter, Request, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_pipeline import create_rag_chain, get_answer

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, app_request: Request):

    try:
        rag_chain = create_rag_chain(
            llm=app_request.app.state.llm,
            vector_store=app_request.app.state.vector_store,
            video_id=request.video_id
        )

        answer = get_answer(
            rag_chain=rag_chain,
            question=request.question
        )

        return ChatResponse(
            video_id=request.video_id,
            question=request.question,
            answer=answer
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
