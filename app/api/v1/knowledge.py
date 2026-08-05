from fastapi import APIRouter
from typing import List, Dict, Any
from pydantic import BaseModel

from app.knowledge.permissions import DocumentPermissions
from app.knowledge.evaluation import EvaluationMetrics, RetrievalResult, evaluate_retrieval
from app.knowledge.analytics import analytics_tracker, AnalyticsReport

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

# Models
class QueryRequest(BaseModel):
    query: str
    k: int = 5

class RerankRequest(BaseModel):
    query: str
    results: List[Dict[str, Any]]

class RewriteRequest(BaseModel):
    query: str

class EvaluateRequest(BaseModel):
    query: str
    results: List[RetrievalResult]
    total_relevant: int

class DocumentBase(BaseModel):
    title: str
    content: str
    permissions: DocumentPermissions

# CRUD Endpoints
@router.post("/documents", status_code=201)
async def create_document(doc: DocumentBase):
    return {"status": "success", "id": "doc_new", "title": doc.title}

@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    return {"id": document_id, "title": "Mock Document", "content": "..."}

@router.put("/documents/{document_id}")
async def update_document(document_id: str, doc: DocumentBase):
    return {"status": "success", "id": document_id}

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    return {"status": "success", "id": document_id}

# Operational Endpoints
@router.post("/query")
async def query_knowledge(req: QueryRequest):
    # Mock retrieval logic
    await analytics_tracker.track_query("user_api", req.query, 120.0, True)
    return {"query": req.query, "results": [{"chunk_id": "c1", "content": "Relevant answer mock"}]}

@router.post("/rerank")
async def rerank_results(req: RerankRequest):
    return {"query": req.query, "reranked_results": req.results}

@router.post("/rewrite")
async def rewrite_query(req: RewriteRequest):
    return {"original": req.query, "rewritten": f"{req.query} (expanded concept)"}

@router.post("/evaluate", response_model=EvaluationMetrics)
async def evaluate_system(req: EvaluateRequest):
    return evaluate_retrieval(req.results, req.total_relevant)

@router.get("/analytics", response_model=AnalyticsReport)
async def get_analytics():
    return await analytics_tracker.generate_report()

# System Config Endpoints
@router.get("/indexes")
async def list_indexes():
    return {"indexes": ["default", "tenant_1", "tenant_2"]}

@router.post("/indexes/reindex-all")
async def reindex_all():
    return {"status": "reindexing_started"}

@router.get("/embeddings")
async def get_embeddings_models():
    return {"models": ["text-embedding-3-small", "cohere-embed-english-v3.0"]}

@router.get("/providers")
async def get_providers():
    return {"providers": ["openai", "cohere", "huggingface", "azure"]}

@router.get("/vectorstores")
async def get_vectorstores():
    return {"vectorstores": ["pinecone", "qdrant", "chroma", "weaviate"]}
