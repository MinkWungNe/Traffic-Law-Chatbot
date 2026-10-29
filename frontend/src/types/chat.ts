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
  isStopped?: boolean;
}

export interface UserProfile {
  id: string;
  email: string;
  role: "admin" | "user";
  is_active: boolean;
  created_at?: string;
}

export interface SessionItem {
  id: string;
  title: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface AuditLogItem {
  id: string;
  actor_id?: string | null;
  actor_email: string;
  action: string;
  target_id?: string | null;
  target_email?: string | null;
  details?: Record<string, any> | null;
  ip_address?: string | null;
  user_agent?: string | null;
  created_at: string;
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
