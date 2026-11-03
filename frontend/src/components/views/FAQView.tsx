"use client";

import React, { useState, useMemo, useEffect, useRef } from "react";
import { useChatStore } from "@/stores/useChatStore";
import { FAQ_ITEMS, FAQ_TOPICS } from "@/data/faqData";
import {
  Search,
  X,
  Bot,
  Sparkles,
  Filter,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  ShieldAlert,
  Wine,
  Gauge,
  Camera,
  Route,
  FileText,
  Layers,
  Info,
  Scale,
  Car,
  Bike,
  CheckCircle2,
} from "lucide-react";

// Ánh xạ icon chuyên đề pháp luật (Object lookup thay cho switch-case)
const TOPIC_ICON_MAP: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  Layers,
  Wine,
  ShieldAlert,
  AlertTriangle,
  Gauge,
  Camera,
  Route,
  FileText,
};

const renderTopicIcon = (iconName: string, className = "shrink-0") => {
  const Icon = TOPIC_ICON_MAP[iconName] || Info;
  return <Icon size={15} className={className} />;
};

// Đếm số lượng câu hỏi thuộc từng chuyên đề (tính tĩnh 1 lần ở module scope)
const TOPIC_COUNTS: Record<string, number> = {
  all: FAQ_ITEMS.length,
  ...FAQ_ITEMS.reduce<Record<string, number>>((acc, item) => {
    acc[item.topicId] = (acc[item.topicId] || 0) + 1;
    return acc;
  }, {}),
};

export const FAQView: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTopic, setActiveTopic] = useState<string>("all");
  const [filterHasPoints, setFilterHasPoints] = useState(false);
  const [filterHasDetention, setFilterHasDetention] = useState(false);
  const [filterIsSevere, setFilterIsSevere] = useState(false);

  // Quản lý trạng thái mở rộng duy nhất 1 thẻ tại 1 thời điểm (Strict Accordion)
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const searchInputRef = useRef<HTMLInputElement>(null);
  const { setActiveTab, sendMessage, setInputText } = useChatStore();

  // Phím tắt '/' để focus vào ô tìm kiếm, 'Esc' để xóa nội dung
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

  // Bộ lọc dữ liệu đa tiêu chí (Early return ngắt sớm tối ưu hiệu năng)
  const filteredFaqs = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    return FAQ_ITEMS.filter((item) => {
      if (activeTopic !== "all" && item.topicId !== activeTopic) return false;
      if (filterHasPoints && item.pointsDeducted <= 0) return false;
      if (filterHasDetention && !item.detentionDays) return false;
      if (filterIsSevere && !item.isSevere) return false;
      if (!term) return true;

      return (
        item.question.toLowerCase().includes(term) ||
        item.fullAnswer.toLowerCase().includes(term) ||
        item.penaltyMoney.toLowerCase().includes(term) ||
        item.lawCite.toLowerCase().includes(term)
      );
    });
  }, [searchTerm, activeTopic, filterHasPoints, filterHasDetention, filterIsSevere]);

  // Kiểm tra xem có bộ lọc nào đang được kích hoạt hay không
  const hasActiveFilters =
    activeTopic !== "all" ||
    filterHasPoints ||
    filterHasDetention ||
    filterIsSevere ||
    Boolean(searchTerm.trim());

  // Đặt lại toàn bộ bộ lọc
  const handleResetFilters = () => {
    setActiveTopic("all");
    setFilterHasPoints(false);
    setFilterHasDetention(false);
    setFilterIsSevere(false);
    setSearchTerm("");
  };

  // Chuyển đổi trạng thái mở rộng của một thẻ (Chỉ 1 thẻ mở tại 1 thời điểm)
  const toggleExpand = (id: string) => {
    setExpandedId((curr) => (curr === id ? null : id));
  };

  // Chuyển câu hỏi sang Tab Chatbot AI và kích hoạt truy vấn tự động
  const handleAskAI = (promptText: string) => {
    setActiveTab("chat");
    setInputText(promptText);
    sendMessage(promptText);
  };

  // Thông tin chuyên đề đang được chọn
  const currentTopicMeta = FAQ_TOPICS.find((t) => t.id === activeTopic) || FAQ_TOPICS[0];

  return (
    <div className="absolute inset-0 w-full h-full overflow-hidden px-5 py-5 z-10 select-text flex flex-col">
      <div className="max-w-7xl w-full mx-auto flex flex-col gap-3 flex-1 min-h-0">
        {/* ========================================================================= */}
        {/* HEADER CĂN GIỮA NGOÀI KHUNG (ĐỒNG BỘ DESIGN SYSTEM)                         */}
        {/* ========================================================================= */}
        <header className="w-full text-center py-1 shrink-0 flex flex-col items-center">
          <h1 className="text-2xl font-extrabold text-primary-navy tracking-tight">
            Câu hỏi Thường gặp về Giao thông &amp; Xử phạt
          </h1>
        </header>

        {/* ========================================================================= */}
        {/* KHUNG HỢP NHẤT TOÀN DIỆN (UNIFIED WORKSPACE CONTAINER)                     */}
        {/* ========================================================================= */}
        <div className="w-full bg-white/70 rounded-2xl border border-slate-200/80 shadow-md p-4 flex flex-col gap-3.5 flex-1 min-h-0 overflow-hidden">
          {/* THANH TÌM KIẾM SPOTLIGHT TOÀN PHẦN */}
          <div className="flex items-center gap-2.5 shrink-0">
            <div className="spotlight-border relative flex-1 flex items-center bg-white rounded-lg border border-slate-200 focus-within:border-primary-navy/40 transition-colors [--glow-color:#94A3B8] [--glow-size:240px]">
              <Search size={17} className="absolute left-3.5 text-slate-400 pointer-events-none shrink-0" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Tìm tình huống vi phạm (VD: rẽ phải đèn đỏ, nồng độ cồn, trừ 10 điểm, phạt nguội xe thuê)... (Bấm '/' để tìm)"
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

            {hasActiveFilters && (
              <button
                type="button"
                onClick={handleResetFilters}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-[12px] font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 border border-slate-200 cursor-pointer transition-colors shrink-0"
                title="Khôi phục trạng thái mặc định"
              >
                <RotateCcw size={13} />
                <span>Đặt lại lọc</span>
              </button>
            )}
          </div>

          {/* VÙNG LÀM VIỆC 2 CỘT (TOPIC INDEX RAIL + KNOWLEDGE FEED) */}
          <div className="flex-1 flex gap-4 min-h-0 overflow-hidden">
            {/* CỘT TRÁI (260px CỐ ĐỊNH): THANH ĐIỀU HƯỚNG CHUYÊN ĐỀ & BỘ LỌC CHẾ TÀI */}
            <aside className="w-[260px] shrink-0 flex flex-col gap-3.5 overflow-hidden border-r border-slate-200/80 pr-3">
              {/* PHẦN 1: DANH MỤC CHUYÊN ĐỀ PHÁP LUẬT */}
              <div className="flex-1 min-h-0 flex flex-col gap-1 overflow-hidden">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-1">
                  Chuyên đề pháp luật
                </span>
                <div className="flex-1 min-h-0 flex flex-col gap-1.5 overflow-y-auto p-1">
                  {FAQ_TOPICS.map((topic) => {
                    const isActive = activeTopic === topic.id;
                    const count = TOPIC_COUNTS[topic.id] || 0;
                    return (
                      <button
                        key={topic.id}
                        type="button"
                        onClick={() => setActiveTopic(topic.id)}
                        className={`spotlight-border [--glow-size:50px] [--border-width:1px] flex items-center justify-between px-2.5 py-1.5 rounded-xl text-[12.5px] text-left transition-all cursor-pointer ${
                          isActive
                            ? "opacity-100 bg-white font-bold text-primary-navy shadow-sm border border-primary-navy/30 ring-1 ring-primary-navy/15"
                            : "opacity-80 text-slate-700 hover:opacity-100 hover:text-slate-900 hover:bg-white/80 border border-transparent"
                        }`}
                      >
                        <div className="flex items-center gap-2 min-w-0 pr-1">
                          {renderTopicIcon(
                            topic.iconName,
                            isActive ? "text-accent-red" : "text-slate-500 transition-colors"
                          )}
                          <span className="truncate">{topic.label}</span>
                        </div>
                        <span
                          className={`text-[10.5px] px-1.5 py-0.5 rounded-full font-mono shrink-0 transition-colors ${
                            isActive
                              ? "bg-primary-navy/10 text-primary-navy font-bold"
                              : "bg-slate-200/70 text-slate-600"
                          }`}
                        >
                          {count}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* PHẦN 2: BỘ LỌC CHẾ TÀI NHANH */}
              <div className="flex flex-col gap-1.5 pt-2 border-t border-slate-200/80 shrink-0">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-1 flex items-center gap-1">
                  <Filter size={12} /> Lọc chế tài vi phạm
                </span>

                <label className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg cursor-pointer text-[12px] opacity-80 hover:opacity-100 text-slate-600 hover:text-slate-900 select-none transition-colors">
                  <input
                    type="checkbox"
                    checked={filterHasPoints}
                    onChange={(e) => setFilterHasPoints(e.target.checked)}
                    className="w-3.5 h-3.5 rounded text-primary-navy focus:ring-primary-navy/40 accent-primary-navy cursor-pointer"
                  />
                  <span>Có trừ điểm GPLX</span>
                </label>

                <label className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg cursor-pointer text-[12px] opacity-80 hover:opacity-100 text-slate-600 hover:text-slate-900 select-none transition-colors">
                  <input
                    type="checkbox"
                    checked={filterHasDetention}
                    onChange={(e) => setFilterHasDetention(e.target.checked)}
                    className="w-3.5 h-3.5 rounded text-primary-navy focus:ring-primary-navy/40 accent-primary-navy cursor-pointer"
                  />
                  <span>Có tạm giữ phương tiện</span>
                </label>

                <label className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg cursor-pointer text-[12px] opacity-80 hover:opacity-100 text-slate-600 hover:text-slate-900 select-none transition-colors">
                  <input
                    type="checkbox"
                    checked={filterIsSevere}
                    onChange={(e) => setFilterIsSevere(e.target.checked)}
                    className="w-3.5 h-3.5 rounded text-primary-navy focus:ring-primary-navy/40 accent-primary-navy cursor-pointer"
                  />
                  <span>Mức phạt trên 5.000.000đ</span>
                </label>
              </div>
            </aside>

            {/* CỘT PHẢI (FLEX-1 CUỘN ĐỘC LẬP): FEED THẺ HỒ SƠ PHÁP LÝ (LEGAL FACT SHEETS) */}
            <main className="flex-1 flex flex-col min-h-0 overflow-hidden">
              {/* THANH TRẠNG THÁI FEED TRÊN CÙNG */}
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-200/60 shrink-0">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-[14.5px] text-primary-navy">
                    {currentTopicMeta.label}
                  </span>
                </div>

                {expandedId && (
                  <button
                    type="button"
                    onClick={() => setExpandedId(null)}
                    className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-navy hover:text-blue-900 cursor-pointer transition-colors"
                  >
                    <ChevronUp size={14} />
                    <span>Thu gọn thẻ đang xem</span>
                  </button>
                )}
              </div>

              {/* DANH SÁCH CUỘN THẺ CÂU HỎI */}
              <div className="flex-1 overflow-y-auto pr-1.5 p-1 flex flex-col gap-3 min-h-0">
                {filteredFaqs.length === 0 ? (
                  /* EMPTY STATE KHI KHÔNG TÌM THẤY KẾT QUẢ */
                  <div className="flex-1 flex flex-col items-center justify-center p-8 text-center gap-3 bg-white/40 rounded-xl border border-dashed border-slate-200">
                    <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
                      <Search size={22} />
                    </div>
                    <div className="flex flex-col gap-1 max-w-md">
                      <h3 className="font-bold text-slate-800 text-[15px]">
                        Không tìm thấy tình huống phù hợp
                      </h3>
                      <p className="text-[12.5px] text-slate-500 leading-relaxed">
                        Không có câu hỏi thường gặp nào khớp với từ khóa hoặc bộ lọc đã chọn. Bạn có thể đặt câu hỏi trực tiếp cho Trợ lý AI để được tra cứu toàn văn các văn bản pháp luật.
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleAskAI(searchTerm || "Tôi muốn hỏi về quy định xử phạt vi phạm giao thông.")}
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-primary-navy hover:bg-slate-800 text-white font-semibold text-[13px] shadow-xs cursor-pointer transition-all mt-1"
                    >
                      <Bot size={16} />
                      <span>Hỏi Trợ lý AI về câu này</span>
                    </button>
                  </div>
                ) : (
                  /* DANH SÁCH THẺ FACT SHEET */
                  filteredFaqs.map((faq) => {
                    const isExpanded = expandedId === faq.id;

                    return (
                      <article
                        key={faq.id}
                        className={`spotlight-border shrink-0 bg-white rounded-xl border transition-all duration-150 ${
                          isExpanded
                            ? "border-primary-navy/30 shadow-xs"
                            : "border-slate-200/80 hover:shadow-2xs"
                        }`}
                      >
                        {/* KHỐI TRIGGER THẺ (CLICK TOÀN BỘ ĐỂ ĐÓNG/MỞ) */}
                        <div
                          onClick={() => toggleExpand(faq.id)}
                          className="p-3.5 cursor-pointer select-none flex flex-col gap-2 group/card"
                          role="button"
                          tabIndex={0}
                          onKeyDown={(e) => {
                            if (e.key === "Enter" || e.key === " ") {
                              e.preventDefault();
                              toggleExpand(faq.id);
                            }
                          }}
                          aria-expanded={isExpanded}
                        >
                          {/* HÀNG 1: METADATA BADGES & NÚT TRẠNG THÁI */}
                          <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-1.5 flex-wrap">
                              {/* Phân loại phương tiện */}
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-slate-100 text-slate-700 shrink-0">
                                {faq.vehicleType === "xemay" && <Bike size={12} className="text-slate-500" />}
                                {faq.vehicleType === "oto" && <Car size={12} className="text-slate-500" />}
                                {faq.vehicleType === "chung" && <Scale size={12} className="text-slate-500" />}
                                <span>{faq.vehicleLabel}</span>
                              </span>

                              {/* Chuyên đề */}
                              <span className="px-2 py-0.5 rounded-md text-[11px] font-semibold bg-blue-50 text-primary-navy border border-blue-100/80 shrink-0">
                                {faq.topicLabel}
                              </span>

                              {/* Chế tài nghiêm trọng */}
                              {faq.isSevere && (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10.5px] font-bold bg-red-50 text-accent-red border border-red-200/60 shrink-0">
                                  <AlertTriangle size={11} />
                                  <span>Nghiêm trọng</span>
                                </span>
                              )}
                            </div>

                            {/* Nút Chevron trạng thái */}
                            <div className="flex items-center gap-1 text-[11.5px] font-semibold text-slate-400 group-hover/card:text-primary-navy transition-colors shrink-0">
                              <span>{isExpanded ? "Thu gọn" : "Chi tiết"}</span>
                              <ChevronDown
                                size={15}
                                className={`transition-transform duration-200 ${
                                  isExpanded ? "rotate-180 text-primary-navy" : ""
                                }`}
                              />
                            </div>
                          </div>

                          {/* HÀNG 2: TIÊU ĐỀ CÂU HỎI */}
                          <h2 className="text-[14.5px] font-bold text-slate-900 group-hover/card:text-primary-navy transition-colors leading-snug">
                            {faq.question}
                          </h2>

                          {/* HÀNG 3: DẢI CHẾ TÀI CỐT LÕI (INLINE SPECS - GỌN GÀNG, KHÔNG LỒNG CARD, KHÔNG TRÙNG LẶP) */}
                          <div className="flex items-center gap-2 flex-wrap text-[11.5px] pt-0.5">
                            <span className="font-semibold text-slate-700">
                              Mức phạt: <span className="font-bold text-primary-navy">{faq.penaltyMoney}</span>
                            </span>

                            {faq.pointsDeducted > 0 && (
                              <>
                                <span className="text-slate-300">•</span>
                                <span className="inline-flex items-center gap-1 font-bold text-accent-red">
                                  <ShieldAlert size={12} />
                                  <span>Trừ {faq.pointsDeducted} điểm GPLX</span>
                                </span>
                              </>
                            )}

                            {faq.detentionDays && (
                              <>
                                <span className="text-slate-300">•</span>
                                <span className="inline-flex items-center gap-1 font-semibold text-amber-800">
                                  <AlertTriangle size={12} />
                                  <span>{faq.detentionDays}</span>
                                </span>
                              </>
                            )}
                          </div>
                        </div>

                        {/* KHỐI NỘI DUNG CHI TIẾT (MỞ RỘNG ACCORDION MƯỢT MÀ) */}
                        <div
                          className={`grid transition-[grid-template-rows] duration-300 ease-out ${
                            isExpanded ? "grid-rows-[1fr]" : "grid-rows-[0fr]"
                          }`}
                        >
                          <div className="overflow-hidden">
                            <div className="px-3.5 pb-3.5 pt-2.5 border-t border-slate-100 flex flex-col gap-2.5 text-[12.5px] text-slate-600 leading-relaxed">
                            <div>
                              <span className="font-bold text-slate-800">Giải thích chi tiết: </span>
                              <span>{faq.fullAnswer}</span>
                            </div>

                            {faq.exceptions && (
                              <div className="p-2.5 rounded-lg bg-emerald-50/70 border border-emerald-200/80 text-emerald-950 flex items-start gap-2">
                                <CheckCircle2 size={15} className="text-emerald-700 shrink-0 mt-0.5" />
                                <div>
                                  <span className="font-bold">Trường hợp không bị phạt / Ngoại lệ: </span>
                                  <span>{faq.exceptions}</span>
                                </div>
                              </div>
                            )}

                            {/* 3. CĂN CỨ PHÁP LÝ */}
                            <div className="text-[11.5px] text-slate-600 font-mono bg-slate-50 p-2.5 rounded-lg border border-slate-200/60 leading-relaxed">
                              <span className="font-bold text-slate-700">Căn cứ pháp lý: </span>
                              <span>{faq.lawCite}</span>
                            </div>

                            {/* 4. FOOTER MỞ RỘNG: GỢI Ý HỎI TIẾP VÀ NÚT HỎI SÂU CÙNG AI */}
                            <div className="pt-2 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                              {faq.aiPrompts && faq.aiPrompts.length > 0 ? (
                                <div className="flex items-center gap-1.5 flex-wrap flex-1 min-w-0">
                                  <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1 shrink-0">
                                    <Sparkles size={11} className="text-accent-red" /> Gợi ý hỏi tiếp:
                                  </span>
                                  {faq.aiPrompts.map((prompt, idx) => (
                                    <button
                                      key={idx}
                                      type="button"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleAskAI(prompt);
                                      }}
                                      className="px-2 py-0.5 rounded-full bg-slate-100 hover:bg-blue-50 hover:text-primary-navy hover:border-blue-200 border border-slate-200 text-slate-600 text-[11px] transition-colors cursor-pointer truncate max-w-[280px] text-left"
                                      title={prompt}
                                    >
                                      &ldquo;{prompt}&rdquo;
                                    </button>
                                  ))}
                                </div>
                              ) : <div />}

                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleAskAI(faq.question);
                                }}
                                className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary-navy hover:bg-slate-800 text-white font-semibold text-[11.5px] shadow-2xs transition-all cursor-pointer shrink-0"
                              >
                                <Bot size={13} />
                                <span>Hỏi sâu cùng AI →</span>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                      </article>
                    );
                  })
                )}
              </div>
            </main>
          </div>
        </div>
      </div>
    </div>
  );
};
