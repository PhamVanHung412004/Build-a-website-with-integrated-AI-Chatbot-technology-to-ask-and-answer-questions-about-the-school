from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from typing import List, Dict, Optional, Tuple
import os
import pickle
import json

class FaissSearcher:
    """
    Class để load và search trong Faiss vector database đã lưu
    """
    
    def __init__(
        self, 
        index_path: str,
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        Initialize searcher với index đã lưu
        
        Args:
            index_path: Đường dẫn đến folder chứa faiss index
            embedding_model: Model embedding (phải giống với lúc tạo index)
        """
        # Load embeddings (phải dùng cùng model với lúc tạo index)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load FAISS index
        print(f"Loading index from {index_path}...")
        self.vectorstore = FAISS.load_local(
            index_path, 
            self.embeddings,
            allow_dangerous_deserialization=True  # Cần để load index
        )
        
        # Load metadata nếu có
        self.metadata = self._load_metadata(index_path)
        
        print(f"✅ Loaded index successfully!")
        if self.metadata:
            print(f"📊 Total documents: {self.metadata.get('total_documents', 'Unknown')}")
    
    def _load_metadata(self, index_path: str) -> Dict:
        """Load metadata của index nếu có"""
        metadata_path = f"{index_path}_metadata.pkl"
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                return pickle.load(f)
        return {}
    
    def search(
        self, 
        query: str, 
        k: int = 4,
        search_type: str = "similarity",
        **kwargs
    ) -> List:
        """
        Search cơ bản
        
        Args:
            query: Câu query
            k: Số kết quả trả về
            search_type: "similarity" hoặc "mmr"
            
        Returns:
            List of documents
        """
        if search_type == "similarity":
            return self.vectorstore.similarity_search(query, k=k, **kwargs)
        elif search_type == "mmr":
            return self.vectorstore.max_marginal_relevance_search(
                query, k=k, fetch_k=k*3, **kwargs
            )
        else:
            raise ValueError(f"Unknown search_type: {search_type}")
    
    def search_with_score(
        self, 
        query: str, 
        k: int = 4,
        score_threshold: Optional[float] = None
    ) -> List[Tuple]:
        """
        Search với similarity scores
        
        Args:
            query: Câu query
            k: Số kết quả
            score_threshold: Chỉ trả về kết quả có score < threshold
            
        Returns:
            List of (document, score) tuples
        """
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        if score_threshold:
            # Filter theo score (lower is better cho L2 distance)
            results = [(doc, score) for doc, score in results if score < score_threshold]
        
        return results
    
    def search_with_filter(
        self,
        query: str,
        k: int = 4,
        filter_dict: Dict = None,
        search_type: str = "similarity"
    ) -> List:
        """
        Search với filter metadata
        
        Args:
            query: Câu query
            k: Số kết quả
            filter_dict: Dict các metadata cần filter
            search_type: "similarity" hoặc "mmr"
            
        Returns:
            List of filtered documents
        """
        # Faiss không support filter trực tiếp, phải search nhiều rồi filter
        results = self.search(query, k=k*3, search_type=search_type)
        
        if not filter_dict:
            return results[:k]
        
        # Manual filter
        filtered_results = []
        for doc in results:
            match = all(
                doc.metadata.get(key) == value 
                for key, value in filter_dict.items()
            )
            if match:
                filtered_results.append(doc)
                if len(filtered_results) >= k:
                    break
        
        return filtered_results
    
    def hybrid_search(
        self,
        query: str,
        k: int = 4,
        rerank: bool = True
    ) -> List:
        """
        Hybrid search: kết hợp similarity và keyword matching
        
        Args:
            query: Câu query
            k: Số kết quả
            rerank: Có rerank kết quả không
            
        Returns:
            List of documents
        """
        # 1. Semantic search
        semantic_results = self.search(query, k=k*2)
        
        # 2. Keyword search trong content
        keywords = query.lower().split()
        keyword_scores = {}
        
        for doc in semantic_results:
            content_lower = doc.page_content.lower()
            score = sum(1 for keyword in keywords if keyword in content_lower)
            keyword_scores[id(doc)] = score
        
        # 3. Rerank nếu cần
        if rerank:
            # Sort by keyword match score
            semantic_results.sort(
                key=lambda doc: keyword_scores.get(id(doc), 0), 
                reverse=True
            )
        
        return semantic_results[:k]
    
    def get_relevant_context(
        self,
        query: str,
        k: int = 4,
        max_tokens: int = 2000
    ) -> str:
        """
        Lấy context cho LLM
        
        Args:
            query: Câu query
            k: Số chunks
            max_tokens: Giới hạn tokens
            
        Returns:
            Combined context string
        """
        docs = self.search(query, k=k)
        
        context_parts = []
        current_tokens = 0
        
        for i, doc in enumerate(docs):
            # Ước tính tokens (rough estimate: 1 token ≈ 4 chars)
            doc_tokens = len(doc.page_content) // 4
            
            if current_tokens + doc_tokens > max_tokens:
                # Truncate nếu quá dài
                remaining_tokens = max_tokens - current_tokens
                remaining_chars = remaining_tokens * 4
                truncated_content = doc.page_content[:remaining_chars] + "..."
                context_parts.append(f"[Tài liệu {i+1}]\n{truncated_content}")
                break
            else:
                metadata_str = f"(Trang {doc.metadata.get('page', 'N/A')})"
                context_parts.append(f"[Tài liệu {i+1}] {metadata_str}\n{doc.page_content}")
                current_tokens += doc_tokens
        
        return "\n\n---\n\n".join(context_parts)
    
    def save_search_results(
        self,
        query: str,
        results: List,
        output_path: str,
        format: str = "json"
    ):
        """
        Lưu kết quả search
        
        Args:
            query: Query đã search
            results: Kết quả search
            output_path: Đường dẫn output
            format: "json" hoặc "txt"
        """
        if format == "json":
            data = {
                "query": query,
                "num_results": len(results),
                "results": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": score if isinstance(doc, tuple) else None
                    }
                    for doc, score in results if isinstance(results[0], tuple)
                ] if isinstance(results[0], tuple) else [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in results
                ]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        elif format == "txt":
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Query: {query}\n")
                f.write(f"Number of results: {len(results)}\n")
                f.write("="*80 + "\n\n")
                
                for i, item in enumerate(results):
                    if isinstance(item, tuple):
                        doc, score = item
                        f.write(f"Result {i+1} (Score: {score:.4f})\n")
                    else:
                        doc = item
                        f.write(f"Result {i+1}\n")
                    
                    f.write(f"Page: {doc.metadata.get('page', 'N/A')}\n")
                    f.write(f"Type: {doc.metadata.get('type', 'N/A')}\n")
                    f.write(f"Content:\n{doc.page_content}\n")
                    f.write("-"*80 + "\n\n")


# Các helper functions để sử dụng nhanh
def quick_search(index_path: str, query: str, k: int = 4):
    """Quick search function"""
    searcher = FaissSearcher(index_path)
    results = searcher.search_with_score(query, k=k)
    
    for doc, score in results:
        print(f"Score: {score:.4f}")
        print(f"Page: {doc.metadata.get('page', 'N/A')}")
        print(f"Content: {doc.page_content[:200]}...")
        print("-" * 50)
    
    return results


def create_qa_chain(index_path: str, llm_model: Optional[str] = None):
    """
    Tạo QA chain với Faiss retriever
    
    Args:
        index_path: Path đến faiss index
        llm_model: Model name cho HuggingFace (optional)
    
    Returns:
        RetrievalQA chain
    """
    from langchain.chains import RetrievalQA
    from langchain.llms import HuggingFacePipeline
    from transformers import pipeline
    
    # Load vector store
    searcher = FaissSearcher(index_path)
    
    # Create retriever
    retriever = searcher.vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 8}
    )
    
    # Create LLM (sử dụng model nhỏ cho tiết kiệm)
    if llm_model is None:
        llm_model = "google/flan-t5-base"  # Model nhỏ, free
    
    pipe = pipeline(
        "text2text-generation",
        model=llm_model,
        max_length=512,
        temperature=0.7
    )
    llm = HuggingFacePipeline(pipeline=pipe)
    
    # Create QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    return qa_chain


# Example usage
if __name__ == "__main__":
    # # 1. Load và search cơ bản
    searcher = FaissSearcher(r"E:\PROJECT_GITHUB\Build-a-website-with-integrated-AI-Chatbot-technology-to-ask-and-answer-questions-about-the-school\VectorDB")

    # 4. Hybrid search
    user = input("Bạn hãy nhập thông tin    ")
    hybrid_results = searcher.hybrid_search(user, k=5)
    
    print(hybrid_results)
    # # 5. Get context cho LLM
    # context = searcher.get_relevant_context("câu hỏi", k=4, max_tokens=2000)
    # print(f"Context for LLM:\n{context}")
    
    # 6. Save results
    # searcher.save_search_results(
    #     "test query",
    #     results,
    #     "./search_results.json",
    #     format="json"
    # )