"use client";

import React, { useState, useEffect } from "react";
import { fetchLegalDocuments, LegalDocItem } from "@/lib/api";
import { Search, X, FileQuestion } from "lucide-react";

const SAMPLE_DOCS: LegalDocItem[] = [
  {
    id: "doc-1",
    category: "luat",
    typeLabel: "Luật",
    typeBadgeBg: "bg-red-50 border-red-200",
    typeBadgeText: "text-red-700",
    title: "Luật Trật tự, an toàn giao thông đường bộ 2024",
    number: "Số 36/2024/QH15",
    date: "27/06/2024",
    status: "Hiệu lực từ 01/01/2025",
    desc: "Quy định toàn diện về quy tắc giao thông đường bộ; điều kiện phương tiện tham gia giao thông; người điều khiển phương tiện; chỉ huy, điều khiển giao thông và giải quyết tai nạn giao thông đường bộ.",
  },
  {
    id: "doc-2",
    category: "nghi-dinh",
    typeLabel: "Nghị định",
    typeBadgeBg: "bg-blue-50 border-blue-200",
    typeBadgeText: "text-blue-700",
    title: "Nghị định quy định xử phạt vi phạm hành chính trong lĩnh vực giao thông đường bộ và đường sắt",
    number: "Số 100/2019/NĐ-CP",
    date: "30/12/2019",
    status: "Đang có hiệu lực thi hành",
    desc: "Quy định chi tiết các mức phạt tiền, hình thức phạt bổ sung (tước quyền sử dụng giấy phép lái xe), biện pháp khắc phục hậu quả và tạm giữ phương tiện đối với người vi phạm.",
  },
  {
    id: "doc-3",
    category: "nghi-dinh",
    typeLabel: "Nghị định",
    typeBadgeBg: "bg-blue-50 border-blue-200",
    typeBadgeText: "text-blue-700",
    title: "Nghị định sửa đổi, bổ sung một số điều của các Nghị định quy định xử phạt vi phạm hành chính trong lĩnh vực hàng hải, giao thông đường bộ, đường sắt",
    number: "Số 123/2021/NĐ-CP",
    date: "28/12/2021",
    status: "Đang có hiệu lực thi hành",
    desc: "Tăng mạnh mức xử phạt đối với nhiều hành vi vi phạm có nguy cơ cao gây tai nạn giao thông: chạy quá tốc độ, không chấp hành đèn tín hiệu giao thông, đi ngược chiều trên cao tốc.",
  },
  {
    id: "doc-4",
    category: "quy-chuan",
    typeLabel: "Quy chuẩn",
    typeBadgeBg: "bg-emerald-50 border-emerald-200",
    typeBadgeText: "text-emerald-700",
    title: "Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ (QCVN 41:2019/BGTVT)",
    number: "Thông tư 54/2019/TT-BGTVT",
    date: "31/12/2019",
    status: "Đang có hiệu lực thi hành",
    desc: "Quy định quy chuẩn về hình dáng, kích thước, màu sắc và ý nghĩa của các loại biển báo hiệu đường bộ, vạch kẻ đường, đèn tín hiệu giao thông và các thiết bị phụ trợ.",
  },
];

export const LegalDocsView: React.FC = () => {
  const [docs, setDocs] = useState<LegalDocItem[]>(SAMPLE_DOCS);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("all");

  useEffect(() => {
    let isMounted = true;
    fetchLegalDocuments().then((res) => {
      if (isMounted && res && res.length > 0) {
        setDocs(res);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const filteredDocs = docs.filter((doc) => {
    const matchCat = activeCategory === "all" || doc.category === activeCategory;
    const matchSearch =
      !searchTerm ||
      doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.desc.toLowerCase().includes(searchTerm.toLowerCase());
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
            Các văn bản luật giao thông đường bộ cốt lõi được hệ thống AI trích xuất, đối soát và tham chiếu trả lời trực tiếp cho công dân.
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
              placeholder="Nhập số hiệu văn bản, từ khóa pháp lý (ví dụ: 100/2019, 36/2024, nồng độ cồn)..."
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
              { id: "luat", label: "Luật" },
              { id: "nghi-dinh", label: "Nghị định" },
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
          {filteredDocs.map((doc) => (
            <div
              key={doc.id}
              className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs hover:shadow-md transition-all flex flex-col gap-3"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${doc.typeBadgeBg} ${doc.typeBadgeText}`}>
                    {doc.typeLabel}
                  </span>
                  <span className="text-[12px] font-medium text-slate-500">{doc.number}</span>
                  <span className="text-[12px] text-slate-400">• Ngày ban hành: {doc.date}</span>
                </div>
                <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
                  {doc.status}
                </span>
              </div>
              <h3 className="text-[16px] font-bold text-slate-900 leading-snug">{doc.title}</h3>
              <p className="text-[13px] text-slate-600 leading-relaxed">{doc.desc}</p>
            </div>
          ))}
          {filteredDocs.length === 0 && (
            <div className="text-center py-12 text-slate-400 flex flex-col items-center">
              <FileQuestion size={44} className="mb-2 text-slate-300" />
              <p>Không tìm thấy văn bản phù hợp với từ khóa.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
