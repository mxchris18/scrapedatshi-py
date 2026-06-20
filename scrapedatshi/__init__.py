"""
scrapedatshi
~~~~~~~~~~~~
Official Python SDK for the scrapedatshi RAG pipeline API.

Quick start::

    from scrapedatshi import ScrapedatshiClient

    client = ScrapedatshiClient(api_key="sds_...")

    # Chunk a URL to JSON (no embedding required)
    result = client.pipeline.chunk_url("https://docs.example.com")
    for chunk in result.chunks:
        print(chunk.content)

    # Full pipeline — embed + inject to vector DB
    result = client.pipeline.sync(
        url="https://docs.example.com",
        embedding_provider="openai",
        embedding_api_key="sk-...",
        vector_db="pinecone",
        vector_db_config={
            "api_key": "pc-...",
            "index_host": "https://my-index-abc123.svc.pinecone.io",
        },
    )

    # Schema extraction — extract structured data using your LLM
    result = client.pipeline.extract(
        url="https://example.com/products/widget",
        schema={"title": "string — product name", "price": "number — price in USD"},
        llm_provider="openai",
        llm_api_key="sk-...",
    )
    print(result.extracted)

Full documentation: https://docs.scrapedatshi.com/sdk/python
Supported providers: from scrapedatshi.providers import EMBEDDING_PROVIDERS, VECTOR_DB_PROVIDERS, LLM_PROVIDERS
"""

from scrapedatshi.client import ScrapedatshiClient
from scrapedatshi.exceptions import (
    AuthError,
    InsufficientCreditsError,
    RateLimitError,
    ScrapedatshiError,
    ServerError,
    TierError,
    TimeoutError,
    ValidationError,
)
from scrapedatshi.models import (
    Chunk,
    ChunkResult,
    CrawlChunkResult,
    ExtractResult,
    IngestResult,
    SyncResult,
)

__version__ = "0.2.0"
__author__ = "scrapedatshi"
__all__ = [
    # Client
    "ScrapedatshiClient",
    # Exceptions
    "ScrapedatshiError",
    "AuthError",
    "InsufficientCreditsError",
    "RateLimitError",
    "TierError",
    "ValidationError",
    "ServerError",
    "TimeoutError",
    # Models
    "Chunk",
    "ChunkResult",
    "CrawlChunkResult",
    "SyncResult",
    "IngestResult",
    "ExtractResult",
]
