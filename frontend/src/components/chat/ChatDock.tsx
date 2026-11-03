"use client";

import React, { useState, useRef, useEffect } from "react";
import { useChatStore } from "@/stores/useChatStore";
import { Paperclip, ArrowUp, Square, Info } from "lucide-react";

export const ChatDock: React.FC = () => {
  const {
    inputText, setInputText,
    sendMessage, stopGeneration, isLoading,
  } = useChatStore();

  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isMultiline, setIsMultiline] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage((curr) => (curr === msg ? null : curr));
    }, 3000);
  };

  const hasText = inputText.trim().length > 0;

  const adjustTextareaHeight = () => {
    const el = textareaRef.current;
    if (!el) return;

    const hasLineBreak = inputText.includes("\n");

    // Chỉ đưa về 1 dòng khi chuỗi rỗng hoàn toàn hoặc chỉ có khoảng trắng không chứa ký tự xuống dòng
    if (!inputText || (!hasLineBreak && inputText.trim() === "")) {
      setIsMultiline(false);
      el.style.height = "32px";
      return;
    }

    el.style.height = "auto";
    // Threshold giữa 1 dòng (32px) và 2 dòng (>= 44px)
    const isMulti = hasLineBreak || el.scrollHeight > 35;
    setIsMultiline(isMulti);

    if (isMulti) {
      const nextHeight = Math.min(el.scrollHeight, 120);
      el.style.height = `${Math.max(nextHeight, 44)}px`;
    } else {
      el.style.height = "32px";
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputText]);

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
    setIsMultiline(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = "32px";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const renderActionButtons = () => (
    <div
      className={`transition-opacity duration-200 ease-out flex items-center justify-center shrink-0 w-8 h-8 ${
        hasText || isLoading
          ? "opacity-100 pointer-events-auto"
          : "opacity-0 pointer-events-none"
      }`}
    >
      {isLoading ? (
        <button
          type="button"
          onClick={stopGeneration}
          className="w-8 h-8 rounded-full bg-slate-900 hover:bg-black text-white flex items-center justify-center transition-all duration-150 hover:scale-105 active:scale-95 shrink-0 shadow-xs cursor-pointer"
          title="Dừng phản hồi"
          aria-label="Dừng phản hồi"
        >
          <Square size={12} fill="currentColor" className="shrink-0" />
        </button>
      ) : (
        <button
          type="submit"
          className="w-8 h-8 rounded-full bg-accent-red hover:bg-red-700 text-white flex items-center justify-center transition-all duration-150 hover:scale-105 active:scale-95 shrink-0 shadow-xs cursor-pointer"
          title="Gửi câu hỏi"
          aria-label="Gửi câu hỏi"
        >
          <ArrowUp size={16} strokeWidth={2.5} className="shrink-0" />
        </button>
      )}
    </div>
  );

  return (
    <div
      id="chatDockLayer"
      className="fixed bottom-0 left-[270px] right-0 z-30 pointer-events-none select-none pb-3 pt-3 bg-gradient-to-t from-canvas/60 via-canvas/30 to-transparent"
    >
      <div className="w-full max-w-3xl mx-auto px-4 pointer-events-auto">
        {/* Subtle toast feedback thay thế alert */}
        {toastMessage && (
          <div className="flex justify-center mb-2 animate-slide-up">
            <div className="bg-slate-900/90 text-white text-[12px] font-medium px-3.5 py-1.5 rounded-full shadow-lg backdrop-blur-xs flex items-center gap-1.5 border border-slate-700/50">
              <Info size={14} className="text-accent-red shrink-0" />
              <span>{toastMessage}</span>
            </div>
          </div>
        )}

        {/* Thanh Chatdock với hiệu ứng slideUp khi xuất hiện */}
        <form
          onSubmit={handleSubmit}
          id="chatDockForm"
          className="spotlight-border relative bg-white border-2 border-subtle rounded-2xl shadow-lg px-3.5 py-2 flex flex-col transition-all duration-200 animate-slide-up"
          style={{ "--glow-color": "#b3b3b3", "--glow-size": "350px" } as React.CSSProperties}
        >
          <div
            className={`relative z-10 grid w-full transition-all duration-200 ${
              isMultiline
                ? "grid-cols-[auto_1fr_auto] gap-y-1.5"
                : "grid-cols-[auto_1fr_auto] items-center gap-x-2"
            }`}
            style={{
              gridTemplateAreas: isMultiline
                ? `"input input input" "divider divider divider" "attach spacer action"`
                : `"attach input action"`,
            }}
          >
            {/* 1. Nút đính kèm tệp */}
            <div style={{ gridArea: "attach" }} className="flex items-center shrink-0">
              <button
                type="button"
                onClick={() => showToast("Tính năng tải đính kèm hồ sơ, biên bản đang được phát triển.")}
                className="w-8 h-8 rounded-full text-slate-500 hover:text-primary-navy hover:bg-slate-100 transition-colors flex items-center justify-center shrink-0 cursor-pointer"
                title="Đính kèm tệp"
              >
                <Paperclip size={18} className="shrink-0" />
              </button>
            </div>

            {/* 2. Textarea duy nhất (Bảo toàn focus & con trỏ chuột tuyệt đối) */}
            <div style={{ gridArea: "input" }} className="w-full min-w-0">
              <textarea
                ref={textareaRef}
                rows={1}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Hỏi VinaLaw về luật giao thông, mức phạt, biển báo..."
                className={`w-full bg-transparent border-0 text-[14px] leading-[20px] text-slate-900 placeholder:text-slate-400 focus:ring-0 focus:outline-none resize-none overflow-y-auto block ${
                  isMultiline
                    ? "px-1 py-1 min-h-[44px] max-h-[120px]"
                    : "px-2 py-1.5 h-[32px]"
                }`}
              />
            </div>

            {/* 3. Đường kẻ phân tách giữa 2 tầng khi nhiều dòng */}
            {isMultiline && (
              <div
                style={{ gridArea: "divider" }}
                className="w-full h-px bg-slate-100/90 -my-0.5 animate-fade-in"
              />
            )}

            {/* 4. Spacer khoảng trống giữa attach và action ở hàng dưới */}
            {isMultiline && <div style={{ gridArea: "spacer" }} />}

            {/* 5. Cụm nút gửi / dừng với hiệu ứng fade */}
            <div style={{ gridArea: "action" }} className="flex items-center justify-end shrink-0">
              {renderActionButtons()}
            </div>
          </div>
        </form>
        <p className="text-center text-[11px] text-slate-400 mt-2">
          VinaLaw-Traffic có thể đưa ra kết quả tham khảo. Vui lòng đối chiếu với văn bản pháp luật hiện hành.
        </p>
      </div>
    </div>
  );
};
