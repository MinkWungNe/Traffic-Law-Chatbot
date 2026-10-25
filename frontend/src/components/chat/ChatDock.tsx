"use client";

import React from "react";
import { useChatStore } from "@/stores/useChatStore";

export const ChatDock: React.FC = () => {
  const { sendMessage, inputText, setInputText, isLoading } = useChatStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const query = inputText.trim();
    if (!query || isLoading) return;
    if (query.length < 2) {
      alert("Vui lòng nhập câu hỏi có ít nhất 2 ký tự.");
      return;
    }
    sendMessage(query);
  };

  return (
    <div
      id="chatDockLayer"
      className="fixed bottom-0 left-[270px] right-0 z-30 pointer-events-none select-none pb-3 pt-3 bg-gradient-to-t from-canvas/60 via-canvas/30 to-transparent"
    >
      <div className="w-full max-w-3xl mx-auto px-4 pointer-events-auto">
        <form
          onSubmit={handleSubmit}
          id="chatDockForm"
          className="spotlight-border relative bg-white border-2 border-subtle rounded-2xl shadow-lg px-3.5 py-2.5 flex flex-col gap-1 transition-all"
          style={{ "--glow-color": "#b3b3b3", "--glow-size": "350px" } as React.CSSProperties}
        >
          <div className="relative z-10 flex items-center gap-2">
            {/* Nút đính kèm file */}
            <button
              type="button"
              onClick={() => alert("Tính năng tải đính kèm hồ sơ, biên bản đang được phát triển.")}
              className="p-1.5 rounded-full text-slate-500 hover:text-primary-navy hover:bg-slate-100 transition-colors flex items-center justify-center shrink-0 cursor-pointer"
              title="Đính kèm tệp"
            >
              <span className="material-symbols-outlined text-[20px]">attach_file</span>
            </button>

            {/* Nút tải ảnh hiện trường */}
            <button
              type="button"
              onClick={() => alert("Tính năng phân tích hình ảnh hiện trường vi phạm đang được phát triển.")}
              className="p-1.5 rounded-full text-slate-500 hover:text-primary-navy hover:bg-slate-100 transition-colors flex items-center justify-center shrink-0 cursor-pointer"
              title="Tải ảnh hiện trường"
            >
              <span className="material-symbols-outlined text-[20px]">add_photo_alternate</span>
            </button>

            {/* Ô nhập câu hỏi */}
            <input
              type="text"
              autoComplete="off"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Hỏi VinaLaw về luật giao thông, mức phạt, biển báo..."
              className="w-full bg-transparent border-0 text-[14px] text-slate-900 placeholder:text-slate-400 focus:ring-0 focus:outline-none px-2 py-1"
            />

            {/* Nút gửi đỏ tròn */}
            <button
              type="submit"
              disabled={isLoading || inputText.trim().length < 2}
              className="w-8 h-8 rounded-full bg-accent-red hover:bg-red-700 disabled:opacity-30 text-white flex items-center justify-center transition-transform hover:scale-105 shrink-0 shadow-xs cursor-pointer"
              title="Gửi câu hỏi"
            >
              <span className="material-symbols-outlined text-[17px]">arrow_upward</span>
            </button>
          </div>
        </form>
        <p className="text-center text-[11px] text-slate-400 mt-2">
          VinaLaw-Traffic có thể đưa ra kết quả tham khảo. Vui lòng đối chiếu với văn bản pháp luật hiện hành.
        </p>
      </div>
    </div>
  );
};