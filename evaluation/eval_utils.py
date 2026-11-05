"""
Module: eval_utils.py
Mục đích: Module tiện ích dùng chung (Shared Utilities) cho Phân hệ 4 (Evaluation & Testing).
Chức năng:
  1. Regex trích xuất căn cứ pháp lý quy chuẩn Việt Nam (Nghị định, Luật, Thông tư, Quy chuẩn, Điều khoản).
  2. Thuật toán hợp nhất xếp hạng RRF (Reciprocal Rank Fusion) chuẩn khoa học.
  3. Thuật toán chấm điểm mức độ liên quan văn bản theo truy vấn (Query-Document Semantic Matcher)
     phục vụ Re-ranking không rò rỉ dữ liệu (No Data Leakage).
Người phụ trách: Thành viên 4 (Evaluation Lead)
"""

import re
from typing import List, Dict, Any, Optional, Set


# =====================================================================
# 1. BIỂU THỨC CHÍNH QUY (REGEX) BÓC TÁCH CĂN CỨ PHÁP LÝ VIỆT NAM
# =====================================================================

def extract_legal_citations(text: str) -> List[str]:
    """
    Bóc tách toàn bộ danh xưng văn bản pháp luật và điều khoản xuất hiện trong chuỗi.
    Dùng chung cho BenchmarkRunner, RagasEvaluator và CitationAuditor.

    Args:
        text (str): Đoạn văn bản chứa câu hỏi, câu trả lời hoặc căn cứ luật.

    Returns:
        List[str]: Danh sách các căn cứ pháp lý chuẩn hóa (ví dụ: ["Điều 6", "Nghị định 168/2024/NĐ-CP"]).
    """
    if not text or not isinstance(text, str):
        return []

    citations: Set[str] = set()

    # 1. Nghị định (VD: "Nghị định 168/2024/NĐ-CP", "NĐ 100/2019/NĐ-CP", "Nghị định 123/2021")
    nd_matches = re.finditer(
        r'(?:nghị\s*định|nđ)\s+(?:số\s+)?(\d+/\d+/(?:nđ-cp|nd-cp)|\d+/\d+)',
        text,
        re.IGNORECASE
    )
    for m in nd_matches:
        raw = m.group(1).upper()
        if not raw.endswith("/NĐ-CP") and not raw.endswith("/ND-CP"):
            citations.add(f"Nghị định {raw}/NĐ-CP")
        else:
            norm = raw.replace("ND-CP", "NĐ-CP")
            citations.add(f"Nghị định {norm}")

    # 2. Thông tư (VD: "Thông tư 73/2024/TT-BCA", "TT 79/2024")
    tt_matches = re.finditer(
        r'(?:thông\s*tư|tt)\s+(?:số\s+)?(\d+/\d+/(?:tt-[a-z]+)|\d+/\d+)',
        text,
        re.IGNORECASE
    )
    for m in tt_matches:
        raw = m.group(1).upper()
        if not re.search(r'TT-[A-Z]+', raw):
            citations.add(f"Thông tư {raw}/TT-BCA")
        else:
            citations.add(f"Thông tư {raw}")

    # 3. Luật giao thông & đường bộ
    text_lower = text.lower()
    if re.search(r'luật\s+trật\s+tự[,\s]+an\s+toàn\s+giao\s+thông|luật\s+36/2024|luật\s+ttatgt', text_lower):
        citations.add("Luật Trật tự, an toàn giao thông đường bộ")
    if re.search(r'luật\s+đường\s+bộ|luật\s+35/2024', text_lower):
        citations.add("Luật Đường bộ")
    if re.search(r'luật\s+giao\s+thông\s+đường\s+bộ\s+2008|luật\s+23/2008', text_lower):
        citations.add("Luật Giao thông đường bộ 2008")
    if re.search(r'luật\s+xử\s+lý\s+vi\s+phạm\s+hành\s+chính|luật\s+15/2012', text_lower):
        citations.add("Luật Xử lý vi phạm hành chính")

    # 4. Quy chuẩn kỹ thuật (VD: "QCVN 41:2019/BGTVT")
    if re.search(r'qcvn\s*41', text_lower):
        citations.add("Quy chuẩn QCVN 41:2019/BGTVT")

    # 5. Điều luật (VD: "Điều 5", "Điều 6", "Điều 67")
    dieu_matches = re.finditer(r'\bđiều\s+(\d+)\b', text, re.IGNORECASE)
    for m in dieu_matches:
        citations.add(f"Điều {m.group(1)}")

    return sorted(list(citations))


# =====================================================================
# 2. THUẬT TOÁN HỢP NHẤT XẾP HẠNG RRF (RECIPROCAL RANK FUSION)
# =====================================================================

def reciprocal_rank_fusion(
    ranked_lists: List[List[Dict[str, Any]]],
    k: int = 60,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Thuật toán chuẩn RRF (Reciprocal Rank Fusion) kết hợp kết quả từ nhiều bộ tìm kiếm
    (ví dụ: Lexical BM25 và Dense Vector) mà không làm rò rỉ nhãn Ground Truth.

    Score(d) = SUM_m [ 1 / (k + rank_m(d)) ]

    Args:
        ranked_lists: Danh sách các bảng xếp hạng (mỗi bảng là list các doc dict).
        k: Hằng số làm mịn rank (mặc định 60 theo chuẩn Cormack et al.).
        top_k: Số lượng tài liệu lấy ra sau khi hợp nhất.

    Returns:
        List[Dict[str, Any]]: Danh sách tài liệu được xếp hạng lại theo RRF score.
    """
    scores: Dict[str, float] = {}
    doc_map: Dict[str, Dict[str, Any]] = {}

    for r_list in ranked_lists:
        for rank, doc in enumerate(r_list, start=1):
            doc_id = doc.get("title", "") + "::" + doc.get("snippet", "")[:60]
            if doc_id not in doc_map:
                doc_map[doc_id] = dict(doc)
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank))

    # Sắp xếp giảm dần theo điểm số RRF tổng hợp
    sorted_doc_ids = sorted(scores.keys(), key=lambda did: scores[did], reverse=True)

    fused_docs = []
    for did in sorted_doc_ids[:top_k]:
        d = dict(doc_map[did])
        d["rrf_score"] = round(scores[did], 6)
        fused_docs.append(d)

    return fused_docs


# =====================================================================
# 3. THUẬT TOÁN CHẤM ĐIỂM LIÊN QUAN TRUY VẤN - TÀI LIỆU (RE-RANKER)
# =====================================================================

def compute_query_document_relevance(query: str, doc_title: str, doc_snippet: str) -> float:
    """
    Chấm điểm độ liên quan ngữ nghĩa và ngữ cảnh giữa câu hỏi (Query) và tài liệu (Document)
    dựa hoàn toàn trên nội dung text, TUYỆT ĐỐI KHÔNG SỬ DỤNG GROUND TRUTH.

    Tiêu chí chấm điểm:
      1. Khớp thực thể phương tiện (ô tô, xe máy, xe tải, xe đạp điện...).
      2. Khớp cụm từ hành vi vi phạm (vượt đèn đỏ, nồng độ cồn, quá tốc độ, đi ngược chiều...).
      3. Khớp từ khóa chế tài (phạt tiền, tước bằng, trừ điểm, tạm giữ).
      4. Mật độ trùng lặp từ khóa n-gram và BM25 term overlap.

    Returns:
        float: Điểm liên quan [0.0 -> 10.0].
    """
    if not query:
        return 0.0

    q_lower = query.lower()
    content = f"{doc_title} {doc_snippet}".lower()
    score = 0.0

    # 1. Khớp nhóm phương tiện
    vehicles = [
        "xe máy", "mô tô", "ô tô", "xe tải", "xe buýt", "xe khách",
        "xe đạp điện", "xe máy điện", "máy kéo", "xe chuyên dùng"
    ]
    for v in vehicles:
        if v in q_lower and v in content:
            score += 2.5

    # 2. Khớp hành vi vi phạm cốt lõi
    actions = [
        ("đèn đỏ", "tín hiệu đèn"),
        ("nồng độ cồn", "rượu bia"),
        ("tốc độ", "chạy quá"),
        ("ngược chiều", "đi ngược"),
        ("làn đường", "sai làn"),
        ("giấy phép", "gplx"),
        ("không đội mũ", "mũ bảo hiểm"),
        ("điện thoại", "thiết bị âm thanh"),
        ("trừ điểm", "điểm gplx"),
        ("chuyển hướng", "xi nhan")
    ]
    for kw_tuple in actions:
        if any(kw in q_lower for kw in kw_tuple) and any(kw in content for kw in kw_tuple):
            score += 3.0

    # 3. Mật độ từ khóa chung (Token Overlap)
    q_words = set(re.findall(r'\b[a-zA-Z0-9à-ỹÀ-Ỹ_]+\b', q_lower))
    # Bỏ các stop-words tiếng Việt cơ bản
    stopwords = {"là", "gì", "như", "thế", "nào", "bao", "nhiêu", "tiền", "khi", "bị", "có", "không", "thì", "được", "người", "xe"}
    meaningful_q_words = q_words - stopwords

    if meaningful_q_words:
        matched_words = sum(1 for w in meaningful_q_words if w in content)
        overlap_ratio = matched_words / len(meaningful_q_words)
        score += overlap_ratio * 4.0

    # 4. Điểm thưởng nếu tiêu đề tài liệu chứa trực tiếp điều khoản quy chuẩn
    if "điều" in doc_title.lower() or "nghị định" in doc_title.lower():
        score += 0.5

    return round(score, 4)

