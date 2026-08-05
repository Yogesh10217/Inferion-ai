import io
from typing import Protocol
from app.knowledge.pipeline import PipelineStage, DocumentContext

class StorageProvider(Protocol):
    """Protocol for fetching documents from storage."""
    async def get_document(self, document_id: str) -> bytes:
        ...

class DocumentIngestionStage(PipelineStage):
    """Parses various document formats (PDF, DOCX, TXT, etc.)."""
    
    def __init__(self, storage_provider: StorageProvider):
        self.storage_provider = storage_provider

    async def process(self, context: DocumentContext) -> DocumentContext:
        """Fetches and parses the document."""
        try:
            raw_data = await self.storage_provider.get_document(context.document_id)
            context.raw_content = raw_data
            
            mime_type = context.metadata.get("mime_type", "")
            file_name = context.metadata.get("file_name", "").lower()
            
            blocks = []
            full_text = ""
            
            if "pdf" in mime_type or file_name.endswith(".pdf"):
                import fitz
                doc = fitz.open(stream=raw_data, filetype="pdf")
                global_offset = 0
                for page_num, page in enumerate(doc):
                    page_dict = page.get_text("dict")
                    for block in page_dict.get("blocks", []):
                        if "lines" in block:
                            block_text = ""
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    block_text += span["text"]
                                block_text += "\n"
                            
                            start_offset = global_offset
                            end_offset = start_offset + len(block_text)
                            global_offset = end_offset
                            
                            full_text += block_text
                            
                            blocks.append({
                                "text": block_text,
                                "page_number": page_num + 1,
                                "start_offset": start_offset,
                                "end_offset": end_offset,
                                "type": "text"
                            })
                context.metadata["mime_type"] = "application/pdf"
            elif "wordprocessingml" in mime_type or file_name.endswith(".docx"):
                import docx
                doc = docx.Document(io.BytesIO(raw_data))
                global_offset = 0
                for para in doc.paragraphs:
                    if not para.text.strip():
                        continue
                    block_text = para.text + "\n"
                    start_offset = global_offset
                    end_offset = start_offset + len(block_text)
                    global_offset = end_offset
                    
                    full_text += block_text
                    
                    heading = None
                    if para.style and para.style.name.startswith("Heading"):
                        heading = para.text.strip()
                    
                    blocks.append({
                        "text": block_text,
                        "page_number": 1, 
                        "start_offset": start_offset,
                        "end_offset": end_offset,
                        "section_heading": heading,
                        "type": "text"
                    })
                context.metadata["mime_type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            else:
                text = raw_data.decode('utf-8', errors='ignore')
                full_text = text
                blocks.append({
                    "text": text,
                    "page_number": 1,
                    "start_offset": 0,
                    "end_offset": len(text),
                    "type": "text"
                })
                context.metadata["mime_type"] = "text/plain"
            
            context.parsed_content = full_text
            context.metadata["blocks"] = blocks
            
        except Exception as e:
            context.errors.append(f"Ingestion failed: {e}")
            
        return context
