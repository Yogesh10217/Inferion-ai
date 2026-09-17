"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  GitBranch,
  Bot,
  Key,
  BookOpen,
  Brain,
  DollarSign,
  Building2,
  Puzzle,
  Settings,
  ExternalLink,
  Activity,
  ChevronRight,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/routing", label: "Routing Tracer", icon: GitBranch },
  { href: "/dashboard/agents", label: "Agent Sandbox", icon: Bot },
  { href: "/dashboard/keys", label: "API Keys", icon: Key },
  { href: "/dashboard/knowledge", label: "RAG Visualizer", icon: BookOpen },
  { href: "/dashboard/memory", label: "Memory Explorer", icon: Brain },
  { href: "/dashboard/finops", label: "FinOps", icon: DollarSign },
  { href: "/dashboard/orgs", label: "Orgs & Tenants", icon: Building2 },
  { href: "/dashboard/plugins", label: "Plugins", icon: Puzzle },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-[220px] bg-white border-r border-slate-200/60 flex flex-col z-40">
      {/* Logo */}
      <div className="px-5 pt-6 pb-5 border-b border-slate-100">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-xl bg-[#0a152d] flex items-center justify-center text-white font-bold text-sm shadow-sm">
            ✦
          </div>
          <div>
            <div className="font-display font-bold text-[13px] text-[#0a1b33] leading-none">
              Inferion AI
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">Admin Console</div>
          </div>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive =
            href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-[13px] font-medium transition-all ${
                isActive
                  ? "bg-[#0a152d] text-white shadow-sm"
                  : "text-[#64748b] hover:text-[#0a1b33] hover:bg-slate-50"
              }`}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 pb-5 pt-3 border-t border-slate-100 space-y-2">
        <a
          href="http://localhost:8002/docs"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2 px-3 py-2 rounded-xl text-[12px] font-medium text-slate-500 hover:text-[#0a1b33] hover:bg-slate-50 transition-all"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          API Docs
        </a>
        <div className="flex items-center gap-2 px-3 py-1.5">
          <Activity className="w-3 h-3 text-emerald-500" />
          <span className="text-[11px] text-emerald-600 font-medium">All systems healthy</span>
        </div>
      </div>
    </aside>
  );
}
