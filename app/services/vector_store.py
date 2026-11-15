from langchain_chroma import Chroma

def load_vector_store(embeddings):

    vector_store = Chroma(
        collection_name="youtube_transcripts",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

    return vector_store