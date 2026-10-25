"use client";

import React from "react";

/* Layer 0: Họa tiết nền Trống đồng Đông Sơn xoay độc lập (Ambient Horizon Layer 0) */
export const DongSonAmbient: React.FC = () => {
  return (
    <div
      id="dongsonAmbientLayer"
      className="absolute inset-0 w-full h-full pointer-events-none select-none overflow-hidden z-0"
      aria-hidden="true"
    >
      <div
        className="w-[90%] aspect-square absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none select-none opacity-[0.1] transition-opacity duration-600"
        style={{
          maskImage: "radial-gradient(circle closest-side at 50% 50%, #000 35%, rgba(0,0,0,0.7) 60%, rgba(0,0,0,0.2) 82%, transparent 95%)",
          WebkitMaskImage: "radial-gradient(circle closest-side at 50% 50%, #000 35%, rgba(0,0,0,0.7) 60%, rgba(0,0,0,0.2) 82%, transparent 95%)",
        }}
      >
        <div className="w-full h-full animate-[spinDongSonCounterClockwise_120s_linear_infinite] will-change-transform [transform-origin:50%_50%]">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/assets/TrongDongDongSon.svg"
            alt=""
            className="w-full h-full object-contain pointer-events-none select-none block"
            loading="eager"
          />
        </div>
      </div>
    </div>
  );
};
