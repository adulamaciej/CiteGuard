import os
import sys
from dotenv import load_dotenv
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import DOCS_PATH, CHROMA_PATH, COLLECTION_NAME, LANGCHAIN_DOCS, LANGGRAPH_DOCS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()


from logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


def load_documents():
    all_docs = []
    for path in [LANGCHAIN_DOCS, LANGGRAPH_DOCS]:
        loader = DirectoryLoader(path, glob="**/*.mdx", loader_cls=TextLoader,
                                  loader_kwargs={"encoding": "utf-8"}, show_progress=True)
        all_docs.extend(loader.load())
    return all_docs


def split_documents(documents):
    """Splitting documents into smaller chunks for retrieval."""
    splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=100)
    return splitter.split_documents(documents)


def index_documents():
    """Loading, splitting, and indexing  documents into ChromaDB (overwrites existing collection)."""
    logger.info("Loading documents...")
    documents = load_documents()
    logger.info(f"Loaded {len(documents)} documents.")

    logger.info("Splitting into chunks...")
    chunks = split_documents(documents)
    logger.info(f"Created {len(chunks)} chunks.")

    logger.info("Embedding and indexing...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


    # Delete existing collection first to avoid duplicate entries on re-runs
    existing_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )
    existing_store.delete_collection()
    logger.info("Cleared any existing collection.")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
    )

    logger.info(f"Indexed {len(chunks)} chunks into ChromaDB at {CHROMA_PATH}")
    return vectorstore


# For manual debugging: python rag/indexer.py
if __name__ == "__main__":
    index_documents()