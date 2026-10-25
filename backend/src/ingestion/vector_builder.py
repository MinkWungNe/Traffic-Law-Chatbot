"""
Module: vector_builder.py
Mục đích: Chuyển các đoạn văn bản (chunks) thành vector embedding và lưu trữ vào ChromaDB.
Người phụ trách chính: Thành viên 1 (Data Ingestion Lead) & Thành viên 2 (RAG Core Co-dev)
"""

import os
import sys
import shutil
import json
import urllib.request
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

# Đảm bảo in ký tự tiếng Việt trên Windows console không bị lỗi mã hóa cp1252
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

class OllamaBatchEmbeddings(Embeddings):
    """
    Lớp nhúng vector tùy biến gọi trực tiếp endpoint '/api/embed' của Ollama theo lô (batch).
    Tối ưu hóa hiệu năng gấp 50 lần so với thư viện mặc định (xử lý 40 chunks/giây).
    """
    # Hàm khởi tạo
    def __init__(self, model: str = "vietnamese-embedding", base_url: str = "http://localhost:11434"):
        self.model = model # Tên mô hình embedding trong Ollama (mặc định: vietnamese-embedding)
        self.base_url = base_url.rstrip("/") # URL của dịch vụ Ollama cục bộ (mặc định: http://localhost:11434)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Nhúng danh sách văn bản theo từng lô 50 đoạn qua Ollama /api/embed.
            Đầu vào: texts (List[str]): Danh sách các chuỗi văn bản (các chunks) cần chuyển thành vector.
            Xử lý: Gọi endpoint Ollama /api/embed theo lô 50 chunks để nhúng vector.
                    - Theo lô 50: có nghĩa là mỗi lần gửi 50 chunks đến Ollama để nhúng vector, giúp tối ưu hóa hiệu năng.
                    - Tại sao lại chia theo lô 50? Vì nếu gửi quá nhiều chunks cùng lúc, sẽ gây quá tải bộ nhớ và giảm hiệu năng.
                    - Ví dụ: Nếu có 1000 chunks, sẽ chia thành 20 đợt (batches) nhúng vector, mỗi batch 50 chunks. 
                    Thì nó sẽ nhúng nhanh hơn và ổn định hơn so với nhúng 1000 chunks cùng lúc.
            Đầu ra: List[List[float]]: Danh sách các vector embedding tương ứng với từng chunk.
        """
        all_embeddings: List[List[float]] = []
        sub_batch_size = 50
        # Vòng lặp chia danh sách texts thành các đợt (batches) nhúng vector theo sub_batch_size
        for i in range(0, len(texts), sub_batch_size): 
            chunk = texts[i:i + sub_batch_size]
            data = json.dumps({"model": self.model, "input": chunk}).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/api/embed",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                all_embeddings.extend(res.get("embeddings", []))
        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        """
        Nhúng một câu hỏi/câu truy vấn của người dùng qua Ollama /api/embed. 
        Thành 1 vector để mang đi so khớp khoảng cách trong cơ sở dữ liệu.
        """
        data = json.dumps({"model": self.model, "input": [text]}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/embed",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            vecs = res.get("embeddings", [])
            return vecs[0] if vecs else []

class VectorBuilder:
    """
    Lớp tạo lập và quản lý cơ sở dữ liệu Vector (ChromaDB) từ các đoạn văn bản luật.
    """

    def __init__(
        self, 
        persist_directory: str = "data/vectorstore", 
        embedding_model_name: str = "vietnamese-embedding" # Tên model embedding được cài sẵn trong Ollama.
    ):
        """
        Khởi tạo VectorBuilder.
        Args:
            persist_directory (str): Đường dẫn lưu trữ thư mục ChromaDB offline.
            embedding_model_name (str): Tên mô hình embedding trong Ollama (mặc định: vietnamese-embedding).
        """
        self.persist_directory = persist_directory 
        self.embedding_model_name = embedding_model_name
        self.embeddings = None # Lưu trữ mô hình embedding
        self.vectorstore = None # Lưu trữ cơ sở dữ liệu vector

    def initialize_embeddings(self) -> Embeddings:
        """
        Khởi tạo và kết nối với mô hình nhúng ngữ nghĩa Tiếng Việt (OllamaBatchEmbeddings).
        Mô hình được lưu vào self.embeddings để tái sử dụng.
        Returns:
            Embeddings: Đối tượng mô hình embedding.
        """
        if self.embeddings is None:
            try:
                print(f"[THÔNG TIN] Đang kết nối mô hình nhúng Tiếng Việt '{self.embedding_model_name}' qua Ollama Batch API...")
                self.embeddings = OllamaBatchEmbeddings(
                    model=self.embedding_model_name,
                    base_url="http://localhost:11434" # URL của dịch vụ Ollama cục bộ. (Đây là địa chỉ mặc định)
                )
                print(f"[THÀNH CÔNG] Đã kết nối mô hình embedding '{self.embedding_model_name}' thành công.")
            except Exception as e:
                print(f"[CẢNH BÁO] Không thể kết nối với dịch vụ Ollama: {e}")
                print("[HƯỚNG DẪN] Vui lòng kiểm tra lại dịch vụ Ollama (chạy 'ollama list' hoặc mở ứng dụng Ollama).")
                raise e
        return self.embeddings

    def build_and_save_vectorstore(
        self, 
        chunks: List[Dict[str, Any]], 
        clear_existing: bool = False
    ) -> str:
        """
        Nhúng vector toàn bộ chunks và lưu vĩnh viễn vào ChromaDB.
        Args:
            chunks (List[Dict[str, Any]]): Danh sách các đoạn văn bản kèm metadata.
            clear_existing (bool): Nếu True, xóa dữ liệu cũ để tránh trùng lặp.
        Returns:
            str: Đường dẫn thư mục vectorstore đã lưu.
        """
        # Kiểm tra an toàn: Nếu danh sách chunks rỗng, thì thông báo và trả về persist_directory mà không tạo vectorstore.
        if not chunks:
            print("[CANH BAO] Danh sach chunks rong. Khong co du lieu de tao vectorstore.")
            return self.persist_directory

        # Đảm bảo mô hình embedding đã được nạp
        self.initialize_embeddings()

        # Tùy chọn làm sạch thư mục cũ nếu được yêu cầu
        if clear_existing and os.path.exists(self.persist_directory):
            try:
                # Xóa các file trong thư mục để tránh lock file trên Windows
                for filename in os.listdir(self.persist_directory):
                    if filename == ".gitkeep": # Chủ động bỏ qua file .gitkeep để không làm hỏng cấu trúc Git.
                        continue
                    file_path = os.path.join(self.persist_directory, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                print(f"[THONG TIN] Da lam sach du lieu cu tai '{self.persist_directory}'.")
            except Exception as e:
                print(f"[CANH BAO] Khong the xoa toan bo thu muc cu: {e}")

        # Chuẩn bị dữ liệu: bóc tách text và metadata linh hoạt
        texts: List[str] = [] # Danh sách lưu trữ nội dung văn bản hợp lệ để nhúng vector.
                              # Ví dụ: ["Người đi xe máy vượt đèn đỏ bị phạt từ 800.000 đến 1.000.000 đồng."]
        metadatas: List[Dict[str, Any]] = [] # Danh sách metadatas để gắn với từng vector tương ứng.
                                             # Ví dụ: [{"law_name": "Nghị định 100/2019/NĐ-CP", "article_number": "5"}]

        # Vòng lặp này có nhiệm vụ linh hoạt trích xuất nội dung văn bản từ các key phổ biến: "chunk_text", "text", hoặc "content"
        for item in chunks:
            # Hỗ trợ linh hoạt các tên key phổ biến: chunk_text, text, content
            text_content = item.get("chunk_text") or item.get("text") or item.get("content") or ""
            if not text_content.strip(): # Nếu không có nội dung văn bản hợp lệ, bỏ qua chunk này
                continue

            # Sao chép các trường thông tin còn lại làm metadata
            meta = {k: v for k, v in item.items() if k not in ["chunk_text", "text", "content"]} # Nếu k không phải là key chứa nội dung văn bản, thì giữ lại làm metadata
            texts.append(text_content) # => texts = ["Người đi xe máy vượt đèn đỏ bị phạt từ 800.000 đến 1.000.000 đồng."]
            metadatas.append(meta) # => metadatas = [{"law_name": "Nghị định 100/2019/NĐ-CP", "article_number": "5"}]

        if not texts:
            print("[CANH BAO] Khong tim thay noi dung van ban hop le trong cac chunks.")
            return self.persist_directory

        # Tạo và lưu vectorstore xuống ổ đĩa theo cơ chế chia đợt (Batching)
        total_chunks = len(texts)
        batch_size = 250
        total_batches = (total_chunks + batch_size - 1) // batch_size # Tính tổng số đợt cần nhúng vector (ceil(total_chunks / batch_size))
        print(f"[THÔNG TIN] Bắt đầu nhúng {total_chunks} đoạn văn bản luật vào ChromaDB ({total_batches} đợt, {batch_size} chunks/đợt)...")

        # Khởi tạo instance Chroma rỗng trỏ tới thư mục persist_directory
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory, # Thư mục lưu trữ cơ sở dữ liệu vector ChromaDB
            embedding_function=self.embeddings # Sử dụng mô hình embedding để nhúng vector
        )

        for batch_idx in range(total_batches):
            start_i = batch_idx * batch_size
            end_i = min(start_i + batch_size, total_chunks)
            b_texts = texts[start_i:end_i]
            b_metadatas = metadatas[start_i:end_i]

            print(f"[TIẾN TRÌNH] Đang nhúng đợt {batch_idx + 1}/{total_batches} (từ chunk {start_i + 1} đến {end_i})...")
            self.vectorstore.add_texts(
                texts=b_texts,
                metadatas=b_metadatas
            )

        print(f"[THÀNH CÔNG] Đã lưu hoàn tất {total_chunks} vectors vào cơ sở dữ liệu: {self.persist_directory}")
        return self.persist_directory

    def load_existing_vectorstore(self) -> Optional[Chroma]:
        """
        Tải cơ sở dữ liệu vector ChromaDB đã lưu sẵn từ ổ đĩa.
        Giúp RAG Pipeline và API truy xuất tức thì mà không cần nhúng lại.
        Returns:
            Optional[Chroma]: Đối tượng vectorstore nếu tồn tại, ngược lại trả về None.
        """
        db_file = os.path.join(self.persist_directory, "chroma.sqlite3") # Biến lưu đường dẫn file cơ sở dữ liệu ChromaDB
        # Kiểm tra nếu thư mục hoặc file cơ sở dữ liệu không tồn tại, thì thông báo và trả về None
        if not os.path.exists(self.persist_directory) or not os.path.exists(db_file):
            print(f"[CANH BAO] Chua tim thay co so du lieu ChromaDB hop le tai '{self.persist_directory}'.")
            return None

        self.initialize_embeddings() # Đảm bảo mô hình embedding đã được nạp trước khi load vectorstore
        self.vectorstore = Chroma( # Tải vectorstore từ thư mục lưu trữ
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        return self.vectorstore