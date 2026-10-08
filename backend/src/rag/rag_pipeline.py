"""
Module: rag_pipeline.py
Mục đích: Khởi tạo luồng RAG hoàn chỉnh kết hợp Retriever (ChromaDB) + Prompt + LLM Engine.
Người phụ trách chính: Thành viên 2 (RAG Core Lead) & Thành viên 3 (API Co-dev)
"""

from typing import Dict, Any, List
from .llm_engine import LLMEngine
from .prompt_templates import get_rag_prompt_template

class LegalRAGPipeline:
    """
    Lớp điều phối toàn bộ chuỗi hỏi đáp RAG tư vấn pháp luật giao thông.
    """

    def __init__(self, vectorstore_dir: str = "data/vectorstore", model_path: str = "models/vinallama-7b-chat.Q4_K_M.gguf"):
        """
        Khởi tạo Pipeline RAG.
        Args:
            vectorstore_dir (str): Thư mục chứa cơ sở dữ liệu vector ChromaDB.
            model_path (str): Đường dẫn file mô hình LLM.
        """
        self.vectorstore_dir = vectorstore_dir
        self.llm_engine = LLMEngine(model_path=model_path)
        self.vectorstore = None

    def initialize_pipeline(self):
        """
        Khởi tạo kết nối Vectorstore và tải LLM.
        """
        # TODO [Cơ bản]: Kết nối ChromaDB qua langchain_chroma
        # TODO [Cơ bản]: Gọi self.llm_engine.load_model()
        pass

    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Truy xuất Top-K đoạn văn bản luật liên quan nhất từ ChromaDB.
        Args:
            query (str): Câu hỏi của người dùng.
            top_k (int): Số lượng đoạn trích xuất.
        Returns:
            List[Dict[str, Any]]: Danh sách tài liệu liên quan kèm độ tương đồng và metadata.
        """
        # TODO [Cơ bản]: Gọi self.vectorstore.similarity_search_with_score(query, k=top_k)
        # Mock dữ liệu mẫu trả về để test giao tiếp:
        return [
            {
                "title": "Nghị định 100/2019/NĐ-CP (sửa đổi bởi NĐ 123/2021/NĐ-CP)",
                "snippet": "Quy định xử phạt vi phạm hành chính trong lĩnh vực giao thông đường bộ.",
                "score": 0.89
            }
        ]

    def answer_question(self, query: str, top_k: int = 3, temperature: float = 0.2) -> Dict[str, Any]:
        """
        Thực hiện toàn bộ quy trình RAG: Tìm tài liệu -> Ghép prompt -> Sinh câu trả lời.
        Args:
            query (str): Câu hỏi người dùng.
            top_k (int): Số đoạn tài liệu tham khảo.
            temperature (float): Độ sáng tạo.
        Returns:
            Dict[str, Any]: Kết quả gồm 'answer', 'sources', 'query'.
        """
        sources = self.retrieve_context(query, top_k=top_k)
        
        # Ghép ngữ cảnh
        context_text = "\n\n".join([f"[{s['title']}]: {s['snippet']}" for s in sources])
        prompt_template = get_rag_prompt_template()
        full_prompt = prompt_template.format(context=context_text, question=query)

        # Sinh câu trả lời từ LLM (hoặc mock nếu chưa nạp LLM)
        answer = self.llm_engine.generate(full_prompt)
        if not answer:
            answer = f"Theo quy định hiện hành đối với hành vi trong câu hỏi '{query}', bạn cần tuân thủ các chỉ dẫn của cơ quan chức năng và quy chuẩn báo hiệu đường bộ."

        return {
            "query": query,
            "answer": answer,
            "sources": sources
        }
