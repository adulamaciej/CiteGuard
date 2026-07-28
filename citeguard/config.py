import os

MODEL = os.getenv("CITEGUARD_MODEL", "claude-haiku-4-5-20251001")
JUDGE_MODEL = os.getenv("CITEGUARD_JUDGE_MODEL", "claude-sonnet-5")

DOCS_PATH = "./langchain-source/src/oss/langchain"
CHROMA_PATH = "./data/chroma"
COLLECTION_NAME = "langchain_docs"