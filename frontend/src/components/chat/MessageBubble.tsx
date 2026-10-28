"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChatMessage } from "@/types/chat";
import { useChatStore } from "@/stores/useChatStore";
import { User, BookOpen, Copy, Check, ThumbsUp, ThumbsDown } from "lucide-react";

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const { sendMessage } = useChatStore();
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState<boolean | null>(null);

  if (message.role === "user") {
    return (
      <div className="flex items-start justify-end gap-3 w-full max-w-2xl ml-auto">
        <div className="flex flex-col items-end gap-1">
          <div className="bg-primary-navy text-white rounded-2xl rounded-tr-xs px-4 py-3 text-[14px] leading-relaxed shadow-xs">
            {message.content}
          </div>
          {message.timestamp && (
            <span className="text-[11px] text-slate-400 mr-1">{message.timestamp}</span>
          )}
        </div>
        <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300 flex items-center justify-center shrink-0 text-slate-600 font-semibold text-[13px]">
          <User size={18} className="shrink-0" />
        </div>
      </div>
    );
  }

  // AI Message
  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const followUpChips = [
    "Quy trình nộp phạt nguội online như thế nào?",
    "Biển phụ nào thì xe máy được rẽ phải khi đèn đỏ?",
    "Thủ tục nộp phạt và nhận lại bằng lái xe bị tạm giữ?",
  ];

  return (
    <div className="flex items-start gap-3 w-full max-w-3xl">
      <div className="w-8 h-8 rounded-full bg-accent-red flex items-center justify-center shrink-0 p-1.5 shadow-xs">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/assets/Chatbot_Logo.svg" alt="" className="w-full h-full object-contain filter invert brightness-0" />
      </div>

      <div className="flex-1 bg-white border border-slate-200/80 rounded-2xl p-5 shadow-xs flex flex-col gap-4 text-[13.5px] leading-relaxed">
        {/* Header với Live API / Offline Badge */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-2">
          <span className="font-semibold text-primary-navy text-[13px]">VinaLaw Assistant</span>
          {message.isFallback === false ? (
            <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              FastAPI RAG Live
            </span>
          ) : message.isFallback === true ? (
            <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
              Dữ liệu Offline dự phòng
            </span>
          ) : null}
        </div>

        {/* Markdown Response Content */}
        <div className="prose prose-slate max-w-none text-slate-800 text-[13.5px] leading-relaxed [&>h3]:text-[15px] [&>h3]:font-bold [&>h3]:text-primary-navy [&>h3]:mb-2 [&>h4]:text-[14px] [&>h4]:font-bold [&>h4]:text-slate-900 [&>h4]:mt-3 [&>h4]:mb-1 [&>ul]:list-disc [&>ul]:pl-5 [&>ul]:my-2 [&>p]:my-2 [&>blockquote]:border-l-4 [&>blockquote]:border-primary-navy [&>blockquote]:pl-3 [&>blockquote]:italic [&>blockquote]:text-slate-600">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>

        {/* Legal Citations if available */}
        {message.sources && message.sources.length > 0 && (
          <div className="flex flex-col gap-2 pt-3 border-t border-slate-100">
            <div className="text-[11.5px] font-bold text-slate-400 tracking-wider uppercase flex items-center gap-1.5">
              <BookOpen size={15} className="text-primary-navy shrink-0" />
              Căn cứ pháp lý nguyên văn
            </div>
            <div className="flex flex-col gap-2">
              {message.sources.map((src, i) => {
                const excerpt = src.snippet || src.raw;
                return (
                  <div key={i} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 flex flex-col gap-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-semibold text-slate-900 text-[12.5px]">{src.title}</span>
                      {typeof src.score === "number" && (
                        <span className="text-[10.5px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded shrink-0">
                          Độ khớp: {Math.round(src.score * 100)}%
                        </span>
                      )}
                    </div>
                    {excerpt && <p className="text-slate-600 text-[12px] italic leading-relaxed">{excerpt}</p>}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Action Toolbar & Follow-up Chips */}
        <div className="flex flex-col gap-2.5 pt-2 border-t border-slate-100">
          <div className="flex items-center justify-between text-slate-400 text-[12px]">
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={handleCopy}
                className="p-1.5 rounded-md hover:bg-slate-100 hover:text-slate-700 transition-colors flex items-center justify-center cursor-pointer"
                title="Sao chép"
              >
                {copied ? (
                  <Check size={16} className="text-emerald-600 shrink-0" />
                ) : (
                  <Copy size={16} className="shrink-0" />
                )}
              </button>
              <button
                type="button"
                onClick={() => setLiked(liked === true ? null : true)}
                className={`p-1.5 rounded-md hover:bg-slate-100 transition-colors flex items-center justify-center cursor-pointer ${
                  liked === true ? "text-emerald-600" : "hover:text-slate-700"
                }`}
                title="Hữu ích"
              >
                <ThumbsUp size={16} className="shrink-0" />
              </button>
              <button
                type="button"
                onClick={() => setLiked(liked === false ? null : false)}
                className={`p-1.5 rounded-md hover:bg-slate-100 transition-colors flex items-center justify-center cursor-pointer ${
                  liked === false ? "text-red-600" : "hover:text-slate-700"
                }`}
                title="Chưa hài lòng"
              >
                <ThumbsDown size={16} className="shrink-0" />
              </button>
            </div>
            {message.timestamp && <span>{message.timestamp}</span>}
          </div>

          {/* Follow-up chips */}
          <div className="flex flex-wrap items-center gap-2 pt-0.5">
            <span className="text-[11.5px] font-medium text-slate-500">Hỏi tiếp:</span>
            {followUpChips.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => sendMessage(chip)}
                className="px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200/80 border border-slate-200 text-[11.5px] text-slate-700 transition-colors cursor-pointer"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
