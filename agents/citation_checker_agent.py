import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)


def check_citations(question: str, answer: str, retrieved_chunks: list) -> dict:
    """
    Verifies whether the answer is faithfully grounded in the retrieved chunks.
    Returns a dict with 'verified' (bool) and 'reasoning' (str).
    """
    context = "\n\n---\n\n".join([
        f"Source: {chunk.metadata.get('source', 'unknown')}\n{chunk.page_content}"
        for chunk in retrieved_chunks
    ])

    prompt = f"""You are a fact-checker verifying whether an AI-generated answer is faithfully grounded in the provided source documents.

SOURCE DOCUMENTS:
{context}

QUESTION:
{question}

GENERATED ANSWER:
{answer}

Carefully check: does every claim in the generated answer come from the source documents above?
Flag any claim that is not directly supported by the sources, even if it sounds plausible.

Respond in this exact format:
VERIFIED: yes or no
REASONING: brief explanation, noting any unsupported claims if found"""

    llm = ChatOpenAI(model="gpt-5-mini", max_tokens=2500)
    response = llm.invoke(prompt)
    result_text = response.content

    verified = "VERIFIED: YES" in result_text.upper()
    reasoning = result_text.split("REASONING:")[-1].strip() if "REASONING:" in result_text else result_text

    logger.info(f"Citation check result: verified={verified}")

    return {
        "verified": verified,
        "reasoning": reasoning,
        "raw_response": result_text
    }


if __name__ == "__main__":
    from rag.retriever import retrieve_relevant_chunks
    from agents.answer_agent import generate_answer

    question = "How do I build a multi-agent system with LangGraph?"
    chunks = retrieve_relevant_chunks(question)
    answer = generate_answer(question, chunks)

    print(f"=== QUESTION ===\n{question}\n")
    print(f"=== ANSWER ===\n{answer}\n")

    check = check_citations(question, answer, chunks)
    print(f"=== CITATION CHECK ===")
    print(f"Verified: {check['verified']}")
    print(f"Reasoning: {check['reasoning']}")