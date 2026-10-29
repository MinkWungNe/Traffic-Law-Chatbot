"use client";

import React from "react";
import { useSpotlight } from "@/hooks/useSpotlight";
import { useChatStore } from "@/stores/useChatStore";
import { Sidebar } from "@/components/layout/Sidebar";
import { DongSonAmbient } from "@/components/ambient/DongSonAmbient";
import { ChatScrollArea } from "@/components/chat/ChatScrollArea";
import { ChatDock } from "@/components/chat/ChatDock";
import { LegalDocsView } from "@/components/views/LegalDocsView";
import { FAQView } from "@/components/views/FAQView";
import { LoginView } from "@/components/views/LoginView";
import { AdminView } from "@/components/views/AdminView";

export default function Home() {
  // Kích hoạt bộ điều phối Spotlight Border toàn hệ thống
  useSpotlight();

  const { activeTab } = useChatStore();

  // Màn hình Đăng nhập (Full Screen 4 Layers)
  if (activeTab === "login") {
    return <LoginView />;
  }

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-canvas select-none">
      {/* Cột Trái: Sidebar 270px cố định */}
      <Sidebar />

      {/* Cột Phải: Viewport chính với kiến trúc 3 tầng xếp lớp (3-Layer Viewport Stacking) */}
      <section className="flex-1 h-screen relative overflow-hidden flex flex-col min-w-0">
        {/* Layer 0: Họa tiết Trống đồng Đông Sơn 90% xoay độc lập 120s nền chung cho mọi tab */}
        {activeTab !== "admin" && <DongSonAmbient />}

        {/* Nội dung chính theo Tab */}
        {activeTab === "chat" && (
          <>
            {/* Layer 10: Khung cuộn tin nhắn chiếm trọn 100vh */}
            <ChatScrollArea />
            {/* Layer 30: Thanh Chat Dock nổi cố định ở đáy */}
            <ChatDock />
          </>
        )}

        {activeTab === "docs" && <LegalDocsView />}

        {activeTab === "faq" && <FAQView />}

        {activeTab === "admin" && <AdminView />}
      </section>
    </main>
  );
}
