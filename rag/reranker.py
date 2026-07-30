from sentence_transformers import CrossEncoder

_reranker = None


def get_reranker():
    """Lazily loads the reranker (loaded once, then reused)."""
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker


def rerank_chunks(query: str, chunks: list, top_n: int = 4):
    """
    Re-scores the retrieved chunks against the question using a cross-encoder
    and returns the top_n most relevant ones.
    """
    if not chunks:
        return []

    reranker = get_reranker()
    pairs = [(query, chunk.page_content) for chunk in chunks]
    scores = reranker.predict(pairs)

    scored_chunks = list(zip(chunks, scores))
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    return [chunk for chunk, score in scored_chunks[:top_n]]