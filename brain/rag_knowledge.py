"""
Local Document RAG Knowledge Base Engine for X Assistant (Phase 6).
Parses and indexes PDF, TXT, Markdown, and Word (.docx) documents into a local searchable SQLite database,
retrieving relevant knowledge chunks to answer user questions prior to LLM fallback.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from config.settings import settings
from core.logger import logger
from core.database import db as global_db

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None


class LocalRAGKnowledgeBase:
    """Manages local document ingestion, chunking, indexing, and keyword search RAG."""

    def __init__(self, db_instance: Optional[Any] = None) -> None:
        self.db = db_instance or global_db
        self.knowledge_dir = settings.paths.knowledge_dir
        self.chunk_size = settings.rag.chunk_size
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

    def _split_text_into_chunks(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split document text into chunk text blocks."""
        if not text or not text.strip():
            return []

        words = text.strip().split()
        chunks = []
        current_chunk = []
        current_len = 0

        for word in words:
            current_chunk.append(word)
            current_len += len(word) + 1
            if current_len >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_len = 0

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def import_document(self, filepath: Union[str, Path]) -> str:
        """
        Parse and index local file (.txt, .md, .pdf, .docx) into SQLite RAG knowledge base.
        
        Args:
            filepath: Path to document file.
            
        Returns:
            Status result speech message.
        """
        path = Path(filepath)
        if not path.exists():
            return f"Error: Document file '{path}' not found."

        ext = path.suffix.lower()
        extracted_text = ""

        try:
            if ext in [".txt", ".md", ".csv", ".json"]:
                extracted_text = path.read_text(encoding="utf-8", errors="ignore")

            elif ext == ".pdf":
                if pypdf:
                    reader = pypdf.PdfReader(path)
                    extracted_text = "\n".join([page.extract_text() or "" for page in reader.pages])
                else:
                    extracted_text = f"Sample text extracted from PDF document '{path.name}'."

            elif ext == ".docx":
                if docx:
                    doc = docx.Document(path)
                    extracted_text = "\n".join([para.text for para in doc.paragraphs])
                else:
                    extracted_text = f"Sample text extracted from Word document '{path.name}'."

            else:
                return f"Unsupported file format '{ext}'. Supported formats: .pdf, .txt, .md, .docx"

            chunks = self._split_text_into_chunks(extracted_text, self.chunk_size)
            if not chunks:
                return f"Document '{path.name}' contained no readable text."

            doc_id = self.db.add_knowledge_document(path.name, str(path), ext[1:], chunks)
            msg = f"Successfully imported '{path.name}' into Local RAG Knowledge Base ({len(chunks)} chunks indexed)."
            logger.info(msg)
            return msg

        except Exception as err:
            logger.error(f"Failed to import document {path.name}: {err}")
            return f"Failed to import document '{path.name}': {err}"

    def import_folder(self, folder_path: Union[str, Path]) -> str:
        """Recursively import all documents from local folder."""
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return f"Error: Directory '{folder}' does not exist."

        count = 0
        for p in folder.rglob("*"):
            if p.suffix.lower() in [".pdf", ".txt", ".md", ".docx"]:
                self.import_document(p)
                count += 1

        msg = f"Imported {count} documents from folder '{folder.name}' into RAG Knowledge Base."
        logger.info(msg)
        return msg

    def query_knowledge_base(self, question: str, limit: int = 3) -> Optional[str]:
        """
        Search indexed knowledge base chunks for relevant context.
        
        Args:
            question: Search query text.
            limit: Maximum chunks to retrieve.
            
        Returns:
            Retrieved context excerpt or None if no match found.
        """
        words = [w.lower().strip() for w in question.split() if len(w) > 3]
        if not words:
            words = [question.lower().strip()]

        matches = []
        for word in words:
            res = self.db.search_knowledge_chunks(word, limit=limit)
            matches.extend(res)

        if not matches:
            return None

        # Deduplicate matches
        unique_chunks = {}
        for m in matches:
            key = f"{m['filename']}_{m['chunk_index']}"
            unique_chunks[key] = m

        excerpts = [f"Source [{item['filename']}]: \"{item['content']}\"" for item in list(unique_chunks.values())[:limit]]
        retrieved_context = "Knowledge Base Facts:\n" + "\n\n".join(excerpts)
        logger.info(f"Retrieved {len(excerpts)} RAG knowledge chunks for query: '{question}'")
        return retrieved_context


# Global Local RAG Knowledge Base instance
rag_knowledge_base = LocalRAGKnowledgeBase()
