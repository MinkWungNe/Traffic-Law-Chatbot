"use client";

import React, { useEffect, useRef } from "react";
import { useChatStore } from "@/stores/useChatStore";
import { MessageBubble } from "./MessageBubble";
import { StarterCards } from "./StarterCards";
import { Loader2 } from "lucide-react";

export const ChatScrollArea: React.FC = () => {
  const { messages, sendMessage, isLoading } = useChatStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, isLoading]);

  return (
    <div
      ref={scrollRef}
      id="chatScrollArea"
      className="absolute inset-0 w-full h-full overflow-y-auto px-4 md:px-8 py-6 z-10 select-text"
    >
      <div className="max-w-3xl h-full mx-auto flex flex-col gap-6 pb-30">
        {/* Welcome Hero khi chưa có tin nhắn */}
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center pt-10 md:pt-14 text-center max-w-2xl mx-auto">
            <h1 className="text-[24px] md:text-[28px] font-bold text-slate-900 tracking-tight leading-snug">
              Tôi có thể hỗ trợ gì về Luật Giao thông?
            </h1>
            <StarterCards onSelectPrompt={(prompt) => sendMessage(prompt)} />
          </div>
        ) : (
          /* Danh sách tin nhắn hội thoại */
          <div className="flex flex-col gap-6 pt-4 pb-30">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isLoading && (
              <div className="flex items-center gap-3 text-slate-400 text-[13px] animate-pulse">
                <div className="w-8 h-8 rounded-full bg-accent-red flex items-center justify-center shrink-0 p-1.5 shadow-xs">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src="/assets/Chatbot_Logo.svg" alt="" className="w-full h-full object-contain filter invert brightness-0" />
                </div>
                <div className="bg-white border border-slate-200/80 rounded-2xl px-4 py-2.5 shadow-xs flex items-center gap-2">
                  <Loader2 size={16} className="animate-spin text-accent-red shrink-0" />
                  <span>VinaLaw đang tra cứu căn cứ pháp luật...</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
