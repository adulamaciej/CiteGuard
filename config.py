import os

# Resolving paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCS_PATH = os.path.join(BASE_DIR, "langchain-source/src/oss/langchain")
CHROMA_PATH = os.path.join(BASE_DIR, "data/chroma")
COLLECTION_NAME = "langchain_docs"