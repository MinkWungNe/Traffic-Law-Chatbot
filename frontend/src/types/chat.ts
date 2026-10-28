import type { LucideIcon } from "lucide-react";

export interface Citation {
  title: string;
  snippet?: string;
  score?: number | null;
  article?: string;
  penalty?: string;
  link?: string;
  raw?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "bot";
  content: string;
  sources?: Citation[];
  timestamp?: string;
  isFallback?: boolean;
}

export interface UserProfile {
  username: string;
  fullName?: string;
  avatar?: string;
  token?: string;
}

export interface StarterCardItem {
  id: string;
  icon: LucideIcon;
  title: string;
  description: string;
  prompt: string;
  glowColor: string;
  iconBg: string;
  iconColor: string;
  cardBorder?: string;
  hoverArrowColor?: string;
}
