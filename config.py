import os

# Resolving paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCS_PATH = os.path.join(BASE_DIR, "docs/src/oss")
LANGCHAIN_DOCS = os.path.join(DOCS_PATH, "langchain")
LANGGRAPH_DOCS = os.path.join(DOCS_PATH, "langgraph")
CHROMA_PATH = os.path.join(BASE_DIR, "data/chroma")
COLLECTION_NAME = "langchain_docs"