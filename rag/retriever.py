import os
from langchain_openai import OpenAIEmbeddings
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import CHROMA_PATH, COLLECTION_NAME

from langchain_chroma import Chroma


def get_vectorstore():
    """Load the existing ChromaDB vectorstore."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )


def retrieve_relevant_chunks(query: str, k: int = 15):
    """Retrieve the k most relevant chunks for a given query."""
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return results


# for debugging and testing purposes
if __name__ == "__main__":
    query = "How do I build a multi-agent system with LangGraph?"
    results = retrieve_relevant_chunks(query)
    print(f"=== QUERY: {query} ===\n")
    for i, doc in enumerate(results):
        print(f"--- Result {i+1} (source: {doc.metadata.get('source', 'unknown')}) ---")
        print(doc.page_content[:300])
        print()