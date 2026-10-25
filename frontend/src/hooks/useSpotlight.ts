"use client";

import { useEffect } from "react";

/**
 * Hook tự động điều phối hiệu ứng Spotlight Border toàn hệ thống.
 * - Lắng nghe di chuyển chuột và cập nhật biến CSS --mouse-x, --mouse-y trên các phần tử .spotlight-border.
 * - Tự động dọn sạch biến CSS khi con trỏ di chuyển ra ngoài hoặc rời cửa sổ, trả viền về mặc định.
 */
export function useSpotlight() {
  useEffect(() => {
    let currentSpotlight: HTMLElement | null = null;

    const handleMouseMove = (e: MouseEvent) => {
      const target = (e.target as HTMLElement | null)?.closest?.(".spotlight-border") as HTMLElement | null;

      // Khi con trỏ di chuyển ra ngoài hoặc sang phần tử khác: reset phần tử cũ
      if (currentSpotlight && currentSpotlight !== target) {
        currentSpotlight.style.removeProperty("--mouse-x");
        currentSpotlight.style.removeProperty("--mouse-y");
        currentSpotlight = null;
      }

      if (target) {
        currentSpotlight = target;
        const rect = target.getBoundingClientRect();
        target.style.setProperty("--mouse-x", `${e.clientX - rect.left}px`);
        target.style.setProperty("--mouse-y", `${e.clientY - rect.top}px`);
      }
    };

    const handleMouseLeave = () => {
      if (currentSpotlight) {
        currentSpotlight.style.removeProperty("--mouse-x");
        currentSpotlight.style.removeProperty("--mouse-y");
        currentSpotlight = null;
      }
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    document.addEventListener("mouseleave", handleMouseLeave, { passive: true });

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseleave", handleMouseLeave);
      if (currentSpotlight) {
        currentSpotlight.style.removeProperty("--mouse-x");
        currentSpotlight.style.removeProperty("--mouse-y");
      }
    };
  }, []);
}
