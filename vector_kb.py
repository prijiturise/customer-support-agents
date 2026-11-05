import os
import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

class VectorKnowledgeBase:
    def __init__(self, kb_dir="knowledge_base"):
        self.kb_dir = kb_dir
        # Compact, high-speed semantic embedding model (384 dimensions)
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.chunks = []
        self.sources = []
        self.index = None
        self.reload()

    def _extract_text(self, filepath: str) -> str:
        """Extract text from PDF, MD, or TXT documents."""
        if filepath.endswith(".pdf"):
            reader = PdfReader(filepath)
            extracted = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted.append(text)
            return "\n".join(extracted)
        elif filepath.endswith((".md", ".txt")):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def reload(self):
        """Scans knowledge_base/ folder, chunks documents, and builds the FAISS index."""
        self.chunks = []
        self.sources = []
        if not os.path.exists(self.kb_dir):
            os.makedirs(self.kb_dir, exist_ok=True)

        for filename in os.listdir(self.kb_dir):
            filepath = os.path.join(self.kb_dir, filename)
            if not os.path.isfile(filepath):
                continue

            content = self._extract_text(filepath)
            # Split by double newlines or major section breaks
            sections = [s.strip() for s in content.split("\n\n") if len(s.strip()) > 20]

            for sec in sections:
                self.chunks.append(sec)
                self.sources.append(filename)

        if self.chunks:
            # Generate dense embeddings
            embeddings = self.encoder.encode(self.chunks, convert_to_numpy=True)
            # Normalize vectors for exact cosine similarity
            faiss.normalize_L2(embeddings)
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            self.index.add(embeddings)
        else:
            self.index = None

    def search(self, query: str, top_k: int = 3, threshold: float = 0.20) -> str:
        """Queries the FAISS index and returns matching passages with filenames."""
        if self.index is None or len(self.chunks) == 0:
            return "NO_MATCH: Knowledge base contains no indexed documents."

        query_vector = self.encoder.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vector)
        distances, indices = self.index.search(query_vector, top_k)

        matches = []
        for score, idx in zip(distances[0], indices[0]):
            if idx != -1 and score >= threshold:
                source = self.sources[idx]
                chunk_text = self.chunks[idx]
                matches.append(f"[{source}] (Score: {score:.2f}):\n{chunk_text}")

        if not matches:
            return "NO_MATCH: No relevant company policies or manual entries found."

        return "\n\n---\n\n".join(matches)

# Global singleton instance
kb_engine = VectorKnowledgeBase()

if __name__ == "__main__":
    print(f"Total chunks indexed: {len(kb_engine.chunks)}")
    test_query = "Where is my order? shipping status and delay"
    print("\n--- Test Search ---")
    print(kb_engine.search(test_query))