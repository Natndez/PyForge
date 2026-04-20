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

# Ignore very common words to ensure retrieval focuses on actual concepts
STOP_WORDS = {
    "a",
    "an",
    "the",
    "do",
    "is",
    "what",
    "when",
    "why",
    "how",
    "work",
    "works",
    "in",
    "on",
    "of",
    "to",
    "and",
    "or",
}

# These words are useful alone, but become too broad when the query already
# contains a more specific concept such as "class" or "loop".
LOW_SIGNAL_QUERY_TOKENS = {"python"}


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

def normalize_token(token: str) -> str:
    # Basic normalization helps singular/plural forms match more often.
    if token.endswith("ies") and len(token) > 3:
        return token[:-3] + "y"

    # Handle words like "classes" -> "class".
    if token.endswith("sses") and len(token) > 4:
        return token[:-2]

    # Handle simple plurals like "modules" -> "module".
    if token.endswith("es") and len(token) > 3 and not token.endswith("sses"):
        return token[:-1]

    # Avoid breaking words like "class" -> "clas".
    if token.endswith("s") and len(token) > 3 and not token.endswith("ss"):
        return token[:-1]

    return token

def tokenize(text: str) -> set[str]:
    # Lowercase, normalize, and drop weak words so scoring focuses on actual meaning, not grammatical correctness
    tokens = {
        normalize_token(token.lower())
        for token in TOKEN_PATTERN.findall(text)
    }
     # Making sure STOP words are not included
    return {token for token in tokens if token and token not in STOP_WORDS}


def score_chunk(query_tokens: set[str], chunk: KnowledgeChunk) -> int:
    # Give title matches more weight than category/content matches
    title_tokens = tokenize(chunk.title)
    category_tokens = tokenize(chunk.category)
    content_tokens = tokenize(chunk.content)
    
    title_overlap = query_tokens & title_tokens
    category_overlap = query_tokens & category_tokens
    content_overlap = query_tokens & content_tokens
    
    return (len(title_overlap) * 3) + (len(category_overlap) * 2) + len(content_overlap)


def retrieve_sources(query: str, top_k: int = 3) -> list[RetrievalResult]:
    # Convert the incoming question into tokens once, then compare against every
    # knowledge chunk in the local corpus.
    query_tokens = tokenize(query)

    # If the query already contains a more specific concept, treat broad context
    # words like "python" as low-signal so they do not overpower the real topic.
    if len(query_tokens) > 1:
        query_tokens -= LOW_SIGNAL_QUERY_TOKENS

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
