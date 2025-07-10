import torch
import faiss
from llama_index.core import (
    VectorStoreIndex, 
    StorageContext,
    Settings
)
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core import load_index_from_storage

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

class VectorDB_Manager:
    def __init__(self, embed_model: HuggingFaceEmbedding, dimension: int = 1024):
        """
        embed_model: Model embedding (BGE-M3)
        dimension: Dimension của embedding vector (BGE-M3 = 1024)
        """
        self.embed_model = embed_model
        self.dimension = dimension
        self.index = None
        self.vector_store = None
        
        # Set global settings
        Settings.embed_model = embed_model

    def load_index(self, persist_dir: str):
        print("Path vector DB: ", persist_dir)
        """Load index từ disk"""
        
        # Load FAISS index
        faiss_index = faiss.read_index(f"{persist_dir}/vector_index.faiss")
        
        # Tạo vector store
        self.vector_store = FaissVectorStore(faiss_index=faiss_index)
        
        # Tạo storage context
        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store,
            persist_dir=persist_dir
        )
        
        # Load index
        self.index = load_index_from_storage(
            storage_context=storage_context,
            embed_model=self.embed_model
        )
        
        print(f"✅ Đã load FAISS index từ {persist_dir}")
        return self.index