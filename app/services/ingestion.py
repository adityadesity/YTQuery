
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.documents import Document
# from langchain_core.document_loaders import Text
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_video_id(url: str) -> str:
    """Extract the video ID from a YouTube URL."""

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    if hostname in ["www.youtube.com", "youtube.com", "m.youtube.com"]:
        video_id = parse_qs(parsed_url.query).get("v", [None])[0]

    elif hostname == "youtu.be":
        video_id = parsed_url.path.strip("/").split("/")[0]

    else:
        raise ValueError("Invalid YouTube URL")

    if not video_id:
        raise ValueError("Could not extract YouTube video ID")

    return video_id


def fetch_transcript(video_id: str):
    """Fetch the transcript for a YouTube video."""

    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
    return " ".join([ft.text for ft in transcript])


def create_document(transcript, video_id: str) -> list[Document]:
    """Convert transcript entries into LangChain Documents."""

    document = Document(
                page_content=transcript,
                metadata={
                    "video_id": video_id,

                }
            )
    return document


def split_documents(documents: Document, video_id) -> list[Document]:
    """Split transcript documents into smaller chunks."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    
    chunks = splitter.split_documents([documents])

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = index

    return chunks


def ingest_video(url: str, vector_store) -> dict:
    """Extract, process, and store a YouTube video's transcript."""

    video_id = extract_video_id(url)

    existing = vector_store.get(
    where={"video_id": video_id},
    include=[]
    )

    if existing["ids"]:
        return {
            "video_id": video_id,
            "total_chunks": len(existing["ids"]),
            "status": "already_ingested"
        }

    transcript = fetch_transcript(video_id)

    document = create_document(transcript, video_id)

    chunks = split_documents(document, video_id)

    if not chunks:
        raise ValueError("No transcript content available for ingestion")

    vector_store.add_documents(chunks)

    return {
        "video_id": video_id,
        "total_chunks": len(chunks),
        "status": "success"
    }
