# scrapedatshi-py

Official Python SDK for the [scrapedatshi](https://scrapedatshi.com) RAG pipeline API.

Scrape URLs, chunk documents, embed content, and inject into vector databases — all from a clean, typed Python interface.

---

## Installation

```bash
pip install scrapedatshi
```

Requires Python 3.10+.

---

## Quick Start

```python
from scrapedatshi import ScrapedatshiClient

client = ScrapedatshiClient(api_key="sds_...")

# Chunk a URL to JSON (no embedding required)
result = client.pipeline.chunk_url("https://docs.example.com")

print(f"Got {result.total_chunks} chunks")
print(f"Cost: ${result.credits_used:.4f} | Remaining: ${result.credits_remaining:.4f}")
for chunk in result.chunks:
    print(chunk.content[:80])
```

---

## Authentication

Pass your API key directly or set the `SCRAPEDATSHI_API_KEY` environment variable:

```bash
export SCRAPEDATSHI_API_KEY="sds_..."
```

```python
# Explicit key
client = ScrapedatshiClient(api_key="sds_...")

# From environment variable
client = ScrapedatshiClient()
```

Get your API key at [scrapedatshi.com/portal/register](https://scrapedatshi.com/portal/register).
New accounts receive **$1.00 free credits** — no credit card required.

---

## Pricing

scrapedatshi uses a **pay-per-use credit wallet** — no subscriptions, no monthly fees.
Credits are deducted after each successful API call. Failed requests are never charged.

| Operation | Rate | Applies To |
|---|---|---|
| URL Fetch | $0.0020 / URL | `/v1/rag-chunk`, `/v1/crawl`, `/v1/crawl-chunk`, `/v1/sync`, `/v1/ingest` |
| Spider Fetch | $0.0050 / URL | `/v1/spider` (replaces URL fetch) |
| Chunk Fee | $0.0005 / chunk | All routes — per chunk generated |
| Injection Fee | $0.0030 / chunk | `/v1/sync`, `/v1/ingest` — per chunk upserted to vector DB |
| Contextual Retrieval | $0.0030 / URL | When `contextual_retrieval=True` |

**Example:** `sync()` on 1 URL → 10 chunks = $0.0020 + (10 × $0.0005) + (10 × $0.0030) = **$0.0370**

Top up your balance at [scrapedatshi.com/portal/billing](https://scrapedatshi.com/portal/billing).

---

## Pipeline Methods

### Chunk to JSON

No embedding or vector DB required. Returns structured JSON chunks from any source.

#### Chunk a URL

```python
result = client.pipeline.chunk_url("https://docs.example.com")

# result.chunks              → list[Chunk]
# result.total_chunks        → int
# result.source              → str (the URL)
# result.credits_used        → float
# result.credits_remaining   → float
# result.content_truncated   → bool (True if content exceeded ~75,000 words)
```

#### Chunk a local file

Supports PDF, DOCX, TXT, MD, and HTML.

```python
result = client.pipeline.chunk_file("./docs/manual.pdf")

print(f"Got {result.total_chunks} chunks from {result.source}")
print(f"Cost: ${result.credits_used:.4f}")
```

#### Crawl a website

Crawls via sitemap and chunks all pages.

```python
result = client.pipeline.crawl("https://example.com", max_pages=10)

print(f"Crawled {result.pages_crawled} pages → {result.total_chunks} chunks")
print(f"Cost: ${result.credits_used:.4f}")
```

---

### Full Pipeline — Embed + Inject

Scrape, embed, and inject directly into your vector database in one call.

#### Sync a URL

```python
result = client.pipeline.sync(
    url="https://docs.example.com",
    embedding_provider="openai",
    embedding_api_key="sk-...",
    vector_db="pinecone",
    vector_db_api_key="pc-...",
    index_name="my-docs",
)

print(f"Upserted {result.vectors_upserted} vectors ({result.total_tokens} tokens)")
print(f"Cost: ${result.credits_used:.4f}")
```

#### Ingest a local file

```python
result = client.pipeline.ingest(
    file_path="./docs/manual.pdf",
    embedding_provider="openai",
    embedding_api_key="sk-...",
    vector_db="pinecone",
    vector_db_api_key="pc-...",
    index_name="my-docs",
)
```

---

### Contextual Retrieval (RAG 2.0)

Prepend an LLM-generated document summary to every chunk before embedding, dramatically improving retrieval accuracy.

Additional cost: $0.0030 per URL when `contextual_retrieval=True`.

```python
result = client.pipeline.chunk_url(
    "https://docs.example.com",
    contextual_retrieval=True,
    llm_provider="openai",
    llm_api_key="sk-...",
    llm_model="gpt-4o-mini",
)
```

Supported LLM providers: `openai`, `anthropic`, `gemini`

---

## Async Support

All methods have an `_async` variant for use with `asyncio`.

```python
import asyncio
from scrapedatshi import ScrapedatshiClient

async def main():
    async with ScrapedatshiClient(api_key="sds_...") as client:
        result = await client.pipeline.chunk_url_async("https://docs.example.com")
        print(f"Got {result.total_chunks} chunks — cost ${result.credits_used:.4f}")

asyncio.run(main())
```

#### Parallel processing with `asyncio.gather`

```python
async def main():
    async with ScrapedatshiClient(api_key="sds_...") as client:
        urls = [
            "https://docs.example.com/page1",
            "https://docs.example.com/page2",
            "https://docs.example.com/page3",
        ]
        results = await asyncio.gather(
            *[client.pipeline.chunk_url_async(url) for url in urls]
        )
        total = sum(r.total_chunks for r in results)
        total_cost = sum(r.credits_used for r in results)
        print(f"Processed {len(urls)} URLs → {total} total chunks — total cost ${total_cost:.4f}")
```

---

## Response Models

All methods return typed Pydantic models with full IDE autocomplete support.
Every response includes `credits_used` and `credits_remaining` for programmatic spend tracking.

### `ChunkResult`

```python
result.chunks                  # list[Chunk]
result.total_chunks            # int
result.source                  # str
result.contextual_retrieval_used  # bool
result.content_truncated       # bool — True if content exceeded ~75,000 words
result.credits_used            # float — credits deducted for this request
result.credits_remaining       # float — account balance after this request
```

### `Chunk`

```python
chunk.content              # str — the chunk text
chunk.token_estimate       # int — estimated token count
chunk.metadata             # dict — source URL, page number, etc.
```

### `CrawlChunkResult`

```python
result.chunks              # list[Chunk]
result.total_chunks        # int
result.pages_crawled       # int
result.source_url          # str
result.credits_used        # float
result.credits_remaining   # float
```

### `SyncResult` / `IngestResult`

```python
result.status              # "success" | "partial" | "error"
result.chunks_created      # int
result.vectors_upserted    # int
result.total_tokens        # int
result.embedding_provider  # str
result.vector_db_provider  # str
result.credits_used        # float
result.credits_remaining   # float
```

---

## Error Handling

```python
from scrapedatshi.exceptions import (
    AuthError,              # Invalid or missing API key (401/403)
    InsufficientCreditsError,  # Balance too low — top up at portal/billing (402)
    RateLimitError,         # Per-request hard cap or rate limit exceeded (429)
    ValidationError,        # Bad request payload (422)
    ServerError,            # API server error (5xx)
    TimeoutError,           # Request timed out
    ScrapedatshiError       # Base exception — catch-all
)

try:
    result = client.pipeline.sync(
        url="https://docs.example.com",
        embedding_provider="openai",
        embedding_api_key="sk-...",
        vector_db="pinecone",
        vector_db_api_key="pc-...",
        index_name="my-docs",
    )
except InsufficientCreditsError:
    print("Balance too low — top up at scrapedatshi.com/portal/billing")
except RateLimitError as e:
    print(f"Rate limit hit: {e.message}")
except ScrapedatshiError as e:
    print(f"API error {e.status_code}: {e.message}")
```

---

## Hard Caps

Per-request hard caps protect server stability and apply to all accounts:

| Cap | Limit |
|---|---|
| Max pages / crawl | 35 |
| Max pages / spider | 35 |
| Max chunks / request | 35,000 |
| Max content size | ~75,000 words (auto-truncated) |

Exceeding a hard cap returns HTTP 400. Content exceeding the size limit is automatically
truncated — check `result.content_truncated` to detect this.

---

## Development

```bash
git clone https://github.com/mxchris18/scrapedatshi-py
cd scrapedatshi-py
pip install -e ".[dev]"
pytest
```

---

## License

MIT — see [LICENSE](https://github.com/mxchris18/scrapedatshi-py/blob/main/LICENSE).
