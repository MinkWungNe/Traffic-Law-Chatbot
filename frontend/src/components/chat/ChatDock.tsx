"use client";

import React, { useState } from "react";
import { useChatStore } from "@/stores/useChatStore";
import { Paperclip, ImagePlus, ArrowUp, Square, Info } from "lucide-react";

export const ChatDock: React.FC = () => {
  const {
    inputText, setInputText,
    sendMessage, stopGeneration, isLoading,
  } = useChatStore();

  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage((curr) => (curr === msg ? null : curr));
    }, 3000);
  };

  const hasText = inputText.trim().length > 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) {
      stopGeneration();
      return;
    }
    const query = inputText.trim();
    if (!query) return;
    if (query.length < 2) {
      showToast("Vui lòng nhập câu hỏi có ít nhất 2 ký tự.");
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
        {/* Subtle toast feedback thay thế alert */}
        {toastMessage && (
          <div className="flex justify-center mb-2 animate-in fade-in slide-in-from-bottom-2 duration-150">
            <div className="bg-slate-900/90 text-white text-[12px] font-medium px-3.5 py-1.5 rounded-full shadow-lg backdrop-blur-xs flex items-center gap-1.5 border border-slate-700/50">
              <Info size={14} className="text-accent-red shrink-0" />
              <span>{toastMessage}</span>
            </div>
          </div>
        )}

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
              onClick={() => showToast("Tính năng tải đính kèm hồ sơ, biên bản đang được phát triển.")}
              className="p-1.5 rounded-full text-slate-500 hover:text-primary-navy hover:bg-slate-100 transition-colors flex items-center justify-center shrink-0 cursor-pointer"
              title="Đính kèm tệp"
            >
              <Paperclip size={18} className="shrink-0" />
            </button>

            {/* Nút tải ảnh hiện trường */}
            <button
              type="button"
              onClick={() => showToast("Tính năng phân tích hình ảnh hiện trường vi phạm đang được phát triển.")}
              className="p-1.5 rounded-full text-slate-500 hover:text-primary-navy hover:bg-slate-100 transition-colors flex items-center justify-center shrink-0 cursor-pointer"
              title="Tải ảnh hiện trường"
            >
              <ImagePlus size={18} className="shrink-0" />
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

            {/* Nút gửi / Dừng câu hỏi */}
            {isLoading ? (
              <button
                type="button"
                onClick={stopGeneration}
                className="w-8 h-8 rounded-full bg-slate-900 hover:bg-black text-white flex items-center justify-center transition-all duration-150 hover:scale-105 active:scale-95 shrink-0 shadow-xs cursor-pointer animate-in fade-in zoom-in-75"
                title="Dừng phản hồi"
                aria-label="Dừng phản hồi"
              >
                <Square size={12} fill="currentColor" className="shrink-0" />
              </button>
            ) : hasText ? (
              <button
                type="submit"
                className="w-8 h-8 rounded-full bg-accent-red hover:bg-red-700 text-white flex items-center justify-center transition-all duration-150 hover:scale-105 active:scale-95 shrink-0 shadow-xs cursor-pointer animate-in fade-in zoom-in-75"
                title="Gửi câu hỏi"
                aria-label="Gửi câu hỏi"
              >
                <ArrowUp size={16} strokeWidth={2.5} className="shrink-0" />
              </button>
            ) : null}
          </div>
        </form>
        <p className="text-center text-[11px] text-slate-400 mt-2">
          VinaLaw-Traffic có thể đưa ra kết quả tham khảo. Vui lòng đối chiếu với văn bản pháp luật hiện hành.
        </p>
      </div>
    </div>
  );
};
