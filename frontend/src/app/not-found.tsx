import React from "react";
import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex h-screen w-screen flex-col items-center justify-center bg-canvas p-6 text-text-main font-sans">
      <div className="flex flex-col items-center text-center max-w-md mx-auto">
        {/* Hàng số 404 với số 0 được thay thế bằng hình CarCrash */}
        <div className="flex items-center justify-center gap-2 text-primary-navy font-extrabold text-[100px] leading-none select-none">
          <span>4</span>
          <div className="w-[88px] h-[88px] flex items-center justify-center text-primary-navy">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/assets/CarCrash.svg"
              alt="Car Crash"
              className="w-full h-full object-contain [filter:brightness(0)_saturate(100%)_invert(17%)_sepia(57%)_saturate(1700%)_hue-rotate(195deg)_brightness(94%)_contrast(92%)]"
            />
          </div>
          <span>4</span>
        </div>

        {/* Dòng chữ báo lỗi thuần văn bản (không badge, không toast) */}
        <p className="mt-4 text-[15px] text-slate-600 font-medium leading-relaxed">
          Trang bạn đang tìm kiếm không tồn tại hoặc đã bị di chuyển.
        </p>

        {/* Nút đưa về trang chủ */}
        <Link
          href="/"
          className="mt-6 inline-flex items-center justify-center px-6 py-2.5 rounded-xl bg-primary-navy hover:bg-slate-800 text-white text-[14px] font-semibold transition-colors duration-150 shadow-xs cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-navy/40"
        >
          Về trang chủ
        </Link>
      </div>
    </main>
  );
}
