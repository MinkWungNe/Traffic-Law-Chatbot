import type { Metadata } from "next";
import { Be_Vietnam_Pro } from "next/font/google";
import "./globals.css";

const beVietnamPro = Be_Vietnam_Pro({
  weight: ["300", "400", "500", "600", "700"],
  subsets: ["latin", "vietnamese"],
  variable: "--font-be-vietnam-pro",
  display: "swap",
});

export const metadata: Metadata = {
  title: "VinaLaw-Traffic - Trợ lý AI Luật Giao thông",
  description: "Hệ thống tư vấn pháp luật giao thông đường bộ Việt Nam thông minh",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className={`${beVietnamPro.variable} h-full antialiased`}>
      <body className="h-full w-full overflow-hidden select-none bg-canvas text-text-main font-sans">
        {children}
      </body>
    </html>
  );
}
