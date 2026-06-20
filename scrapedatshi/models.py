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


# ── Schema Extract response ───────────────────────────────────────────────────


class ExtractResult(BaseModel):
    """
    Response from pipeline.extract() — structured data extracted from a URL using an LLM.

    The ``extracted`` field contains either a single dict (default) or a list of dicts
    when ``extract_as_list=True`` was used.

    Example::

        result = client.pipeline.extract(
            url="https://example.com/products",
            schema={"title": "string — product name", "price": "number — price in USD"},
            llm_provider="openai",
            llm_api_key="sk-...",
        )
        print(result.extracted)
        # → {"title": "Widget Pro", "price": 29.99}

        # List mode — extract all matching items on the page
        result = client.pipeline.extract(
            url="https://example.com/products",
            schema={"title": "string — product name", "price": "number — price in USD"},
            llm_provider="openai",
            llm_api_key="sk-...",
            extract_as_list=True,
        )
        print(result.extracted)
        # → [{"title": "Widget Pro", "price": 29.99}, {"title": "Widget Lite", "price": 9.99}]
        print(f"Extracted {result.item_count} items")
        print(f"Cost: ${result.credits_used:.4f} | Remaining: ${result.credits_remaining:.4f}")
    """

    extracted: Any = Field(
        ...,
        description=(
            "Extracted data matching your schema. "
            "A dict when extract_as_list=False (default), "
            "or a list[dict] when extract_as_list=True."
        ),
    )
    field_count: int = Field(
        ..., description="Number of schema fields that were defined."
    )
    item_count: int | None = Field(
        None,
        description="Number of items extracted (only set when extract_as_list=True).",
    )
    url: str = Field(..., description="The URL that was scraped and extracted from.")
    llm_provider: str = Field(..., description="LLM provider used for extraction.")
    llm_model: str = Field(..., description="LLM model used for extraction.")
    schema_fields: list[str] = Field(
        default_factory=list,
        description="List of field names defined in the schema.",
    )
    js_render: bool = Field(
        False, description="Whether JS rendering was used for this request."
    )
    content_warning: str | None = Field(
        None,
        description=(
            "Warning message if the page content was thin or potentially incomplete "
            "(e.g. JS-heavy page that may need js_render=True)."
        ),
    )
    credits_used: float = Field(
        0.0,
        description="Credits deducted for this request (fetch fee + orchestration + per-field fee).",
    )
    credits_remaining: float = Field(
        0.0,
        description="Account credit balance after this request.",
    )

    @property
    def is_list(self) -> bool:
        """True if the extracted result is a list (extract_as_list mode)."""
        return isinstance(self.extracted, list)

    def __len__(self) -> int:
        if isinstance(self.extracted, list):
            return len(self.extracted)
        return 1

    def __repr__(self) -> str:
        mode = f"list[{self.item_count}]" if self.is_list else "object"
        return (
            f"ExtractResult(url={self.url!r}, fields={self.field_count}, "
            f"mode={mode}, credits_used={self.credits_used:.4f})"
        )
