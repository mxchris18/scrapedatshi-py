"""
scrapedatshi.models
~~~~~~~~~~~~~~~~~~~
Pydantic response models for all scrapedatshi API endpoints.

All models use strict typing so IDEs can provide full IntelliSense
autocomplete on response objects.

Every response includes ``credits_used`` and ``credits_remaining`` fields
so you can track spend programmatically without hitting the billing API.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# ── Shared primitives ─────────────────────────────────────────────────────────


class Chunk(BaseModel):
    """A single text chunk produced by the pipeline."""

    content: str = Field(..., description="The chunk text content.")
    token_estimate: int = Field(
        ..., description="Estimated token count for this chunk."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata attached to this chunk (source URL, page number, etc.).",
    )

    def __len__(self) -> int:
        return len(self.content)

    def __repr__(self) -> str:
        preview = self.content[:60].replace("\n", " ")
        return f"Chunk(tokens={self.token_estimate}, content={preview!r}...)"


# ── Chunk to JSON responses ───────────────────────────────────────────────────


class ChunkResult(BaseModel):
    """
    Response from chunk_url(), chunk_file(), or crawl() in Chunk-to-JSON mode.

    Example::

        result = client.pipeline.chunk_url("https://docs.example.com")
        for chunk in result.chunks:
            print(chunk.content)
        print(f"Cost: ${result.credits_used:.4f} | Remaining: ${result.credits_remaining:.4f}")
    """

    chunks: list[Chunk] = Field(
        ..., description="List of text chunks extracted from the source."
    )
    total_chunks: int = Field(..., description="Total number of chunks returned.")
    source: str = Field(
        ..., description="The source URL or filename that was processed."
    )
    contextual_retrieval_used: bool = Field(
        False,
        description="Whether Contextual Retrieval (RAG 2.0) was applied to enrich chunks.",
    )
    content_truncated: bool = Field(
        False,
        description=(
            "True if the source content exceeded the maximum content size (~75,000 words) "
            "and was automatically truncated before chunking."
        ),
    )
    credits_used: float = Field(
        0.0,
        description="Credits deducted for this request (URL fetch fee + chunk fee).",
    )
    credits_remaining: float = Field(
        0.0,
        description="Account credit balance after this request.",
    )

    def __len__(self) -> int:
        return self.total_chunks

    def __repr__(self) -> str:
        return f"ChunkResult(total_chunks={self.total_chunks}, source={self.source!r}, credits_used={self.credits_used:.4f})"


class CrawlChunkResult(BaseModel):
    """
    Response from crawl() in Chunk-to-JSON mode.
    Contains chunks from all crawled pages combined.

    Example::

        result = client.pipeline.crawl("https://example.com/sitemap.xml", max_pages=10)
        print(f"Crawled {result.pages_crawled} pages → {result.total_chunks} chunks")
        print(f"Cost: ${result.credits_used:.4f} | Remaining: ${result.credits_remaining:.4f}")
    """

    chunks: list[Chunk] = Field(..., description="All chunks from all crawled pages.")
    total_chunks: int = Field(
        ..., description="Total number of chunks across all pages."
    )
    pages_crawled: int = Field(..., description="Number of pages successfully crawled.")
    source_url: str = Field(
        ..., description="The root URL or sitemap URL that was crawled."
    )
    contextual_retrieval_used: bool = Field(False)
    credits_used: float = Field(
        0.0,
        description="Credits deducted for this request (URL fetch fees + chunk fees).",
    )
    credits_remaining: float = Field(
        0.0,
        description="Account credit balance after this request.",
    )

    def __len__(self) -> int:
        return self.total_chunks

    def __repr__(self) -> str:
        return (
            f"CrawlChunkResult(pages={self.pages_crawled}, "
            f"total_chunks={self.total_chunks}, source={self.source_url!r}, "
            f"credits_used={self.credits_used:.4f})"
        )


# ── Full Pipeline responses ───────────────────────────────────────────────────


class SyncResult(BaseModel):
    """
    Response from pipeline.sync() — URL-based full pipeline (embed + vector DB inject).

    Example::

        result = client.pipeline.sync(
            url="https://docs.example.com",
            embedding_provider="openai",
            embedding_api_key="sk-...",
            vector_db="pinecone",
            vector_db_api_key="...",
            index_name="my-index",
        )
        print(f"Upserted {result.vectors_upserted} vectors")
        print(f"Cost: ${result.credits_used:.4f} | Remaining: ${result.credits_remaining:.4f}")
    """

    status: str = Field(..., description="'success' or 'error'.")
    chunks_created: int = Field(..., description="Number of text chunks generated.")
    vectors_upserted: int = Field(
        ..., description="Number of vectors written to the vector DB."
    )
    total_tokens: int = Field(
        ..., description="Total tokens processed across all chunks."
    )
    embedding_provider: str = Field(
        ..., description="Embedding provider used (e.g. 'openai')."
    )
    vector_db_provider: str = Field(
        ..., description="Vector DB provider used (e.g. 'pinecone')."
    )
    contextual_retrieval_used: bool = Field(False)
    credits_used: float = Field(
        0.0,
        description="Credits deducted for this request (URL fetch + chunk fees + injection fees).",
    )
    credits_remaining: float = Field(
        0.0,
        description="Account credit balance after this request.",
    )

    def __repr__(self) -> str:
        return (
            f"SyncResult(status={self.status!r}, chunks={self.chunks_created}, "
            f"vectors={self.vectors_upserted}, tokens={self.total_tokens}, "
            f"credits_used={self.credits_used:.4f})"
        )


class IngestResult(BaseModel):
    """
    Response from pipeline.ingest() — file-based full pipeline (embed + vector DB inject).

    Example::

        result = client.pipeline.ingest(
            file_path="./docs/manual.pdf",
            embedding_provider="openai",
            embedding_api_key="sk-...",
            vector_db="pinecone",
            vector_db_api_key="...",
            index_name="my-index",
        )
        print(f"Cost: ${result.credits_used:.4f} | Remaining: ${result.credits_remaining:.4f}")
    """

    status: str
    chunks_created: int
    vectors_upserted: int
    total_tokens: int
    embedding_provider: str
    vector_db_provider: str
    filename: str = Field("", description="Original filename that was ingested.")
    contextual_retrieval_used: bool = Field(False)
    credits_used: float = Field(
        0.0,
        description="Credits deducted for this request (file parse + chunk fees + injection fees).",
    )
    credits_remaining: float = Field(
        0.0,
        description="Account credit balance after this request.",
    )

    def __repr__(self) -> str:
        return (
            f"IngestResult(status={self.status!r}, file={self.filename!r}, "
            f"chunks={self.chunks_created}, vectors={self.vectors_upserted}, "
            f"credits_used={self.credits_used:.4f})"
        )
