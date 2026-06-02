from __future__ import annotations

from typing import Literal
from typing import Any, Optional

import httpx

from .exceptions import (
    AuthenticationError,
    CognitorError,
    ConflictError,
    NotFoundError,
    ServerError,
    ValidationError,
)
from .models import (
    Collection,
    CompactionResult,
    Document,
    ListDocumentsResult,
    Metadata,
    SearchResponse,
    Vector,
)


class Cognitor:
    """
    Client for the Cognitor REST API.
    """

    def __init__(
        self,
        base_url: str,
        *,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        headers: dict[str, str] = {}
        if api_key:
            headers["X-API-Key"] = api_key
        self._http = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=timeout,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Cognitor:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return
        try:
            message: str = response.json().get("message") or response.text
        except Exception:
            message = response.text
        code = response.status_code
        if code == 401:
            raise AuthenticationError(message, code)
        if code == 404:
            raise NotFoundError(message, code)
        if code == 409:
            raise ConflictError(message, code)
        if code in (400, 422):
            raise ValidationError(message, code)
        if code >= 500:
            raise ServerError(message, code)
        raise CognitorError(message, code)

    # ------------------------------------------------------------------
    # Base
    # ------------------------------------------------------------------

    def ping(self) -> str:
        response = self._http.get("/")
        self._raise_for_status(response)
        return response.json()

    def health_ready(self) -> Literal["ready", "loading"]:
        response = self._http.get("/health/ready")
        if response.status_code == 200:
            return "ready"
        if response.status_code == 503:
            return "loading"
        self._raise_for_status(response)
        return "loading"

    # ------------------------------------------------------------------
    # Collections
    # ------------------------------------------------------------------

    def list_collections(self) -> list[Collection]:
        response = self._http.get("/collections")
        self._raise_for_status(response)
        return [Collection.from_dict(c) for c in response.json()["collections"]]

    def get_collection(self, name: str) -> Collection:
        response = self._http.get(f"/collections/{name}")
        self._raise_for_status(response)
        return Collection.from_dict(response.json())

    def create_collection(
        self,
        name: str,
        *,
        dim: Optional[int] = None,
        emb_model: Optional[str] = None,
    ) -> Collection:
        body: dict[str, Any] = {"name": name}
        if dim is not None:
            body["dim"] = dim
        if emb_model is not None:
            body["emb_model"] = emb_model
        response = self._http.post("/collections", json=body)
        self._raise_for_status(response)
        return Collection.from_dict(response.json())

    def delete_collection(self, name: str) -> None:
        response = self._http.delete(f"/collections/{name}")
        self._raise_for_status(response)

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    def add_documents(
        self,
        collection: str,
        texts: list[str],
        metadatas: list[Metadata],
        *,
        vectors: Optional[list[Vector]] = None,
    ) -> list[str]:
        body: dict[str, Any] = {"texts": texts, "metadatas": metadatas}
        if vectors is not None:
            body["vectors"] = vectors
        response = self._http.post(f"/collections/{collection}/documents", json=body)
        self._raise_for_status(response)
        return response.json()["ids"]

    def bulk_add_documents(
        self,
        collection: str,
        texts: list[str],
        metadatas: list[Metadata],
        *,
        vectors: Optional[list[Vector]] = None,
        batch_size: int = 512,
    ) -> list[str]:
        body: dict[str, Any] = {"texts": texts, "metadatas": metadatas}
        if vectors is not None:
            body["vectors"] = vectors
        response = self._http.post(
            f"/collections/{collection}/documents/bulk",
            json=body,
            params={"batch_size": batch_size},
        )
        self._raise_for_status(response)
        return response.json()["ids"]

    def list_documents(
        self,
        collection: str,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> ListDocumentsResult:
        response = self._http.get(
            f"/collections/{collection}/documents",
            params={"offset": offset, "limit": limit},
        )
        self._raise_for_status(response)
        return ListDocumentsResult.from_dict(response.json())

    def get_document(self, collection: str, doc_id: str) -> Document:
        response = self._http.get(f"/collections/{collection}/documents/{doc_id}")
        self._raise_for_status(response)
        return Document.from_dict(response.json())

    def delete_document(self, collection: str, doc_id: str) -> None:
        response = self._http.delete(f"/collections/{collection}/documents/{doc_id}")
        self._raise_for_status(response)

    def update_document_metadata(
        self, collection: str, doc_id: str, metadata: Metadata
    ) -> Document:
        response = self._http.patch(
            f"/collections/{collection}/documents/{doc_id}/metadata",
            json={"metadata": metadata},
        )
        self._raise_for_status(response)
        return Document.from_dict(response.json())

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        collection: str,
        *,
        query_text: Optional[str] = None,
        query_vector: Optional[Vector] = None,
        top_k: int = 5,
        filters: Optional[Metadata] = None,
        include_vectors: bool = False,
        perform_extractive_qa: bool = True,
        perform_reranking: bool = True
    ) -> SearchResponse:
        body: dict[str, Any] = {
            "top_k": top_k, "include_vectors": include_vectors,
            "perform_extractive_qa": perform_extractive_qa,
            "perform_reranking": perform_reranking
        }
        if query_text is not None:
            body["query_text"] = query_text
        if query_vector is not None:
            body["query_vector"] = query_vector
        if filters is not None:
            body["filters"] = filters
        response = self._http.post(f"/collections/{collection}/search", json=body)
        self._raise_for_status(response)
        return SearchResponse.from_dict(response.json())

    # ------------------------------------------------------------------
    # Admin
    # ------------------------------------------------------------------

    def compact(self, collection: str) -> CompactionResult:
        response = self._http.post(f"/admin/collections/{collection}/compact")
        self._raise_for_status(response)
        return CompactionResult.from_dict(response.json())

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    
    def register(self, username: str, password: str) -> str:
        body = {"username": username, "password": password}
        response = self._http.post("/auth/register", json=body)
        self._raise_for_status(response)
        return response.json()["api_key"]
    
    def login(self, username: str, password: str) -> str:
        body = {"username": username, "password": password}
        response = self._http.post("/auth/login", json=body)
        self._raise_for_status(response)
        return response.json()["api_key"]