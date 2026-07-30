import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DOCS_PATH, CHROMA_PATH, COLLECTION_NAME

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()


def load_documents():
    """Loading all .mdx files from the docs path."""
    loader = DirectoryLoader(
        DOCS_PATH,
        glob="**/*.mdx",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    return loader.load()


def split_documents(documents):
    """Splitting documents into smaller chunks for retrieval."""
    splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=100)
    return splitter.split_documents(documents)


def index_documents():
    """Loading, splitting, and indexing  documents into ChromaDB (overwrites existing collection)."""
    print("Loading documents...")
    documents = load_documents()
    print(f"Loaded {len(documents)} documents.")

    print("Splitting into chunks...")
    chunks = split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    print("Embedding and indexing (this uses a free local model, no API cost)...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


    # Delete existing collection first to avoid duplicate entries on re-runs
    existing_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )
    existing_store.delete_collection()
    print("Cleared any existing collection.")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
    )

    print(f"✅ Indexed {len(chunks)} chunks into ChromaDB at {CHROMA_PATH}")
    return vectorstore


# For manual debugging: python rag/indexer.py
if __name__ == "__main__":
    index_documents()