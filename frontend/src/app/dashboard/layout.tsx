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
        {children}
      </div>
    </div>
  );
}
