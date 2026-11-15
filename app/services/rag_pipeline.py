
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough


def create_rag_chain(llm, vector_store, video_id: str):
    """
    Create a RAG chain for a specific YouTube video.
    """

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5,
            "filter": {"video_id": video_id}
        }
    )
    if not retriever:
        print("No context found") 

    prompt = ChatPromptTemplate.from_template("""
    You are a helpful assistant that answers questions about YouTube videos.

    Answer the question using only the provided context. Answer as if you know the answer, do not tell the user you are refering a context.
    If the answer is not available in the context, say that you don't know.
    
    Context:
    {context}

    Question:
    {question}

    Answer:
    """)

    def format_docs(docs):
        return "\n\n".join(
            doc.page_content for doc in docs
        )

    rag_chain = (
        RunnableParallel(
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough()
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def get_answer(rag_chain, question: str) -> str:
    """
    Invoke the RAG chain and return the answer.
    """

    return rag_chain.invoke(question)
