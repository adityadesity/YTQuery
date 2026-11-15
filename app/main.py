from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.services.model_loader import (
    load_embedding_model,
    load_llm
)

from app.services.vector_store import (
    load_vector_store
)
from app.routers import video, chat


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialize models
    app.state.embeddings = load_embedding_model()
    app.state.llm = load_llm()

    # Initialize vector store
    app.state.vector_store = load_vector_store(
        app.state.embeddings
    )

    yield

    # Cleanup if required



app = FastAPI(
    title="YouTube RAG Chatbot",
    description="Chat with YouTube videos using RAG",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(video.router)
app.include_router(chat.router)
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# HTML templates
templates = Jinja2Templates(
    directory="app/templates"
)


# Frontend route
@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={"request": request}
)

