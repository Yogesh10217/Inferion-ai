from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .lifecycle import DocumentState, transition_document_state
from .models import KnowledgeDocument


async def get_next_version(session: AsyncSession, knowledge_base_id: str, document_name: str) -> int:
    """
    Calculates the next version number for a document in a given knowledge base.
    This prevents blindly overwriting embeddings of existing documents.
    """
    stmt = (
        select(KnowledgeDocument)
        .where(KnowledgeDocument.knowledge_base_id == knowledge_base_id)
        .where(KnowledgeDocument.name == document_name)
        .order_by(KnowledgeDocument.version.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    latest_doc = result.scalar_one_or_none()

    if not latest_doc:
        return 1
    return latest_doc.version + 1


async def archive_previous_versions(
    session: AsyncSession,
    knowledge_base_id: str,
    document_name: str,
    current_version: int,
    user_id: str
):
    """
    Marks all previous versions of a document as ARCHIVED.
    """
    stmt = (
        select(KnowledgeDocument)
        .where(KnowledgeDocument.knowledge_base_id == knowledge_base_id)
        .where(KnowledgeDocument.name == document_name)
        .where(KnowledgeDocument.version < current_version)
        .where(KnowledgeDocument.status == DocumentState.ACTIVE.value)
    )
    result = await session.execute(stmt)
    documents = result.scalars().all()

    for doc in documents:
        transition_document_state(doc, DocumentState.ARCHIVED, user_id=user_id)
