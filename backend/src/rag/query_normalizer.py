"""
Module: query_normalizer.py
Mục đích: Tiền xử lý câu hỏi người dùng, nhận diện phương tiện và mở rộng thuật ngữ pháp lý.
Nhóm phụ trách: Nhóm 1 - Query Normalizer & Legal Synonyms
"""

import os
import json
import re
from typing import Dict, Any, List, Optional, Tuple

class QueryNormalizer:
    """
    Bộ chuẩn hóa và mở rộng câu truy vấn dựa trên từ điển pháp lý.
    Sử dụng Singleton Pattern để nạp từ điển vào RAM 1 lần duy nhất.
    """
    _instance: Optional["QueryNormalizer"] = None
    _dictionary_cache: Optional[Dict[str, Any]] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QueryNormalizer, cls).__new__(cls)
        return cls._instance

    def __init__(self, dictionary_path: Optional[str] = None):
        if self._dictionary_cache is None:
            self._dictionary_cache = self._load_dictionary(dictionary_path)

    def _discover_dictionary_path(self, given_path: Optional[str]) -> str:
        """Tự động tìm kiếm đường dẫn file legal_synonyms.json."""
        if given_path and os.path.exists(given_path):
            return given_path

        candidates = [
            os.path.join("data", "dictionaries", "legal_synonyms.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "dictionaries", "legal_synonyms.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "dictionaries", "legal_synonyms.json"),
        ]
        for path in candidates:
            norm_path = os.path.normpath(path)
            if os.path.exists(norm_path):
                return norm_path

        raise FileNotFoundError("Không tìm thấy file từ điển pháp lý 'legal_synonyms.json'!")

    def _load_dictionary(self, path: Optional[str]) -> Dict[str, Any]:
        file_path = self._discover_dictionary_path(path)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    @property
    def vehicles(self) -> Dict[str, Any]:
        return self._dictionary_cache.get("vehicles", {}) if self._dictionary_cache else {}

    @property
    def violations(self) -> Dict[str, Any]:
        return self._dictionary_cache.get("violations", {}) if self._dictionary_cache else {}

    def normalize_and_expand(self, query: str) -> Dict[str, Any]:
        """
        Phân tích và mở rộng câu truy vấn:
        - Bắt loại phương tiện với cơ chế Longest-Match First.
        - Bắt hành vi vi phạm.
        - Nhận diện ý định hỏi về độ tuổi lái xe (Age Intent).
        - Tạo câu truy vấn mở rộng (query_expanded) cho BM25.
        """
        raw_query = str(query or "").strip()
        lower_query = raw_query.lower()

        detected_vehicle: Optional[str] = None
        vehicle_synonyms: List[str] = []
        matched_vehicle_key: Optional[str] = None

        # 1. Quét phương tiện: Sắp xếp theo chiều dài từ khóa giảm dần (Longest-Match First)
        sorted_vehicle_keys = sorted(self.vehicles.keys(), key=len, reverse=True)
        for key in sorted_vehicle_keys:
            if re.search(r"(?:\b|^)" + re.escape(key) + r"(?:\b|$)", lower_query):
                item = self.vehicles[key]
                detected_vehicle = item.get("canonical_vehicle")
                vehicle_synonyms = item.get("synonyms", [])
                matched_vehicle_key = key
                break

        # 2. Quét hành vi vi phạm: Sắp xếp theo chiều dài từ khóa giảm dần
        matched_violations: List[str] = []
        violation_synonyms: List[str] = []
        sorted_violation_keys = sorted(self.violations.keys(), key=len, reverse=True)
        
        covered_spans: List[Tuple[int, int]] = []
        for v_key in sorted_violation_keys:
            match = re.search(r"(?:\b|^)" + re.escape(v_key) + r"(?:\b|$)", lower_query)
            if match:
                start, end = match.span()
                if any(start >= c_start and end <= c_end for c_start, c_end in covered_spans):
                    continue
                covered_spans.append((start, end))
                matched_violations.append(v_key)
                syns = self.violations[v_key]
                for s in syns:
                    if s not in violation_synonyms and s.lower() not in lower_query:
                        violation_synonyms.append(s)

        # 3. Nhận diện ý định hỏi độ tuổi (Age Intent)
        is_age_query = any(k in lower_query for k in ["bao nhiêu tuổi", "độ tuổi", "đủ tuổi", "tuổi lái xe", "tuổi được lái"])

        # 4. Tạo query_expanded cho BM25
        expanded_tokens = []
        for s in vehicle_synonyms:
            if s.lower() not in lower_query and s not in expanded_tokens:
                expanded_tokens.append(s)
        for s in violation_synonyms:
            if s.lower() not in lower_query and s not in expanded_tokens:
                expanded_tokens.append(s)

        if is_age_query and "tuổi của người lái xe" not in expanded_tokens:
            expanded_tokens.append("tuổi của người lái xe")

        if expanded_tokens:
            query_expanded = f"{raw_query} ({', '.join(expanded_tokens)})"
        else:
            query_expanded = raw_query

        return {
            "query_original": raw_query,
            "query_expanded": query_expanded,
            "detected_vehicle": detected_vehicle,
            "matched_vehicle_key": matched_vehicle_key,
            "matched_violations": matched_violations,
            "expanded_tokens": expanded_tokens,
            "is_age_query": is_age_query
        }
