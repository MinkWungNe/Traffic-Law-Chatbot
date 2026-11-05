"""
Module: llm_engine.py
Mục đích: Khởi tạo và quản lý mô hình ngôn ngữ lớn qua Ollama sử dụng langchain_ollama.
Nhóm phụ trách: Nhóm 5 - LLM Engine & Inference Hyperparameters
"""

import sys
import logging
from typing import Optional, Any

# Đảm bảo in ký tự tiếng Việt trên Windows console không bị lỗi mã hóa cp1252
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = logging.getLogger("rag.llm_engine")

try:
    from langchain_ollama import OllamaLLM
    HAS_LANGCHAIN_OLLAMA = True
except ImportError:
    from langchain_community.llms import Ollama as OllamaLLM
    HAS_LANGCHAIN_OLLAMA = False

class LLMEngine:
    """
    Lớp quản lý việc tải mô hình và thực thi suy luận (inference) từ mô hình ngôn ngữ lớn qua Ollama.
    """

    def __init__(
        self, 
        model_name: str = "vinallama-traffic-law",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.15,
        num_ctx: int = 4096
    ):
        """
        Khởi tạo LLMEngine.
        Args:
            model_name (str): Tên mô hình trong Ollama (mặc định: vinallama-traffic-law).
            base_url (str): Địa chỉ dịch vụ Ollama cục bộ.
            temperature (float): Độ sáng tạo sinh văn bản (mặc định 0.15 để đảm bảo tính chuẩn xác pháp lý).
            num_ctx (int): Giới hạn độ dài ngữ cảnh (4096 tokens).
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.num_ctx = num_ctx
        self.model: Optional[Any] = None
        self._load_attempted: bool = False
    
    def load_model(self) -> Optional[Any]:
        """
        Kết nối với mô hình LLM qua Ollama.
        """
        if self.model is not None:
            return self.model

        if self._load_attempted and self.model is None:
            return None

        self._load_attempted = True

        try:
            print(f"[THÔNG TIN] Đang kết nối mô hình LLM '{self.model_name}' qua Ollama ({self.base_url})...")
            self.model = OllamaLLM(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature,
                num_ctx=self.num_ctx,
                top_p=0.9,
                repeat_penalty=1.1
            )
            print(f"[THÀNH CÔNG] Đã kết nối thành công mô hình '{self.model_name}' qua OllamaLLM.")
            return self.model
        except Exception as e:
            print(f"[CẢNH BÁO] Không thể kết nối mô hình Ollama: {e}. Hệ thống sẵn sàng cho chế độ Fallback.")
            self.model = None
            return None

    def generate(self, prompt: str) -> str:
        """
        Sinh câu trả lời từ chuỗi prompt.
        Hỗ trợ 2 tầng: Suy luận AI thật qua Ollama (nếu dịch vụ Ollama bật) hoặc Fallback minh bạch.
        """
        if self.model is None and not self._load_attempted:
            self.load_model()

        if self.model is not None:
            try:
                response = self.model.invoke(prompt)
                return str(response).strip()
            except Exception as e:
                logger.warning(f"Lỗi trong quá trình sinh từ LLM thật: {e}")

        # Chế độ Fallback thông báo minh bạch khi dịch vụ Ollama chưa bật
        return (
            "⚠️ [THÔNG BÁO HỆ THỐNG - DỊCH VỤ OLLAMA CHƯA SẴN SÀNG]\n\n"
            "Hệ thống đã trích xuất thành công các căn cứ pháp lý liên quan nhất bên dưới, "
            "tuy nhiên dịch vụ suy luận mô hình AI cục bộ (Ollama) hiện chưa được bật trên máy chủ.\n\n"
            "Vui lòng tham khảo các căn cứ pháp lý nguyên văn được trích dẫn chi tiết ở phần 'Căn cứ pháp lý' bên dưới, "
            "hoặc khởi động dịch vụ Ollama (`ollama serve`) để nhận câu trả lời tổng hợp tự động."
        )
