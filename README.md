
# TubeQuery – YouTube RAG Chatbot

TubeQuery is a Retrieval-Augmented Generation (RAG) application that allows users to interact with YouTube videos through natural language.

Instead of watching an entire video to find specific information, users can ingest a video's transcript and ask questions about its content. TubeQuery retrieves relevant transcript chunks and uses a locally hosted Large Language Model (LLM) to generate context-aware answers.

The application uses local Ollama models for embeddings and text generation, so no external LLM API key is required.

## Features

- **YouTube Transcript Ingestion:** Extract transcripts directly from YouTube video URLs.
- **Text Chunking:** Split transcripts into smaller, overlapping chunks using LangChain's Recursive Character Text Splitter.
- **Vector Storage:** Generate embeddings and store transcript chunks in ChromaDB.
- **Semantic Search:** Retrieve relevant transcript chunks based on user queries.
- **RAG-based Question Answering:** Generate answers using retrieved context and a locally hosted LLM.
- **Video-specific Retrieval:** Maintain separate retrieval contexts for different videos using metadata filtering.
- **Duplicate Prevention:** Avoid ingesting the same video multiple times.
- **Video Management:** Ingest and delete videos through the application interface.
- **Web Interface:** Interact with ingested videos through a simple chat interface.

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | HTML, CSS, JavaScript |
| LLM Orchestration | LangChain |
| LLM | Ollama - Qwen3 4B |
| Embedding Model | Ollama - Nomic Embed Text |
| Vector Database | ChromaDB |
| Transcript Extraction | YouTube Transcript API |
| Text Splitting | Recursive Character Text Splitter |
| API Documentation | Swagger UI |

## Architecture

```text
              User
               |
               v
        Web Interface
        (HTML/CSS/JS)
               |
               v
          FastAPI
               |
       +-------+-------+
       |               |
       v               v
 Video Ingestion    Chat Endpoint
       |               |
       v               v
 YouTube Transcript  User Question
       |               |
       v               v
 Text Chunking      Embedding /
       |             Retrieval
       v               |
 Ollama Embeddings     v
       |           ChromaDB
       v               |
    ChromaDB            v
       |           Relevant Chunks
       |               |
       +---------------+
                       |
                       v
                 RAG Pipeline
                       |
                       v
                  Ollama LLM
                       |
                       v
                 Generated Answer
```

## Project Structure

```text
youtube_chatbot/
│
├── app/
│   ├── main.py
│   │
│   ├── routers/
│   │   ├── video.py
│   │   └── chat.py
│   │
│   ├── schemas/
│   │   ├── video.py
│   │   └── chat.py
│   │
│   ├── services/
│   │   ├── model_loader.py
│   │   ├── vector_store.py
│   │   ├── ingestion.py
│   │   └── rag_pipeline.py
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       │
│       └── js/
│           └── app.js
│
├── chroma/
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

Follow these steps to set up and run TubeQuery locally.

### 1. Prerequisites

Make sure the following are installed:

- Python 3.10 or later (Python 3.13 is used for development).
- Git.
- Ollama.

Download Ollama from:

https://ollama.com/download

### 2. Clone the Repository

```bash
git clone https://github.com/adityadesity/YTQuery.git
```

Navigate to the project directory:

```bash
cd youtube_chatbot
```

Replace `YOUR_USERNAME` with your GitHub username and update the repository URL if needed.

### 3. Create a Virtual Environment

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 5. Set Up Ollama Models

TubeQuery uses two locally hosted models through Ollama.

Pull the embedding model:

```bash
ollama pull nomic-embed-text
```

Pull the language model:

```bash
ollama pull qwen3:4b
```

Verify that the models are available:

```bash
ollama list
```

Make sure the Ollama service is running before starting the application.

Ollama typically exposes its local API at:

```text
http://localhost:11434
```

### 6. Run the Application

From the project root directory, start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

Open the URL in your browser to access TubeQuery.

### 7. API Documentation

FastAPI automatically generates interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## How to Use

1. Open TubeQuery in your browser.
2. Paste a valid YouTube video URL into the ingestion field.
3. Click **Ingest Video**.
4. The application extracts the video's transcript, splits it into chunks, generates embeddings, and stores them in ChromaDB.
5. Once ingestion is complete, select the video from the sidebar.
6. Enter a question related to the video.
7. TubeQuery retrieves relevant transcript chunks and generates an answer using the LLM.
8. You can delete an ingested video from the sidebar when it is no longer needed.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/videos/ingest` | Ingest a YouTube video |
| DELETE | `/videos/{video_id}` | Delete an ingested video |
| POST | `/chat/` | Ask a question about an ingested video |

### Example: Ingest a Video

**Request**

```http
POST /videos/ingest
Content-Type: application/json
```

```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Example Response**

```json
{
    "video_id": "VIDEO_ID",
    "total_chunks": 42,
    "status": "success"
}
```

### Example: Ask a Question

**Request**

```http
POST /chat/
Content-Type: application/json
```

```json
{
    "video_id": "VIDEO_ID",
    "question": "What are the main topics discussed in this video?"
}
```

**Example Response**

```json
{
    "video_id": "VIDEO_ID",
    "question": "What are the main topics discussed in this video?",
    "answer": "The video discusses..."
}
```

## RAG Pipeline

The application follows a standard Retrieval-Augmented Generation workflow.

### 1. Ingestion

- Extract the YouTube video ID from the provided URL.
- Fetch the video transcript using YouTube Transcript API.
- Convert transcript entries into LangChain Documents.
- Split the transcript into smaller chunks.

Current chunking configuration:

| Parameter | Value |
|---|---|
| Chunk size | 500 |
| Chunk overlap | 100 |
| Text splitter | RecursiveCharacterTextSplitter |

### 2. Embedding and Storage

- Generate vector embeddings using `nomic-embed-text`.
- Store the transcript chunks, embeddings, and metadata in ChromaDB.
- Associate each chunk with its corresponding video ID.

### 3. Retrieval

- Convert the user's question into an embedding.
- Perform similarity-based retrieval against ChromaDB.
- Retrieve the top 4 relevant chunks.
- Apply metadata filtering to ensure that retrieval is restricted to the selected video.

### 4. Generation

- Pass the retrieved context and user question to the Qwen3 4B model.
- Generate an answer grounded in the retrieved transcript.
- Return the generated response to the frontend.

## Configuration

The models and vector database are configured in:

```text
app/services/model_loader.py
app/services/vector_store.py
```

Current model configuration:

```python
OllamaEmbeddings(model="nomic-embed-text")

ChatOllama(
    model="qwen3:4b",
    temperature=0.5
)
```

Vector database configuration:

- Database: ChromaDB
- Collection: `sample`
- Persistence directory: `./chroma`

## Important Notes

- The application requires an active internet connection to fetch YouTube transcripts.
- Ollama must be installed and running locally.
- The required Ollama models must be downloaded before starting the application.
- Not all YouTube videos have accessible transcripts. Ingestion may fail if a transcript is unavailable.
- Vector data is persisted locally in the `chroma/` directory.
- The current frontend keeps its video list in browser memory. Refreshing the page clears the displayed list, although the underlying ChromaDB data remains persisted.
- The application is intended for local development and learning. Production deployment would require additional considerations around persistence, authentication, concurrency, and error handling.

## Future Improvements

- Persistent video registry and video title extraction.
- Streaming LLM responses.
- Conversation history and contextual follow-up questions.
- Source citations with transcript timestamps.
- Improved retrieval strategies such as MMR and query expansion.
- Background processing for long-running ingestion tasks.
- Docker-based deployment.
- Authentication and user-specific video libraries.

## License

This project is open-source and available under the MIT License.

---

**Built with Python, FastAPI, LangChain, ChromaDB, and Ollama.**
