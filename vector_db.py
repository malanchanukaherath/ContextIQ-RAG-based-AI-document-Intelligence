import logging

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue


logger = logging.getLogger(__name__)

class QdrantStorage:
    def __init__(self, path="./qdrant_storage", collection="docs", dim=768):
        # Use local file storage instead of server connection
        self.client = QdrantClient(path=path)
        self.collection = collection
        self.default_dim = dim
        if not self.client.collection_exists(self.collection):
            self._create_collection(dim)
        else:
            self._ensure_collection_dim(dim)

    def _create_collection(self, dim: int):
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(
                size=dim,
                distance=Distance.COSINE
            )
        )

    def _get_collection_dim(self):
        info = self.client.get_collection(self.collection)
        vectors_cfg = getattr(info.config.params, "vectors", None)

        # Qdrant can represent vector config as either a single vector params
        # object or a named-vector dictionary.
        if isinstance(vectors_cfg, dict):
            first_cfg = next(iter(vectors_cfg.values()), None)
            return getattr(first_cfg, "size", None)

        return getattr(vectors_cfg, "size", None)

    def _ensure_collection_dim(self, required_dim: int):
        current_dim = self._get_collection_dim()
        if current_dim is None:
            return

        if int(current_dim) != int(required_dim):
            logger.warning(
                "Recreating collection '%s' due to vector dimension change (%s -> %s)",
                self.collection,
                current_dim,
                required_dim,
            )
            self.client.delete_collection(self.collection)
            self._create_collection(required_dim)
    
    def upsert(self, ids, vectors, payloads):
        if not vectors:
            return

        required_dim = len(vectors[0])
        if any(len(v) != required_dim for v in vectors):
            raise ValueError("All vectors must have the same dimensionality before upsert")

        self._ensure_collection_dim(required_dim)
        points = [PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
        self.client.upsert(self.collection, points=points)

    def search(self, query_vector, top_k=5):
        results = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=top_k
        ).points

        contexts = []
        sources = set()
        scores = []
        payloads = []

        for r in results:
            payload = getattr(r, "payload", None) or {}
            text = payload.get("text", "")
            source = payload.get("source", "")
            score = getattr(r, "score", 0.0)
            
            contexts.append(text)
            sources.add(source)
            scores.append(score)
            payloads.append(payload)
        
        return {
            "contexts": contexts, 
            "sources": list(sources),
            "scores": scores,
            "payloads": payloads
        }
    
    def delete_by_source(self, source_id: str):
        """Delete all vectors associated with a specific source document"""
        # Delete points matching the source filter
        self.client.delete(
            collection_name=self.collection,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=source_id)
                    )
                ]
            )
        )
    
    def get_all_sources(self):
        """Get all unique source documents in the collection"""
        try:
            # Scroll through all points to collect unique sources
            scroll_result = self.client.scroll(
                collection_name=self.collection,
                limit=10000,  # Adjust based on your collection size
                with_payload=True,
                with_vectors=False
            )
            
            sources = set()
            for point in scroll_result[0]:  # scroll_result is (points, next_page_offset)
                payload = getattr(point, "payload", None) or {}
                source = payload.get("source", "")
                if source:
                    sources.add(source)
            
            return list(sources)
        except Exception as e:
            return []
    