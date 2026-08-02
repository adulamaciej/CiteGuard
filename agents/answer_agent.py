import os
import sys
import logging

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_openai import ChatOpenAI


def generate_answer(question: str, retrieved_chunks: list) -> str:
    """Generate an answer to the question using retrieved documentation chunks as context."""
    logger.info(f"Generating answer for: {question}")
    context = "\n\n---\n\n".join([
        f"Source: {chunk.metadata.get('source', 'unknown')}\n{chunk.page_content}"
        for chunk in retrieved_chunks
    ])

    prompt = f""""You are a documentation assistant for LangChain and LangGraph.".
Answer the user's question using ONLY the information in the provided context below.
If the context doesn't contain enough information to answer, say so explicitly.

CONTEXT:
{context}

QUESTION:
{question}

Provide a clear, concise answer based strictly on the context above."""

    llm = ChatOpenAI(model="gpt-5-mini", max_tokens=1000)
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    from rag.retriever import retrieve_relevant_chunks

    question = "How do I build a multi-agent system with LangGraph?"
    chunks = retrieve_relevant_chunks(question)
    answer = generate_answer(question, chunks)

    print(f"=== QUESTION ===\n{question}\n")
    print(f"=== ANSWER ===\n{answer}")