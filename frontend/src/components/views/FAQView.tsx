"use client";

import React, { useState } from "react";
import { useChatStore } from "@/stores/useChatStore";
import { Search, X, ChevronDown, AlertTriangle, Bot } from "lucide-react";

interface FAQItem {
  id: string;
  category: "xemay" | "oto" | "nongdocon" | "tocdo" | "gplx" | "phatnguoi";
  catLabel: string;
  question: string;
  answer: string;
  lawCite: string;
  penaltySummary: string;
}

const SAMPLE_FAQS: FAQItem[] = [
  {
    id: "faq-1",
    category: "xemay",
    catLabel: "Xe máy",
    question: "Xe máy rẽ phải khi đèn đỏ không có biển báo phụ thì bị phạt bao nhiêu tiền?",
    answer: "Người điều khiển xe máy rẽ phải khi đèn đỏ mà không có hiệu lệnh của CSGT, đèn mũi tên xanh hoặc biển phụ 'Đèn đỏ được phép rẽ phải' là hành vi không chấp hành hiệu lệnh của đèn tín hiệu giao thông.",
    penaltySummary: "Phạt tiền từ 800.000đ – 1.000.000đ. Tước quyền sử dụng Giấy phép lái xe từ 01 – 03 tháng.",
    lawCite: "Điểm e Khoản 4 và Điểm b Khoản 10 Điều 6 Nghị định 100/2019/NĐ-CP.",
  },
  {
    id: "faq-2",
    category: "nongdocon",
    catLabel: "Nồng độ cồn",
    question: "Mức phạt nồng độ cồn kịch khung đối với xe máy và ô tô năm 2026?",
    answer: "Khi nồng độ cồn vượt quá 80mg/100ml máu hoặc 0.4mg/1 lít khí thở: Xe máy bị phạt từ 6 - 8 triệu đồng, tước bằng 22 - 24 tháng, tạm giữ xe đến 7 ngày. Ô tô bị phạt từ 30 - 40 triệu đồng, tước bằng 22 - 24 tháng, tạm giữ xe đến 7 ngày.",
    penaltySummary: "Xe máy: 6-8 triệu đ | Ô tô: 30-40 triệu đ. Tước GPLX 22 - 24 tháng.",
    lawCite: "Điều 5 và Điều 6 Nghị định 100/2019/NĐ-CP.",
  },
  {
    id: "faq-3",
    category: "tocdo",
    catLabel: "Tốc độ",
    question: "Chạy quá tốc độ từ 10km/h đến 20km/h bị phạt bao nhiêu?",
    answer: "Đối với xe máy: Phạt tiền từ 800.000đ - 1.000.000đ. Đối với ô tô: Phạt tiền từ 4.000.000đ - 6.000.000đ và tước GPLX từ 01 - 03 tháng.",
    penaltySummary: "Xe máy: 800k - 1 triệu đ | Ô tô: 4 - 6 triệu đ (tước GPLX 1 - 3 tháng).",
    lawCite: "Điểm a Khoản 4 Điều 6 (xe máy) & Điểm i Khoản 5 Điều 5 (ô tô) Nghị định 100/2019/NĐ-CP.",
  },
  {
    id: "faq-4",
    category: "phatnguoi",
    catLabel: "Phạt nguội",
    question: "Làm thế nào để kiểm tra và nộp phạt nguội online toàn quốc?",
    answer: "Người dân có thể tra cứu phạt nguội qua Cổng thông tin điện tử Cục Cảnh sát giao thông (csgt.vn) hoặc ứng dụng VNeID. Nộp phạt trực tuyến nhanh gọn qua Cổng Dịch vụ công Quốc gia (dichvucong.gov.vn) bằng mã quyết định xử phạt.",
    penaltySummary: "Nộp trực tuyến không cần đến trực tiếp trụ sở công an, biên lai điện tử có giá trị pháp lý.",
    lawCite: "Thông tư 15/2022/TT-BCA và quy chế Cổng Dịch vụ công Quốc gia.",
  },
];

export const FAQView: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [expandedId, setExpandedId] = useState<string | null>("faq-1");
  const { setActiveTab, sendMessage } = useChatStore();

  const filteredFaqs = SAMPLE_FAQS.filter((faq) => {
    const matchCat = activeCategory === "all" || faq.category === activeCategory;
    const matchSearch =
      !searchTerm ||
      faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      faq.penaltySummary.toLowerCase().includes(searchTerm.toLowerCase());
    return matchCat && matchSearch;
  });

  return (
    <div className="absolute inset-0 w-full h-full overflow-y-auto px-4 md:px-8 py-8 z-10 select-text">
      <div className="max-w-4xl mx-auto flex flex-col gap-6 pb-20">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
            Câu hỏi Thường gặp về Giao thông &amp; Xử phạt
          </h1>
          <p className="text-sm md:text-base text-slate-600 leading-relaxed">
            Tổng hợp các thắc mắc và tình huống pháp lý phổ biến được người dân hỏi nhiều nhất qua Trợ lý AI.
          </p>
        </div>

        {/* Search & Filters */}
        <div className="bg-white rounded-xl p-4 shadow-sm border border-subtle flex flex-col gap-4">
          <div className="relative flex items-center">
            <Search size={20} className="absolute left-4 text-slate-400 shrink-0 pointer-events-none" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm kiếm câu hỏi, tình huống xử phạt (VD: nồng độ cồn, vượt đèn đỏ, bằng lái)..."
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

          <div className="flex items-center gap-2 flex-wrap pt-1">
            {[
              { id: "all", label: "Tất cả" },
              { id: "xemay", label: "Xe máy" },
              { id: "oto", label: "Ô tô" },
              { id: "nongdocon", label: "Nồng độ cồn" },
              { id: "tocdo", label: "Tốc độ" },
              { id: "phatnguoi", label: "Phạt nguội" },
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

        {/* FAQs Accordion List */}
        <div className="flex flex-col gap-3">
          {filteredFaqs.map((faq) => {
            const isExpanded = expandedId === faq.id;
            return (
              <div
                key={faq.id}
                className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden transition-all"
              >
                <button
                  type="button"
                  onClick={() => setExpandedId(isExpanded ? null : faq.id)}
                  className="w-full p-4 flex items-center justify-between gap-4 text-left hover:bg-slate-50/60 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-50 text-primary-navy border border-blue-100 shrink-0">
                      {faq.catLabel}
                    </span>
                    <span className="font-bold text-slate-900 text-[14.5px]">{faq.question}</span>
                  </div>
                  <ChevronDown
                    size={18}
                    className={`text-slate-400 transition-transform shrink-0 ${
                      isExpanded ? "rotate-180 text-primary-navy" : ""
                    }`}
                  />
                </button>

                {isExpanded && (
                  <div className="px-5 pb-5 pt-1 border-t border-slate-100 flex flex-col gap-3 text-[13.5px] leading-relaxed text-slate-700">
                    <p>{faq.answer}</p>
                    <div className="p-3 rounded-lg bg-amber-50/60 border border-amber-200/80 text-amber-900 font-medium text-[12.5px] flex items-center gap-2">
                      <AlertTriangle size={16} className="text-amber-600 shrink-0" />
                      <span>{faq.penaltySummary}</span>
                    </div>
                    <div className="text-[12px] text-slate-500 italic">Căn cứ: {faq.lawCite}</div>

                    <div className="pt-2 flex justify-end">
                      <button
                        type="button"
                        onClick={() => {
                          setActiveTab("chat");
                          sendMessage(faq.question);
                        }}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary-navy hover:bg-blue-900 text-white font-medium text-[12px] shadow-xs cursor-pointer transition-colors"
                      >
                        <Bot size={15} className="shrink-0" />
                        <span>Hỏi sâu hơn về tình huống này</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
