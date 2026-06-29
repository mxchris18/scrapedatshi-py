"""
scrapedatshi.providers
~~~~~~~~~~~~~~~~~~~~~~
Reference constants for all supported providers.

Use these to discover which embedding providers, vector databases, and LLM
providers are compatible with the scrapedatshi API — and what fields each
requires.

**Provider types:**

- **Embedding providers** use embedding-specific models to convert text into
  vectors (e.g. ``text-embedding-3-small``). Used by ``sync()`` and ``ingest()``.

- **LLM providers** use chat/completion models for Contextual Retrieval (RAG 2.0)
  and Schema Extraction. A model name is always required — no default is applied.
  Check your provider's documentation for models available on your API key.

- **Vector DB providers** store and query your embedded vectors.

Example::

    from scrapedatshi.providers import EMBEDDING_PROVIDERS, VECTOR_DB_PROVIDERS, LLM_PROVIDERS

    # List all supported embedding providers
    for key, info in EMBEDDING_PROVIDERS.items():
        print(f"{key}: {info['label']}")

    # Check required fields for a vector DB
    print(VECTOR_DB_PROVIDERS["pinecone"]["required_fields"])
    # → ["api_key", "index_host"]
"""

from __future__ import annotations

# ── Embedding Providers ───────────────────────────────────────────────────────
# Embedding providers convert text chunks into vectors.
# Used by sync() and ingest() pipeline methods.
#
# Cloud providers require an API key and a model name.
# Local providers (Ollama) require a publicly accessible endpoint (ngrok) and a model name.

EMBEDDING_PROVIDERS: dict[str, dict] = {
    "openai": {
        "label": "OpenAI",
        "requires_api_key": True,
        "local": False,
        "notes": (
            "Models discovered dynamically after key verification. "
            "Common models: text-embedding-3-small (1536 dims), "
            "text-embedding-3-large (3072 dims), text-embedding-ada-002 (1536 dims). "
            "See https://platform.openai.com/docs/models/embeddings for all available models."
        ),
    },
    "cohere": {
        "label": "Cohere",
        "requires_api_key": True,
        "local": False,
        "notes": (
            "Models discovered dynamically after key verification. "
            "Common models: embed-english-v3.0 (1024 dims), "
            "embed-multilingual-v3.0 (1024 dims), embed-english-light-v3.0 (384 dims). "
            "See https://docs.cohere.com/docs/cohere-embed for all available models."
        ),
    },
    "gemini": {
        "label": "Google Gemini",
        "requires_api_key": True,
        "local": False,
        "notes": (
            "Models discovered dynamically after key verification. "
            "Common models: gemini-embedding-001 (3072 dims), text-embedding-004 (768 dims). "
            "Note: Google API returns model names with a 'models/' prefix. "
            "See https://ai.google.dev/gemini-api/docs/models for all available models."
        ),
    },
    "mistral": {
        "label": "Mistral",
        "requires_api_key": True,
        "local": False,
        "notes": (
            "Current model: mistral-embed (1024 dims). "
            "See https://docs.mistral.ai/capabilities/embeddings/ for available models."
        ),
    },
    "voyage": {
        "label": "Voyage AI",
        "requires_api_key": True,
        "local": False,
        "notes": (
            "Models: voyage-3 (1024 dims), voyage-3-lite (512 dims), "
            "voyage-code-3 (1024 dims), voyage-finance-2 (1024 dims), "
            "voyage-law-2 (1024 dims). "
            "See https://docs.voyageai.com/docs/embeddings for all available models."
        ),
    },
    "ollama": {
        "label": "Ollama (Local)",
        "requires_api_key": False,
        "local": True,
        "notes": (
            "Runs locally — no API key required. "
            "You must expose your Ollama instance publicly using ngrok (or similar tunnel) "
            "before use. Run: 'ngrok http 11434', then pass the HTTPS URL as "
            "'embedding_endpoint' in your request. "
            "A model name is required (e.g. 'nomic-embed-text', 'mxbai-embed-large'). "
            "Embedding dimensions vary by model. "
            "See https://ollama.com/library for available embedding models."
        ),
    },
}

# ── Vector Database Providers ─────────────────────────────────────────────────
# required_fields: fields that must be provided for the provider to work.
# optional_fields: fields that can be omitted (have defaults or are optional).
# local: True for providers that run on the user's own machine/filesystem.

VECTOR_DB_PROVIDERS: dict[str, dict] = {
    "pinecone": {
        "label": "Pinecone",
        "required_fields": ["api_key", "index_host"],
        "optional_fields": ["namespace"],
        "local": False,
        "notes": (
            "Index must be pre-created in the Pinecone dashboard before ingesting. "
            "index_host format: https://your-index-abc123.svc.pinecone.io"
        ),
    },
    "qdrant": {
        "label": "Qdrant",
        "required_fields": ["url", "collection_name"],
        "optional_fields": ["api_key"],
        "local": False,
        "notes": (
            "api_key is optional for local Qdrant instances. "
            "url format: https://your-cluster.qdrant.io"
        ),
    },
    "chroma": {
        "label": "ChromaDB (Local)",
        "required_fields": ["collection_name"],
        "optional_fields": ["host", "port"],
        "local": True,
        "notes": (
            "ChromaDB must be running locally (or on a reachable host). "
            "host defaults to 'localhost', port defaults to 8000. "
            "Collection is created automatically if it does not exist. "
            "Run ChromaDB with: 'chroma run --path ./chroma_data'"
        ),
    },
    "supabase": {
        "label": "Supabase (pgvector)",
        "required_fields": ["connection_string", "table_name"],
        "optional_fields": ["vector_column"],
        "local": False,
        "notes": (
            "connection_string format: postgresql://user:pass@db.project.supabase.co:5432/postgres. "
            "vector_column defaults to 'embedding' if not specified. "
            "Table is created automatically on first ingest."
        ),
    },
    "weaviate": {
        "label": "Weaviate",
        "required_fields": ["url", "class_name"],
        "optional_fields": ["api_key"],
        "local": False,
        "notes": (
            "api_key is optional for local Weaviate instances. "
            "url format: https://your-cluster.weaviate.cloud"
        ),
    },
    "mongodb": {
        "label": "MongoDB Atlas",
        "required_fields": ["connection_string", "database_name", "collection_name"],
        "optional_fields": ["index_name"],
        "local": False,
        "notes": (
            "Collection is created automatically on first ingest. "
            "You must manually create a Vector Search index in the Atlas UI after first ingest. "
            "index_name defaults to 'vector_index'."
        ),
    },
    "azure_cosmos": {
        "label": "Azure Cosmos DB (NoSQL)",
        "required_fields": ["connection_string", "database_name", "container_name"],
        "optional_fields": [],
        "local": False,
        "notes": (
            "Database and container must be pre-created in the Azure portal "
            "with a vector index policy configured. "
            "connection_string format: AccountEndpoint=https://...;AccountKey=..."
        ),
    },
    "azure_cosmos_mongo": {
        "label": "Azure Cosmos DB (MongoDB API)",
        "required_fields": ["connection_string", "database_name", "collection_name"],
        "optional_fields": ["index_name"],
        "local": False,
        "notes": (
            "Use this for 'Azure Cosmos DB for MongoDB' accounts. "
            "For 'Azure Cosmos DB for NoSQL' accounts, use 'azure_cosmos' instead. "
            "connection_string format: mongodb+srv://account:key@account.mongocluster.cosmos.azure.com"
        ),
    },
    "lancedb": {
        "label": "LanceDB (Local)",
        "required_fields": ["db_path", "table_name"],
        "optional_fields": [],
        "local": True,
        "notes": (
            "LanceDB stores data as files on your local filesystem. "
            "db_path is a local directory path (e.g. './lancedb'). "
            "The directory and table are created automatically on first ingest. "
            "Requires the 'lancedb' and 'pyarrow' packages on the server."
        ),
    },
}

# ── LLM Providers ─────────────────────────────────────────────────────────────
# Used for Contextual Retrieval (RAG 2.0) and Schema Extraction.
#
# IMPORTANT: A model name is always required — no default is applied by the API.
# Check your provider's documentation for models available on your API key.
#
# Model tiers affect the context window used for schema extraction:
#   Standard models (names containing "mini", "flash", "haiku", "lite", "nano"):
#     → 8,000 character context window
#   Advanced models (all others):
#     → 30,000 character context window
# Use an advanced model for long-form pages (documentation, legal docs, research papers).

LLM_PROVIDERS: dict[str, dict] = {
    "openai": {
        "label": "OpenAI",
        "requires_api_key": True,
        "notes": (
            "A model name is required — no default is applied. "
            "Check https://platform.openai.com/docs/models for models available on your API key. "
            "Model tier affects context window: standard models (gpt-4o-mini, etc.) use 8k chars; "
            "advanced models (gpt-4o, etc.) use 30k chars."
        ),
    },
    "anthropic": {
        "label": "Anthropic",
        "requires_api_key": True,
        "notes": (
            "A model name is required — no default is applied. "
            "Check https://docs.anthropic.com/en/docs/about-claude/models for models available on your API key. "
            "Model tier affects context window: standard models (haiku) use 8k chars; "
            "advanced models (sonnet, opus) use 30k chars."
        ),
    },
    "gemini": {
        "label": "Google Gemini",
        "requires_api_key": True,
        "notes": (
            "A model name is required — no default is applied. "
            "Check https://ai.google.dev/gemini-api/docs/models for models available on your API key. "
            "Model tier affects context window: standard models (flash, lite, nano) use 8k chars; "
            "advanced models (pro, etc.) use 30k chars. "
            "Note: Google API returns model names with a 'models/' prefix."
        ),
    },
}

# ── Convenience sets ──────────────────────────────────────────────────────────

SUPPORTED_EMBEDDING_PROVIDERS: frozenset[str] = frozenset(EMBEDDING_PROVIDERS.keys())
SUPPORTED_VECTOR_DB_PROVIDERS: frozenset[str] = frozenset(VECTOR_DB_PROVIDERS.keys())
SUPPORTED_LLM_PROVIDERS: frozenset[str] = frozenset(LLM_PROVIDERS.keys())
