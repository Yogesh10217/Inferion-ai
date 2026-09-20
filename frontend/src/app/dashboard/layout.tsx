import type { Metadata } from "next";
import { Sidebar } from "@/components/dashboard/Sidebar";

export const metadata: Metadata = {
  title: "Inferion AI — Admin Dashboard",
  description: "Enterprise control plane for Inferion AI — routing, agents, memory, FinOps, and tenants.",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-[#f9fafb] overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 ml-[220px] overflow-auto">
        {/* ── Demo Mode Banner ─────────────────────────────────────────────── */}
        <div className="sticky top-0 z-50 flex items-center justify-center gap-2 bg-amber-400 px-4 py-2 text-[12px] font-semibold text-amber-900 shadow-sm">
          <span>⚠️</span>
          <span>
            DEMO MODE — All metrics and charts display simulated data. Connect
            the backend API to see live data.
          </span>
          <a
            href="https://github.com/Yogesh10217/Inferion-ai#-quick-start"
            target="_blank"
            rel="noopener noreferrer"
            className="ml-2 underline hover:text-amber-950"
          >
            Quick Start →
          </a>
        </div>
        {children}
      </div>
    </div>
  );
}
