from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

Vector = list[float]
Metadata = dict[str, Any]


@dataclass
class Collection:
    name: str
    dim: int
    doc_count: int
    emb_model: Optional[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Collection:
        return cls(
            name=d["name"],
            dim=d["dim"],
            doc_count=d["doc_count"],
            emb_model=d.get("emb_model"),
        )


@dataclass
class Document:
    id: str
    vector: Vector
    text: str
    metadata: Metadata

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Document:
        return cls(
            id=d["id"],
            vector=d["vector"],
            text=d["text"],
            metadata=d["metadata"],
        )


@dataclass
class ListDocumentsResult:
    documents: list[Document]
    total: int
    offset: int
    limit: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ListDocumentsResult:
        return cls(
            documents=[Document.from_dict(doc) for doc in d["documents"]],
            total=d["total"],
            offset=d["offset"],
            limit=d["limit"],
        )


@dataclass
class SearchResult:
    id: str
    score: float
    text: str
    metadata: Metadata
    vector: Optional[Vector]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SearchResult:
        return cls(
            id=d["id"],
            score=d["score"],
            text=d["text"],
            metadata=d["metadata"],
            vector=d.get("vector"),
        )


@dataclass
class SearchResponse:
    results: list[SearchResult]
    total: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SearchResponse:
        return cls(
            results=[SearchResult.from_dict(r) for r in d["results"]],
            total=d["total"],
        )


@dataclass
class CompactionResult:
    collection_name: str
    vectors_before: int
    live_count: int
    deleted_count: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CompactionResult:
        return cls(
            collection_name=d["collection_name"],
            vectors_before=d["vectors_before"],
            live_count=d["live_count"],
            deleted_count=d["deleted_count"],
        )
