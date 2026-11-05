import os
import pickle
import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

class VectorKnowledgeBase:
    def __init__(self, kb_dir="knowledge_base", index_dir="faiss_index"):
        self.kb_dir = kb_dir
        self.index_dir = index_dir
        self.index_file = os.path.join(index_dir, "index.faiss")
        self.meta_file = os.path.join(index_dir, "metadata.pkl")
        
        # Dense semantic embedding model (384 dimensions)
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.chunks = []
        self.sources = []
        self.index = None
        
        # Load from disk if available, otherwise build fresh
        if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
            self.load_from_disk()
        else:
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
        """Scans knowledge_base/, builds the FAISS index, and saves it to the faiss_index/ folder."""
        self.chunks = []
        self.sources = []
        os.makedirs(self.kb_dir, exist_ok=True)
        os.makedirs(self.index_dir, exist_ok=True)

        for filename in os.listdir(self.kb_dir):
            filepath = os.path.join(self.kb_dir, filename)
            if not os.path.isfile(filepath):
                continue

            content = self._extract_text(filepath)
            sections = [s.strip() for s in content.split("\n\n") if len(s.strip()) > 20]

            for sec in sections:
                self.chunks.append(sec)
                self.sources.append(filename)

        if self.chunks:
            embeddings = self.encoder.encode(self.chunks, convert_to_numpy=True)
            faiss.normalize_L2(embeddings)
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            self.index.add(embeddings)

            # Persist FAISS index and metadata files to disk
            faiss.write_index(self.index, self.index_file)
            with open(self.meta_file, "wb") as f:
                pickle.dump({"chunks": self.chunks, "sources": self.sources}, f)
            print(f"[FAISS] Created and saved database to '{self.index_file}'")
        else:
            self.index = None

    def load_from_disk(self):
        """Loads an existing FAISS index and metadata directly from disk."""
        self.index = faiss.read_index(self.index_file)
        with open(self.meta_file, "rb") as f:
            data = pickle.load(f)
            self.chunks = data["chunks"]
            self.sources = data["sources"]
        print(f"[FAISS] Loaded database from '{self.index_file}' with {len(self.chunks)} chunks.")

    def search(self, query: str, top_k: int = 3, threshold: float = 0.20) -> str:
        """Queries the persistent FAISS index and returns matching passages."""
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
    test_query = "Where is my order? shipping delay"
    print("\n--- Test Search ---")
    print(kb_engine.search(test_query))