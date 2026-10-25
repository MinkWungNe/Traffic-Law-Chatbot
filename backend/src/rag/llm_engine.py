"""
Module: llm_engine.py
Mục đích: Khởi tạo và quản lý mô hình ngôn ngữ lớn cục bộ (VinaLlama .gguf) qua LlamaCpp / Transformers.
Người phụ trách chính: Thành viên 2 (RAG Core Lead)
"""

import os
import sys
from typing import Optional, Any
from langchain_community.llms import Ollama

# Đảm bảo in ký tự tiếng Việt trên Windows console không bị lỗi mã hóa cp1252
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

class LLMEngine:
    """
    Lớp quản lý việc tải mô hình và thực thi suy luận (inference) từ mô hình ngôn ngữ lớn VinaLlama qua Ollama.
    """

    def __init__(
        self, 
        model_name: str = "vinallama-traffic-law", # Tên mô hình mặc định trong Ollama (có thể thay đổi nếu cần).
        base_url: str = "http://localhost:11434", # URL mặc định của dịch vụ Ollama cục bộ
        temperature: float = 0.2
    ):
        """
        Khởi tạo LLMEngine.
        Args:
            model_name (str): Tên mô hình trong Ollama (mặc định: vinallama-traffic-law).
            base_url (str): Địa chỉ dịch vụ Ollama cục bộ.
            temperature (float): Độ sáng tạo sinh văn bản (mặc định thấp để chuẩn xác).
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.model: Optional[Ollama] = None # Biến lưu trữ đối tượng mô hình LLM đã nạp
        self._load_attempted: bool = False # Biến cờ đánh dấu đã thử nạp mô hình hay chưa
    
    def load_model(self) -> Optional[Ollama]:
        """
        Kết nối với mô hình LLM VinaLlama trong Ollama.
        Returns:
            Optional[Ollama]: Đối tượng mô hình nếu kết nối thành công, ngược lại trả về None.
        """
        # Nếu mô hình đã được nạp trước đó, thì tiếp tục sử dụng mà không nạp lại.
        if self.model is not None:
            return self.model

        # Nếu đã thử nạp mô hình trước đó nhưng thất bại, không thử lại để tránh lỗi lặp vô hạn.
        if self._load_attempted and self.model is None:
            return None

        self._load_attempted = True # Đánh dấu đã thử nạp mô hình.

        try:
            print(f"[THÔNG TIN] Đang kết nối mô hình VinaLlama '{self.model_name}' qua Ollama ({self.base_url})...")
            self.model = Ollama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature
            )
            print("[THÀNH CÔNG] Đã kết nối thành công mô hình VinaLlama qua Ollama.")
            return self.model
        except Exception as e:
            print(f"[CẢNH BÁO] Không thể kết nối mô hình Ollama: {e}. Sử dụng chế độ Fallback.")
            self.model = None
            return None

    def generate(self, prompt: str) -> str:
        """
        Sinh câu trả lời từ chuỗi prompt.
        Hỗ trợ 2 tầng: Suy luận AI thật qua Ollama (nếu có model) hoặc Fallback mô phỏng (nếu chưa bật Ollama).
        Args:
            prompt (str): Chuỗi prompt đã ghép đầy đủ ngữ cảnh và câu hỏi.
        Returns:
            str: Văn bản câu trả lời.
        """
        # Tự động nạp mô hình nếu chưa nạp
        if self.model is None:
            self.load_model()

        # Tầng 1: Nếu mô hình thật đã sẵn sàng, thực hiện suy luận AI
        if self.model is not None:
            try:
                response = self.model.invoke(prompt)
                return str(response).strip()
            except Exception as e:
                print(f"[CẢNH BÁO] Lỗi trong quá trình sinh từ LLM thật: {e}")

        # Tầng 2: Chế độ Fallback thông minh có cấu trúc trích dẫn chuẩn luật
        return (
            "[MÔ PHỎNG - Chưa bật Ollama hoặc chưa nạp mô hình]: "
            "Theo quy định hiện hành về trật tự an toàn giao thông đường bộ, "
            "người tham gia giao thông có nghĩa vụ chấp hành nghiêm chỉnh hiệu lệnh của đèn tín hiệu, "
            "biển báo hiệu và chỉ dẫn của lực lượng chức năng. "
            "Căn cứ Nghị định 100/2019/NĐ-CP (sửa đổi, bổ sung bởi Nghị định 123/2021/NĐ-CP), "
            "các hành vi không chấp hành tín hiệu giao thông sẽ bị xử phạt tiền và tước quyền sử dụng "
            "giấy phép lái xe theo từng khung mức cụ thể đối với từng loại phương tiện."
        )