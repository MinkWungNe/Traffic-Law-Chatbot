"""
Module: hybrid_retriever.py
Mục đích: Tìm kiếm lai kết hợp Dense Vector (ChromaDB) + Sparse Lexical (BM25) và Weighted RRF.
Nhóm phụ trách: Nhóm 2 - Hybrid Retrieval & Re-ranking
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from rank_bm25 import BM25Okapi

logger = logging.getLogger("rag.hybrid_retriever")

class HybridRetriever:
    """
    Bộ truy xuất lai kết hợp Dense Semantic Search và BM25 Lexical Search.
    Áp dụng Weighted Reciprocal Rank Fusion (RRF) và Tái xếp hạng theo Phương tiện.
    """

    def __init__(
        self,
        vectorstore: Any,
        chunks_path: Optional[str] = None
    ):
        """
        Khởi tạo HybridRetriever.
        Args:
            vectorstore: Thể hiện ChromaDB vectorstore đã được khởi tạo.
            chunks_path: Đường dẫn tới file legal_chunks.json để xây dựng chỉ mục BM25.
        """
        self.vectorstore = vectorstore
        self.chunks_path = self._discover_chunks_path(chunks_path)
        self.bm25: Optional[BM25Okapi] = None
        self.corpus_chunks: List[Dict[str, Any]] = []
        self.penalty_points_map: Dict[str, Dict[str, Any]] = {}
        self._init_bm25_index()

    def _discover_chunks_path(self, given_path: Optional[str]) -> str:
        if given_path and os.path.exists(given_path):
            return given_path

        candidates = [
            os.path.join("data", "processed", "legal_chunks.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "processed", "legal_chunks.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "legal_chunks.json"),
        ]
        for path in candidates:
            norm_path = os.path.normpath(path)
            if os.path.exists(norm_path):
                return norm_path
        raise FileNotFoundError("Không tìm thấy file 'legal_chunks.json' để xây dựng chỉ mục BM25!")

    def _tokenize(self, text: str) -> List[str]:
        """Tách từ đơn giản cho tiếng Việt dựa trên ký tự từ vựng."""
        text = text.lower()
        tokens = re.findall(r"\w+", text)
        return tokens

    def _init_bm25_index(self):
        """Khởi tạo chỉ mục BM25 từ file legal_chunks.json."""
        try:
            with open(self.chunks_path, "r", encoding="utf-8") as f:
                self.corpus_chunks = json.load(f)

            tokenized_corpus = [
                self._tokenize(chunk.get("chunk_text", "") + " " + chunk.get("law_name", "") + " " + chunk.get("article_title", ""))
                for chunk in self.corpus_chunks
            ]
            self.bm25 = BM25Okapi(tokenized_corpus)
            logger.info(f"Đã xây dựng BM25 index thành công cho {len(self.corpus_chunks)} chunks.")

            # Lập bản đồ tra cứu nhanh chunk trừ điểm GPLX theo số Điều (Nghị định 168)
            for chunk in self.corpus_chunks:
                txt = chunk.get("chunk_text", "").lower()
                law = chunk.get("law_name", "")
                art = str(chunk.get("article_number") or "").strip()
                if "168" in law and "trừ điểm giấy phép lái xe như sau" in txt and art:
                    self.penalty_points_map[art] = chunk
        except Exception as e:
            logger.error(f"Lỗi khởi tạo BM25 index: {e}")
            self.bm25 = None

    def _normalize_distance_to_similarity(self, distance: float) -> float:
        """
        Chuẩn hóa khoảng cách L2 Squared về điểm tương đồng [0.0, 1.0].
        Khoảng cách càng nhỏ (gần 0), điểm tương đồng càng gần 1.0.
        """
        d = max(0.0, float(distance))
        return 1.0 / (1.0 + d)

    def retrieve(
        self,
        query_info: Dict[str, Any],
        top_k: int = 4,
        dense_candidates: int = 20,
        bm25_candidates: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Thực hiện tìm kiếm lai:
        1. Dense Search qua ChromaDB (dùng query_original).
        2. Sparse Search qua BM25 (dùng query_expanded).
        3. Kết hợp bằng Weighted RRF.
        4. Dynamic Metadata Re-ranking theo detected_vehicle và age intent.
        5. Trả về Top-K với trường 'score' là điểm tương đồng [0.0, 1.0].
        """
        query_original = query_info.get("query_original", "")
        query_expanded = query_info.get("query_expanded", query_original)
        detected_vehicle = query_info.get("detected_vehicle")
        is_age_query = query_info.get("is_age_query", False)

        dense_map: Dict[str, Dict[str, Any]] = {}
        bm25_map: Dict[str, Dict[str, Any]] = {}

        # 1. Luồng Dense Vector Search (ChromaDB)
        if self.vectorstore is not None:
            try:
                dense_results = self.vectorstore.similarity_search_with_score(query_original, k=dense_candidates)
                for rank, (doc, dist) in enumerate(dense_results, start=1):
                    text_key = doc.page_content.strip()
                    sim_score = self._normalize_distance_to_similarity(dist)
                    
                    law_name = doc.metadata.get("law_name") or "Văn bản pháp luật"
                    article_number = str(doc.metadata.get("article_number") or "")
                    article_title = str(doc.metadata.get("article_title") or "")
                    title = f"{law_name} (Điều {article_number})" if article_number and not article_number.lower().startswith("điều") else (f"{law_name} ({article_number})" if article_number else law_name)

                    dense_map[text_key] = {
                        "rank": rank,
                        "doc": doc,
                        "title": title,
                        "snippet": doc.page_content,
                        "distance": dist,
                        "similarity_score": sim_score,
                        "article_number": article_number,
                        "article_title": article_title,
                        "law_name": law_name
                    }
            except Exception as e:
                logger.warning(f"Lỗi truy vấn Dense ChromaDB: {e}")

        # 2. Luồng Sparse BM25 Search
        if self.bm25 is not None and self.corpus_chunks:
            try:
                tokenized_q = self._tokenize(query_expanded)
                bm25_scores = self.bm25.get_scores(tokenized_q)
                
                top_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:bm25_candidates]
                for rank, idx in enumerate(top_indices, start=1):
                    score_val = float(bm25_scores[idx])
                    if score_val <= 5.0:
                        continue
                    chunk = self.corpus_chunks[idx]
                    text_key = chunk.get("chunk_text", "").strip()
                    law_name = chunk.get("law_name") or "Văn bản pháp luật"
                    article_number = str(chunk.get("article_number") or "")
                    article_title = str(chunk.get("article_title") or "")
                    title = f"{law_name} (Điều {article_number})" if article_number and not article_number.lower().startswith("điều") else (f"{law_name} ({article_number})" if article_number else law_name)

                    bm25_map[text_key] = {
                        "rank": rank,
                        "title": title,
                        "snippet": chunk.get("chunk_text", ""),
                        "bm25_score": score_val,
                        "article_number": article_number,
                        "article_title": article_title,
                        "law_name": law_name
                    }
            except Exception as e:
                logger.warning(f"Lỗi truy vấn BM25: {e}")

        # 3. Thuật toán Weighted Reciprocal Rank Fusion (RRF)
        all_keys = set(dense_map.keys()).union(set(bm25_map.keys()))
        candidates: List[Dict[str, Any]] = []

        for key in all_keys:
            d_info = dense_map.get(key)
            b_info = bm25_map.get(key)

            r_dense = d_info["rank"] if d_info else 100
            r_bm25 = b_info["rank"] if b_info else 100

            # Hiệu chuẩn RRF: Nếu Dense quá yếu (< 0.48) và không có từ khóa hỗ trợ, hạ thứ hạng Dense
            eff_r_dense = r_dense
            if d_info and d_info["similarity_score"] < 0.48 and not b_info:
                eff_r_dense = r_dense + 50

            # Nếu BM25 có độ khớp từ khóa rất cao (> 40.0), tăng trọng số BM25
            bm25_weight = 0.35
            if b_info and b_info.get("bm25_score", 0.0) > 40.0:
                bm25_weight = 0.55

            # Công thức Weighted RRF cải tiến
            score_rrf = (0.65 / (60.0 + eff_r_dense)) + (bm25_weight / (60.0 + r_bm25))

            info = d_info if d_info else b_info
            snippet = info["snippet"]
            title = info["title"]
            article_number = info["article_number"]
            article_title = info["article_title"]
            law_name = info["law_name"]

            # Điểm tương đồng phục vụ so ngưỡng và hiển thị Frontend
            if d_info:
                sim_score = d_info["similarity_score"]
                if b_info and b_info["bm25_score"] > 25.0:
                    sim_score = min(0.95, sim_score + 0.05)
            else:
                raw_bm25 = b_info.get("bm25_score", 0.0)
                sim_score = min(0.85, max(0.05, raw_bm25 / 55.0))

            # 4. Tái xếp hạng thông minh (Dynamic Re-ranking)
            snippet_lower = snippet.lower()
            title_lower = (article_title + " " + title).lower()

            # A. Re-ranking theo Phương tiện
            if detected_vehicle == "mo_to_xe_may":
                # Chỉ phạt khi tiêu đề hoặc nội dung thuần túy về xe máy chuyên dùng (không áp dụng cho điều khoản chung như Điều 59)
                is_pure_cmv = ("xe máy chuyên dùng" in title_lower) or ("xe máy chuyên dùng" in snippet_lower and "xe gắn máy" not in snippet_lower and "xe mô tô" not in snippet_lower)
                if is_pure_cmv:
                    score_rrf *= 0.35
                if any(k in snippet_lower or k in title_lower for k in ["xe mô tô", "xe gắn máy", "mô tô"]):
                    score_rrf *= 1.40
                # Phạt các văn bản không thuộc phạm vi xử phạt giao thông đường bộ thông thường
                if any(k in title_lower for k in ["an ninh, trật tự", "đường sắt", "vũ khí", "chế tạo, tàng trữ"]):
                    score_rrf *= 0.25

            elif detected_vehicle == "o_to":
                if any(k in snippet_lower or k in title_lower for k in ["xe ô tô", "ô tô"]):
                    score_rrf *= 1.25
                elif "xe mô tô" in snippet_lower and "xe ô tô" not in snippet_lower:
                    score_rrf *= 0.60

            elif detected_vehicle == "xe_may_chuyen_dung":
                if "xe máy chuyên dùng" in snippet_lower or "xe máy chuyên dùng" in title_lower:
                    score_rrf *= 1.45

            elif detected_vehicle == "xe_tho_so":
                # Thưởng mạnh Điều 9 hoặc các chunk về xe đạp, xe thô sơ
                if any(k in snippet_lower or k in title_lower for k in ["xe đạp", "xe đạp máy", "xe thô sơ"]):
                    score_rrf *= 1.50
                # Phạt nặng ô tô và mô tô
                if "xe ô tô" in snippet_lower and "xe đạp" not in snippet_lower:
                    score_rrf *= 0.35
                if "xe mô tô" in snippet_lower and "xe đạp" not in snippet_lower:
                    score_rrf *= 0.40

            elif detected_vehicle == "nguoi_di_bo":
                if "người đi bộ" in snippet_lower or "người đi bộ" in title_lower:
                    score_rrf *= 1.55
                if "xe ô tô" in snippet_lower or "xe mô tô" in snippet_lower:
                    score_rrf *= 0.40

            # B. Re-ranking cho câu hỏi Độ tuổi lái xe (Age Intent)
            if is_age_query:
                if any(k in snippet_lower or k in title_lower for k in [
                    "tuổi của người lái xe", 
                    "tuổi, sức khỏe của người điều khiển", 
                    "độ tuổi của người lái xe",
                    "người đủ 16 tuổi",
                    "người đủ 18 tuổi"
                ]):
                    score_rrf *= 2.20
                # Hạ điểm các chunk chỉ nói về quy định chuyển tiếp hoặc GPLX đơn thuần
                if "chuyển tiếp" in title_lower or "chuyển tiếp" in snippet_lower:
                    score_rrf *= 0.40

            candidates.append({
                "title": title,
                "snippet": snippet,
                "score": round(float(sim_score), 4),
                "score_rrf": score_rrf,
                "article": article_number
            })

        # Sắp xếp các ứng viên theo Score_RRF giảm dần
        candidates.sort(key=lambda x: x["score_rrf"], reverse=True)

        # C. Tự động liên kết Khoản trừ điểm GPLX nếu câu hỏi quan tâm đến trừ điểm / bằng lái
        is_points_query = any(k in query_original.lower() for k in ["trừ điểm", "bằng lái", "gplx", "bị trừ", "tước bằng", "tước gplx"])
        if is_points_query and candidates:
            top_article = str(candidates[0].get("article") or "").strip()
            if top_article and top_article in self.penalty_points_map:
                penalty_chunk = self.penalty_points_map[top_article]
                p_text = penalty_chunk.get("chunk_text", "").strip()
                # Kiểm tra xem chunk trừ điểm này đã có trong candidates[:top_k] chưa
                already_in_top = any(c.get("snippet", "").strip() == p_text for c in candidates[:top_k])
                if not already_in_top:
                    law_name = penalty_chunk.get("law_name") or "Văn bản pháp luật"
                    p_title = f"{law_name} (Điều {top_article})"
                    penalty_candidate = {
                        "title": p_title,
                        "snippet": p_text,
                        "score": candidates[0].get("score", 0.55),
                        "score_rrf": candidates[0].get("score_rrf", 0.01) * 0.99,
                        "article": top_article
                    }
                    candidates.insert(1, penalty_candidate)

        return candidates[:top_k]
