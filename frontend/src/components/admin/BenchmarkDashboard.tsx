"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  BarChart3,
  Play,
  RefreshCw,
  Search,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  FileSpreadsheet,
  Cpu,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  X,
  SlidersHorizontal,
  Download,
  Copy,
  Check,
  FileText,
} from "lucide-react";
import { useAuthStore } from "@/stores/useAuthStore";
import { benchmarkApi } from "@/lib/benchmarkApi";
import { BenchmarkReportResponse, BenchmarkQueryItem } from "@/types/benchmark";

export const BenchmarkDashboard: React.FC = () => {
  const { token } = useAuthStore();

  const [report, setReport] = useState<BenchmarkReportResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Filters & Search & Pagination
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "passed" | "failed">("all");
  const [selectedItem, setSelectedItem] = useState<BenchmarkQueryItem | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Execution parameters
  const [sampleLimit, setSampleLimit] = useState<number>(50);
  const [topK, setTopK] = useState<number>(3);
  const [elapsedTimer, setElapsedTimer] = useState<number>(0);
  const [isCopied, setIsCopied] = useState(false);

  // Load latest benchmark results on mount
  useEffect(() => {
    let isMounted = true;

    async function fetchLatestResults() {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const data = await benchmarkApi.getResults(token || undefined);
        if (isMounted) {
          setReport(data);
        }
      } catch (err: any) {
        if (isMounted) {
          setErrorMessage(err.message || "Không thể tải báo cáo đánh giá.");
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

  // Reset page when filter or search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, statusFilter]);

  // Handle trigger benchmark run
  const handleRunBenchmark = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const data = await benchmarkApi.runBenchmark(token || undefined, topK, sampleLimit);
      setReport(data);
      setSuccessMessage(
        `Đã hoàn thành đánh giá ${data.metadata?.evaluated_samples || sampleLimit} mẫu thử! Hit-rate@3 đạt ${
          data.summary_metrics?.hit_rate_percentage || "0%"
        } (MRR: ${data.summary_metrics?.mrr?.toFixed(4) || "0"}).`
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

  // Filtered queries
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

  // Pagination calculation
  const totalPages = Math.max(1, Math.ceil(filteredQueries.length / pageSize));
  const paginatedQueries = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredQueries.slice(start, start + pageSize);
  }, [filteredQueries, currentPage, pageSize]);

  // Statistics calculation
  const totalQuestions = report?.detailed_results?.length || 0;
  const passedQuestions = useMemo(() => {
    if (!report?.detailed_results) return 0;
    return report.detailed_results.filter((i) => i.is_passed ?? (i.hit > 0)).length;
  }, [report]);
  const failedQuestions = totalQuestions - passedQuestions;
  const passRatePercentage = totalQuestions > 0 ? ((passedQuestions / totalQuestions) * 100).toFixed(1) : "0.0";

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
  const missPercent = totalQuestions > 0 ? Math.round((missCount / totalQuestions) * 100) : 0;

  // Copy modal detail JSON
  const handleCopyModalDetail = () => {
    if (!selectedItem) return;
    navigator.clipboard.writeText(JSON.stringify(selectedItem, null, 2));
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto pb-10">
      {/* 1. TOP CONTROL & CONTEXT BAR */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-3">
            <h2 className="text-[17px] font-bold text-primary-navy tracking-tight">
              Báo cáo Đo lường Chất lượng AI (RAG Benchmark)
            </h2>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-semibold bg-slate-100 text-slate-700 border border-slate-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              ChromaDB HNSW
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[12px] text-slate-500">
            <span>
              Mô hình: <strong className="text-slate-700 font-mono">bkai-foundation-models/vietnamese-bi-encoder</strong>
            </span>
            <span>•</span>
            <span>
              Bộ luật: <strong className="text-slate-700">Nghị định 168/2024 &amp; Luật TTATGTĐB 2024</strong>
            </span>
            <span>•</span>
            <span>
              Cập nhật: <strong className="text-slate-700 font-mono">{report?.metadata?.timestamp || "Chưa có dữ liệu"}</strong>
            </span>
          </div>
        </div>

        {/* Execution Controls & Export */}
        <div className="flex items-center gap-2.5 shrink-0 flex-wrap">
          {report && (
            <button
              onClick={handleExportJSON}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-[12.5px] font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors cursor-pointer"
              title="Xuất file JSON báo cáo nghiệm thu"
            >
              <Download size={14} />
              <span>Xuất JSON</span>
            </button>
          )}

          <div className="flex items-center gap-2 bg-slate-50 p-1.5 rounded-xl border border-slate-200 text-[12px]">
            <SlidersHorizontal size={14} className="text-slate-400 ml-1" />
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
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-[13px] font-semibold text-white shadow-xs transition-all cursor-pointer ${
              isRunning
                ? "bg-slate-400 cursor-not-allowed"
                : "bg-accent-red hover:bg-red-700 active:translate-y-[1px]"
            }`}
          >
            {isRunning ? (
              <>
                <RefreshCw size={15} className="animate-spin" />
                <span className="font-mono">Đang đánh giá ({elapsedTimer}s)...</span>
              </>
            ) : (
              <>
                <Play size={15} />
                <span>Chạy Benchmark Đánh giá</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* SUCCESS MESSAGE BANNER */}
      {successMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[13px] flex items-center justify-between shadow-xs animate-in fade-in duration-150">
          <div className="flex items-center gap-2">
            <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
            <span className="font-medium">{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage(null)} className="cursor-pointer text-slate-400 hover:text-slate-700">
            <X size={15} />
          </button>
        </div>
      )}

      {/* ERROR MESSAGE NOTIFICATION */}
      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-800 text-[13px] flex items-center justify-between shadow-xs animate-in fade-in duration-150">
          <div className="flex items-center gap-2">
            <AlertCircle size={16} className="text-accent-red shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="cursor-pointer text-slate-400 hover:text-slate-700">
            <X size={15} />
          </button>
        </div>
      )}

      {/* LOADING SKELETAL STATE */}
      {isLoading ? (
        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs h-36 flex flex-col justify-between animate-pulse">
                <div className="h-4 bg-slate-200 rounded w-1/2" />
                <div className="h-8 bg-slate-200 rounded w-3/4" />
                <div className="h-3 bg-slate-200 rounded w-full" />
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-7 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs h-64 animate-pulse" />
            <div className="lg:col-span-5 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs h-64 animate-pulse" />
          </div>
        </div>
      ) : (
        <>
          {/* 2. KPI BENTO METRIC CARDS */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Card 1: Hit-rate@3 */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-500 mb-2">
                <span className="text-[12px] font-semibold uppercase tracking-wider">Hit-rate@3 (Top-3)</span>
                <span className="px-2 py-0.5 rounded-md text-[11px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Mục tiêu: ≥ 80%
                </span>
              </div>
              <div className="text-3xl font-mono font-bold text-slate-900 tracking-tight">
                {report?.summary_metrics?.hit_rate_percentage || "—"}
              </div>
              <div className="text-[11.5px] text-slate-500 mt-2">
                Tỷ lệ truy xuất trúng ít nhất 1 điều luật trong Top 3 tài liệu
              </div>
            </div>

            {/* Card 2: Mean Reciprocal Rank (MRR) */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-500 mb-2">
                <span className="text-[12px] font-semibold uppercase tracking-wider">Chỉ số MRR</span>
                <span className="px-2 py-0.5 rounded-md text-[11px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Mục tiêu: ≥ 0.70
                </span>
              </div>
              <div className="text-3xl font-mono font-bold text-slate-900 tracking-tight">
                {report?.summary_metrics?.mrr !== undefined ? report.summary_metrics.mrr.toFixed(4) : "—"}
              </div>
              <div className="text-[11.5px] text-slate-500 mt-2">
                Thứ hạng tương hỗ trung bình của điều luật chuẩn đầu tiên
              </div>
            </div>

            {/* Card 3: Recall@3 */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-500 mb-2">
                <span className="text-[12px] font-semibold uppercase tracking-wider">Độ phủ Recall@3</span>
                <span className="px-2 py-0.5 rounded-md text-[11px] font-mono font-bold bg-slate-100 text-slate-700 border border-slate-200">
                  Độ bao phủ luật
                </span>
              </div>
              <div className="text-3xl font-mono font-bold text-slate-900 tracking-tight">
                {report?.summary_metrics?.recall_percentage || "—"}
              </div>
              <div className="text-[11.5px] text-slate-500 mt-2">
                Tỷ lệ điều luật tìm thấy trên tổng số điều luật chuẩn cần viện dẫn
              </div>
            </div>

            {/* Card 4: Độ trễ trung bình */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-slate-500 mb-2">
                <span className="text-[12px] font-semibold uppercase tracking-wider">Độ trễ trung bình</span>
                <span className="px-2 py-0.5 rounded-md text-[11px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  &lt; 500ms
                </span>
              </div>
              <div className="text-3xl font-mono font-bold text-slate-900 tracking-tight">
                {report?.summary_metrics?.avg_latency_per_query_ms !== undefined
                  ? `${report.summary_metrics.avg_latency_per_query_ms.toFixed(2)} ms`
                  : "—"}
              </div>
              <div className="text-[11.5px] text-slate-500 mt-2">
                Thời gian phản hồi tìm kiếm vector trung bình trên mỗi câu hỏi
              </div>
            </div>
          </div>

          {/* 3. MID SECTION: ASYMMETRIC SPLIT (7:5) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column (7 cols): Phân bố Hiệu năng & Thứ hạng Top-K */}
            <div className="lg:col-span-7 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs flex flex-col justify-between">
              <div>
                <h3 className="text-[14px] font-bold text-primary-navy mb-1 flex items-center gap-2">
                  <BarChart3 size={16} className="text-accent-red" />
                  <span>Phân bố Thứ hạng Tìm kiếm Đúng (Rank Distribution)</span>
                </h3>
                <p className="text-[12px] text-slate-500 mb-4">
                  Vị trí xuất hiện của căn cứ pháp lý chính xác trong danh sách tài liệu RAG truy xuất
                </p>

                <div className="flex flex-col gap-3">
                  {/* Rank 1 */}
                  <div>
                    <div className="flex items-center justify-between text-[12px] mb-1">
                      <span className="font-semibold text-slate-700">Tìm thấy ngay tại Vị trí 1 (Rank 1 - Tối ưu)</span>
                      <div className="flex items-center gap-2 font-mono">
                        <span className="text-slate-400 text-[11px]">({rank1Count} câu)</span>
                        <span className="font-bold text-slate-900">{rank1Percent}%</span>
                      </div>
                    </div>
                    <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-600 rounded-full transition-all duration-500"
                        style={{ width: `${rank1Percent}%` }}
                      />
                    </div>
                  </div>

                  {/* Rank 2 - 3 */}
                  <div>
                    <div className="flex items-center justify-between text-[12px] mb-1">
                      <span className="font-semibold text-slate-700">Tìm thấy tại Vị trí 2 hoặc 3 (Rank 2-3)</span>
                      <div className="flex items-center gap-2 font-mono">
                        <span className="text-slate-400 text-[11px]">({rank23Count} câu)</span>
                        <span className="font-bold text-slate-900">{rank23Percent}%</span>
                      </div>
                    </div>
                    <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-amber-500 rounded-full transition-all duration-500"
                        style={{ width: `${rank23Percent}%` }}
                      />
                    </div>
                  </div>

                  {/* Miss / Not found in Top-K */}
                  <div>
                    <div className="flex items-center justify-between text-[12px] mb-1">
                      <span className="font-semibold text-slate-700">Không tìm thấy trong Top-3 (Cần bổ sung chunking)</span>
                      <div className="flex items-center gap-2 font-mono">
                        <span className="text-slate-400 text-[11px]">({missCount} câu)</span>
                        <span className="font-bold text-slate-900">{missPercent}%</span>
                      </div>
                    </div>
                    <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-red-500 rounded-full transition-all duration-500"
                        style={{ width: `${missPercent}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11.5px] text-slate-500">
                <span>Đối sánh: Semantic Embedding &amp; Lexical Citation Boundary</span>
                <span className="font-mono text-emerald-700 font-semibold">Chuẩn đồ án tốt nghiệp</span>
              </div>
            </div>

            {/* Right Column (5 cols): Thông số Kiểm thử & Mẫu */}
            <div className="lg:col-span-5 bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs flex flex-col justify-between">
              <div>
                <h3 className="text-[14px] font-bold text-primary-navy mb-1 flex items-center gap-2">
                  <Cpu size={16} className="text-accent-red" />
                  <span>Thống kê Bộ Dữ liệu Kiểm thử</span>
                </h3>
                <p className="text-[12px] text-slate-500 mb-4">
                  Tập câu hỏi thực tế về xử phạt vi phạm giao thông đường bộ
                </p>

                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase block">Tổng số mẫu test</span>
                    <span className="text-xl font-mono font-bold text-slate-900">{totalQuestions}</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase block">Tỷ lệ Đạt chuẩn</span>
                    <span className="text-xl font-mono font-bold text-emerald-600">{passRatePercentage}%</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase block">Số câu Đạt (Pass)</span>
                    <span className="text-xl font-mono font-bold text-emerald-600">{passedQuestions}</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase block">Số câu Lệch (Fail)</span>
                    <span className="text-xl font-mono font-bold text-red-600">{failedQuestions}</span>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11.5px] text-slate-500">
                <span>Tệp dữ liệu: 683_CauHoi_TTATGTDB.csv</span>
                <span className="font-mono text-slate-700">K = {report?.metadata?.top_k || topK}</span>
              </div>
            </div>
          </div>

          {/* 4. BOTTOM SECTION: QUERY INSPECTOR TABLE */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden flex flex-col">
            {/* Table Toolbar */}
            <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <h3 className="text-[14px] font-bold text-primary-navy">
                  Chi tiết Kiểm định Căn cứ Pháp lý (Query Inspector)
                </h3>
                <span className="px-2 py-0.5 rounded-full text-[11px] font-mono bg-slate-100 text-slate-600 font-bold">
                  {filteredQueries.length} câu
                </span>
              </div>

              <div className="flex items-center gap-3 w-full sm:w-auto">
                {/* Filter Tabs */}
                <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-[12px]">
                  <button
                    onClick={() => setStatusFilter("all")}
                    className={`px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                      statusFilter === "all" ? "bg-white text-primary-navy shadow-xs" : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    Tất cả ({totalQuestions})
                  </button>
                  <button
                    onClick={() => setStatusFilter("passed")}
                    className={`px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                      statusFilter === "passed" ? "bg-white text-emerald-700 shadow-xs" : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    Đạt ({passedQuestions})
                  </button>
                  <button
                    onClick={() => setStatusFilter("failed")}
                    className={`px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                      statusFilter === "failed" ? "bg-white text-red-700 shadow-xs" : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    Chưa đạt ({failedQuestions})
                  </button>
                </div>

                {/* Search Input */}
                <div className="relative flex-1 sm:w-64">
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Tìm câu hỏi, số điều, văn bản..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full h-[34px] pl-8 pr-3 rounded-xl bg-slate-50 border border-slate-200 text-[12px] text-slate-800 placeholder:text-slate-400 outline-none focus:bg-white focus:border-slate-300"
                  />
                </div>
              </div>
            </div>

            {/* Table Content */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-[12.5px] border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold text-[11px] uppercase tracking-wider">
                    <th className="py-2.5 px-4 w-14 font-mono">ID</th>
                    <th className="py-2.5 px-4 min-w-[320px]">Câu hỏi Kiểm thử</th>
                    <th className="py-2.5 px-4 min-w-[200px]">Căn cứ Chuẩn (Ground Truth)</th>
                    <th className="py-2.5 px-4 min-w-[200px]">Tài liệu RAG Truy xuất</th>
                    <th className="py-2.5 px-4 text-center w-24">Thứ hạng</th>
                    <th className="py-2.5 px-4 text-center w-24">Trạng thái</th>
                    <th className="py-2.5 px-4 text-right w-20">Chi tiết</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {paginatedQueries.map((item) => {
                    const isPassed = item.is_passed ?? (item.hit > 0);
                    const rankNum = item.first_rank ?? (item as any).rank ?? 0;
                    return (
                      <tr
                        key={item.id}
                        onClick={() => setSelectedItem(item)}
                        className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                      >
                        <td className="py-3 px-4 font-mono text-slate-400 text-[11.5px]">
                          #{item.id.toString().padStart(3, "0")}
                        </td>
                        <td className="py-3 px-4 text-slate-800 font-medium line-clamp-2 pr-4 leading-relaxed">
                          {item.question}
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex flex-wrap gap-1 max-w-[240px]">
                            {item.ground_truth_citations?.slice(0, 3).map((cite, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 rounded-md text-[11px] font-mono bg-slate-100 text-slate-700 border border-slate-200 truncate max-w-[200px]"
                                title={cite}
                              >
                                {cite}
                              </span>
                            ))}
                            {(item.ground_truth_citations?.length || 0) > 3 && (
                              <span className="text-[10px] text-slate-400 font-mono">
                                +{item.ground_truth_citations.length - 3}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex flex-wrap gap-1 max-w-[240px]">
                            {(item.retrieved_sources || []).slice(0, 3).map((src, idx) => {
                              const srcName = typeof src === "string" ? src : (src as any).source || (src as any).document;
                              const isMatch = item.ground_truth_citations?.some((gt) =>
                                gt.toLowerCase().includes(srcName?.toLowerCase() || "")
                              );
                              return (
                                <span
                                  key={idx}
                                  className={`px-2 py-0.5 rounded-md text-[11px] font-mono truncate max-w-[200px] border ${
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
                          </div>
                        </td>
                        <td className="py-3 px-4 text-center font-mono text-[12px]">
                          {rankNum > 0 ? (
                            <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-bold border border-slate-200">
                              Top {rankNum}
                            </span>
                          ) : (
                            <span className="text-slate-400">—</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span
                            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold border ${
                              isPassed
                                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                                : "bg-red-50 text-red-700 border-red-200"
                            }`}
                          >
                            {isPassed ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                            <span>{isPassed ? "Đạt" : "Lệch"}</span>
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedItem(item);
                            }}
                            className="px-2.5 py-1 rounded-lg bg-slate-100 group-hover:bg-primary-navy group-hover:text-white text-slate-700 text-[11px] font-semibold transition-colors cursor-pointer"
                          >
                            Xem
                          </button>
                        </td>
                      </tr>
                    );
                  })}

                  {filteredQueries.length === 0 && !isLoading && (
                    <tr>
                      <td colSpan={7} className="py-12 text-center text-slate-400">
                        Không tìm thấy câu hỏi kiểm thử nào phù hợp với bộ lọc.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {filteredQueries.length > pageSize && (
              <div className="p-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-[12px] text-slate-600">
                <div className="font-mono text-[11.5px]">
                  Hiển thị{" "}
                  <strong>
                    {(currentPage - 1) * pageSize + 1} -{" "}
                    {Math.min(currentPage * pageSize, filteredQueries.length)}
                  </strong>{" "}
                  trong tổng số <strong>{filteredQueries.length}</strong> câu
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
                    title="Trang trước"
                  >
                    <ChevronLeft size={16} />
                  </button>

                  <span className="px-2 font-mono font-semibold">
                    Trang {currentPage} / {totalPages}
                  </span>

                  <button
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
                    title="Trang sau"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* 5. QUERY DETAIL MODAL / DRAWER */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-3xl p-6 flex flex-col max-h-[85vh] animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4 shrink-0">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-mono font-bold text-[12px]">
                  #{selectedItem.id.toString().padStart(3, "0")}
                </span>
                <h3 className="font-bold text-[15px] text-primary-navy">Chi tiết Đánh giá Câu hỏi Kiểm thử</h3>
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
              <div>
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Câu hỏi kiểm thử:
                </span>
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-medium leading-relaxed">
                  {selectedItem.question}
                </div>
              </div>

              {/* Ground Truth Answer (if available) */}
              {(selectedItem as any).ground_truth_answer && (
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Câu trả lời chuẩn (Ground Truth Answer):
                  </span>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 text-[12.5px] leading-relaxed">
                    {(selectedItem as any).ground_truth_answer}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Căn cứ pháp lý chuẩn (Ground Truth):
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

              <div>
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Kết quả tính toán toán học:
                </span>
                <div className="grid grid-cols-4 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-200 text-center">
                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold block">HIT@K</span>
                    <span className="font-mono font-bold text-slate-900">{selectedItem.hit}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold block">RECALL@K</span>
                    <span className="font-mono font-bold text-slate-900">{selectedItem.recall}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold block">FIRST RANK</span>
                    <span className="font-mono font-bold text-slate-900">
                      {selectedItem.first_rank ?? (selectedItem as any).rank ?? 0}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 font-semibold block">STATUS</span>
                    <span
                      className={`font-mono font-bold ${
                        (selectedItem.is_passed ?? selectedItem.hit > 0) ? "text-emerald-600" : "text-red-600"
                      }`}
                    >
                      {(selectedItem.is_passed ?? selectedItem.hit > 0) ? "PASS" : "FAIL"}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex justify-end shrink-0 mt-2">
              <button
                onClick={() => setSelectedItem(null)}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-[13px] font-semibold cursor-pointer"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
