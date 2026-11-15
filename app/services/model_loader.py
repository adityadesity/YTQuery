from langchain_ollama import (
    OllamaEmbeddings,
    ChatOllama
)

def load_embedding_model():
    return OllamaEmbeddings(
        model="nomic-embed-text"
    )

def load_llm():
    return ChatOllama(
        model="qwen3:4b",
        temperature=0.5
    )