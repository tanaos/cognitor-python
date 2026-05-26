# cognitor-python

Python SDK for [Cognitor](https://github.com/tanaos/cognitor).

## Installation

```bash
pip install cognitor
```

## Quick start

```python
from cognitor import Cognitor

with Cognitor("http://localhost:8000", api_key="your-api-key") as client:
    print(client.ping())
```

The `api_key` parameter is optional — omit it if your server does not require authentication.

## Usage

### Collections

```python
# Create a collection (server-side embedding)
collection = client.create_collection(
    "my-collection",
    emb_model="text-embedding-3-small",
)

# Create a collection with a fixed vector dimension (client-side embedding)
collection = client.create_collection("my-collection", dim=1536)

# List all collections
collections = client.list_collections()

# Get a single collection
collection = client.get_collection("my-collection")

# Delete a collection
client.delete_collection("my-collection")
```

### Documents

```python
# Add documents (texts are embedded server-side when emb_model is set)
ids = client.add_documents(
    "my-collection",
    texts=["Hello world", "Cognitor is a vector store"],
    metadatas=[{"source": "docs"}, {"source": "docs"}],
)

# Add documents with explicit vectors (client-side embedding)
ids = client.add_documents(
    "my-collection",
    texts=["Hello world"],
    metadatas=[{"source": "docs"}],
    vectors=[[0.1, 0.2, ...]],
)

# Add a large number of documents in batches
ids = client.bulk_add_documents(
    "my-collection",
    texts=[...],
    metadatas=[...],
    batch_size=512,
)

# List documents (paginated)
page = client.list_documents("my-collection", offset=0, limit=50)
print(page.total, page.documents)

# Get a single document
doc = client.get_document("my-collection", doc_id)

# Update document metadata
doc = client.update_document_metadata("my-collection", doc_id, {"source": "updated"})

# Delete a document
client.delete_document("my-collection", doc_id)
```

### Search

```python
# Search by text (requires server-side embedding model)
response = client.search("my-collection", query_text="Hello", top_k=10)

# Search by vector
response = client.search("my-collection", query_vector=[0.1, 0.2, ...], top_k=10)

# Filter results by metadata
response = client.search(
    "my-collection",
    query_text="Hello",
    filters={"source": "docs"},
)

# Include vectors in results
response = client.search("my-collection", query_text="Hello", include_vectors=True)

for hit in response.results:
    print(f"score={hit.score:.4f}  text={hit.text!r}")
```

### Admin

```python
# Compact a collection (removes deleted vectors)
result = client.compact("my-collection")
print(result.deleted_count, "vectors removed")
```

## Error handling

All errors are subclasses of `CognitorError`.

| Exception | HTTP status |
|---|---|
| `AuthenticationError` | 401 |
| `NotFoundError` | 404 |
| `ConflictError` | 409 |
| `ValidationError` | 400 / 422 |
| `ServerError` | 5xx |

```python
from cognitor_client import Cognitor, NotFoundError, AuthenticationError

try:
    collection = client.get_collection("nonexistent")
except NotFoundError as e:
    print("not found:", e)
except AuthenticationError as e:
    print("unauthorized:", e)
```

## Connection management

Use the client as a context manager (recommended) to ensure the underlying HTTP connection is closed:

```python
with Cognitor("http://localhost:8000") as client:
    ...
```

Or close it manually:

```python
client = Cognitor("http://localhost:8000")
try:
    ...
finally:
    client.close()
```
