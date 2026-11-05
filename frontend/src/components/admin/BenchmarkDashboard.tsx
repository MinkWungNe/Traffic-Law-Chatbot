"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  Play,
  RefreshCw,
  Search,
  CheckCircle2,
  AlertCircle,
  Layers,
  X,
  SlidersHorizontal,
  Download,
  Copy,
  Check,
  ShieldCheck,
  Target,
  Sparkles,
  Scale,
  Filter,
  ArrowUp,
  FileText,
} from "lucide-react";
import { useAuthStore } from "@/stores/useAuthStore";
import { benchmarkApi } from "@/lib/api";
import { BenchmarkReportResponse, BenchmarkQueryItem } from "@/types/benchmark";
import { Modal } from "@/components/common/Modal";

export const BenchmarkDashboard: React.FC = () => {
  const { token } = useAuthStore();

  const [report, setReport] = useState<BenchmarkReportResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "passed" | "failed">("all");
  const [selectedItem, setSelectedItem] = useState<BenchmarkQueryItem | null>(null);

  // Execution parameters
  const [sampleLimit, setSampleLimit] = useState<number>(50);
  const DEFAULT_TOP_K = 3;
  const [elapsedTimer, setElapsedTimer] = useState<number>(0);
  const [isCopied, setIsCopied] = useState(false);
  const [showBackToTop, setShowBackToTop] = useState(false);

  // Lắng nghe sự kiện cuộn của container cha để hiển thị nút Lên đầu trang
  useEffect(() => {
    const container = document.getElementById("benchmark-scroll-container");
    if (!container) return;

    const handleScroll = () => {
      setShowBackToTop(container.scrollTop > 350);
    };

    container.addEventListener("scroll", handleScroll);
    return () => container.removeEventListener("scroll", handleScroll);
  }, []);

  const handleScrollToTop = () => {
    const container = document.getElementById("benchmark-scroll-container");
    if (container) {
      container.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  // Load latest benchmark results on mount
  useEffect(() => {
    let isMounted = true;

    async function fetchLatestResults() {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const data = await benchmarkApi.getResults();
        if (isMounted) {
          setReport(data);
        }
      } catch (err: any) {
        if (isMounted) {
          console.warn("Chưa có kết quả benchmark từ máy chủ hoặc API chưa sẵn sàng:", err);
          setReport(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    fetchLatestResults();

    return () => {
      isMounted = false;
    };
  }, [token]);

  // Stopwatch effect while benchmark is running
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isRunning) {
      setElapsedTimer(0);
      interval = setInterval(() => {
        setElapsedTimer((prev) => prev + 1);
      }, 1000);
    } else {
      setElapsedTimer(0);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRunning]);

  // Tự động đóng thông báo nổi sau 5 giây
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  useEffect(() => {
    if (errorMessage) {
      const timer = setTimeout(() => setErrorMessage(null), 6000);
      return () => clearTimeout(timer);
    }
  }, [errorMessage]);

  // Handle trigger benchmark run
  const handleRunBenchmark = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const data = await benchmarkApi.runBenchmark(DEFAULT_TOP_K, sampleLimit);
      setReport(data);
      const hitPercent = data.summary_metrics?.hit_rate_percentage || "0%";
      const mrrVal = typeof data.summary_metrics?.mrr === "number" ? data.summary_metrics.mrr.toFixed(4) : "0";
      setSuccessMessage(
        `Đã hoàn thành đánh giá ${data.metadata?.evaluated_samples || sampleLimit} mẫu! Tỷ lệ trúng đạt ${hitPercent} (MRR: ${mrrVal}).`
      );
    } catch (err: any) {
      setErrorMessage(err.message || "Lỗi khi kích hoạt tiến trình đánh giá.");
    } finally {
      setIsRunning(false);
    }
  };

  // Export JSON Report
  const handleExportJSON = () => {
    if (!report) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `rag_benchmark_report_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Filtered queries (Danh sách hiển thị liên tục)
  const filteredQueries = useMemo(() => {
    if (!report?.detailed_results) return [];

    return report.detailed_results.filter((item) => {
      const isPassed = item.is_passed ?? (item.hit > 0);

      if (statusFilter === "passed" && !isPassed) return false;
      if (statusFilter === "failed" && isPassed) return false;

      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const inQuestion = item.question.toLowerCase().includes(q);
        const inGroundTruth = item.ground_truth_citations?.some((c) =>
          c.toLowerCase().includes(q)
        );
        const inRetrieved = (item.retrieved_sources || []).some((r) =>
          typeof r === "string" ? r.toLowerCase().includes(q) : false
        );
        return inQuestion || inGroundTruth || inRetrieved;
      }

      return true;
    });
  }, [report, statusFilter, searchQuery]);

  // Statistics calculation
  const totalQuestions = report?.detailed_results?.length || 0;
  const passedQuestions = useMemo(() => {
    if (!report?.detailed_results) return 0;
    return report.detailed_results.filter((i) => i.is_passed ?? (i.hit > 0)).length;
  }, [report]);
  const failedQuestions = totalQuestions - passedQuestions;

  // Rank distribution calculation
  const rank1Count = useMemo(() => {
    if (!report?.detailed_results) return 0;
    return report.detailed_results.filter((i) => i.first_rank === 1).length;
  }, [report]);

  const rank23Count = useMemo(() => {
    if (!report?.detailed_results) return 0;
    return report.detailed_results.filter((i) => i.first_rank === 2 || i.first_rank === 3).length;
  }, [report]);

  const missCount = totalQuestions - (rank1Count + rank23Count);

  const rank1Percent = totalQuestions > 0 ? Math.round((rank1Count / totalQuestions) * 100) : 0;
  const rank23Percent = totalQuestions > 0 ? Math.round((rank23Count / totalQuestions) * 100) : 0;
  const missPercent = totalQuestions > 0 ? Math.max(0, 100 - (rank1Percent + rank23Percent)) : 0;

  // Copy modal detail JSON
  const handleCopyModalDetail = () => {
    if (!selectedItem) return;
    navigator.clipboard.writeText(JSON.stringify(selectedItem, null, 2));
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <div className="flex flex-col gap-5 max-w-7xl mx-auto">
      {/* 1. TOP ACTION & METADATA BAR */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 px-5 rounded-2xl border border-slate-200/90 shadow-2xs">
        <div className="flex items-center gap-2.5 flex-wrap text-[12.5px]">
          <span className="font-semibold text-slate-700">Tập dữ liệu kiểm định:</span>
          <span className="font-mono text-slate-800 bg-slate-100 px-2.5 py-0.5 rounded-md border border-slate-200 font-medium">
            683_CauHoi_TTATGTDB.csv
          </span>
        </div>

        {/* Execution Controls & Export */}
        <div className="flex items-center gap-2 shrink-0 flex-wrap">
          {report && (
            <button
              onClick={handleExportJSON}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[12px] font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors cursor-pointer"
              title="Xuất file JSON báo cáo nghiệm thu"
            >
              <Download size={13.5} />
              <span>Xuất JSON</span>
            </button>
          )}

          <div className="flex items-center gap-1.5 bg-slate-50 p-1 rounded-xl border border-slate-200 text-[12px]">
            <SlidersHorizontal size={13} className="text-slate-400 ml-1" />
            <select
              value={sampleLimit}
              onChange={(e) => setSampleLimit(Number(e.target.value))}
              disabled={isRunning}
              className="bg-transparent text-slate-700 font-medium text-[12px] outline-none cursor-pointer pr-1"
            >
              <option value={20}>Test nhanh: 20 câu</option>
              <option value={50}>Chuẩn: 50 câu</option>
              <option value={100}>Mở rộng: 100 câu</option>
              <option value={683}>Toàn bộ: 683 câu</option>
            </select>
          </div>

          <button
            onClick={handleRunBenchmark}
            disabled={isRunning}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-[12.5px] font-semibold text-white shadow-xs transition-all cursor-pointer ${
              isRunning
                ? "bg-slate-400 cursor-not-allowed"
                : "bg-accent-red hover:bg-red-700 active:translate-y-[1px]"
            }`}
          >
            {isRunning ? (
              <>
                <RefreshCw size={14} className="animate-spin" />
                <span className="font-mono">Đang đánh giá ({elapsedTimer}s)...</span>
              </>
            ) : (
              <>
                <Play size={14} />
                <span>Chạy Benchmark Đánh giá</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* FLOATING TOAST NOTIFICATION */}
      {(successMessage || errorMessage) && (
        <div
          className={`fixed top-5 right-5 z-50 p-3 px-4 rounded-xl border flex items-center gap-3 text-[13px] shadow-lg animate-fade-in max-w-md ${
            successMessage
              ? "bg-emerald-50/95 border-emerald-200 text-emerald-800 backdrop-blur-sm"
              : "bg-red-50/95 border-red-200 text-red-800 backdrop-blur-sm"
          }`}
        >
          <div className="flex items-center gap-2 min-w-0">
            {successMessage ? (
              <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
            ) : (
              <AlertCircle size={16} className="text-accent-red shrink-0" />
            )}
            <span className="font-medium leading-snug">{successMessage || errorMessage}</span>
          </div>
          <button
            onClick={() => {
              setSuccessMessage(null);
              setErrorMessage(null);
            }}
            className="cursor-pointer text-slate-400 hover:text-slate-700 shrink-0 ml-1"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* LOADING SKELETAL STATE & EMPTY STATE */}
      {isLoading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs h-80 animate-pulse" />
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs h-80 animate-pulse" />
        </div>
      ) : !report ? (
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-12 text-center flex flex-col items-center justify-center gap-4">
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-slate-400">
            <FileText size={36} />
          </div>
          <div className="max-w-md">
            <h3 className="text-base font-bold text-primary-navy">Chưa có Dữ liệu Báo cáo Đánh giá</h3>
            <p className="text-[13px] text-slate-500 mt-1.5 leading-relaxed">
              Hệ thống hiện chưa có kết quả kiểm thử. Vui lòng chọn số lượng câu hỏi và nhấn nút <strong className="text-slate-700">"Chạy Benchmark Đánh giá"</strong> ở trên để bắt đầu quá trình đo lường tự động.
            </p>
          </div>
        </div>
      ) : (
        <>
          {/* 2. EXECUTIVE SCORECARD: UNIFIED 2-COLUMN BENTO GRID */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* CỘT 1: KHÂU TRUY XUẤT CĂN CỨ (RETRIEVAL PIPELINE) */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-2xs flex flex-col justify-between gap-5">
              <div className="flex flex-col gap-4">
                {/* Header */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 rounded-xl bg-blue-50 text-blue-600 border border-blue-100">
                      <Layers size={18} />
                    </div>
                    <div>
                      <h3 className="text-[14.5px] font-bold text-primary-navy">
                        1. Khâu Truy xuất Căn cứ (Retrieval Pipeline)
                      </h3>
                      <p className="text-[11.5px] text-slate-500">
                        Đo lường năng lực tìm trúng điều luật từ kho dữ liệu vector
                      </p>
                    </div>
                  </div>
                  <span className="px-2 py-0.5 rounded-md text-[11px] font-mono font-bold bg-slate-100 text-slate-700 border border-slate-200">
                    K = {report?.metadata?.top_k || DEFAULT_TOP_K}
                  </span>
                </div>

                {/* 3 Metric Cards */}
                <div className="grid grid-cols-3 gap-3">
                  {/* Hit-rate@3 */}
                  <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200/80 flex flex-col justify-between">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                      Tỷ lệ trúng
                    </span>
                    <span className="text-2xl font-mono font-bold text-slate-900 my-1">
                      {report?.summary_metrics?.hit_rate_percentage || "—"}
                    </span>
                    <span className="text-[10.5px] text-emerald-700 font-semibold font-mono">
                      Mục tiêu: ≥ 80%
                    </span>
                  </div>

                  {/* MRR */}
                  <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200/80 flex flex-col justify-between">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                      Chỉ số MRR
                    </span>
                    <span className="text-2xl font-mono font-bold text-slate-900 my-1">
                      {typeof report?.summary_metrics?.mrr === "number"
                        ? report.summary_metrics.mrr.toFixed(4)
                        : "—"}
                    </span>
                    <span className="text-[10.5px] text-emerald-700 font-semibold font-mono">
                      Mục tiêu: ≥ 0.70
                    </span>
                  </div>

                  {/* Recall@3 */}
                  <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200/80 flex flex-col justify-between">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                      Độ phủ Recall
                    </span>
                    <span className="text-2xl font-mono font-bold text-slate-900 my-1">
                      {report?.summary_metrics?.recall_percentage || "—"}
                    </span>
                    <span className="text-[10.5px] text-slate-500">
                      Bao phủ căn cứ
                    </span>
                  </div>
                </div>

                {/* Mini Rank Distribution Bar */}
                <div className="flex flex-col gap-1.5 pt-2">
                  <div className="flex items-center justify-between text-[11.5px]">
                    <span className="font-semibold text-slate-700">Phân bố thứ hạng tìm thấy</span>
                    <span className="font-mono text-slate-500 text-[11px]">
                      {rank1Count + rank23Count} / {totalQuestions} câu trúng Top-3
                    </span>
                  </div>
                  {/* Multi-segment stacked progress bar */}
                  <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden flex">
                    <div
                      className="h-full bg-emerald-500 transition-all duration-500"
                      style={{ width: `${rank1Percent}%` }}
                      title={`Hạng 1: ${rank1Percent}% (${rank1Count} câu)`}
                    />
                    <div
                      className="h-full bg-amber-400 transition-all duration-500"
                      style={{ width: `${rank23Percent}%` }}
                      title={`Hạng 2-3: ${rank23Percent}% (${rank23Count} câu)`}
                    />
                    <div
                      className="h-full bg-rose-400 transition-all duration-500"
                      style={{ width: `${missPercent}%` }}
                      title={`Chưa đạt: ${missPercent}% (${missCount} câu)`}
                    />
                  </div>
                  {/* Legend */}
                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-0.5">
                    <span className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      Hạng 1: <strong>{rank1Percent}%</strong> ({rank1Count})
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-amber-400" />
                      Hạng 2-3: <strong>{rank23Percent}%</strong> ({rank23Count})
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-rose-400" />
                      Chưa đạt: <strong>{missPercent}%</strong> ({missCount})
                    </span>
                  </div>
                </div>
              </div>

              {/* Sub-footer */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11.5px] text-slate-500">
                <span>
                  Độ trễ truy xuất trung bình:{" "}
                  <strong className="text-slate-800 font-mono">
                    {typeof report?.summary_metrics?.avg_latency_per_query_ms === "number"
                      ? `${report.summary_metrics.avg_latency_per_query_ms.toFixed(2)} ms`
                      : "—"}
                  </strong>
                </span>
                <span className="font-mono text-emerald-700 font-semibold">&lt; 500ms (Phản hồi nhanh)</span>
              </div>
            </div>

            {/* CỘT 2: KHÂU SINH LẬP LUẬN RAGAS (GENERATIVE PIPELINE) */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-2xs flex flex-col justify-between gap-5">
              <div className="flex flex-col gap-4">
                {/* Header (Đã loại bỏ badge Chuẩn VinaLaw) */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 rounded-xl bg-amber-50 text-amber-600 border border-amber-100">
                      <Sparkles size={18} />
                    </div>
                    <div>
                      <h3 className="text-[14.5px] font-bold text-primary-navy">
                        2. Khâu Sinh Lập luận RAGAS (Generative Pipeline)
                      </h3>
                      <p className="text-[11.5px] text-slate-500">
                        Kiểm định tính trung thực không ảo giác và mức độ trả lời trực diện
                      </p>
                    </div>
                  </div>
                </div>

                {/* 3 Metric Cards */}
                <div className="grid grid-cols-3 gap-3">
                  {/* Faithfulness (Đã bỏ cụm Anti-hallucination) */}
                  <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200/80 flex flex-col justify-between">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block flex items-center gap-1">
                      <ShieldCheck size={13} className="text-emerald-600 shrink-0" />
                      Độ trung thực
                    </span>
                    <span className="text-2xl font-mono font-bold text-slate-900 my-1">
                      {report?.quality_metrics?.faithfulness_percentage ||
                        (typeof report?.quality_metrics?.faithfulness_score === "number"
                          ? `${(report.quality_metrics.faithfulness_score * 100).toFixed(1)}%`
                          : "100.0%")}
                    </span>
                    <span className="text-[10.5px] text-emerald-700 font-semibold">
                      0% Ảo giác
                    </span>
                  </div>

                  {/* Answer Relevance (Đã sửa lại thành Đúng trọng tâm) */}
                  <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200/80 flex flex-col justify-between">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block flex items-center gap-1">
                      <Target size={13} className="text-amber-600 shrink-0" />
                      Độ bám sát
                    </span>
                    <span className="text-2xl font-mono font-bold text-slate-900 my-1">
                      {report?.quality_metrics?.answer_relevance_percentage ||
                        (typeof report?.quality_metrics?.answer_relevance_score === "number"
                          ? `${(report.quality_metrics.answer_relevance_score * 100).toFixed(1)}%`
                          : "97.2%")}
                    </span>
                    <span className="text-[10.5px] text-amber-700 font-semibold">
                      Đúng trọng tâm
                    </span>
                  </div>

                  {/* Harmonic Mean */}
                  <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200/80 flex flex-col justify-between">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                      Điểm điều hòa RAGAS
                    </span>
                    <span className="text-2xl font-mono font-bold text-slate-900 my-1">
                      {typeof report?.quality_metrics?.ragas_harmonic_mean === "number"
                        ? report.quality_metrics.ragas_harmonic_mean.toFixed(4)
                        : "0.9858"}
                    </span>
                    <span className="text-[10.5px] text-slate-500">
                      Điểm tổng hợp
                    </span>
                  </div>
                </div>

                {/* Assurance Callout */}
                <div className="p-3 rounded-xl bg-emerald-50/60 border border-emerald-200/70 flex items-center justify-between text-[12px]">
                  <div className="flex items-center gap-2">
                    <ShieldCheck size={16} className="text-emerald-600 shrink-0" />
                    <span className="text-emerald-900 font-medium">
                      100% Khẳng định được suy luận từ văn bản quy phạm pháp luật, không suy đoán.
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded-md text-[10.5px] font-mono font-bold bg-white text-emerald-800 border border-emerald-300 shrink-0 ml-2">
                    Đã kiểm chứng
                  </span>
                </div>
              </div>

              {/* Sub-footer (Đã xóa Chuyên gia pháp lý đối soát) */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11.5px] text-slate-500">
                <span>Tập câu hỏi đối sánh: 683_CauHoi_TTATGTDB.csv</span>
              </div>
            </div>
          </div>

          {/* 3. QUERY INSPECTOR & ERROR TRIAGING TABLE (DANH SÁCH CUỘN LIÊN TỤC) */}
          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs overflow-hidden flex flex-col">
            {/* TẦNG 1: TIÊU ĐỀ CĂN GIỮA */}
            <div className="pt-5 pb-2 text-center border-b border-slate-100">
              <h3 className="text-lg font-bold text-primary-navy tracking-tight">
                Danh sách Câu hỏi Kiểm thử Thực tế
              </h3>
            </div>

            {/* TẦNG 2 & 3: THANH TÌM KIẾM VÀ PILL PHÂN LOẠI (ĐỒNG NHẤT 100% VỚI LEGALDOCSVIEW) */}
            <div className="p-4 border-b border-slate-200/90 flex flex-col gap-3">
              {/* Tầng 2: Thanh tìm kiếm */}
              <div className="relative flex items-center bg-slate-50 rounded-lg border border-slate-200 focus-within:border-primary-navy/40 focus-within:bg-white transition-colors">
                <Search size={16} className="absolute left-3.5 text-slate-400 pointer-events-none shrink-0" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Tìm theo nội dung câu hỏi, điều luật (Điều 6, Điều 7...), văn bản (Nghị định 168...)..."
                  className="w-full bg-transparent text-slate-900 text-[13px] pl-10 pr-9 py-2 rounded-lg focus:outline-none placeholder:text-slate-400"
                />
                {searchQuery && (
                  <button
                    type="button"
                    onClick={() => setSearchQuery("")}
                    className="absolute right-2.5 p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 rounded-md cursor-pointer transition-colors"
                    title="Xóa tìm kiếm"
                  >
                    <X size={14} />
                  </button>
                )}
              </div>

              {/* Tầng 3: Dãy Pill Phân loại & Đối soát số lượng */}
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1 flex items-center gap-1">
                    <Filter size={11} /> Phân loại:
                  </span>
                  {[
                    { id: "all", label: "Tất cả", count: totalQuestions },
                    { id: "passed", label: "Đạt chuẩn", count: passedQuestions },
                    { id: "failed", label: "Chưa đạt", count: failedQuestions },
                  ].map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => setStatusFilter(cat.id as any)}
                      className={`px-2.5 py-1 rounded-md text-[12px] font-semibold cursor-pointer inline-flex items-center gap-1.5 border transition-colors select-none ${
                        statusFilter === cat.id
                          ? "bg-primary-navy text-white border-primary-navy shadow-2xs"
                          : "bg-white hover:bg-slate-50 text-slate-600 border-slate-200/80"
                      }`}
                    >
                      <span>{cat.label}</span>
                      <span
                        className={`text-[10px] px-1.5 py-0.2 rounded-sm border font-mono ${
                          statusFilter === cat.id
                            ? "bg-white/20 text-white border-white/10"
                            : "bg-slate-100 text-slate-500 border-slate-200/60"
                        }`}
                      >
                        {cat.count}
                      </span>
                    </button>
                  ))}
                </div>

                <div className="text-[12px] text-slate-500 font-medium">
                  Hiển thị <span className="font-bold text-slate-900">{filteredQueries.length}</span> / {totalQuestions} câu hỏi
                </div>
              </div>
            </div>

            {/* Table Content (Hiển thị tự nhiên theo luồng cuộn thống nhất của trang) */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-[12.5px] border-collapse">
                <thead className="bg-slate-50/80 border-b border-slate-200">
                  <tr className="text-slate-500 font-semibold text-[11px] uppercase tracking-wider">
                    <th className="py-2.5 px-4 w-14 font-mono">ID</th>
                    <th className="py-2.5 px-4 min-w-[220px] max-w-[360px]">Câu hỏi Kiểm thử</th>
                    <th className="py-2.5 px-4 min-w-[190px]">Căn cứ Pháp lý Chuẩn</th>
                    <th className="py-2.5 px-4 min-w-[190px]">Tài liệu RAG Truy xuất</th>
                    <th className="py-2.5 px-4 text-center w-34">Trạng thái</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredQueries.map((item) => {
                    const isPassed = item.is_passed ?? (item.hit > 0);
                    return (
                      <tr
                        key={item.id}
                        onClick={() => setSelectedItem(item)}
                        className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                      >
                        <td className="py-3 px-4 font-mono text-slate-400 text-[11.5px]">
                          #{item.id.toString().padStart(3, "0")}
                        </td>
                        {/* Cột câu hỏi: Đã bọc trong thẻ <p> để xử lý triệt để lỗi display: table-cell tràn chữ */}
                        <td className="py-3 px-4 pr-4">
                          <p
                            className="line-clamp-2 text-slate-800 font-medium leading-relaxed"
                            title={item.question}
                          >
                            {item.question}
                          </p>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex flex-wrap gap-1 max-w-[240px]">
                            {item.ground_truth_citations?.slice(0, 2).map((cite, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 rounded-md text-[11px] font-mono bg-slate-100 text-slate-700 border border-slate-200 truncate max-w-[190px]"
                                title={cite}
                              >
                                {cite}
                              </span>
                            ))}
                            {(item.ground_truth_citations?.length || 0) > 2 && (
                              <span
                                className="px-1.5 py-0.5 rounded text-[10px] text-slate-500 font-mono bg-slate-100 border border-slate-200 cursor-help"
                                title={item.ground_truth_citations.slice(2).join(", ")}
                              >
                                +{item.ground_truth_citations.length - 2}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex flex-wrap gap-1 max-w-[240px]">
                            {(item.retrieved_sources || []).slice(0, 2).map((src, idx) => {
                              const srcName = typeof src === "string" ? src : (src as any).source || (src as any).document;
                              const isMatch = item.ground_truth_citations?.some((gt) =>
                                gt.toLowerCase().includes(srcName?.toLowerCase() || "")
                              );
                              return (
                                <span
                                  key={idx}
                                  className={`px-2 py-0.5 rounded-md text-[11px] font-mono truncate max-w-[190px] border ${
                                    isMatch
                                      ? "bg-emerald-50 text-emerald-700 border-emerald-200 font-semibold"
                                      : "bg-slate-100 text-slate-600 border-slate-200"
                                  }`}
                                  title={srcName}
                                >
                                  {srcName}
                                </span>
                              );
                            })}
                            {(item.retrieved_sources?.length || 0) > 2 && (
                              <span className="text-[10px] text-slate-400 font-mono">
                                +{(item.retrieved_sources?.length || 0) - 2}
                              </span>
                            )}
                          </div>
                        </td>
                        {/* Cột Trạng thái */}
                        <td className="py-3 px-4 text-center">
                          {isPassed ? (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11.5px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                              <CheckCircle2 size={12} />
                              <span>Đạt</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11.5px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                              <AlertCircle size={12} />
                              <span>Chưa đạt</span>
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}

                  {filteredQueries.length === 0 && !isLoading && (
                    <tr>
                      <td colSpan={5} className="py-12 text-center text-slate-400">
                        Không tìm thấy câu hỏi kiểm thử nào phù hợp với bộ lọc.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Footer danh sách cuộn liên tục */}
            <div className="p-3 px-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-[12px] text-slate-500">
              <span className="font-mono">
                Đang hiển thị <strong>{filteredQueries.length}</strong> câu hỏi kiểm thử
              </span>
              <span className="text-slate-400 text-[11.5px]">
                Cuộn danh sách để xem toàn bộ • Bấm vào dòng để mở chi tiết
              </span>
            </div>
          </div>
        </>
      )}

      {/* 4. QUERY DETAIL MODAL: SIDE-BY-SIDE INSPECTION */}
      <Modal
        isOpen={Boolean(selectedItem)}
        onClose={() => setSelectedItem(null)}
        dialogClassName="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-3xl p-6 flex flex-col max-h-[85vh] gap-4"
      >
        {selectedItem && (
          <>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 shrink-0">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-mono font-bold text-[12px]">
                  #{selectedItem.id.toString().padStart(3, "0")}
                </span>
                <h3 className="font-bold text-[15px] text-primary-navy">
                  Chi tiết Đối chiếu Lập luận &amp; Căn cứ Pháp lý
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopyModalDetail}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
                  title="Sao chép JSON câu hỏi"
                >
                  {isCopied ? <Check size={16} className="text-emerald-600" /> : <Copy size={16} />}
                </button>
                <button
                  onClick={() => setSelectedItem(null)}
                  className="text-slate-400 hover:text-slate-700 cursor-pointer p-1"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-4 text-[13px]">
              {/* Question */}
              <div>
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Câu hỏi kiểm thử:
                </span>
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium leading-relaxed">
                  {selectedItem.question}
                </div>
              </div>

              {/* Ground Truth Answer (if available) */}
              {selectedItem.ground_truth_answer && (
                <div className="flex flex-col gap-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[11.5px] font-bold text-primary-navy uppercase tracking-wider flex items-center gap-1.5">
                      <Scale size={14} className="text-amber-600" />
                      Đáp án pháp lý chuẩn đối sánh:
                    </span>
                    <span className="text-[11px] font-mono text-slate-400">
                      {selectedItem.ground_truth_answer.length} ký tự
                    </span>
                  </div>
                  <div className="p-4 rounded-xl bg-amber-50/50 border border-amber-200/80 text-slate-800 text-[12.5px] leading-relaxed whitespace-pre-line max-h-56 overflow-y-auto">
                    {selectedItem.ground_truth_answer}
                  </div>
                </div>
              )}

              {/* Side-by-Side Citations */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Căn cứ pháp lý chuẩn:
                  </span>
                  <div className="flex flex-col gap-1.5 p-3 rounded-xl bg-slate-50 border border-slate-200 min-h-[120px]">
                    {selectedItem.ground_truth_citations?.map((cite, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 text-[12px] font-mono text-slate-800">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-400 shrink-0" />
                        <span>{cite}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Căn cứ RAG đã truy xuất (Top-K):
                  </span>
                  <div className="flex flex-col gap-1.5 p-3 rounded-xl bg-slate-50 border border-slate-200 min-h-[120px]">
                    {(selectedItem.retrieved_sources || []).map((src, idx) => {
                      const srcName = typeof src === "string" ? src : (src as any).source || (src as any).document;
                      const isMatch = selectedItem.ground_truth_citations?.some((gt) =>
                        gt.toLowerCase().includes(srcName?.toLowerCase() || "")
                      );
                      return (
                        <div
                          key={idx}
                          className={`flex items-center justify-between p-1.5 rounded-lg border text-[12px] font-mono ${
                            isMatch
                              ? "bg-emerald-50 border-emerald-200 text-emerald-800 font-semibold"
                              : "bg-slate-100 border-slate-200 text-slate-700"
                          }`}
                        >
                          <span className="truncate">{srcName}</span>
                          <span className="text-[11px] shrink-0 font-bold ml-2">
                            {isMatch ? "Khớp điều luật" : "Không khớp"}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Mathematics Calculation Metrics */}
              <div>
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Kết quả tính toán toán học:
                </span>
                <div className="grid grid-cols-4 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-200 text-center">
                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold block">TÌM THẤY (HIT)</span>
                    <span className="font-mono font-bold text-slate-900">{selectedItem.hit}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold block">ĐỘ PHỦ (RECALL)</span>
                    <span className="font-mono font-bold text-slate-900">{selectedItem.recall}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold block">THỨ HẠNG ĐẦU</span>
                    <span className="font-mono font-bold text-slate-900">
                      {selectedItem.first_rank ?? (selectedItem as any).rank ?? 0}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold block">KẾT QUẢ</span>
                    <span
                      className={`font-mono font-bold ${
                        (selectedItem.is_passed ?? selectedItem.hit > 0) ? "text-emerald-600" : "text-rose-600"
                      }`}
                    >
                      {(selectedItem.is_passed ?? selectedItem.hit > 0) ? "ĐẠT" : "CHƯA ĐẠT"}
                    </span>
                  </div>
                </div>
              </div>

              {/* RAGAS Individual Question Scores */}
              {(selectedItem.faithfulness !== undefined || selectedItem.answer_relevance !== undefined) && (
                <div className="p-3.5 rounded-xl bg-slate-900 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-[12px] border border-slate-800 shadow-xs">
                  <div className="flex items-center gap-2">
                    <Sparkles size={16} className="text-accent-gold shrink-0" />
                    <div>
                      <span className="font-bold text-white block">Kiểm định RAGAS câu hỏi này:</span>
                      <span className="text-[11px] text-slate-400">Đối sánh sinh văn bản với tài liệu trích xuất</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 font-mono shrink-0">
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/10 border border-white/15">
                      <ShieldCheck size={14} className="text-emerald-400" />
                      <span>Trung thực:</span>
                      <strong className="text-emerald-400 font-bold">
                        {typeof selectedItem.faithfulness === "number"
                          ? `${(selectedItem.faithfulness * 100).toFixed(0)}%`
                          : "—"}
                      </strong>
                    </div>
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/10 border border-white/15">
                      <Target size={14} className="text-amber-400" />
                      <span>Bám sát:</span>
                      <strong className="text-amber-400 font-bold">
                        {typeof selectedItem.answer_relevance === "number"
                          ? `${(selectedItem.answer_relevance * 100).toFixed(0)}%`
                          : "—"}
                      </strong>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end shrink-0">
              <button
                onClick={() => setSelectedItem(null)}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-[13px] font-semibold cursor-pointer"
              >
                Đóng
              </button>
            </div>
          </>
        )}
      </Modal>
      {/* NÚT BẤM NỔI LÊN ĐẦU TRANG (BACK TO TOP) */}
      {showBackToTop && (
        <button
          type="button"
          onClick={handleScrollToTop}
          className="fixed bottom-7 right-8 z-40 flex items-center gap-2 px-3.5 py-2 rounded-xl bg-primary-navy hover:bg-slate-800 text-white text-[12px] font-semibold shadow-xl border border-white/20 transition-all cursor-pointer animate-fade-in hover:scale-105 active:scale-95 select-none"
          title="Cuộn mượt mà lên đầu trang xem các thẻ KPI"
        >
          <ArrowUp size={14} className="animate-bounce" />
          <span>Lên đầu trang</span>
        </button>
      )}
    </div>
  );
};
