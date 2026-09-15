import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Inferion AI | High-Performance LLM Inference Engine",
  description: "High-throughput LLM inference for modern AI applications. Real-time model serving, dynamic batching, and enterprise governance with sub-millisecond latency.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-[#f9fafb] text-[#0a1b33] selection:bg-[#0a1b33] selection:text-white">
        {children}
      </body>
    </html>
  );
}
