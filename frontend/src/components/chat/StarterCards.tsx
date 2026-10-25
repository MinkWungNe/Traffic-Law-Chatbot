"use client";

import React from "react";
import { StarterCardItem } from "@/types/chat";

interface StarterCardsProps {
  onSelectPrompt: (prompt: string) => void;
}

const STARTER_CARDS: StarterCardItem[] = [
  {
    id: "card-speed",
    icon: "speed",
    title: "Vi phạm tốc độ",
    description: "Mức phạt chạy quá tốc độ 10-20km/h...",
    prompt:
      "Quy định tốc độ tối đa cho phép và mức xử phạt hành vi chạy quá tốc độ từ 10km/h đến 20km/h đối với xe máy và ô tô theo luật hiện hành?",
    glowColor: "#E11D48",
    iconBg: "bg-rose-50 border-rose-100",
    iconColor: "text-rose-600",
    hoverArrowColor: "group-hover:text-rose-600",
  },
  {
    id: "card-alcohol",
    icon: "no_drinks",
    title: "Nồng độ cồn & Ma túy",
    description: "Mức phạt kịch khung & tước GPLX...",
    prompt:
      "Mức phạt vi phạm nồng độ cồn vượt quá 0.4mg/l khí thở đối với xe máy và ô tô năm 2026? Có bị giữ phương tiện và tước giấy phép lái xe bao lâu?",
    glowColor: "#D97706",
    iconBg: "bg-amber-50 border-amber-100",
    iconColor: "text-amber-600",
    hoverArrowColor: "group-hover:text-amber-600",
  },
  {
    id: "card-fine",
    icon: "videocam",
    title: "Phạt nguội & Đăng kiểm",
    description: "Cách kiểm tra lỗi phạt nguội chưa...",
    prompt:
      "Quy trình tra cứu thông báo phạt nguội trực tuyến toàn quốc và thủ tục nộp phạt trước khi đi đăng kiểm xe ô tô?",
    glowColor: "#2563EB",
    iconBg: "bg-blue-50 border-blue-100",
    iconColor: "text-blue-600",
    hoverArrowColor: "group-hover:text-blue-600",
  },
  {
    id: "card-signs",
    icon: "traffic",
    title: "Quy chuẩn biển báo & Làn đ...",
    description: "Biển cấm rẽ trái có cấm quay đầu...",
    prompt:
      "Quy chuẩn biển báo đường bộ: Biển cấm rẽ trái có cấm quay đầu xe không và mức phạt đối với lỗi đi sai làn đường, không tuân thủ vạch kẻ đường?",
    glowColor: "#059669",
    iconBg: "bg-emerald-50 border-emerald-100",
    iconColor: "text-emerald-600",
    hoverArrowColor: "group-hover:text-emerald-600",
  },
];

export const StarterCards: React.FC<StarterCardsProps> = ({ onSelectPrompt }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 max-w-2xl mx-auto w-full mt-7">
      {STARTER_CARDS.map((card) => (
        <button
          key={card.id}
          onClick={() => onSelectPrompt(card.prompt)}
          className="starter-card spotlight-border group relative bg-white border border-subtle rounded-xl p-3 text-left transition-all cursor-pointer shadow-xs"
          style={{ "--glow-color": card.glowColor } as React.CSSProperties}
        >
          <div className="relative z-10 flex items-center gap-3.5 w-full min-w-0">
            <div
              className={`w-10 h-10 rounded-full border flex items-center justify-center shrink-0 ${card.iconBg}`}
            >
              <span className={`material-symbols-outlined text-[20px] ${card.iconColor}`}>
                {card.icon}
              </span>
            </div>
            <div className="flex flex-col min-w-0 flex-1 pr-1">
              <span className="text-[13.5px] font-bold text-slate-900 truncate leading-snug group-hover:text-primary-navy transition-colors">
                {card.title}
              </span>
              <span className="text-[12px] text-slate-400 font-normal truncate mt-0.5 leading-tight">
                {card.description}
              </span>
            </div>
            <span
              className={`material-symbols-outlined text-[18px] text-slate-400 ${card.hoverArrowColor} group-hover:translate-x-0.5 transition-all shrink-0`}
            >
              arrow_forward
            </span>
          </div>
        </button>
      ))}
    </div>
  );
};
