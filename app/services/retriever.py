from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


# The retriever reads from a local JSON file for now. Later we can swap this out
# for a database, vector index, or embedding-backed search without changing the
# route layer.
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge_base.json"

# We keep tokenization intentionally simple: pull out word-like chunks and ignore
# punctuation. This gives us an easy baseline before moving to more advanced
# retrieval techniques.
TOKEN_PATTERN = re.compile(r"[a-zA-Z_]+")


@dataclass
class KnowledgeChunk:
    # Structured chunks make retrieval results easier to reason about than raw dicts.
    # Each chunk is one small knowledge unit the app can retrieve and cite.
    title: str
    category: str
    content: str


@dataclass
class RetrievalResult:
    # Returning both the chunk and its score lets the UI show "why" something was
    # retrieved and lets later stages decide whether the match is trustworthy.
    chunk: KnowledgeChunk
    score: int


def load_knowledge_base() -> list[KnowledgeChunk]:
    # Centralizing file loading keeps data access out of the route layer.
    with DATA_PATH.open("r", encoding="utf-8") as file:
        raw_items = json.load(file)

    return [KnowledgeChunk(**item) for item in raw_items]


def tokenize(text: str) -> set[str]:
    # Lowercased word tokens give us a simple, transparent search baseline.
    # Using a set means repeated words do not inflate the score.
    return {token.lower() for token in TOKEN_PATTERN.findall(text)}


def score_chunk(query_tokens: set[str], chunk: KnowledgeChunk) -> int:
    # We score against the title, category, and content so short labels like
    # "python-basics" can still help retrieval.
    chunk_tokens = tokenize(f"{chunk.title} {chunk.category} {chunk.content}")
    # Score by token overlap; later we can swap this for embeddings.
    return len(query_tokens & chunk_tokens)


def retrieve_sources(query: str, top_k: int = 3) -> list[RetrievalResult]:
    # Convert the incoming question into tokens once, then compare against every
    # knowledge chunk in the local corpus.
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    # Build scored results first, then sort. Keeping the score attached to the
    # chunk avoids recomputing it later.
    ranked_chunks = sorted(
        [
            RetrievalResult(chunk=chunk, score=score_chunk(query_tokens, chunk))
            for chunk in load_knowledge_base()
        ],
        key=lambda result: result.score,
        reverse=True,
    )

    # Ignore zero-score chunks so the UI only shows relevant context.
    # top_k limits how much context we show and, later, how much context we pass
    # into generation.
    return [result for result in ranked_chunks[:top_k] if result.score > 0]
