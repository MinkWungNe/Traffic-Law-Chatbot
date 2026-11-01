"use client";

import React, { useState, useEffect, useMemo, useRef } from "react";
import { LEGAL_DOCUMENTS, LegalDocItem } from "@/data/legalDocuments";
import { useChatStore } from "@/stores/useChatStore";
import {
  Search,
  X,
  ExternalLink,
  Layers,
  BookOpen,
  GitBranch,
  Copy,
  Check,
  Calendar,
  Building2,
  Bot,
  Filter,
  ChevronRight,
  Sparkles,
  Info,
  FileQuestion,
  LayoutGrid,
  Columns,
  PenLine,
} from "lucide-react";

// Trích xuất metadata nguồn gốc văn bản (Chính thức .gov.vn vs Tham khảo lưu trữ)
const getSourceMeta = (url?: string) => {
  if (!url) return null;
  if (url.includes("congbao.chinhphu.vn")) {
    return { label: "Công báo Chính phủ", isOfficial: true };
  }
  if (url.includes("bocongan.gov.vn")) {
    return { label: "Cổng TTĐT Bộ Công an", isOfficial: true };
  }
  if (url.includes("luatvietnam.vn")) {
    return { label: "Lưu trữ (LuatVietnam)", isOfficial: false };
  }
  if (url.includes("hethongphapluat.com")) {
    return { label: "Lưu trữ (hethongphapluat)", isOfficial: false };
  }
  if (url.includes(".gov.vn")) {
    return { label: "Cổng TTĐT Nhà nước", isOfficial: true };
  }
  return { label: "Toàn văn VBPL", isOfficial: false };
};

// Hiển thị chấm trạng thái chuẩn pháp lý (Status Dot Indicator tĩnh, trang trọng)
const renderStatusDot = (status: string) => {
  const isPartiallyExpired = status.toLowerCase().includes("hết hiệu lực một phần");
  const isExpired = status.toLowerCase().includes("hết hiệu lực") && !isPartiallyExpired;

  let dotColor = "bg-emerald-500";
  let textColor = "text-emerald-700";

  if (isExpired) {
    dotColor = "bg-slate-400";
    textColor = "text-slate-600";
  } else if (isPartiallyExpired) {
    dotColor = "bg-amber-500";
    textColor = "text-amber-700";
  }

  return (
    <div className="flex items-center gap-1.5 shrink-0 select-none">
      <span className={`inline-flex rounded-full h-2 w-2 ${dotColor}`} />
      <span className={`text-[11.5px] font-semibold ${textColor}`}>{status}</span>
    </div>
  );
};

// Bảng ánh xạ kiểu dáng Badge phân loại văn bản (UI Presentation Layer)
const DOC_TYPE_BADGE_STYLE: Record<string, string> = {
  luat: "bg-red-50 text-red-700 border-red-200",
  "nghi-dinh": "bg-blue-50 text-blue-700 border-blue-200",
  "thong-tu": "bg-purple-50 text-purple-700 border-purple-200",
  "quy-chuan": "bg-emerald-50 text-emerald-700 border-emerald-200",
};

const getDocTypeBadgeStyle = (category?: string): string => {
  if (!category) return "bg-slate-50 text-slate-700 border-slate-200";
  return DOC_TYPE_BADGE_STYLE[category] || "bg-slate-50 text-slate-700 border-slate-200";
};

// Bảng ánh xạ nhãn quan hệ văn bản trong phả hệ (UI Presentation Layer)
const RELATION_LABELS: Record<"goc" | "sua_doi", string> = {
  goc: "Văn bản gốc",
  sua_doi: "Sửa đổi, bổ sung",
};

// Thống kê số lượng phân nhóm cố định (Module level - không tính toán lại khi render)
const STATS = {
  total: LEGAL_DOCUMENTS.length,
  luat: LEGAL_DOCUMENTS.filter((d) => d.category === "luat").length,
  nghiDinh: LEGAL_DOCUMENTS.filter((d) => d.category === "nghi-dinh").length,
  thongTu: LEGAL_DOCUMENTS.filter((d) => d.category === "thong-tu").length,
  quyChuan: LEGAL_DOCUMENTS.filter((d) => d.category === "quy-chuan").length,
};

export const LegalDocsView: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [selectedDocId, setSelectedDocId] = useState<string>("doc-01");
  const [viewMode, setViewMode] = useState<"split" | "grid">("split");
  const [isCopied, setIsCopied] = useState<boolean>(false);

  const searchInputRef = useRef<HTMLInputElement>(null);
  const { setActiveTab, sendMessage, setInputText } = useChatStore();

  // Phím tắt bàn phím '/' để focus vào ô tìm kiếm, 'Esc' để xóa từ khóa tìm kiếm (chỉ gắn 1 lần)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const activeTag = (document.activeElement as HTMLElement)?.tagName;
      if (e.key === "/" && activeTag !== "INPUT" && activeTag !== "TEXTAREA") {
        e.preventDefault();
        searchInputRef.current?.focus();
      } else if (e.key === "Escape") {
        setSearchTerm("");
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Bộ lọc tìm kiếm thông minh đa tiêu chí
  const filteredDocs = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    return LEGAL_DOCUMENTS.filter((doc) => {
      const matchCat = activeCategory === "all" || doc.category === activeCategory;

      if (!term) return matchCat;

      const inTitle = doc.title.toLowerCase().includes(term);
      const inNumber = doc.number.toLowerCase().includes(term);
      const inDesc = doc.desc.toLowerCase().includes(term);
      const inIssuer = doc.issuer?.toLowerCase().includes(term) || false;
      const inRelated =
        doc.relatedDocs?.some(
          (r) => r.title.toLowerCase().includes(term) || r.number.toLowerCase().includes(term)
        ) || false;

      return matchCat && (inTitle || inNumber || inDesc || inIssuer || inRelated);
    });
  }, [searchTerm, activeCategory]);

  // Xác định văn bản đang được chọn hiển thị ở khung Inspector (ưu tiên kết quả tìm kiếm)
  const selectedDoc = useMemo(() => {
    return filteredDocs.find((d) => d.id === selectedDocId) || filteredDocs[0] || LEGAL_DOCUMENTS[0];
  }, [selectedDocId, filteredDocs]);

  const hasLineage = Boolean(selectedDoc.relatedDocs && selectedDoc.relatedDocs.length > 0);

  // Sao chép số hiệu văn bản vào clipboard
  const handleCopyCitation = (text: string) => {
    navigator.clipboard.writeText(text);
    setIsCopied(true);
    setTimeout(() => {
      setIsCopied(false);
    }, 2000);
  };

  // Điều hướng và gửi câu hỏi trực tiếp sang Phân hệ AI Chatbot
  const handleAskAI = (promptText: string) => {
    setActiveTab("chat");
    setInputText(promptText);
    sendMessage(promptText);
  };

  return (
    <div className="absolute inset-0 w-full h-full overflow-y-auto px-5 py-5 z-10 select-text flex flex-col">
      <div className="max-w-7xl w-full mx-auto flex flex-col gap-3 flex-1 min-h-0">
        
        {/* ========================================================================= */}
        {/* HEADER NẰM NGOÀI, ĐƯA VÀO CHÍNH GIỮA                                      */}
        {/* ========================================================================= */}
        <header className="w-full text-center py-0.5">
          <h1 className="text-2xl font-extrabold text-primary-navy tracking-tight">
            Tra cứu Văn bản Quy phạm Pháp luật Giao thông
          </h1>
        </header>

        {/* ========================================================================= */}
        {/* KHUNG ĐỰNG CHUNG TOÀN BỘ NỘI DUNG                                         */}
        {/* ========================================================================= */}
        <div className="w-full bg-white/70 rounded-2xl border border-slate-200/80 shadow-md p-4 flex flex-col gap-3.5 flex-1 min-h-0">
          
          {/* CỤM THANH TÌM KIẾM & BỘ CHUYỂN VIEW NẰM CÙNG MỘT HÀNG */}
          <div className="flex items-center gap-2.5">
            {/* Search Input Box with Spotlight Border (Không tạo style object mới khi render) */}
            <div className="spotlight-border relative flex-1 flex items-center bg-white rounded-lg border border-slate-200 focus-within:border-primary-navy/40 transition-colors [--glow-color:#94A3B8] [--glow-size:240px]">
              <Search size={17} className="absolute left-3.5 text-slate-400 pointer-events-none shrink-0" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Tìm số hiệu (36/2024, 168/2024), nồng độ cồn, trừ điểm GPLX, dừng xe... (Bấm '/' để tìm)"
                className="w-full bg-transparent text-slate-900 text-sm pl-10 pr-9 py-2 rounded-lg focus:outline-none placeholder:text-slate-400"
              />
              {searchTerm && (
                <button
                  type="button"
                  onClick={() => setSearchTerm("")}
                  className="absolute right-2.5 p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md cursor-pointer transition-colors"
                  title="Xóa tìm kiếm (Esc)"
                >
                  <X size={14} />
                </button>
              )}
            </div>

            {/* View Mode Switcher đặt bên phải thanh tìm kiếm */}
            <div className="flex items-center gap-1 shrink-0 bg-slate-100/80 p-1 rounded-lg border border-slate-200/80">
              <button
                type="button"
                onClick={() => setViewMode("split")}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[12px] font-semibold cursor-pointer border transition-all ${
                  viewMode === "split"
                    ? "bg-white text-primary-navy shadow-xs border-slate-200/90"
                    : "text-slate-600 hover:text-slate-900 border-transparent"
                }`}
                title="Chế độ chia đôi: Danh mục Master bên trái & Khung đọc chi tiết bên phải"
              >
                <Columns size={13.5} />
                <span>Split View</span>
              </button>
              <button
                type="button"
                onClick={() => setViewMode("grid")}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[12px] font-semibold cursor-pointer border transition-all ${
                  viewMode === "grid"
                    ? "bg-white text-primary-navy shadow-xs border-slate-200/90"
                    : "text-slate-600 hover:text-slate-900 border-transparent"
                }`}
                title="Chế độ ma trận lưới Bento"
              >
                <LayoutGrid size={13.5} />
                <span>Grid View</span>
              </button>
            </div>
          </div>

          {/* CỤM PHÂN LOẠI & ĐẾM SỐ LƯỢNG */}
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1 flex items-center gap-1">
                <Filter size={11} /> Phân loại:
              </span>
              {[
                { id: "all", label: "Tất cả", count: STATS.total },
                { id: "luat", label: "Luật & Bộ luật", count: STATS.luat },
                { id: "nghi-dinh", label: "Nghị định", count: STATS.nghiDinh },
                { id: "thong-tu", label: "Thông tư", count: STATS.thongTu },
                { id: "quy-chuan", label: "Quy chuẩn", count: STATS.quyChuan },
              ].map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setActiveCategory(cat.id)}
                  className={`px-2.5 py-1 rounded-md text-[12px] font-semibold cursor-pointer inline-flex items-center gap-1.5 border transition-colors ${
                    activeCategory === cat.id
                      ? "bg-primary-navy text-white border-primary-navy shadow-2xs"
                      : "bg-white hover:bg-slate-50 text-slate-600 border-slate-200/80"
                  }`}
                >
                  <span>{cat.label}</span>
                  <span
                    className={`text-[10px] px-1 rounded-sm border ${
                      activeCategory === cat.id
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
              Hiển thị <span className="font-bold text-slate-900">{filteredDocs.length}</span> / {STATS.total} văn bản
            </div>
          </div>

          {/* ======================================================================= */}
          {/* VÙNG LÀM VIỆC NỘI DUNG: SPLIT MASTER-DETAIL                             */}
          {/* ======================================================================= */}
          {viewMode === "split" ? (
            /* ======================== CHẾ ĐỘ SPLIT MASTER-DETAIL ================== */
            <div className="grid grid-cols-12 gap-2 flex-1 items-start min-h-0">
              
              {/* CỘT TRÁI: DANH SÁCH MỤC LỤC MASTER (Sử dụng button chuẩn A11y & spotlight-border) */}
              <div className="col-span-5 flex flex-col gap-2.5 h-[calc(100vh-215px)] overflow-y-auto pl-2 pr-1.5 py-1">
                {filteredDocs.map((doc) => {
                  const isSelected = selectedDoc.id === doc.id;
                  return (
                    <button
                      key={doc.id}
                      type="button"
                      onClick={() => {
                        setSelectedDocId(doc.id);
                      }}
                      aria-selected={isSelected}
                      className={`w-full text-left block p-3.5 rounded-xl border transition-all cursor-pointer relative group bg-white spotlight-border ${
                        isSelected
                          ? "border-primary-navy/40 shadow-md ring-1 ring-primary-navy/15"
                          : "border-slate-200/80 shadow-2xs"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className={`px-2 py-0.5 rounded text-[10.5px] font-bold border ${getDocTypeBadgeStyle(doc.category)}`}>
                            {doc.typeLabel}
                          </span>
                          {doc.isConsolidated && (
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-0.5">
                              <Layers size={10} /> Hợp nhất
                            </span>
                          )}
                          <span className="font-mono text-[11px] font-bold text-slate-600 truncate max-w-[250px]">
                            {doc.number}
                          </span>
                        </div>
                        
                        <ChevronRight
                          size={15}
                          className={`transition-transform shrink-0 ${
                            isSelected
                              ? "text-primary-navy translate-x-0.5"
                              : "text-slate-300 group-hover:text-slate-500 group-hover:translate-x-0.5"
                          }`}
                        />
                      </div>

                      <h4
                        title={doc.title}
                        className={`text-[13.5px] mt-2 leading-snug truncate transition-colors ${
                          isSelected
                            ? "font-extrabold text-primary-navy"
                            : "font-semibold text-slate-800 group-hover:text-primary-navy"
                        }`}
                      >
                        {doc.title}
                      </h4>

                      <div className="mt-2 flex items-center justify-between text-[11.5px] text-slate-500 pt-1.5 border-t border-slate-100/90">
                        <span className="flex items-center gap-1 truncate">
                          <Building2 size={12} className="text-slate-400 shrink-0" />
                          <span className="truncate">{doc.issuer || "Nhà nước"}</span>
                        </span>
                        <span className="flex items-center gap-1 shrink-0 font-medium text-slate-500 text-[11.5px]" title="Ngày có hiệu lực thi hành">
                          <Calendar size={11} className="text-slate-400" />
                          <span>HL: {doc.effectiveDate || doc.date}</span>
                        </span>
                      </div>
                    </button>
                  );
                })}

                {filteredDocs.length === 0 && (
                  <div className="p-8 text-center bg-white rounded-xl border border-dashed border-slate-300 flex flex-col items-center">
                    <FileQuestion size={40} className="text-slate-300 mb-2" />
                    <p className="text-sm font-semibold text-slate-700">Không tìm thấy văn bản phù hợp</p>
                    <p className="text-xs text-slate-500 mt-1">Thử đổi từ khóa hoặc bấm nút "Tất cả" để xem toàn bộ danh mục.</p>
                  </div>
                )}
              </div>

              {/* CỘT PHẢI: KHUNG ĐỌC & INSPECTOR CHI TIẾT */}
              <div className="col-span-7 flex flex-col bg-white rounded-xl px-4 pt-4 border border-slate-200/80 shadow-sm h-[calc(100vh-220px)] overflow-hidden">
                {/* Header của văn bản */}
                <div className="flex flex-col gap-2.5 pb-3 border-b border-slate-100 shrink-0">
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`px-2 py-0.5 rounded-full text-[10.5px] font-bold border ${getDocTypeBadgeStyle(selectedDoc.category)}`}>
                        {selectedDoc.typeLabel}
                      </span>
                      {selectedDoc.isConsolidated && (
                        <span className="px-2 py-0.5 rounded-full text-[10.5px] font-bold bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-1">
                          <Layers size={11} /> Văn bản Hợp nhất
                        </span>
                      )}
                    </div>
                    {/* Chấm trạng thái chuẩn pháp lý */}
                    {renderStatusDot(selectedDoc.status)}
                  </div>

                  {selectedDoc.sourceUrl ? (
                    <a
                      href={selectedDoc.sourceUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group inline-block"
                      title={`Mở toàn văn văn bản gốc từ ${getSourceMeta(selectedDoc.sourceUrl)?.label || "cổng VBPL"}`}
                    >
                      <h2 className="text-lg font-bold text-primary-navy leading-snug tracking-tight group-hover:text-blue-600 group-hover:underline decoration-blue-500/50 underline-offset-4 transition-all cursor-pointer">
                        {selectedDoc.title}
                      </h2>
                    </a>
                  ) : (
                    <h2 className="text-lg font-bold text-primary-navy leading-snug tracking-tight">
                      {selectedDoc.title}
                    </h2>
                  )}

                  {/* Thanh Metadata phẳng (Flat Metadata Strip) - Toàn chiều ngang, ngăn cách bằng khoảng trắng */}
                  <div className="flex items-center gap-5 text-[12px] text-slate-500 pt-1 flex-wrap">
                    {/* Số hiệu chính + Micro Copy Icon */}
                    <div className="flex items-center gap-1 font-mono font-bold text-slate-800 shrink-0">
                      <span>{selectedDoc.number}</span>
                      <button
                        type="button"
                        onClick={() => handleCopyCitation(selectedDoc.number)}
                        className="p-1 rounded text-slate-400 hover:text-primary-navy hover:bg-slate-100 transition-colors cursor-pointer"
                        title="Sao chép số hiệu chính quy"
                      >
                        {isCopied ? (
                          <Check size={12} className="text-emerald-600" />
                        ) : (
                          <Copy size={12} />
                        )}
                      </button>
                    </div>

                    {/* Cơ quan ban hành */}
                    <div className="flex items-center gap-1 text-slate-600 shrink-0">
                      <Building2 size={12.5} className="text-slate-400 shrink-0" />
                      <span>{selectedDoc.issuer}</span>
                    </div>

                    {/* Ngày ban hành & Ngày có hiệu lực */}
                    <div className="flex items-center gap-2 text-[11.5px] text-slate-500 shrink-0">
                      <span title="Ngày ký ban hành văn bản">
                        <span className="text-slate-400">Ban hành:</span>{" "}
                        <span className="font-medium text-slate-600">{selectedDoc.date}</span>
                      </span>
                      <span className="text-slate-300">/</span>
                      <span title="Ngày chính thức có hiệu lực áp dụng">
                        <span className="text-slate-400">Hiệu lực:</span>{" "}
                        <span className="font-semibold text-emerald-700">{selectedDoc.effectiveDate || selectedDoc.date}</span>
                      </span>
                    </div>
                  </div>
                </div>

                {/* VÙNG NỘI DUNG CUỘN LIỀN MẠCH */}
                <div className="flex-1 overflow-y-auto px-1 pr-1.5 pt-3.5 pb-7 flex flex-col gap-4 min-h-0">
                  {/* KHỐI 1: TỔNG QUAN NỘI DUNG QUY ĐỊNH */}
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[11.5px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                      <Info size={13} className="text-primary-navy" />
                      Tóm lược nội dung quy định:
                    </span>
                    <p className="text-[13.5px] text-slate-700 leading-relaxed pl-3">
                      {selectedDoc.desc}
                    </p>
                  </div>

                  {/* KHỐI 2: PHẢ HỆ HỢP NHẤT / SỬA ĐỔI BỔ SUNG (Chỉ hiển thị khi có liên kết) */}
                  {hasLineage && (
                    <div className="flex flex-col gap-2.5 pt-3 border-t border-slate-100">
                      <div className="flex items-center justify-between">
                        <span className="text-[11.5px] font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
                          <GitBranch size={13} className="text-amber-600" />
                          {selectedDoc.isConsolidated ? "Phả hệ các văn bản cấu thành:" : "Văn bản gốc & sửa đổi liên quan:"}
                        </span>
                        <span className="text-[11px] text-slate-400">
                          {selectedDoc.isConsolidated ? "Quốc hội & Bộ Tư pháp" : "Công báo Chính phủ"}
                        </span>
                      </div>

                      <div className="flex flex-col gap-2 pl-3">
                        {selectedDoc.relatedDocs?.map((related, idx) => {
                          const isRoot = related.relationType === "goc";
                          const relSrcMeta = getSourceMeta(related.sourceUrl);
                          return (
                            <div
                              key={idx}
                              className={`p-3 rounded-xl border flex items-center justify-between gap-3 ${
                                isRoot
                                  ? "bg-slate-50/70 border-slate-200/80"
                                  : "bg-blue-50/40 border-blue-200/70"
                              }`}
                            >
                              <div className="flex items-center gap-3 min-w-0">
                                <div
                                  className={`w-10 h-10 rounded-lg shrink-0 flex items-center justify-center ${
                                    isRoot
                                      ? "bg-slate-200/80 text-slate-700"
                                      : "bg-blue-100 text-primary-navy"
                                  }`}
                                  title={isRoot ? "Văn bản gốc ban đầu" : "Văn bản sửa đổi, bổ sung"}
                                >
                                  {isRoot ? <BookOpen size={20} /> : <PenLine size={20} />}
                                </div>
                                <div className="flex flex-col min-w-0">
                                  <div className="flex items-center gap-1.5">
                                    <span
                                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                                        isRoot
                                          ? "bg-slate-200/70 text-slate-700"
                                          : "bg-blue-100 text-blue-800"
                                      }`}
                                    >
                                      {RELATION_LABELS[related.relationType]}
                                    </span>
                                    <span className="text-[11.5px] font-mono font-bold text-slate-700">
                                      {related.number}
                                    </span>
                                  </div>
                                  <p className="text-[12.5px] font-medium text-slate-800 mt-0.5 line-clamp-1">
                                    {related.title}
                                  </p>
                                </div>
                              </div>

                              {related.sourceUrl && (
                                <a
                                  href={related.sourceUrl}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className={`px-2.5 py-1 rounded text-[11px] font-semibold border inline-flex items-center gap-1 shrink-0 transition-colors ${
                                    relSrcMeta?.isOfficial
                                      ? "bg-white hover:bg-slate-50 text-slate-700 border-slate-200 shadow-2xs"
                                      : "bg-amber-50 hover:bg-amber-100/80 text-amber-800 border-amber-200"
                                  }`}
                                  title={`Mở toàn văn từ ${relSrcMeta?.label || "nguồn ngoài"}`}
                                >
                                  <span>{relSrcMeta?.isOfficial ? "Toàn văn" : (relSrcMeta?.label || "Tham khảo")}</span>
                                  <ExternalLink size={11.5} />
                                </a>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* KHỐI 3: TRỢ LÝ AI & TÌNH HUỐNG THỰC TẾ */}
                  <div className="flex flex-col gap-2.5 pt-3 border-t border-slate-100">
                    <div className="flex items-center justify-between">
                      <span className="text-[11.5px] font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1">
                        <Sparkles size={13} className="text-amber-500" />
                        Tình huống người dân thường hỏi:
                      </span>
                      <span className="text-[11px] text-slate-400">Bấm câu hỏi để chat với AI</span>
                    </div>

                    {selectedDoc.sampleAiPrompts && selectedDoc.sampleAiPrompts.length > 0 ? (
                      <div className="flex flex-col gap-2.5 p-1 pl-3">
                        {selectedDoc.sampleAiPrompts.map((prompt, idx) => (
                          <button
                            key={idx}
                            type="button"
                            onClick={() => handleAskAI(prompt)}
                            className="spotlight-border text-left p-3 rounded-xl bg-blue-50/60 border border-blue-200/60 text-primary-navy text-[13px] font-medium transition-all cursor-pointer inline-flex items-center justify-between gap-3 group shadow-2xs active:scale-[0.99] [--glow-color:#1C3D6E]"
                          >
                            <div className="flex items-center gap-2.5 min-w-0">
                              <span className="w-5 h-5 rounded-full bg-blue-100 text-primary-navy border border-blue-200/80 text-[10.5px] font-bold flex items-center justify-center shrink-0">
                                {idx + 1}
                              </span>
                              <span className="truncate">{prompt}</span>
                            </div>
                            <ChevronRight
                              size={14}
                              className="text-primary-navy/60 group-hover:text-primary-navy shrink-0 group-hover:translate-x-0.5 transition-transform"
                            />
                          </button>
                        ))}
                      </div>
                    ) : null}

                    <div className="pt-1 pl-3 pr-1">
                      <button
                        type="button"
                        onClick={() => {
                          setInputText(`Tôi có thắc mắc liên quan đến văn bản ${selectedDoc.number}: `);
                          setActiveTab("chat");
                        }}
                        className="w-full py-2.5 px-3 rounded-lg border border-dashed border-slate-300 hover:border-primary-navy/40 text-slate-600 hover:text-primary-navy text-[12.5px] font-medium transition-colors inline-flex items-center justify-center gap-2 cursor-pointer bg-slate-50/50 hover:bg-white"
                      >
                        <Bot size={14} className="text-primary-navy" />
                        <span>Soạn câu hỏi tùy chỉnh về văn bản này với AI...</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* ======================== CHẾ ĐỘ GRID / BENTO MATRIX ==================== */
            <div className="grid grid-cols-3 gap-4 overflow-y-auto max-h-[calc(100vh-210px)] p-1">
              {filteredDocs.map((doc) => (
                <div
                  key={doc.id}
                  className="bg-white rounded-xl p-5 border border-slate-200/90 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between gap-4 group spotlight-border"
                >
                  <div className="flex flex-col gap-2.5">
                    <div className="flex items-center justify-between gap-2">
                      <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold border ${getDocTypeBadgeStyle(doc.category)}`}>
                        {doc.typeLabel}
                      </span>
                      <span className="text-[11px] text-slate-500 font-medium" title="Ngày có hiệu lực thi hành">
                        HL: {doc.effectiveDate || doc.date}
                      </span>
                    </div>

                    <div className="font-mono text-[12px] font-bold text-slate-600 line-clamp-1">{doc.number}</div>

                    <h3 className="text-[15px] font-bold text-slate-900 group-hover:text-primary-navy transition-colors line-clamp-2 leading-snug">
                      {doc.title}
                    </h3>

                    <p className="text-[12.5px] text-slate-600 line-clamp-3 leading-relaxed">{doc.desc}</p>
                  </div>

                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedDocId(doc.id);
                        setViewMode("split");
                      }}
                      className="text-[12px] font-bold text-primary-navy hover:underline inline-flex items-center gap-1 cursor-pointer"
                    >
                      <span>Mở phân tích</span>
                      <ChevronRight size={13} />
                    </button>

                    <div className="flex items-center gap-1.5">
                      <button
                        type="button"
                        onClick={() => handleAskAI(`Giải thích quy định trọng yếu của văn bản ${doc.number}: ${doc.title}`)}
                        className="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-primary-navy cursor-pointer transition-colors"
                        title="Hỏi AI"
                      >
                        <Bot size={15} />
                      </button>
                      {doc.sourceUrl && (
                        <a
                          href={doc.sourceUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 rounded-md hover:bg-slate-100 text-slate-500 hover:text-primary-navy cursor-pointer transition-colors"
                          title="Mở cổng VBPL"
                        >
                          <ExternalLink size={15} />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
