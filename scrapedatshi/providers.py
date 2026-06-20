"""
scrapedatshi.providers
~~~~~~~~~~~~~~~~~~~~~~
Reference constants for all supported providers.

Use these to discover which embedding providers, vector databases, and LLM
providers are compatible with the scrapedatshi API — and what fields each
requires.

Example::

    from scrapedatshi.providers import EMBEDDING_PROVIDERS, VECTOR_DB_PROVIDERS, LLM_PROVIDERS

    # List all supported embedding providers
    for key, info in EMBEDDING_PROVIDERS.items():
        print(f"{key}: {info['label']} (default model: {info['default_model']})")

    # Check required fields for a vector DB
    print(VECTOR_DB_PROVIDERS["pinecone"]["required_fields"])
    # → ["api_key", "index_host"]
"""

from __future__ import annotations

# ── Embedding Providers ───────────────────────────────────────────────────────
# All providers support dynamic model discovery via the verify-key flow.
# The default_model is used when no model is explicitly specified.

EMBEDDING_PROVIDERS: dict[str, dict] = {
    "openai": {
        "label": "OpenAI",
        "default_model": "text-embedding-3-small",
        "requires_api_key": True,
        "notes": (
            "Models discovered dynamically after key verification. "
            "Common models: text-embedding-3-small (1536 dims), "
            "text-embedding-3-large (3072 dims), text-embedding-ada-002 (1536 dims)."
        ),
    },
    "cohere": {
        "label": "Cohere",
        "default_model": "embed-english-v3.0",
        "requires_api_key": True,
        "notes": (
            "Models discovered dynamically after key verification. "
            "Common models: embed-english-v3.0 (1024 dims), "
            "embed-multilingual-v3.0 (1024 dims), embed-english-light-v3.0 (384 dims)."
        ),
    },
    "gemini": {
        "label": "Google Gemini",
        "default_model": "gemini-embedding-001",
        "requires_api_key": True,
        "notes": (
            "Models discovered dynamically after key verification. "
            "Common models: gemini-embedding-001 (3072 dims), text-embedding-004 (768 dims). "
            "Note: Google API returns model names with a 'models/' prefix."
        ),
    },
    "mistral": {
        "label": "Mistral",
        "default_model": "mistral-embed",
        "requires_api_key": True,
        "notes": "Current model: mistral-embed (1024 dims).",
    },
    "voyage": {
        "label": "Voyage AI",
        "default_model": "voyage-3",
        "requires_api_key": True,
        "notes": (
            "Models: voyage-3 (1024 dims), voyage-3-lite (512 dims), "
            "voyage-code-3 (1024 dims), voyage-finance-2 (1024 dims), "
            "voyage-law-2 (1024 dims)."
        ),
    },
}

# ── Vector Database Providers ─────────────────────────────────────────────────
# required_fields: fields that must be provided for the provider to work.
# optional_fields: fields that can be omitted (have defaults or are optional).

VECTOR_DB_PROVIDERS: dict[str, dict] = {
    "pinecone": {
        "label": "Pinecone",
        "required_fields": ["api_key", "index_host"],
        "optional_fields": ["namespace"],
        "notes": (
            "Index must be pre-created in the Pinecone dashboard before ingesting. "
            "index_host format: https://your-index-abc123.svc.pinecone.io"
        ),
    },
    "qdrant": {
        "label": "Qdrant",
        "required_fields": ["url", "collection_name"],
        "optional_fields": ["api_key"],
        "notes": (
            "api_key is optional for local Qdrant instances. "
            "url format: https://your-cluster.qdrant.io"
        ),
    },
    "supabase": {
        "label": "Supabase (pgvector)",
        "required_fields": ["connection_string", "table_name"],
        "optional_fields": ["vector_column"],
        "notes": (
            "connection_string format: postgresql://user:pass@db.project.supabase.co:5432/postgres. "
            "vector_column defaults to 'embedding' if not specified."
        ),
    },
    "weaviate": {
        "label": "Weaviate",
        "required_fields": ["url", "class_name"],
        "optional_fields": ["api_key"],
        "notes": (
            "api_key is optional for local Weaviate instances. "
            "url format: https://your-cluster.weaviate.cloud"
        ),
    },
    "mongodb": {
        "label": "MongoDB Atlas",
        "required_fields": ["connection_string", "database_name", "collection_name"],
        "optional_fields": ["index_name"],
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
        "notes": (
            "Use this for 'Azure Cosmos DB for MongoDB' accounts. "
            "For 'Azure Cosmos DB for NoSQL' accounts, use 'azure_cosmos' instead. "
            "connection_string format: mongodb+srv://account:key@account.mongocluster.cosmos.azure.com"
        ),
    },
}

# ── LLM Providers ─────────────────────────────────────────────────────────────
# Used for Contextual Retrieval (RAG 2.0) and Schema Extraction.
# Models are discovered dynamically after key verification.

LLM_PROVIDERS: dict[str, dict] = {
    "openai": {
        "label": "OpenAI",
        "default_model": "gpt-4o-mini",
        "notes": (
            "Models discovered dynamically after key verification. "
            "Model tiers affect context window for schema extraction: "
            "Standard models (gpt-4o-mini, etc.) use an 8,000 char context window; "
            "Advanced models (gpt-4o, etc.) use a 30,000 char context window. "
            "Recommended: gpt-4o-mini (fast, low cost) or gpt-4o (best quality for long pages)."
        ),
    },
    "anthropic": {
        "label": "Anthropic",
        "default_model": "claude-3-haiku-20240307",
        "notes": (
            "Models discovered dynamically after key verification. "
            "Model tiers affect context window for schema extraction: "
            "Standard models (haiku) use an 8,000 char context window; "
            "Advanced models (sonnet, opus) use a 30,000 char context window. "
            "Recommended: claude-3-haiku (fast, low cost) or claude-3-5-sonnet (best quality for long pages)."
        ),
    },
    "gemini": {
        "label": "Google Gemini",
        "default_model": "gemini-1.5-flash",
        "notes": (
            "Models discovered dynamically after key verification. "
            "Model tiers affect context window for schema extraction: "
            "Standard models (flash, lite, nano) use an 8,000 char context window; "
            "Advanced models (pro, etc.) use a 30,000 char context window. "
            "Recommended: gemini-1.5-flash (fast, low cost) or gemini-1.5-pro (best quality for long pages). "
            "Note: Google API returns model names with a 'models/' prefix."
        ),
    },
}

# ── Convenience sets ──────────────────────────────────────────────────────────

SUPPORTED_EMBEDDING_PROVIDERS: frozenset[str] = frozenset(EMBEDDING_PROVIDERS.keys())
SUPPORTED_VECTOR_DB_PROVIDERS: frozenset[str] = frozenset(VECTOR_DB_PROVIDERS.keys())
SUPPORTED_LLM_PROVIDERS: frozenset[str] = frozenset(LLM_PROVIDERS.keys())
