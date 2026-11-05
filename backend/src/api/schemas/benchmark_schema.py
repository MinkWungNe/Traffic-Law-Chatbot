"""
Module: benchmark_schema.py
Mục đích: Định nghĩa Pydantic Models chuẩn hóa cho các API Báo cáo Đánh giá RAG (Benchmark & RAGAS).
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BenchmarkMetadata(BaseModel):
    """Metadata thông số kỹ thuật của lần chạy đánh giá."""
    framework: Optional[str] = Field("Hybrid Benchmark Evaluation Engine", description="Tên framework đánh giá")
    dataset_file: Optional[str] = Field("data/raw/683_CauHoi_TTATGTDB.csv", description="Đường dẫn tập dữ liệu kiểm thử")
    total_questions: int = Field(..., description="Tổng số câu hỏi trong tập kiểm thử")
    evaluated_samples: int = Field(..., description="Số lượng câu hỏi thực tế đã đánh giá")
    top_k: int = Field(..., description="Số lượng đoạn trích Top-K tài liệu")
    evaluation_time_seconds: float = Field(..., description="Tổng thời gian thực thi (giây)")
    timestamp: str = Field(..., description="Thời điểm ghi nhận kết quả")


class BenchmarkSummaryMetrics(BaseModel):
    """Các chỉ số đo lường năng lực truy xuất (Retrieval Performance)."""
    hit_rate: float = Field(..., description="Hit-rate@K dạng số thập phân")
    hit_rate_percentage: str = Field(..., description="Hit-rate@K định dạng phần trăm")
    recall_at_k: float = Field(..., description="Recall@K dạng số thập phân")
    recall_percentage: str = Field(..., description="Recall@K định dạng phần trăm")
    mrr: float = Field(..., description="Hạng nghịch đảo trung bình (Mean Reciprocal Rank)")
    avg_latency_per_query_ms: float = Field(..., description="Thời gian phản hồi trung bình mỗi câu (ms)")


class QualityMetrics(BaseModel):
    """Các chỉ số đo lường chất lượng sinh câu trả lời RAGAS (Generative Quality)."""
    faithfulness_score: float = Field(..., description="Điểm độ trung thực / chống sinh ảo giác (0.0 - 1.0)")
    faithfulness_percentage: Optional[str] = Field(None, description="Độ trung thực định dạng phần trăm")
    answer_relevance_score: float = Field(..., description="Điểm độ phù hợp và đúng trọng tâm (0.0 - 1.0)")
    answer_relevance_percentage: Optional[str] = Field(None, description="Độ phù hợp định dạng phần trăm")
    ragas_harmonic_mean: Optional[float] = Field(None, description="Điểm trung bình điều hòa Ragas")


class BenchmarkQueryItem(BaseModel):
    """Chi tiết kết quả đánh giá cho từng câu hỏi đơn lẻ."""
    id: int = Field(..., description="Số thứ tự câu hỏi")
    question: str = Field(..., description="Nội dung câu hỏi kiểm thử")
    ground_truth_answer: Optional[str] = Field(None, description="Câu trả lời pháp lý chuẩn chi tiết")
    ground_truth_citations: List[str] = Field(default_factory=list, description="Căn cứ pháp lý chuẩn (Nghị định, Điều luật)")
    retrieved_sources: Optional[List[str]] = Field(default_factory=list, description="Danh sách tài liệu RAG đã truy xuất")
    retrieved_docs: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Chi tiết các đoạn trích RAG trả về")
    hit: float = Field(..., description="Chỉ số Hit (1.0 nếu tìm thấy ít nhất 1 căn cứ)")
    recall: float = Field(..., description="Chỉ số Recall (tỷ lệ căn cứ tìm thấy / tổng căn cứ chuẩn)")
    first_rank: int = Field(default=0, description="Thứ tự xuất hiện của tài liệu đúng đầu tiên")
    rank: Optional[int] = Field(default=None, description="Alias tương thích ngược cho first_rank")
    reciprocal_rank: Optional[float] = Field(default=0.0, description="Hạng nghịch đảo của câu hỏi")
    is_passed: Optional[bool] = Field(default=True, description="Trạng thái đạt chuẩn (Hit > 0)")
    status: Optional[str] = Field(default="Đạt", description="Nhãn trạng thái tiếng Việt")
    faithfulness: Optional[float] = Field(None, description="Điểm trung thực Ragas riêng cho câu hỏi này")
    answer_relevance: Optional[float] = Field(None, description="Điểm bám sát câu hỏi riêng cho câu hỏi này")
    matched_citations: Optional[List[str]] = Field(default_factory=list, description="Căn cứ đã đối sánh thành công")


class BenchmarkSummaryResponse(BaseModel):
    """Phản hồi nhanh tóm tắt các thẻ KPI (dùng cho Endpoint /latest hoặc header Dashboard)."""
    metadata: BenchmarkMetadata
    summary_metrics: BenchmarkSummaryMetrics
    quality_metrics: Optional[QualityMetrics] = None


class BenchmarkFullReportResponse(BaseModel):
    """Báo cáo đánh giá hoàn chỉnh bao gồm toàn bộ danh sách 683 câu hỏi chi tiết."""
    metadata: BenchmarkMetadata
    summary_metrics: BenchmarkSummaryMetrics
    quality_metrics: Optional[QualityMetrics] = None
    detailed_results: List[BenchmarkQueryItem] = Field(..., description="Danh sách chi tiết toàn bộ các câu hỏi kiểm thử")
    samples: Optional[List[BenchmarkQueryItem]] = Field(None, description="Alias tương thích ngược với Phân hệ 4")


class BenchmarkSamplesResponse(BaseModel):
    """Phản hồi danh sách mẫu kiểm thử có phân trang."""
    total: int = Field(..., description="Tổng số câu hỏi thỏa mãn bộ lọc")
    page: int = Field(..., description="Trang hiện tại")
    limit: int = Field(..., description="Số lượng mỗi trang")
    total_pages: int = Field(..., description="Tổng số trang")
    items: List[BenchmarkQueryItem] = Field(..., description="Danh sách câu hỏi trong trang")
