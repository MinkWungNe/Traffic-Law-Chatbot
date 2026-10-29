"use client";

import React, { useState, useEffect } from "react";
import { fetchLegalDocuments, LegalDocItem } from "@/lib/api";
import {
  Search,
  X,
  FileQuestion,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  BookOpen,
  GitBranch,
  Layers,
} from "lucide-react";

export const LegalDocsView: React.FC = () => {
  const [docs, setDocs] = useState<LegalDocItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [expandedDocIds, setExpandedDocIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    fetchLegalDocuments()
      .then((res) => {
        if (isMounted) {
          setDocs(res || []);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const toggleExpand = (docId: string) => {
    setExpandedDocIds((prev) => {
      const next = new Set(prev);
      if (next.has(docId)) {
        next.delete(docId);
      } else {
        next.add(docId);
      }
      return next;
    });
  };

  const filteredDocs = docs.filter((doc) => {
    const matchCat = activeCategory === "all" || doc.category === activeCategory;
    const matchSearch =
      !searchTerm ||
      doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.desc.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (doc.relatedDocs &&
        doc.relatedDocs.some(
          (r) =>
            r.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            r.number.toLowerCase().includes(searchTerm.toLowerCase())
        ));
    return matchCat && matchSearch;
  });

  return (
    <div className="absolute inset-0 w-full h-full overflow-y-auto px-4 md:px-8 py-8 z-10 select-text">
      <div className="max-w-4xl mx-auto flex flex-col gap-6 pb-20">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
            Tra cứu Văn bản Quy phạm Pháp luật
          </h1>
          <p className="text-sm md:text-base text-slate-600 leading-relaxed">
            Danh mục các văn bản luật giao thông đường bộ cốt lõi, nguồn dữ liệu được đồng bộ từ Cơ sở dữ liệu quốc gia về văn bản pháp luật (vbpl.vn).
          </p>
        </div>

        {/* Search Bar & Filter */}
        <div className="bg-white rounded-xl p-4 shadow-sm border border-subtle flex flex-col gap-4">
          <div className="relative flex items-center">
            <Search size={20} className="absolute left-4 text-slate-400 shrink-0 pointer-events-none" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Nhập số hiệu văn bản, từ khóa pháp lý (ví dụ: 100/2015, 36/2024, nồng độ cồn, cảnh vệ)..."
              className="w-full bg-canvas text-slate-900 text-sm md:text-base pl-12 pr-12 py-3 rounded-lg border border-subtle focus:outline-none focus:bg-white focus:border-slate-300 transition-all placeholder:text-slate-400"
            />
            {searchTerm && (
              <button
                type="button"
                onClick={() => setSearchTerm("")}
                className="absolute right-3 p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full cursor-pointer flex items-center justify-center"
              >
                <X size={16} className="shrink-0" />
              </button>
            )}
          </div>

          {/* Filter Chips */}
          <div className="flex items-center gap-2 flex-wrap pt-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mr-1">Loại văn bản:</span>
            {[
              { id: "all", label: "Tất cả" },
              { id: "luat", label: "Luật & Bộ luật" },
              { id: "nghi-dinh", label: "Nghị định" },
              { id: "thong-tu", label: "Thông tư" },
              { id: "quy-chuan", label: "Quy chuẩn kỹ thuật" },
            ].map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`px-3 py-1 rounded-full text-[12px] font-semibold transition-all cursor-pointer ${
                  activeCategory === cat.id
                    ? "bg-primary-navy text-white shadow-xs"
                    : "bg-canvas hover:bg-slate-100 text-slate-600 border border-slate-200"
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Docs List */}
        <div className="flex flex-col gap-4">
          {isLoading ? (
            <div className="flex flex-col gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs h-36 animate-pulse" />
              ))}
            </div>
          ) : (
            <>
              {filteredDocs.map((doc) => {
                const isConsolidated = !!doc.isConsolidated && (doc.relatedDocs?.length || 0) > 0;
                const isExpanded = expandedDocIds.has(doc.id);

                return (
                  <div
                    key={doc.id}
                    className={`bg-white rounded-xl p-5 border transition-all flex flex-col gap-3 group ${
                      isExpanded
                        ? "border-primary-navy/40 shadow-sm ring-1 ring-primary-navy/10"
                        : "border-slate-200/80 shadow-xs hover:shadow-md"
                    }`}
                  >
                    {/* Header Badges */}
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${doc.typeBadgeBg} ${doc.typeBadgeText}`}>
                          {doc.typeLabel}
                        </span>
                        {isConsolidated && (
                          <span className="px-2 py-0.5 rounded-full text-[11px] font-bold border bg-amber-50 text-amber-800 border-amber-200 flex items-center gap-1">
                            <Layers size={11} className="shrink-0" />
                            Văn bản hợp nhất
                          </span>
                        )}
                        <span className="text-[12px] font-medium text-slate-500 font-mono">{doc.number}</span>
                        <span className="text-[12px] text-slate-400">• Ngày ban hành: {doc.date}</span>
                      </div>
                      <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
                        {doc.status}
                      </span>
                    </div>

                    {/* Title & Interactive Toggle */}
                    {isConsolidated ? (
                      <div className="flex flex-col gap-2">
                        <button
                          type="button"
                          onClick={() => toggleExpand(doc.id)}
                          className="text-left group/btn flex items-start justify-between gap-3 text-[16px] font-bold text-slate-900 leading-snug hover:text-primary-navy transition-colors cursor-pointer select-none"
                          title="Bấm để xem danh sách văn bản gốc và văn bản sửa đổi bổ sung"
                        >
                          <span className="flex-1">{doc.title}</span>
                          <span
                            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[12px] font-semibold transition-all shrink-0 mt-0.5 ${
                              isExpanded
                                ? "bg-primary-navy text-white shadow-xs"
                                : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                            }`}
                          >
                            <span>{isExpanded ? "Đóng nguồn" : "Xem nguồn"}</span>
                            {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                          </span>
                        </button>
                      </div>
                    ) : (
                      <div>
                        {doc.sourceUrl ? (
                          <a
                            href={doc.sourceUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[16px] font-bold text-slate-900 leading-snug hover:text-primary-navy transition-colors inline-flex items-center gap-2 cursor-pointer"
                            title="Mở văn bản trên vbpl.vn tại tab mới"
                          >
                            <span>{doc.title}</span>
                            <ExternalLink size={15} className="text-slate-400 group-hover:text-primary-navy shrink-0 transition-colors" />
                          </a>
                        ) : (
                          <h3 className="text-[16px] font-bold text-slate-900 leading-snug">{doc.title}</h3>
                        )}
                      </div>
                    )}

                    {/* Description */}
                    <p className="text-[13px] text-slate-600 leading-relaxed">{doc.desc}</p>

                    {/* Dropdown Menu for Consolidated Documents */}
                    {isConsolidated && isExpanded && doc.relatedDocs && (
                      <div className="mt-1 pt-3 border-t border-slate-100 flex flex-col gap-3 animate-in fade-in duration-150">
                        <div className="flex items-center justify-between">
                          <span className="text-[12px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                            <BookOpen size={14} className="text-primary-navy" />
                            Danh sách văn bản cấu thành (Nguồn vbpl.vn):
                          </span>
                          {doc.sourceUrl && (
                            <a
                              href={doc.sourceUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-2.5 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 rounded-md text-[12px] font-semibold transition-all inline-flex items-center gap-1.5 shrink-0 shadow-2xs"
                              title="Mở toàn văn văn bản hợp nhất trên vbpl.vn"
                            >
                              <span>Xem văn bản hợp nhất</span>
                              <ExternalLink size={12} />
                            </a>
                          )}
                        </div>

                        <div className="grid grid-cols-1 gap-2.5">
                          {doc.relatedDocs.map((related, idx) => {
                            const isRoot = related.relationType === "goc";
                            return (
                              <div
                                key={idx}
                                className={`rounded-lg p-3 border flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 transition-colors ${
                                  isRoot
                                    ? "bg-slate-50/90 border-slate-200/80 hover:bg-slate-100/70"
                                    : "bg-blue-50/40 border-blue-100 hover:bg-blue-50/70"
                                }`}
                              >
                                <div className="flex items-start gap-2.5 min-w-0">
                                  <div
                                    className={`mt-0.5 p-1.5 rounded shrink-0 ${
                                      isRoot ? "bg-slate-200 text-slate-700" : "bg-blue-100 text-blue-700"
                                    }`}
                                  >
                                    {isRoot ? <BookOpen size={14} /> : <GitBranch size={14} />}
                                  </div>
                                  <div className="flex flex-col min-w-0">
                                    <div className="flex items-center gap-2 flex-wrap">
                                      <span
                                        className={`text-[11px] font-bold px-2 py-0.2 rounded-full border ${
                                          isRoot
                                            ? "bg-white border-slate-300 text-slate-700"
                                            : "bg-white border-blue-200 text-blue-700"
                                        }`}
                                      >
                                        {related.relationLabel}
                                      </span>
                                      <span className="text-[12px] font-mono font-medium text-slate-600">
                                        {related.number}
                                      </span>
                                    </div>
                                    <p className="text-[13px] font-medium text-slate-900 mt-0.5 leading-snug line-clamp-2">
                                      {related.title}
                                    </p>
                                  </div>
                                </div>

                                <a
                                  href={related.sourceUrl}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="self-end sm:self-center px-3 py-1.5 bg-white hover:bg-primary-navy hover:text-white border border-slate-200 text-slate-700 rounded-md text-[12px] font-semibold transition-all inline-flex items-center gap-1.5 shrink-0 shadow-2xs"
                                  title={`Mở ${related.number} trên Cổng VBPL`}
                                >
                                  <span>{isRoot ? "Xem văn bản gốc" : "Xem văn bản sửa đổi"}</span>
                                  <ExternalLink size={13} />
                                </a>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}

              {filteredDocs.length === 0 && (
                <div className="text-center py-12 text-slate-400 flex flex-col items-center">
                  <FileQuestion size={44} className="mb-2 text-slate-300" />
                  <p>Không tìm thấy văn bản phù hợp với từ khóa.</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
