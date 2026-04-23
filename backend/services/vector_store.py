"""
services/vector_store.py
Builds a FAISS index from job embeddings and performs similarity search.

Flow:
  1. embed_jobs() → list of float vectors
  2. build_index(vectors) → faiss.IndexFlatIP (inner-product / cosine)
  3. search(query_vector, k) → indices of top-k jobs
"""
from __future__ import annotations
import logging
import numpy as np

logger = logging.getLogger(__name__)


def _import_faiss():
    try:
        import faiss
        return faiss
    except ImportError as e:
        raise ImportError(
            "faiss-cpu is not installed. Run: pip install faiss-cpu"
        ) from e


def _normalise_vectors(vectors: list[list[float]]) -> np.ndarray:
    """L2-normalise so inner-product == cosine similarity."""
    arr = np.array(vectors, dtype="float32")
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)   # avoid div-by-zero
    return arr / norms


def build_index(job_vectors: list[list[float]]):
    """
    Build and return a FAISS flat index (cosine similarity via inner product).

    Returns:
        (index, dimension)
    """
    faiss = _import_faiss()

    if not job_vectors:
        raise ValueError("Cannot build index from empty vector list.")

    arr = _normalise_vectors(job_vectors)
    dim = arr.shape[1]

    index = faiss.IndexFlatIP(dim)   # Inner-Product on L2-normalised = cosine
    index.add(arr) # type: ignore

    logger.info("FAISS index built: %d vectors, dim=%d", index.ntotal, dim)
    return index, dim


def search(index, query_vector: list[float], k: int = 5) -> tuple[list[int], list[float]]:
    """
    Search the FAISS index for the k most similar jobs.

    Returns a tuple of (indices, scores) for the top results.
    """
    arr = _normalise_vectors([query_vector])   
    k = min(k, index.ntotal)                   

    distances, indices = index.search(arr, k)

    top_indices = indices[0].tolist()
    top_scores  = distances[0].tolist()

    logger.info(
        "FAISS search returned %d results. Top score=%.4f",
        len(top_indices),
        top_scores[0] if top_scores else 0.0,
    )
    return top_indices, top_scores
