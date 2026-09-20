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
        {/* ── System Status Banner ─────────────────────────────────────────────── */}
        <div className="sticky top-0 z-50 flex items-center justify-between bg-slate-900 px-6 py-2 text-[12px] font-medium text-slate-200 border-b border-slate-800 shadow-sm">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-semibold text-white">Inferion Engine:</span>
            <span className="text-slate-400">Connected to Live Control Plane</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400 text-[11px]">
            <span>API: <strong className="text-emerald-400">Online</strong></span>
            <span>Version: <strong>v0.1.0</strong></span>
          </div>
        </div>
        {children}
      </div>
    </div>
  );
}
